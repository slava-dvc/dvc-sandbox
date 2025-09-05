import base64
import gzip
from http import HTTPStatus
from typing import Dict
from fastapi import Body
from fastapi import APIRouter, Depends, Request
from google.cloud import storage
from google.cloud import pubsub_v1

from app.foundation import as_async
from app.foundation.primitives import datetime, json
from app.foundation.server import dependencies, Logger, AppConfig
from app.shared.dependencies import get_genai_client
from infrastructure.queues.meeting_transcripts import transcript_topic_name
from .meeting_processor import MeetingProcessor


router = APIRouter(
    prefix="/meeting",
)

public_router = APIRouter(
    prefix="/meeting",
    tags=["public"]
)


@router.post("/transcript", status_code=HTTPStatus.ACCEPTED)
@public_router.post("/transcript", status_code=HTTPStatus.ACCEPTED)
async def store_transcript(
    request: Request,
    config: AppConfig = Depends(dependencies.get_config),
    logger: Logger = Depends(dependencies.get_logger),
    dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
    publisher: pubsub_v1.PublisherClient = Depends(dependencies.get_publisher_client),
):
    """Store meeting transcript to GCS bucket and publish to Pub/Sub"""
    # Get raw JSON body
    body = await request.json()
    
    # Add timestamp metadata
    body['receivedAt'] = datetime.now()
    
    # Generate timestamp-based filename
    timestamp = datetime.to_tz(datetime.now(), datetime.US_Pacific).strftime("%Y-%m-%d-%H-%M")
    filename = f"meetings/{timestamp}.json.gz"
    
    # Compress JSON data
    data = json.dumps(body)
    compressed_data = gzip.compress(data.encode('utf-8'))
    
    # Upload to bucket
    blob = dataset_bucket.blob(filename)
    blob.content_encoding = 'gzip'
    await as_async(
        blob.upload_from_string,
        data=compressed_data,
        content_type='application/json',
    )
    
    # Publish to Pub/Sub topic
    project_id = config['project_id']
    topic_path = publisher.topic_path(project_id, transcript_topic_name)
    message_data = data.encode('utf-8')
    
    # Use receivedAt as ordering key
    ordering_key = body['receivedAt'].isoformat()
    future = publisher.publish(topic_path, message_data, ordering_key=ordering_key)
    message_id = await as_async(future.result)
    
    logger.info("Stored meeting transcript", labels={
        "filename": filename,
        "bucketName": dataset_bucket.name,
        "compressedSize": len(compressed_data),
        "messageId": message_id,
        "topicName": transcript_topic_name
    })

    return


@router.post("/transcript/consume", status_code=HTTPStatus.OK)
async def consume_transcript(
    transcript_data: Dict = Body(),
    logger: Logger = Depends(dependencies.get_logger),
    database = Depends(dependencies.get_default_database),
    genai_client = Depends(get_genai_client),
):
    """Process meeting transcript from Pub/Sub"""

    logger.info(f"Starting meeting transcript processing", labels={
        "receivedAt": transcript_data.get('receivedAt'),
    })
    
    # Process meeting transcript
    processor = MeetingProcessor(
        genai_client=genai_client,
        database=database,
        logger=logger
    )
    
    result = await processor(transcript_data)
    
    logger.info(f"Finished meeting transcript processing", labels={
        "meetingProcessingResult": result,
    })

    return
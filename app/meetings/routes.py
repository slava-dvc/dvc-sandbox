import gzip
from http import HTTPStatus
from fastapi import APIRouter, Depends, Request
from google.cloud import storage

from app.foundation import as_async
from app.foundation.primitives import datetime, json
from app.foundation.server import dependencies, Logger


router = APIRouter(
    prefix="/meeting",
)


@router.post("/transcript", status_code=HTTPStatus.ACCEPTED)
async def store_transcript(
    request: Request,
    logger: Logger = Depends(dependencies.get_logger),
    dataset_bucket: storage.Bucket = Depends(dependencies.get_dataset_bucket),
):
    """Store meeting transcript to GCS bucket"""
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
    
    logger.info("Stored meeting transcript", labels={
        "filename": filename,
        "bucketName": dataset_bucket.name,
        "compressedSize": len(compressed_data)
    })

    return
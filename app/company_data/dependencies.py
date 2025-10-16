from fastapi import Request, Depends
from pymongo.asynchronous.database import AsyncDatabase
from google.cloud import pubsub

from app.foundation.server import dependencies, Logger
from app.company_data.job_dispatcher import JobDispatcher

__all__ = ['get_job_dispatcher']


def get_job_dispatcher(
    database: AsyncDatabase = Depends(dependencies.get_default_database),
    publisher_client: pubsub.PublisherClient = Depends(dependencies.get_publisher_client),
    logger: Logger = Depends(dependencies.get_logger),
    request: Request = None
) -> JobDispatcher:
    """Dependency to get JobDispatcher instance"""
    config = request.state.config
    return JobDispatcher(
        database=database,
        publisher_client=publisher_client,
        project_id=config['project_id'],
        logger=logger
    )
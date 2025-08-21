from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from pymongo.asynchronous.database import AsyncDatabase

from app.foundation.server import dependencies, Logger
from app.jobs.crud import Crud
from app.jobs.formatter import JobsFormatter

router = APIRouter(
    prefix="/jobs",
)


@router.get("")
async def get_jobs(
    format: str | None = Query(None, description="Output format (markdown)"),
    database: AsyncDatabase = Depends(dependencies.get_default_database),
    logger: Logger = Depends(dependencies.get_logger),
):
    """Get jobs list, optionally formatted as markdown"""
    crud = Crud(database)

    jobs = await crud.get_jobs()

    if format == "markdown":
        return PlainTextResponse(
            content=JobsFormatter(jobs).as_markdown(),
            media_type="text/markdown"
        )

    return {"jobs": [job.model_dump(by_alias=True) for job in jobs], "count": len(jobs)}
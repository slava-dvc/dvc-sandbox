from typing import List
from pymongo.asynchronous.database import AsyncDatabase
from app.foundation.primitives import datetime
from app.jobs.models import Job


class Crud(object):
    """Data access layer for jobs collection"""
    def __init__(self, database: AsyncDatabase):
        self._database = database
        self._jobs_collection = database["jobs"]
    
    async def get_jobs(self) -> List[Job]:
        """Fetch recent jobs from MongoDB jobs collection"""
        two_weeks_ago = datetime.now() - datetime.timedelta(weeks=2)
        query = {'updatedAt': {'$gte': two_weeks_ago}}
        cursor = self._jobs_collection.find(query).sort('updatedAt', -1)
        jobs_data = await cursor.to_list(length=None)
        return [Job.model_validate(job) for job in jobs_data]
    

from pymongo.asynchronous.database import AsyncDatabase
from google import genai

from app.foundation.server import Logger
from app.foundation.primitives import datetime
from app.shared.company import Company


class MeetingProcessor:
    
    def __init__(
        self,
        genai_client: genai.Client,
        database: AsyncDatabase,
        logger: Logger
    ):
        self._genai_client = genai_client
        self._meeting_collection = database["meetings"]
        self._companies_collection = database["companies"]
        self._logger = logger

    async def __call__(self, meeting_data: dict) -> dict:
        """Process meeting transcript data and extract insights"""
        calendar_event = meeting_data.get('calendar_event') or {}
        recording = meeting_data.get('recording') or {}
        recap = meeting_data.get('recap') or ''
        should_process, reason = self._should_process(calendar_event, recording)
        if not should_process:
            return {
                'processed': False,
                'reason': reason,
            }

        attendees = calendar_event.get('attendees') or []
        company = await self._find_company_from_attendees(attendees)
        if not company:
            return {
                'processed': False,
                'reason': "No company found",
                'attendees': calendar_event.get('attendees') or [],
            }

        await self._store_meeting(company, calendar_event, recap, recording)

        return {
            'processed': True,
        }

    async def _find_company_from_attendees(self, attendees):
        domains = set()
        
        for attendee in attendees:
            email = attendee.get('email', '')
            if not email or email.endswith('@davidovs.com'):
                continue
            
            domain = email.split('@')[-1] if '@' in email else None
            if domain:
                domains.add(domain)
        
        if not domains:
            return None
        
        companies = await self._companies_collection.find({"domain": {"$in": list(domains)}}).to_list(None)
        
        if len(companies) == 1:
            return Company.model_validate(companies[0])
        elif len(companies) > 1:
            company_names = [c.get('name', 'Unknown') for c in companies]
            self._logger.warning("Multiple companies in meeting - ambiguous attribution", labels={
                "companies": company_names,
                "count": len(companies)
            })
            return None
        else:
            return None

    async def _store_meeting(self, company: Company, calendar_event: dict, recap: str, recording: dict):
        calendar_event_id = calendar_event.get('id')
        if not calendar_event_id:
            self._logger.warning("No meeting ID found in calendar event")
            return
        
        # Remove fields that start with __
        clean_calendar_event = {k: v for k, v in calendar_event.items() if not k.startswith('__')}
        
        meeting_doc = {
            "calendarEventId": calendar_event_id,
            "companyId": company.id,
            "company": company.model_dump(exclude=company.DATA_FIELDS),
            "calendarEvent": clean_calendar_event,
            "recap": recap,
            "recordingUrl": recording.get('videoUrl'),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
        }
        
        await self._meeting_collection.replace_one(
            {"calendarEventId": calendar_event_id},
            meeting_doc,
            upsert=True
        )
        
        self._logger.info("Stored meeting", labels={
            "calendarEventId": calendar_event_id,
            "companyId": company.id,
            "companyName": company.name,
        })

    def _should_process(self, calendar_event: dict, recording: dict) -> tuple[bool, str]:
        if calendar_event.get('calendarId') != 'deals@davidovs.com':
            return False, "Not a deal meeting"
        if not recording.get('transcript'):
            return False, "No transcript"
        return True, "Valid meeting"

from app.shared.company import CompanyStatus

__all__ = ["ACTIVE_COMPANY_STATUSES"]

ACTIVE_COMPANY_STATUSES = [
    CompanyStatus.INVESTED,
    CompanyStatus.NEW_COMPANY,
    CompanyStatus.OFFERED_TO_INVEST,
    CompanyStatus.SUBMITTED_AL,
    CompanyStatus.DILIGENCE,
    CompanyStatus.CONTACTED,
    CompanyStatus.MEETING,
    CompanyStatus.CHECKIN,
    CompanyStatus.DOCS_SENT,
    CompanyStatus.RADAR
]
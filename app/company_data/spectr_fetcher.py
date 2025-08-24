from http import HTTPStatus
from httpx import HTTPStatusError

from app.shared import Company, SpectrClient
from app.foundation.primitives import datetime
from app.foundation.server import Logger
from .data_syncer import DataFetcher, FetchResult

__all__ = ["SpectrFetcher"]


class SpectrFetcher(DataFetcher):
    def __init__(
            self,
            spectr_client: SpectrClient,
            logger: Logger
    ):
        self._spectr_client = spectr_client
        self._logger = logger

    def source_id(self) -> str:
        return "spectr"

    def should_update(self, company: Company):
        return company.spectrUpdatedAt is None or (
            company.spectrUpdatedAt < datetime.now() - datetime.timedelta(days=14)
        )

    async def fetch_company_data(self, company: Company) -> FetchResult:
        if not company.spectrId:
            return await self._enrich_company(company)
        else:
            return await self._update_company(company)

    async def _enrich_company(self, company: Company) -> FetchResult:
        """Enrich a company without spectrId using its website."""
        enrichment_result = None
        if company.website:
            try:
                enrichment_result = await self._spectr_client.enrich_companies(website_url=company.website)
            except HTTPStatusError as e:
                if e.response.status_code == HTTPStatus.NOT_FOUND:
                    self._logger.info(
                        'Company not found in Spectr',
                        labels={
                            'company': company.model_dump_for_logs(),
                            'reason': 'website_not_found_in_spectr_database'
                        }
                    )
                    return FetchResult()
                raise
        
        if not enrichment_result or not isinstance(enrichment_result, list) or len(enrichment_result) != 1:
            self._logger.info(
                'Spectr enrichment failed',
                labels={
                    'company': company.model_dump_for_logs(),
                    'resultType': type(enrichment_result).__name__,
                    'resultCount': len(enrichment_result) if isinstance(enrichment_result, list) else 0,
                    'reason': 'empty_result_or_multiple_matches_or_invalid_format'
                }
            )
            return FetchResult(raw_data=enrichment_result)

        spectr_company = enrichment_result[0]
        last_updated = datetime.any_to_datetime(spectr_company.get("last_updated"))
        
        return FetchResult(
            raw_data=spectr_company,
            remote_id=spectr_company['id'],
            db_update_fields={
                'spectrId': spectr_company['id'],
                'spectrUpdatedAt': datetime.now(),
                'spectrData': spectr_company
            },
            updated_at=last_updated
        )

    async def _update_company(self, company: Company) -> FetchResult:
        """Update a company that already has a spectrId."""
        try:
            spectr_company = await self._spectr_client.get_company_by_id(company.spectrId)
        except HTTPStatusError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                self._logger.warning(
                    'Spectr company not found',
                    labels={
                        'company': company.model_dump_for_logs(),
                    }
                )
                return FetchResult(
                    raw_data={},
                    remote_id=company.spectrId,
                    db_update_fields={},
                    updated_at=datetime.now()
                )
            raise

        if not spectr_company:
            self._logger.warning(
                'No Spectr data found',
                labels={
                    'company': company.model_dump_for_logs(),
                }
            )
            return FetchResult(
                raw_data={},
                remote_id=company.spectrId,
                db_update_fields={},
                updated_at=datetime.now()
            )
        last_updated = datetime.any_to_datetime(spectr_company.get("last_updated"))

        return FetchResult(
            raw_data=spectr_company,
            remote_id=company.spectrId,
            db_update_fields={
                'spectrUpdatedAt': datetime.now(),
                'spectrData': spectr_company
            },
            updated_at=last_updated
        )

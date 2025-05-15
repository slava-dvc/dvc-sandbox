from typing import Optional, Union, List, Any

from dataclasses import dataclass

@dataclass
class TractionValue:
    value: str | int | float
    change: int | float | None = None
    percentage: int | float | None = None

@dataclass
class TractionMetric:
    """Represents traction metrics for a company."""
    latest: str | int | float
    t1mo: TractionValue
    t2mo: TractionValue

    @classmethod
    def from_dict(cls, traction_metric: dict):
        return cls(

        )

@dataclass
class TractionMetrics:
    popularity_rank: TractionMetric
    web_visits: TractionMetric

    @classmethod
    def from_dict(cls, traction_metrics: dict):
        return cls(

        )

@dataclass
class CompanySummary:
    """Represents a company with its relevant data."""
    company_id: str
    name: str
    website: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    initial_fund: Optional[str] = None
    initial_valuation: Optional[Union[str, float, int]] = None
    current_valuation: Optional[Union[str, float, int]] = None
    logo_url: Optional[str] = None
    last_update: Optional[Any] = None
    new_highlights: Optional[List[str]] = None
    traction_metrics: Optional[dict] = None

    def __lt__(self, other):
        status_map = {
            "Invested": 0,
            "Exit": -2,
            "Offered To Invest": 2,
            "Write-off": -1,
        }

        def get_sorting_tuple(obj):
            highlights_count = 0 if not isinstance(obj.new_highlights, list) else len(obj.new_highlights)
            last_update = datetime.now() if not isinstance(obj.last_update, datetime.datetime) else obj.last_update
            return (
                highlights_count,
                last_update,
                status_map.get(obj.status, 0),
            )
        return get_sorting_tuple(self) < get_sorting_tuple(other)

    @classmethod
    def from_dict(cls, company: dict, company_id, last_update=None):
        stage = company['Company Stage']
        if isinstance(stage, list) and stage:
            stage = stage[0]
        else:
            stage = 'N/A'

        # Handle current valuation - if it's a list, take the first element
        current_val = company['Last Valuation/cap (from DVC Portfolio 3)']
        if isinstance(current_val, list) and current_val:
            current_val = current_val[0]
        else:
            current_val = 'N/A'
        initial_val = company['Entry Valuation /cap (from DVC Portfolio 3)']
        if isinstance(initial_val, list) and initial_val:
            initial_val = initial_val[0]
        else:
            initial_val = 'N/A'

        return cls(
            company_id=company_id,
            name=company['Company'],
            status=company['Status'],
            website=company['URL'],
            stage=stage,
            initial_fund=company['Initial Fund Invested From'],
            initial_valuation=initial_val,
            current_valuation=current_val,
            logo_url=get_preview(company['Logo']),
            last_update=last_update,
            new_highlights=company.get('new_highlights'),
            traction_metrics=company.get('traction_metrics')
        )
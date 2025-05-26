from dataclasses import dataclass, field
from typing import Optional, Union, List, Any, Dict
import pandas as pd
import streamlit as st

from app.dashboard.formatting import format_as_dollars, get_preview, format_compact_number
from app.foundation.primitives import datetime


@dataclass
class Highlight:
    """Highlight information for a company."""
    description: str
    is_positive: bool = True
    metric: Optional[str] = None


# Dictionary mapping highlight IDs to their information
HIGHLIGHTS_DICT = {
    "headcount_surge": Highlight(description="Headcount surge", is_positive=True, metric="employee_count"),
    "raised_last_month": Highlight(description="Raised funding last month", is_positive=True, metric=None),
    "recent_funding": Highlight(description="Recent funding", is_positive=True, metric=None),
    "no_recent_funding": Highlight(description="No recent funding", is_positive=False, metric=None),
    "web_traffic_surge": Highlight(description="Web traffic", is_positive=True, metric="web_visits"),
    "strong_web_traffic_growth": Highlight(description="Web traffic", is_positive=True, metric="web_visits"),
    "app_downloads_surge": Highlight(description="App downloads", is_positive=True, metric="app_downloads"),
    "recent_news": Highlight(description="Recent news", is_positive=True, metric=None),
    "strong_social_growth": Highlight(description="Social media", is_positive=True, metric="linkedin_followers"),
    "strong_app_downloads_growth": Highlight(description="App downloads", is_positive=True, metric="app_downloads")}


@dataclass
class NewsItem:
    """Represents a news item for a company."""
    title: str
    url: str
    date: str
    publisher: str

    @classmethod
    def from_dict(cls, news_item: dict):
        if not news_item:
            return cls(title="", url="", date="", publisher="")
        return cls(
            title=news_item.get('title', ""),
            url=news_item.get('url', ""),
            date=datetime.any_to_datetime(news_item.get('date', "")),
            publisher=news_item.get('publisher', "")
        )


@dataclass
class TractionValue:
    value: str | int | float
    change: int | float | None = None
    percentage: int | float | None = None

    @classmethod
    def from_dict(cls, traction_value: dict):
        if not traction_value:
            return cls(value=0)

        return cls(value=traction_value.get('value', 0), change=traction_value.get('change'),
            percentage=traction_value.get('percentage'))


@dataclass
class TractionMetric:
    """Represents traction metrics for a company."""
    latest: str | int | float
    previous: Dict[str, TractionValue] = field(default_factory=dict)

    def __bool__(self):
        return isinstance(self.latest, (int, float)) and self.latest > 0 and len(self.previous) > 0

    @classmethod
    def from_dict(cls, traction_metric: dict):
        if not traction_metric or not isinstance(traction_metric, dict):
            return None

        previous = {}
        for period in ['1mo', '2mo', '3mo', '4mo', '5mo', '6mo', '12mo', '24mo']:
            previous[period] = TractionValue.from_dict(traction_metric.get(period, {}))

        return cls(latest=traction_metric.get('latest', None), previous=previous, )


@dataclass
class TractionMetrics:
    popularity_rank: Optional[TractionMetric] = None
    web_visits: Optional[TractionMetric] = None
    employee_count: Optional[TractionMetric] = None
    linkedin_followers: Optional[TractionMetric] = None
    twitter_followers: Optional[TractionMetric] = None
    instagram_followers: Optional[TractionMetric] = None
    itunes_reviews: Optional[TractionMetric] = None
    googleplay_reviews: Optional[TractionMetric] = None
    app_downloads: Optional[TractionMetric] = None
    g2_reviews: Optional[TractionMetric] = None
    trustpilot_reviews: Optional[TractionMetric] = None
    chrome_extensions_reviews: Optional[TractionMetric] = None
    chrome_extensions_users: Optional[TractionMetric] = None

    @classmethod
    def from_dict(cls, traction_metrics: Dict) -> 'TractionMetrics':
        if not traction_metrics or not isinstance(traction_metrics, dict):
            return cls()

        metrics = {}

        for metric_name in ['popularity_rank', 'web_visits', 'employee_count', 'linkedin_followers',
            'twitter_followers', 'instagram_followers', 'itunes_reviews', 'googleplay_reviews', 'app_downloads',
            'g2_reviews', 'trustpilot_reviews', 'chrome_extensions_reviews', 'chrome_extensions_users']:
            metric_data = traction_metrics.get(metric_name, {})
            if metric_data:
                metrics[metric_name] = TractionMetric.from_dict(metric_data)
        return cls(**metrics)


@dataclass
class CompanySummary:
    """Represents a company with its relevant data."""
    company_id: str
    name: str
    website: Optional[str] = None
    blurb: None | str = None
    stage: Optional[str] = None
    status: Optional[str] = None
    initial_fund: Optional[str] = None
    initial_valuation: Optional[Union[str, float, int]] = None
    current_valuation: Optional[Union[str, float, int]] = None
    logo_url: Optional[str] = None
    last_update: Optional[Any] = None
    new_highlights: Optional[List[str]] = None
    traction_metrics: TractionMetrics = None
    runway: int | None = None
    expected_performance: str | None = None
    revenue: int | None = None
    burnrate: int | None = None
    customers_cnt: int | None = None
    news: List[NewsItem] = field(default_factory=list)

    def __lt__(self, other):
        status_map = {"Invested": 0, "Exit": -2, "Offered To Invest": 2, "Write-off": -1, }

        def get_sorting_tuple(obj):
            highlights_count = 0 if not isinstance(obj.new_highlights, list) else len(obj.new_highlights)
            last_update = datetime.now() if not isinstance(obj.last_update, datetime.datetime) else obj.last_update
            return (highlights_count, last_update, status_map.get(obj.status, 0),)

        return get_sorting_tuple(self) < get_sorting_tuple(other)

    @staticmethod
    def _extract_value(value):
        """Extract value from potentially list-containing field."""

        extracted = value[0] if isinstance(value, list) and value else value

        # Handle NaN values by converting them to None
        return None if pd.isna(extracted) else extracted or None

    @classmethod
    def from_dict(cls, company: dict, company_id, last_update=None):
        stage = cls._extract_value(company.get('Company Stage'))
        
        runway = None
        try:
            runway = int(company['Runway'])
        except (ValueError, TypeError, KeyError):
            pass
        
        current_val = cls._extract_value(company.get('Last Valuation/cap (from DVC Portfolio 3)'))
        initial_val = cls._extract_value(company.get('Entry Valuation /cap (from DVC Portfolio 3)'))
        news = (company.get('news'))
        if not isinstance(news, list):
            news= []
        return cls(
            company_id=company_id, name=company['Company'], status=company['Status'], website=company['URL'],
            stage=stage, initial_fund=company['Initial Fund Invested From'], initial_valuation=initial_val,
            current_valuation=current_val, logo_url=get_preview(company['Logo']), last_update=last_update,
            new_highlights=company.get('new_highlights'),
            blurb=company.get('Blurb'),
            traction_metrics=TractionMetrics.from_dict(company.get('traction_metrics')),
            runway=runway,
            revenue=cls._extract_value(company.get('Revenue copy')),
            burnrate=cls._extract_value(company.get('Burnrate')),
            customers_cnt=company.get('Number of customers'),
            expected_performance=company.get('Expected Performance'),
            news=[NewsItem.from_dict(n) for n in news]
        )


def show_highlight(highlight: Highlight, metric: TractionMetric = None):
    is_positive = highlight.is_positive
    description = highlight.description
    change = ''
    latest_value = float(metric.latest) if metric is not None else None

    if latest_value is not None:
        month_ago_value = metric.previous.get('1mo').value if metric is not None else None

        if month_ago_value:
            percentage = (latest_value - month_ago_value) / month_ago_value * 100
            change_symbol = "+" if percentage > 0 else ""

            change = f"{change_symbol}{percentage:.1f}% last month"
            if percentage < 0:
                is_positive = False

    badge_color = "green" if is_positive else "orange"
    emoji = "🔥" if is_positive else "⚠️"
    parts = [emoji, description]
    if latest_value is not None:
        parts.append(": ")
        parts.append(format_compact_number(latest_value))
    if change:
        parts.append(f"({change})")
    description = " ".join(parts)
    st.badge(description, color=badge_color)


def filter_highlights(highlights: List[str]) -> List[str]:
    """
    Filter out redundant highlights based on predefined rules.
    If both weak and strong versions of a highlight exist, only keep the strong one.
    """
    if not highlights:
        return []

    # Define pairs of highlights where only the stronger one should be shown
    redundant_pairs = {"web_traffic_surge": "strong_web_traffic_growth",
        "app_downloads_surge": "strong_app_downloads_growth"}

    # Check which highlights to skip
    highlights_to_skip = set()
    for weak_highlight, strong_highlight in redundant_pairs.items():
        if weak_highlight in highlights and strong_highlight in highlights:
            highlights_to_skip.add(weak_highlight)

    # Return filtered highlights
    return [h for h in highlights if h not in highlights_to_skip]


def show_highlights(company_summary: CompanySummary):
    # Display new highlights badge
    new_highlights = company_summary.new_highlights
    if not (isinstance(new_highlights, list) and len(new_highlights) > 0):
        return 0

    # Filter out redundant highlights
    filtered_highlights = filter_highlights(new_highlights)

    # Display filtered highlights
    for highlight_id in filtered_highlights:
        highlight = HIGHLIGHTS_DICT.get(highlight_id)
        if not highlight:
            continue
        metric = None
        if highlight.metric:
            metric = getattr(company_summary.traction_metrics, highlight.metric)
        show_highlight(highlight, metric)
    return len(filtered_highlights)


def show_company_summary(company_summary: CompanySummary):
    company_id = company_summary.company_id
    company_name = company_summary.name
    company_website = company_summary.website
    company_stage = company_summary.stage
    initial_fund = company_summary.initial_fund
    initial_valuation = company_summary.initial_valuation
    current_valuation = company_summary.current_valuation

    company_last_update = company_summary.last_update

    with st.container(border=True):
        # st.write(f"expected_performance: {company_summary.expected_performance}")
        logo_column, info_column, signals_column, button_column = st.columns([1, 7, 4, 1], gap='small')

        with logo_column:
            if company_summary.logo_url:
                try:
                    st.image(company_summary.logo_url, width=64)
                except Exception:
                    st.write("📊")
            else:
                st.write("📊")

        with info_column:
            header = []
            # c1, c2, c3, c4 = st.columns(4)
            # with c1:
            if company_website and isinstance(company_website, str):
                header.append(f"**[{company_name}]({company_website})**")
            else:
                header.append(f"**{company_name}**")
            header.append(company_stage or "—")
            if company_last_update:
                now = datetime.now()
                if company_last_update < now - datetime.timedelta(days=7):
                    header.append(f"🕐 This week")
                elif company_last_update < now - datetime.timedelta(days=30):
                    header.append(f"🕐 This month")
                else:
                    header.append(f"🕐 {company_last_update.strftime('%d %b %Y')}")
            else:
                header.append("❌ No updates")
            st.markdown("&nbsp; | &nbsp;".join(header))
            # with c2:
            #     show_highlights(company_summary)

            # All information in one row using 3 smaller columns
            c1, c2, c3, = st.columns(3)
            c1.markdown(f"Initial Fund: **{initial_fund}**")
            c1.write(company_summary.expected_performance)
            c2.markdown(f"Initial Val: **{format_as_dollars(initial_valuation, '—')}**")
            c2.markdown(f"Current Val: **{format_as_dollars(current_valuation, '—')}**")


        with signals_column:
            show_highlights(company_summary)

        with button_column:
            def update_company_id(company_id):
                st.query_params.update({'company_id': company_id})

            # Push the button higher on the row by adding padding
            st.write("")  # Small spacer to align with company name
            st.button("View", key=f"open_company_{company_id}", on_click=update_company_id, args=[company_id],
                use_container_width=True)

"""Analytics and aggregation schemas."""
from pydantic import BaseModel, UUID4
from datetime import datetime, date
from typing import Optional, List, Dict, Any


class OverviewStats(BaseModel):
    """Overall platform statistics."""
    total_companies: int
    total_profiles: int
    total_sources: int
    total_commitments: int
    total_controversies: int
    total_events: int
    avg_sources_per_company: float
    avg_commitments_per_company: float
    industries_covered: int
    countries_covered: int
    latest_research_date: Optional[datetime] = None
    source_type_breakdown: Dict[str, int]
    commitment_status_breakdown: Dict[str, int]
    risk_level_breakdown: Dict[str, int]


class IndustryStats(BaseModel):
    """DEI statistics by industry."""
    industry: str
    company_count: int
    avg_sources: float
    avg_commitments: float
    total_commitments: int
    active_commitments: int
    total_controversies: int
    avg_risk_score: Optional[float] = None
    companies_with_cdo: int


class CompanyMetrics(BaseModel):
    """Metrics for a single company."""
    source_count: int
    commitment_count: int
    active_commitments: int
    controversy_count: int
    event_count: int
    pledge_count: int
    industry_initiatives: int
    avg_source_reliability: Optional[float] = None
    latest_research: Optional[datetime] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    has_cdo: bool = False
    transparency_rating: Optional[int] = None
    commitment_strength_rating: Optional[int] = None
    recommendation: Optional[str] = None


class CompanyComparison(BaseModel):
    """Company comparison data."""
    id: UUID4
    name: str
    ticker: str
    industry: Optional[str] = None
    metrics: CompanyMetrics


class ComparisonResponse(BaseModel):
    """Response for company comparison."""
    companies: List[CompanyComparison]
    comparison_date: datetime


class TrendDataPoint(BaseModel):
    """Single data point in a trend."""
    date: date
    count: int
    value: Optional[float] = None


class TrendAnalysis(BaseModel):
    """Trend analysis over time."""
    metric: str
    interval: str
    period: Dict[str, str]
    data_points: List[TrendDataPoint]


class RiskDistribution(BaseModel):
    """Risk level distribution."""
    risk_level: str
    count: int
    percentage: float
    avg_lawsuits: float
    avg_controversies: float

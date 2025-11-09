"""Pydantic schemas for request/response validation."""
from app.schemas.common import (
    PaginationParams,
    PaginationMeta,
    PaginatedResponse,
    Headquarters,
    SourceReference,
)
from app.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    Company,
    CompanyWithStats,
    CompanySummary,
)
from app.schemas.profile import (
    ProfileBase,
    Profile,
    ProfileWithCompany,
    AIContext,
    AIKeyInsight,
    AIStrategicImplication,
    DEIPosture,
    CDORole,
    ReportingPractice,
    SupplierDiversity,
    RiskAssessment,
    DataQualityFlags,
    FullProfile,
)
from app.schemas.commitment import (
    CommitmentBase,
    CommitmentCreate,
    CommitmentUpdate,
    Commitment,
    CommitmentWithCompany,
    CommitmentTypeStats,
)
from app.schemas.controversy import (
    ControversyBase,
    ControversyCreate,
    ControversyUpdate,
    Controversy,
    ControversyWithCompany,
)
from app.schemas.event import (
    EventBase,
    EventCreate,
    EventUpdate,
    Event,
    EventWithCompany,
)
from app.schemas.source import (
    DataSourceBase,
    DataSourceCreate,
    DataSourceUpdate,
    DataSource,
    DataSourceWithCompany,
    SourceTypeStats,
)
from app.schemas.analytics import (
    OverviewStats,
    IndustryStats,
    CompanyMetrics,
    CompanyComparison,
    ComparisonResponse,
    TrendDataPoint,
    TrendAnalysis,
    RiskDistribution,
)

__all__ = [
    # Common
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    "Headquarters",
    "SourceReference",
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "Company",
    "CompanyWithStats",
    "CompanySummary",
    # Profile
    "ProfileBase",
    "Profile",
    "ProfileWithCompany",
    "AIContext",
    "AIKeyInsight",
    "AIStrategicImplication",
    "DEIPosture",
    "CDORole",
    "ReportingPractice",
    "SupplierDiversity",
    "RiskAssessment",
    "DataQualityFlags",
    "FullProfile",
    # Commitment
    "CommitmentBase",
    "CommitmentCreate",
    "CommitmentUpdate",
    "Commitment",
    "CommitmentWithCompany",
    "CommitmentTypeStats",
    # Controversy
    "ControversyBase",
    "ControversyCreate",
    "ControversyUpdate",
    "Controversy",
    "ControversyWithCompany",
    # Event
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "Event",
    "EventWithCompany",
    # Source
    "DataSourceBase",
    "DataSourceCreate",
    "DataSourceUpdate",
    "DataSource",
    "DataSourceWithCompany",
    "SourceTypeStats",
    # Analytics
    "OverviewStats",
    "IndustryStats",
    "CompanyMetrics",
    "CompanyComparison",
    "ComparisonResponse",
    "TrendDataPoint",
    "TrendAnalysis",
    "RiskDistribution",
]

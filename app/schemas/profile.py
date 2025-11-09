"""Profile-related schemas."""
from pydantic import BaseModel, UUID4
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.schemas.company import CompanySummary


class ProfileBase(BaseModel):
    """Base profile fields."""
    schema_version: str
    profile_type: str
    generated_at: datetime
    research_captured_at: Optional[datetime] = None
    research_notes: Optional[str] = None
    source_count: int = 0
    is_latest: bool = True


class Profile(ProfileBase):
    """Profile response schema."""
    id: UUID4
    company_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileWithCompany(Profile):
    """Profile with company information."""
    company: Optional[CompanySummary] = None


class AIContext(BaseModel):
    """AI-generated context and analysis."""
    executive_summary: Optional[str] = None
    trend_analysis: Optional[str] = None
    comparative_context: Optional[str] = None
    commitment_strength_rating: Optional[int] = None
    transparency_rating: Optional[int] = None
    recommendation: Optional[str] = None


class AIKeyInsight(BaseModel):
    """AI-generated key insight."""
    id: UUID4
    insight_text: str
    insight_order: int


class AIStrategicImplication(BaseModel):
    """AI-generated strategic implication."""
    id: UUID4
    implication_text: str
    implication_order: int


class DEIPosture(BaseModel):
    """DEI posture assessment."""
    status: str
    evidence_summary: Optional[str] = None
    last_verified_date: Optional[date] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None


class CDORole(BaseModel):
    """Chief Diversity Officer role information."""
    exists: bool
    name: Optional[str] = None
    title: Optional[str] = None
    reports_to: Optional[str] = None
    appointment_date: Optional[date] = None
    c_suite_member: Optional[bool] = False
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None


class ReportingPractice(BaseModel):
    """DEI reporting practices."""
    standalone_dei_report: bool = False
    dei_in_esg_report: bool = False
    dei_in_annual_report: bool = False
    reporting_frequency: Optional[str] = None
    last_report_date: Optional[date] = None
    report_url: Optional[str] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None


class SupplierDiversity(BaseModel):
    """Supplier diversity program information."""
    program_exists: bool = False
    program_status: Optional[str] = None
    spending_disclosed: bool = False
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None


class RiskAssessment(BaseModel):
    """DEI-related risk assessment."""
    overall_risk_score: Optional[int] = None
    risk_level: str
    ongoing_lawsuits: int = 0
    settled_cases: int = 0
    negative_events: int = 0
    high_impact_events: int = 0


class DataQualityFlags(BaseModel):
    """Data quality indicators."""
    incomplete_data: bool = False
    conflicting_sources: bool = False
    outdated_information: bool = False
    verification_needed: Optional[List[str]] = None


class FullProfile(ProfileWithCompany):
    """
    Complete DEI profile with all related data.
    This represents the profiles_full view.
    """
    # AI Analysis
    ai_context: Optional[AIContext] = None
    key_insights: Optional[List[AIKeyInsight]] = None
    strategic_implications: Optional[List[AIStrategicImplication]] = None

    # DEI Components
    dei_posture: Optional[DEIPosture] = None
    cdo_role: Optional[CDORole] = None
    reporting_practices: Optional[ReportingPractice] = None
    supplier_diversity: Optional[SupplierDiversity] = None
    risk_assessment: Optional[RiskAssessment] = None
    data_quality_flags: Optional[DataQualityFlags] = None

    # Counts for related data
    commitment_count: int = 0
    controversy_count: int = 0
    event_count: int = 0

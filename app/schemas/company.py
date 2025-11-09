"""Company-related schemas."""
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from app.schemas.common import Headquarters


class CompanyBase(BaseModel):
    """Base company fields."""
    ticker: str
    name: str
    cik: Optional[str] = None
    industry: Optional[str] = None
    hq_city: Optional[str] = None
    hq_state: Optional[str] = None
    hq_country: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    ticker: Optional[str] = None
    name: Optional[str] = None
    cik: Optional[str] = None
    industry: Optional[str] = None
    hq_city: Optional[str] = None
    hq_state: Optional[str] = None
    hq_country: Optional[str] = None


class Company(CompanyBase):
    """Company response schema."""
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyWithStats(Company):
    """Company with profile statistics."""
    profile_id: Optional[UUID4] = None
    has_profile: bool = False
    source_count: Optional[int] = 0
    commitment_count: Optional[int] = 0
    controversy_count: Optional[int] = 0
    has_cdo: Optional[bool] = False
    risk_level: Optional[str] = None


class CompanySummary(BaseModel):
    """Minimal company summary."""
    id: UUID4
    name: str
    ticker: str
    industry: Optional[str] = None

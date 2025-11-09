"""Controversy-related schemas."""
from pydantic import BaseModel, UUID4
from datetime import date
from typing import Optional, List
from app.schemas.company import CompanySummary
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.source import DataSource


class ControversyBase(BaseModel):
    """Base controversy fields."""
    date: Optional[date] = None
    type: str
    status: str
    description: str
    case_name: Optional[str] = None
    docket_number: Optional[str] = None
    court: Optional[str] = None
    nlrb_case_id: Optional[str] = None
    filing_url: Optional[str] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None
    status_standard: Optional[str] = None


class ControversyCreate(ControversyBase):
    """Schema for creating a controversy."""
    profile_id: UUID4


class ControversyUpdate(BaseModel):
    """Schema for updating a controversy."""
    date: Optional[date] = None
    type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    case_name: Optional[str] = None
    docket_number: Optional[str] = None
    court: Optional[str] = None
    nlrb_case_id: Optional[str] = None
    filing_url: Optional[str] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None
    status_standard: Optional[str] = None


class Controversy(ControversyBase):
    """Controversy response schema."""
    id: UUID4
    profile_id: UUID4

    class Config:
        from_attributes = True


class ControversyWithCompany(Controversy):
    """Controversy with company information."""
    company: Optional[CompanySummary] = None
    sources: Optional[List['DataSource']] = None

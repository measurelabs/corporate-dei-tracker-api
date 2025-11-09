"""Commitment-related schemas."""
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from app.schemas.company import CompanySummary
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.source import DataSource


class CommitmentBase(BaseModel):
    """Base commitment fields."""
    commitment_name: str
    commitment_type: str
    current_status: str
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None
    status_changed_at: Optional[datetime] = None
    previous_status: Optional[str] = None


class CommitmentCreate(CommitmentBase):
    """Schema for creating a commitment."""
    profile_id: UUID4


class CommitmentUpdate(BaseModel):
    """Schema for updating a commitment."""
    commitment_name: Optional[str] = None
    commitment_type: Optional[str] = None
    current_status: Optional[str] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None
    status_changed_at: Optional[datetime] = None
    previous_status: Optional[str] = None


class Commitment(CommitmentBase):
    """Commitment response schema."""
    id: UUID4
    profile_id: UUID4

    class Config:
        from_attributes = True


class CommitmentWithCompany(Commitment):
    """Commitment with company information."""
    company: Optional[CompanySummary] = None
    quote_count: Optional[int] = 0
    source_count: Optional[int] = 0
    sources: Optional[List['DataSource']] = None


class CommitmentTypeStats(BaseModel):
    """Statistics for a commitment type."""
    commitment_type: str
    count: int
    active_count: int
    companies_count: int

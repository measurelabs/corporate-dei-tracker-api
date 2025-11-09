from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CommitmentBase(BaseModel):
    profile_id: str
    commitment_name: str
    commitment_type: str
    current_status: str
    quotes: List[str]
    provenance_ids: List[str]
    status_changed_at: Optional[str] = None
    previous_status: Optional[str] = None


class CommitmentResponse(BaseModel):
    id: str
    profile_id: str
    commitment_name: str
    commitment_type: str
    current_status: str
    quotes: List[str]
    provenance_ids: List[str]
    status_changed_at: Optional[str] = None
    previous_status: Optional[str] = None

    @staticmethod
    def from_db(data: dict) -> "CommitmentResponse":
        """Convert database row to response model"""
        return CommitmentResponse(**data)


class CommitmentWithCompany(CommitmentResponse):
    company: Optional[dict] = None
    quote_count: int = 0
    source_count: int = 0


class CommitmentListResponse(BaseModel):
    data: list[CommitmentResponse]
    pagination: dict


class CommitmentTypeStats(BaseModel):
    commitment_type: str
    count: int
    active_count: int
    companies_count: int

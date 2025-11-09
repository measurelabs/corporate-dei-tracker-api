from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SourceBase(BaseModel):
    profile_id: str
    source_id: str
    source_type: str
    publisher: str
    author: Optional[str] = None
    url: str
    date: str
    title: str
    reliability_score: int
    doc_type: str
    notes: Optional[str] = None


class SourceResponse(BaseModel):
    id: str
    profile_id: str
    source_id: str
    source_type: str
    publisher: str
    author: Optional[str] = None
    url: str
    date: str
    title: str
    reliability_score: int
    doc_type: str
    notes: Optional[str] = None

    @staticmethod
    def from_db(data: dict) -> "SourceResponse":
        """Convert database row to response model"""
        return SourceResponse(**data)


class SourceWithCompany(SourceResponse):
    company: Optional[dict] = None


class SourceListResponse(BaseModel):
    data: list[SourceResponse]
    pagination: dict


class SourceTypeStats(BaseModel):
    source_type: str
    count: int
    avg_reliability: float

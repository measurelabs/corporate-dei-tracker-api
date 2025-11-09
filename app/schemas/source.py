"""Data source-related schemas."""
from pydantic import BaseModel, UUID4
from datetime import date
from typing import Optional
from app.schemas.company import CompanySummary


class DataSourceBase(BaseModel):
    """Base data source fields."""
    source_id: str
    source_type: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    date: Optional[date] = None
    title: Optional[str] = None
    reliability_score: Optional[int] = None
    doc_type: Optional[str] = None
    notes: Optional[str] = None


class DataSourceCreate(DataSourceBase):
    """Schema for creating a data source."""
    profile_id: UUID4


class DataSourceUpdate(BaseModel):
    """Schema for updating a data source."""
    source_id: Optional[str] = None
    source_type: Optional[str] = None
    publisher: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    date: Optional[date] = None
    title: Optional[str] = None
    reliability_score: Optional[int] = None
    doc_type: Optional[str] = None
    notes: Optional[str] = None


class DataSource(DataSourceBase):
    """Data source response schema."""
    id: UUID4
    profile_id: UUID4

    class Config:
        from_attributes = True


class DataSourceWithCompany(DataSource):
    """Data source with company information."""
    company: Optional[CompanySummary] = None


class SourceTypeStats(BaseModel):
    """Statistics for a source type."""
    source_type: str
    count: int
    avg_reliability: Optional[float] = None

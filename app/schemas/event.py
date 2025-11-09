"""Event-related schemas."""
from pydantic import BaseModel, UUID4
from datetime import date
from typing import Optional, List
from app.schemas.company import CompanySummary
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.source import DataSource


class EventBase(BaseModel):
    """Base event fields."""
    date: date
    headline: Optional[str] = None
    event_type: str
    sentiment: Optional[str] = None
    impact: Optional[str] = None
    summary: Optional[str] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None
    impact_magnitude: Optional[str] = None
    impact_direction: Optional[str] = None
    event_category: Optional[str] = None


class EventCreate(EventBase):
    """Schema for creating an event."""
    profile_id: UUID4


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    date: Optional[date] = None
    headline: Optional[str] = None
    event_type: Optional[str] = None
    sentiment: Optional[str] = None
    impact: Optional[str] = None
    summary: Optional[str] = None
    quotes: Optional[List[str]] = None
    provenance_ids: Optional[List[str]] = None
    impact_magnitude: Optional[str] = None
    impact_direction: Optional[str] = None
    event_category: Optional[str] = None


class Event(EventBase):
    """Event response schema."""
    id: UUID4
    profile_id: UUID4

    class Config:
        from_attributes = True


class EventWithCompany(Event):
    """Event with company information."""
    company: Optional[CompanySummary] = None
    sources: Optional[List['DataSource']] = None

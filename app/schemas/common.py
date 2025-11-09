"""Common schemas and utilities."""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = 1
    per_page: int = 20


class PaginationMeta(BaseModel):
    """Pagination metadata in responses."""
    page: int
    per_page: int
    total_pages: int
    total_count: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    data: List[Any]
    pagination: PaginationMeta


class Headquarters(BaseModel):
    """Company headquarters location."""
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class SourceReference(BaseModel):
    """Reference to a data source."""
    source_id: str
    url: Optional[str] = None
    reliability_score: Optional[int] = None
    title: Optional[str] = None

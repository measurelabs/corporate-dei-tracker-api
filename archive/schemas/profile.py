from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProfileBase(BaseModel):
    company_id: str
    schema_version: str
    profile_type: str
    generated_at: str
    research_captured_at: str
    research_notes: Optional[str] = None
    source_count: int
    is_latest: bool


class ProfileResponse(BaseModel):
    id: str
    company_id: str
    schema_version: str
    profile_type: str
    generated_at: str
    research_captured_at: str
    research_notes: Optional[str] = None
    source_count: int
    is_latest: bool
    created_at: str

    @staticmethod
    def from_db(data: dict) -> "ProfileResponse":
        """Convert database row to response model"""
        return ProfileResponse(**data)


class ProfileWithCompany(ProfileResponse):
    company: Optional[dict] = None


class ProfileListResponse(BaseModel):
    data: list[ProfileResponse]
    pagination: dict

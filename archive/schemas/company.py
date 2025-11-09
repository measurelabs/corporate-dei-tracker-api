from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HeadquartersBase(BaseModel):
    city: str
    state: Optional[str] = None
    country: str


class CompanyBase(BaseModel):
    ticker: str
    name: str
    cik: Optional[str] = None
    industry: str
    hq_city: str
    hq_state: Optional[str] = None
    hq_country: str


class CompanyResponse(BaseModel):
    id: str
    ticker: str
    name: str
    cik: Optional[str] = None
    industry: str
    headquarters: HeadquartersBase
    created_at: str
    updated_at: str

    @staticmethod
    def from_db(data: dict) -> "CompanyResponse":
        """Convert database row to response model"""
        return CompanyResponse(
            id=data["id"],
            ticker=data["ticker"],
            name=data["name"],
            cik=data.get("cik"),
            industry=data["industry"],
            headquarters=HeadquartersBase(
                city=data["hq_city"],
                state=data.get("hq_state"),
                country=data["hq_country"]
            ),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )


class CompanyWithProfile(CompanyResponse):
    profile_id: Optional[str] = None
    has_profile: bool = False
    source_count: int = 0
    commitment_count: int = 0


class CompanyListResponse(BaseModel):
    data: list[CompanyResponse]
    pagination: dict

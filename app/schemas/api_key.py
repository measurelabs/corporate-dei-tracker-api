"""API Key schemas for authentication."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class APIKeyBase(BaseModel):
    """Base API key schema."""
    name: str = Field(..., description="Descriptive name for the API key")
    is_admin: bool = Field(default=False, description="Whether this is an admin key")
    expires_at: Optional[datetime] = Field(None, description="When the key expires (None for no expiry)")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key."""
    pass


class APIKeyResponse(BaseModel):
    """Response schema when an API key is created."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key: str = Field(..., description="The actual API key (only shown once)")
    key_prefix: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: dict


class APIKeyInfo(BaseModel):
    """Schema for API key information (without the actual key)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    created_by: Optional[UUID]
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    metadata: dict


class APIKeyUpdate(BaseModel):
    """Schema for updating an API key."""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class APIKeyValidation(BaseModel):
    """Internal schema for validated API key data."""
    id: UUID
    is_admin: bool
    is_active: bool
    expires_at: Optional[datetime]
    metadata: dict

"""API Key Authentication Middleware."""
import hashlib
import secrets
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.database import get_db
from app.schemas.api_key import APIKeyValidation


# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA-256.

    Args:
        api_key: The raw API key

    Returns:
        Hexadecimal hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        A URL-safe random API key (43 characters)
    """
    return secrets.token_urlsafe(32)


async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> APIKeyValidation:
    """
    Verify API key and return key validation data.

    Args:
        api_key: The API key from the request header

    Returns:
        APIKeyValidation object with key details

    Raises:
        HTTPException: If the API key is invalid or expired
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Include 'X-API-Key' header in your request."
        )

    # Hash the provided key
    key_hash = hash_api_key(api_key)

    # Query the database
    db = get_db()
    try:
        response = db.table("api_keys").select("*").eq("key_hash", key_hash).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        key_data = response.data[0]

        # Check if key is active
        if not key_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has been deactivated"
            )

        # Check if key has expired
        expires_at = key_data.get("expires_at")
        if expires_at:
            expiry_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now(expiry_dt.tzinfo) > expiry_dt:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key has expired"
                )

        # Update last_used_at timestamp (fire and forget)
        try:
            db.table("api_keys").update({
                "last_used_at": datetime.utcnow().isoformat()
            }).eq("id", key_data["id"]).execute()
        except Exception:
            # Don't fail the request if we can't update the timestamp
            pass

        # Return validation data
        return APIKeyValidation(
            id=key_data["id"],
            is_admin=key_data.get("is_admin", False),
            is_active=key_data["is_active"],
            expires_at=expires_at,
            metadata=key_data.get("metadata", {})
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating API key: {str(e)}"
        )


async def require_admin_key(
    key_validation: APIKeyValidation = Security(verify_api_key)
) -> APIKeyValidation:
    """
    Require that the API key has admin privileges.

    Args:
        key_validation: The validated API key data

    Returns:
        APIKeyValidation object

    Raises:
        HTTPException: If the API key is not an admin key
    """
    if not key_validation.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API key required for this operation"
        )

    return key_validation

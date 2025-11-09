"""API Key Management Router."""
from fastapi import APIRouter, HTTPException, Security, status
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.api_key import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyInfo,
    APIKeyUpdate,
    APIKeyValidation
)
from app.middleware.auth import (
    require_admin_key,
    verify_api_key,
    generate_api_key,
    hash_api_key
)


router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"],
    responses={
        401: {"description": "Unauthorized - Invalid or missing API key"},
        403: {"description": "Forbidden - Admin key required"}
    }
)


@router.post(
    "/",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key",
    description="Creates a new API key. Requires an admin API key."
)
async def create_api_key(
    key_data: APIKeyCreate,
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    """
    Create a new API key.

    Only admin keys can create new API keys.
    The newly created key is returned in the response and will not be shown again.

    Args:
        key_data: API key creation data
        admin_key: The validated admin API key (from header)

    Returns:
        The created API key with the actual key value
    """
    db = get_db()

    # Generate a new API key
    new_key = generate_api_key()
    key_hash = hash_api_key(new_key)
    key_prefix = new_key[:8]

    try:
        # Insert into database
        response = db.table("api_keys").insert({
            "name": key_data.name,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "is_admin": key_data.is_admin,
            "is_active": True,
            "created_by": str(admin_key.id),
            "expires_at": key_data.expires_at.isoformat() if key_data.expires_at else None,
            "metadata": key_data.metadata
        }).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create API key"
            )

        created_key = response.data[0]

        # Return the full key (only time it will be shown)
        return APIKeyResponse(
            id=created_key["id"],
            name=created_key["name"],
            key=new_key,  # The actual key - only shown once!
            key_prefix=created_key["key_prefix"],
            is_active=created_key["is_active"],
            is_admin=created_key["is_admin"],
            created_at=created_key["created_at"],
            expires_at=created_key.get("expires_at"),
            metadata=created_key.get("metadata", {})
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[APIKeyInfo],
    summary="List all API keys",
    description="Lists all API keys. Requires an admin API key."
)
async def list_api_keys(
    admin_key: APIKeyValidation = Security(require_admin_key),
    include_inactive: bool = False
):
    """
    List all API keys (without the actual key values).

    Only admin keys can list API keys.

    Args:
        admin_key: The validated admin API key
        include_inactive: Whether to include inactive keys

    Returns:
        List of API key information
    """
    db = get_db()

    try:
        query = db.table("api_keys").select("*")

        if not include_inactive:
            query = query.eq("is_active", True)

        response = query.order("created_at", desc=True).execute()

        return [APIKeyInfo(**key) for key in response.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing API keys: {str(e)}"
        )


@router.get(
    "/{key_id}",
    response_model=APIKeyInfo,
    summary="Get API key details",
    description="Get details of a specific API key. Requires an admin API key."
)
async def get_api_key(
    key_id: UUID,
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    """
    Get details of a specific API key.

    Only admin keys can view API key details.

    Args:
        key_id: The UUID of the API key
        admin_key: The validated admin API key

    Returns:
        API key information
    """
    db = get_db()

    try:
        response = db.table("api_keys").select("*").eq("id", str(key_id)).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return APIKeyInfo(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving API key: {str(e)}"
        )


@router.patch(
    "/{key_id}",
    response_model=APIKeyInfo,
    summary="Update API key",
    description="Update API key properties. Requires an admin API key."
)
async def update_api_key(
    key_id: UUID,
    updates: APIKeyUpdate,
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    """
    Update an API key's properties.

    Only admin keys can update API keys.

    Args:
        key_id: The UUID of the API key to update
        updates: The updates to apply
        admin_key: The validated admin API key

    Returns:
        Updated API key information
    """
    db = get_db()

    # Build update dict with only provided fields
    update_data = {}
    if updates.name is not None:
        update_data["name"] = updates.name
    if updates.is_active is not None:
        update_data["is_active"] = updates.is_active
    if updates.expires_at is not None:
        update_data["expires_at"] = updates.expires_at.isoformat()
    if updates.metadata is not None:
        update_data["metadata"] = updates.metadata

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )

    try:
        response = db.table("api_keys").update(update_data).eq("id", str(key_id)).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return APIKeyInfo(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating API key: {str(e)}"
        )


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete API key",
    description="Permanently delete an API key. Requires an admin API key."
)
async def delete_api_key(
    key_id: UUID,
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    """
    Permanently delete an API key.

    Only admin keys can delete API keys.
    This action cannot be undone.

    Args:
        key_id: The UUID of the API key to delete
        admin_key: The validated admin API key
    """
    db = get_db()

    # Prevent deleting the key being used to make the request
    if str(key_id) == str(admin_key.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the API key you are currently using"
        )

    try:
        response = db.table("api_keys").delete().eq("id", str(key_id)).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting API key: {str(e)}"
        )


@router.post(
    "/{key_id}/deactivate",
    response_model=APIKeyInfo,
    summary="Deactivate API key",
    description="Deactivate an API key. Requires an admin API key."
)
async def deactivate_api_key(
    key_id: UUID,
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    """
    Deactivate an API key (soft delete).

    Only admin keys can deactivate API keys.

    Args:
        key_id: The UUID of the API key to deactivate
        admin_key: The validated admin API key

    Returns:
        Updated API key information
    """
    # Prevent deactivating the key being used to make the request
    if str(key_id) == str(admin_key.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate the API key you are currently using"
        )

    db = get_db()

    try:
        response = db.table("api_keys").update({"is_active": False}).eq("id", str(key_id)).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return APIKeyInfo(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating API key: {str(e)}"
        )


@router.post(
    "/{key_id}/activate",
    response_model=APIKeyInfo,
    summary="Activate API key",
    description="Activate a previously deactivated API key. Requires an admin API key."
)
async def activate_api_key(
    key_id: UUID,
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    """
    Activate a previously deactivated API key.

    Only admin keys can activate API keys.

    Args:
        key_id: The UUID of the API key to activate
        admin_key: The validated admin API key

    Returns:
        Updated API key information
    """
    db = get_db()

    try:
        response = db.table("api_keys").update({"is_active": True}).eq("id", str(key_id)).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return APIKeyInfo(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating API key: {str(e)}"
        )


@router.get(
    "/verify/current",
    response_model=APIKeyInfo,
    summary="Verify current API key",
    description="Verify and get information about the API key being used for this request."
)
async def verify_current_key(
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Verify the current API key and return its information.

    This endpoint can be used to test if an API key is valid.

    Args:
        key_validation: The validated API key

    Returns:
        Information about the current API key
    """
    db = get_db()

    try:
        response = db.table("api_keys").select("*").eq("id", str(key_validation.id)).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return APIKeyInfo(**response.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying API key: {str(e)}"
        )

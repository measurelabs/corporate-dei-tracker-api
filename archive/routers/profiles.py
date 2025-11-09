from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_supabase_client
from schemas.profile import ProfileResponse

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/", response_model=dict)
async def list_profiles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    company_id: Optional[str] = None,
    is_latest: Optional[bool] = None
):
    """List all DEI profiles"""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page
    query = supabase.table('profiles').select('*, companies(id, name, ticker)', count='exact')

    if company_id:
        query = query.eq('company_id', company_id)
    if is_latest is not None:
        query = query.eq('is_latest', is_latest)

    query = query.order('created_at', desc=True)
    query = query.range(offset, offset + per_page - 1)

    result = query.execute()

    total_count = result.count if result.count else 0
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    # Transform data
    profiles_data = []
    for row in result.data:
        profile = {
            "id": row["id"],
            "company_id": row["company_id"],
            "schema_version": row["schema_version"],
            "profile_type": row["profile_type"],
            "generated_at": row["generated_at"],
            "research_captured_at": row["research_captured_at"],
            "source_count": row["source_count"],
            "is_latest": row["is_latest"],
            "created_at": row["created_at"]
        }

        # Add company info if available
        if 'companies' in row and row['companies']:
            company = row['companies'] if isinstance(row['companies'], dict) else row['companies'][0]
            profile['company'] = {
                "id": company.get("id"),
                "name": company.get("name"),
                "ticker": company.get("ticker")
            }

        profiles_data.append(profile)

    return {
        "data": profiles_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    }


@router.get("/{profile_id}", response_model=dict)
async def get_profile(
    profile_id: str,
    include: Optional[str] = None
):
    """Get detailed DEI profile"""
    supabase = get_supabase_client()

    # Get profile with company
    result = supabase.table('profiles') \
        .select('*, companies(*)') \
        .eq('id', profile_id) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = result.data[0]

    response = {
        "id": profile_data["id"],
        "company_id": profile_data["company_id"],
        "schema_version": profile_data["schema_version"],
        "profile_type": profile_data["profile_type"],
        "generated_at": profile_data["generated_at"],
        "research_captured_at": profile_data["research_captured_at"],
        "research_notes": profile_data.get("research_notes"),
        "source_count": profile_data["source_count"],
        "is_latest": profile_data["is_latest"],
        "created_at": profile_data["created_at"]
    }

    # Add company
    if 'companies' in profile_data and profile_data['companies']:
        company = profile_data['companies'] if isinstance(profile_data['companies'], dict) else profile_data['companies'][0]
        response['company'] = {
            "id": company.get("id"),
            "name": company.get("name"),
            "ticker": company.get("ticker"),
            "industry": company.get("industry")
        }

    # Include sources if requested
    if include and 'sources' in include:
        sources_result = supabase.table('data_sources') \
            .select('*') \
            .eq('profile_id', profile_id) \
            .execute()
        response['sources'] = sources_result.data

    # Include commitments if requested
    if include and 'commitments' in include:
        commitments_result = supabase.table('commitments') \
            .select('*') \
            .eq('profile_id', profile_id) \
            .execute()
        response['commitments'] = commitments_result.data

    return {"data": response}

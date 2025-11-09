"""Controversies API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import Optional
from supabase import Client
from app.database import get_db
from app.schemas import Controversy, ControversyWithCompany, PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key
from app.utils.cache import cached

router = APIRouter(prefix="/controversies", tags=["controversies"])


@router.get("/", response_model=dict)
@cached("controversies:list", ttl=300)
async def list_controversies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    type: Optional[str] = Query(None, description="Filter by controversy type"),
    status: Optional[str] = Query(None, description="Filter by status (ongoing, settled, dismissed)"),
    search: Optional[str] = Query(None, description="Search in description"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all DEI-related controversies and lawsuits with filtering.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('controversies').select(
        '''
        id,
        profile_id,
        date,
        type,
        status,
        description,
        case_name,
        docket_number,
        court,
        nlrb_case_id,
        filing_url,
        quotes,
        provenance_ids,
        profiles!inner(
            id,
            company_id,
            companies!inner(id, name, ticker, industry)
        )
        ''',
        count='exact'
    )

    # Apply filters
    if profile_id:
        query = query.eq('profile_id', profile_id)
    if type:
        query = query.eq('type', type)
    if status:
        query = query.eq('status', status)
    if search:
        query = query.ilike('description', f'%{search}%')
    if company_id:
        query = query.eq('profiles.company_id', company_id)

    # Order by date descending
    query = query.order('date', desc=True)

    # Get total count
    count_result = query.execute()
    total_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)

    # Apply pagination
    query = query.range(offset, offset + per_page - 1)
    result = query.execute()

    # Calculate pagination
    total_pages = (total_count + per_page - 1) // per_page
    pagination = PaginationMeta(
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count,
        has_next=page < total_pages,
        has_prev=page > 1,
        next_page=page + 1 if page < total_pages else None,
        prev_page=page - 1 if page > 1 else None
    )

    # Transform data
    controversies_data = []
    for controversy in result.data:
        controversy_dict = dict(controversy)
        profiles = controversy_dict.pop('profiles', None)
        if profiles and 'companies' in profiles:
            controversy_dict['company'] = profiles['companies']
        controversies_data.append(controversy_dict)

    return {
        "data": controversies_data,
        "pagination": pagination.dict()
    }


@router.get("/{controversy_id}", response_model=dict)
@cached(
    "controversy:detail",
    ttl=300,
    key_builder=lambda controversy_id, db, key_validation: f"controversy:detail:{controversy_id}"
)
async def get_controversy(
    controversy_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get detailed information about a specific controversy.
    """
    result = db.table('controversies') \
        .select('''
            *,
            profiles!inner(
                id,
                company_id,
                companies!inner(id, name, ticker, industry)
            )
        ''') \
        .eq('id', controversy_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Controversy not found")

    controversy_data = result.data[0]

    # Transform company data
    profiles = controversy_data.pop('profiles', None)
    if profiles and 'companies' in profiles:
        controversy_data['company'] = profiles['companies']

    # Fetch sources via junction table
    sources_result = db.table('controversy_sources') \
        .select('''
            data_sources(
                id,
                source_id,
                source_type,
                publisher,
                author,
                url,
                date,
                title,
                reliability_score,
                doc_type,
                notes
            )
        ''') \
        .eq('controversy_id', controversy_id) \
        .execute()

    if sources_result.data:
        controversy_data['sources'] = [s['data_sources'] for s in sources_result.data if s.get('data_sources')]
    else:
        controversy_data['sources'] = []

    return {"data": controversy_data}

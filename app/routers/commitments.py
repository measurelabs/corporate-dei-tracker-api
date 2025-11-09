"""Commitments API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import Optional
from supabase import Client
from app.database import get_db
from app.schemas import Commitment, CommitmentWithCompany, PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key
from app.utils.cache import cached

router = APIRouter(prefix="/commitments", tags=["commitments"])


@router.get("/", response_model=dict)
@cached("commitments:list", ttl=300)
async def list_commitments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    commitment_type: Optional[str] = Query(None, description="Filter by type (pledge, industry_initiative)"),
    status: Optional[str] = Query(None, description="Filter by status (active, completed, discontinued)"),
    search: Optional[str] = Query(None, description="Search in commitment name"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all DEI commitments and initiatives with filtering.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('commitments').select(
        '''
        id,
        profile_id,
        commitment_name,
        commitment_type,
        current_status,
        status_changed_at,
        previous_status,
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
    if commitment_type:
        query = query.eq('commitment_type', commitment_type)
    if status:
        query = query.eq('current_status', status)
    if search:
        query = query.ilike('commitment_name', f'%{search}%')
    if company_id:
        query = query.eq('profiles.company_id', company_id)

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
    commitments_data = []
    for commitment in result.data:
        commitment_dict = dict(commitment)
        profiles = commitment_dict.pop('profiles', None)
        if profiles and 'companies' in profiles:
            commitment_dict['company'] = profiles['companies']
        commitment_dict['quote_count'] = len(commitment_dict.get('quotes') or [])
        commitment_dict['source_count'] = len(commitment_dict.get('provenance_ids') or [])
        commitments_data.append(commitment_dict)

    return {
        "data": commitments_data,
        "pagination": pagination.dict()
    }


@router.get("/{commitment_id}", response_model=dict)
@cached(
    "commitment:detail",
    ttl=300,
    key_builder=lambda commitment_id, db, key_validation: f"commitment:detail:{commitment_id}"
)
async def get_commitment(
    commitment_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get detailed information about a specific commitment.
    """
    result = db.table('commitments') \
        .select('''
            *,
            profiles!inner(
                id,
                company_id,
                companies!inner(id, name, ticker, industry)
            )
        ''') \
        .eq('id', commitment_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Commitment not found")

    commitment_data = result.data[0]

    # Transform company data
    profiles = commitment_data.pop('profiles', None)
    if profiles and 'companies' in profiles:
        commitment_data['company'] = profiles['companies']

    # Fetch sources via junction table
    sources_result = db.table('commitment_sources') \
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
        .eq('commitment_id', commitment_id) \
        .execute()

    if sources_result.data:
        commitment_data['sources'] = [s['data_sources'] for s in sources_result.data if s.get('data_sources')]
    else:
        commitment_data['sources'] = []

    return {"data": commitment_data}


@router.get("/types/stats", response_model=dict)
@cached("commitments:types:stats", ttl=600)
async def get_commitment_type_stats(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get statistics for all commitment types.

    Returns count of total commitments, active commitments,
    and number of companies for each commitment type.
    """
    # Get all commitments with company info
    result = db.table('commitments') \
        .select('''
            commitment_type,
            current_status,
            profiles!inner(company_id)
        ''') \
        .execute()

    # Calculate statistics
    type_stats = {}
    for commitment in result.data:
        ctype = commitment['commitment_type']
        if ctype not in type_stats:
            type_stats[ctype] = {
                'commitment_type': ctype,
                'count': 0,
                'active_count': 0,
                'companies': set()
            }

        type_stats[ctype]['count'] += 1
        if commitment['current_status'] == 'active':
            type_stats[ctype]['active_count'] += 1
        if 'profiles' in commitment and 'company_id' in commitment['profiles']:
            type_stats[ctype]['companies'].add(commitment['profiles']['company_id'])

    # Convert to list and format
    stats_list = []
    for ctype, stats in type_stats.items():
        stats_list.append({
            'commitment_type': stats['commitment_type'],
            'count': stats['count'],
            'active_count': stats['active_count'],
            'companies_count': len(stats['companies'])
        })

    return {"data": stats_list}

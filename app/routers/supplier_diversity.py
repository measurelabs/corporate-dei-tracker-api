"""Supplier Diversity API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import Optional
from supabase import Client
from app.database import get_db
from app.schemas import PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/supplier-diversity", tags=["supplier_diversity"])


@router.get("/", response_model=dict)
async def list_supplier_diversity(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    program_exists: Optional[bool] = Query(None, description="Filter by program existence"),
    program_status: Optional[str] = Query(None, description="Filter by program status"),
    spending_disclosed: Optional[bool] = Query(None, description="Filter by spending disclosure"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all supplier diversity programs with filtering and pagination.

    Supplier diversity programs track company commitments to engaging
    diverse suppliers in their supply chains.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('supplier_diversity').select(
        '''
        profile_id,
        program_exists,
        program_status,
        spending_disclosed,
        quotes,
        provenance_ids,
        created_at,
        updated_at,
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
    if program_exists is not None:
        query = query.eq('program_exists', program_exists)
    if program_status:
        query = query.eq('program_status', program_status)
    if spending_disclosed is not None:
        query = query.eq('spending_disclosed', spending_disclosed)
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
    supplier_data = []
    for item in result.data:
        item_dict = dict(item)
        profiles = item_dict.pop('profiles', None)
        if profiles and 'companies' in profiles:
            item_dict['company'] = profiles['companies']
        supplier_data.append(item_dict)

    return {
        "data": supplier_data,
        "pagination": pagination.dict()
    }


@router.get("/{profile_id}", response_model=dict)
async def get_supplier_diversity(
    profile_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get supplier diversity program information for a specific profile.
    """
    result = db.table('supplier_diversity') \
        .select('''
            *,
            profiles!inner(
                id,
                company_id,
                companies!inner(id, name, ticker, industry)
            )
        ''') \
        .eq('profile_id', profile_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Supplier diversity program not found")

    supplier_data = result.data[0]

    # Transform company data
    profiles = supplier_data.pop('profiles', None)
    if profiles and 'companies' in profiles:
        supplier_data['company'] = profiles['companies']

    return {"data": supplier_data}


@router.get("/stats/overview", response_model=dict)
async def get_supplier_diversity_stats(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get overall statistics for supplier diversity programs.

    Returns counts and breakdowns by program status and disclosure.
    """
    # Get all supplier diversity records
    result = db.table('supplier_diversity') \
        .select('program_exists, program_status, spending_disclosed') \
        .execute()

    total = len(result.data)
    programs_exist = sum(1 for r in result.data if r.get('program_exists'))
    spending_disclosed = sum(1 for r in result.data if r.get('spending_disclosed'))

    # Status breakdown
    status_breakdown = {}
    for record in result.data:
        status = record.get('program_status', 'unknown')
        if status:
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

    return {
        "data": {
            "total_companies": total,
            "programs_exist": programs_exist,
            "programs_exist_percentage": round((programs_exist / total * 100), 1) if total > 0 else 0,
            "spending_disclosed": spending_disclosed,
            "spending_disclosed_percentage": round((spending_disclosed / total * 100), 1) if total > 0 else 0,
            "status_breakdown": status_breakdown
        }
    }

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_supabase_client
from schemas.company import CompanyResponse, CompanyWithProfile

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=dict)
async def list_companies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    country: Optional[str] = None,
    state: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = Query("name", regex="^(name|ticker|industry|created_at)$"),
    order: str = Query("asc", regex="^(asc|desc)$")
):
    """List all companies with optional filtering and pagination"""
    supabase = get_supabase_client()

    # Calculate offset
    offset = (page - 1) * per_page

    # Build query
    query = supabase.table('companies').select('*', count='exact')

    # Apply filters
    if industry:
        query = query.eq('industry', industry)
    if country:
        query = query.eq('hq_country', country)
    if state:
        query = query.eq('hq_state', state)
    if search:
        query = query.or_(f'name.ilike.%{search}%,ticker.ilike.%{search}%')

    # Apply sorting
    query = query.order(sort, desc=(order == 'desc'))

    # Apply pagination
    query = query.range(offset, offset + per_page - 1)

    # Execute query
    result = query.execute()

    # Calculate pagination info
    total_count = result.count if result.count else 0
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    # Transform data
    companies = [CompanyResponse.from_db(row) for row in result.data]

    return {
        "data": [c.model_dump() for c in companies],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


@router.get("/{company_id}", response_model=dict)
async def get_company(
    company_id: str,
    include: Optional[str] = None
):
    """Get a single company by ID"""
    supabase = get_supabase_client()

    # Check if we should include related data
    if include and 'profile' in include:
        # Get company with profile
        result = supabase.table('companies') \
            .select('*, profiles(*)') \
            .eq('id', company_id) \
            .execute()
    else:
        result = supabase.table('companies') \
            .select('*') \
            .eq('id', company_id) \
            .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    company_data = result.data[0]
    company = CompanyResponse.from_db(company_data)

    response = company.model_dump()

    # Add profile if included
    if include and 'profile' in include and 'profiles' in company_data:
        profiles = company_data.get('profiles', [])
        if profiles:
            profile = profiles[0] if isinstance(profiles, list) else profiles
            response['profile'] = {
                'id': profile.get('id'),
                'generated_at': profile.get('generated_at'),
                'research_captured_at': profile.get('research_captured_at'),
                'source_count': profile.get('source_count'),
                'is_latest': profile.get('is_latest')
            }

    return {"data": response}


@router.get("/ticker/{ticker}", response_model=dict)
async def get_company_by_ticker(ticker: str):
    """Get company by ticker symbol"""
    supabase = get_supabase_client()

    result = supabase.table('companies') \
        .select('*') \
        .eq('ticker', ticker.upper()) \
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail=f"Company with ticker {ticker} not found"
        )

    company = CompanyResponse.from_db(result.data[0])
    return {"data": company.model_dump()}


@router.get("/search/advanced", response_model=dict)
async def advanced_search(
    q: Optional[str] = None,
    industries: Optional[str] = Query(None, description="Comma-separated industries"),
    countries: Optional[str] = Query(None, description="Comma-separated countries"),
    has_profile: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Advanced search with multiple criteria"""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page
    query = supabase.table('companies').select('*', count='exact')

    # Search query
    if q:
        query = query.or_(f'name.ilike.%{q}%,ticker.ilike.%{q}%')

    # Multiple industries
    if industries:
        industry_list = [i.strip() for i in industries.split(',')]
        query = query.in_('industry', industry_list)

    # Multiple countries
    if countries:
        country_list = [c.strip() for c in countries.split(',')]
        query = query.in_('hq_country', country_list)

    query = query.range(offset, offset + per_page - 1)
    result = query.execute()

    total_count = result.count if result.count else 0
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    companies = [CompanyResponse.from_db(row) for row in result.data]

    return {
        "data": [c.model_dump() for c in companies],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    }

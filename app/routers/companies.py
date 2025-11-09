"""Companies API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import List, Optional
from supabase import Client
from app.database import get_db
from app.schemas import Company, CompanyWithStats, PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key
from app.config import get_settings
from app.utils.cache import cached

settings = get_settings()
router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=dict)
@cached("companies:list", ttl=300)
async def list_companies(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    country: Optional[str] = Query(None, description="Filter by headquarters country"),
    state: Optional[str] = Query(None, description="Filter by headquarters state"),
    search: Optional[str] = Query(None, description="Search by company name or ticker"),
    sort: str = Query("name", description="Sort field (name, ticker, industry, created_at)"),
    order: str = Query("asc", description="Sort order (asc, desc)"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all companies with optional filtering and pagination.

    Supports filtering by industry, location, and search.
    Returns paginated results with metadata.
    """
    # Calculate offset
    offset = (page - 1) * per_page

    # Build base query with lightweight profile summary data
    # We select specific fields from profiles_full to avoid loading all the heavy profile data
    query = db.table('companies').select(
        '''
        *
        ''',
        count='exact'
    )

    # We'll need to join with profiles_full separately for the summary fields
    # This is a lightweight query that only pulls the fields we need for badges

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
    if order == "desc":
        query = query.order(sort, desc=True)
    else:
        query = query.order(sort)

    # Get total count (note: we need to get count before executing)
    # The count is already set when we do select(..., count='exact')
    # Apply pagination before executing
    query = query.range(offset, offset + per_page - 1)

    # Execute query
    result = query.execute()
    companies_data = result.data

    # Get total count from the result
    total_count = result.count if hasattr(result, 'count') else len(companies_data)

    # Get company IDs to fetch profile summaries
    company_ids = [c['id'] for c in companies_data]

    # Fetch lightweight profile summary data for these companies
    # Only select the specific fields we need for badges
    # IMPORTANT: Filter for latest profiles only
    profile_summaries = {}
    if company_ids:
        profiles_result = db.table('profiles_full').select(
            'company_id, profile_id, source_count, dei_status, risk_level, commitment_strength_rating, transparency_rating, recommendation'
        ).in_('company_id', company_ids).eq('is_latest', True).execute()

        # Create lookup dict by company_id
        for profile in profiles_result.data:
            profile_summaries[profile['company_id']] = profile

    # Calculate pagination metadata
    total_pages = (total_count + per_page - 1) // per_page
    has_next = page < total_pages
    has_prev = page > 1

    pagination = PaginationMeta(
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_count=total_count,
        has_next=has_next,
        has_prev=has_prev,
        next_page=page + 1 if has_next else None,
        prev_page=page - 1 if has_prev else None
    )

    # Transform data to include lightweight profile info
    for company in companies_data:
        profile = profile_summaries.get(company['id'])
        if profile:
            company['profile_id'] = profile.get('profile_id')
            company['has_profile'] = True
            company['source_count'] = profile.get('source_count', 0)
            company['dei_status'] = profile.get('dei_status')
            company['risk_level'] = profile.get('risk_level')
            company['commitment_strength_rating'] = profile.get('commitment_strength_rating')
            company['transparency_rating'] = profile.get('transparency_rating')
            company['recommendation'] = profile.get('recommendation')
        else:
            company['profile_id'] = None
            company['has_profile'] = False
            company['source_count'] = 0
            company['dei_status'] = None
            company['risk_level'] = None
            company['commitment_strength_rating'] = None
            company['transparency_rating'] = None
            company['recommendation'] = None

    return {
        "data": companies_data,
        "pagination": pagination.dict()
    }


@router.get("/{company_id}", response_model=dict)
@cached(
    "company:detail",
    ttl=300,
    key_builder=lambda company_id, include, db, key_validation: f"company:detail:{company_id}:{include or 'basic'}"
)
async def get_company(
    company_id: str,
    include: Optional[str] = Query(None, description="Include related data: profile, commitments, sources, all"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get detailed information for a specific company.

    Optionally include related data like profile, commitments, and sources.
    """
    # Build select query based on include parameter
    if include == "all":
        select_query = '''
            *,
            profiles!inner(
                *,
                commitments(count),
                controversies(count),
                events(count)
            )
        '''
    elif include == "profile":
        select_query = '''
            *,
            profiles!inner(*)
        '''
    else:
        select_query = '*'

    result = db.table('companies') \
        .select(select_query) \
        .eq('id', company_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Company not found")

    return {"data": result.data[0]}


@router.get("/ticker/{ticker}", response_model=dict)
@cached(
    "company:ticker",
    ttl=300,
    key_builder=lambda ticker, include, db, key_validation: f"company:ticker:{ticker.upper()}:{include or 'basic'}"
)
async def get_company_by_ticker(
    ticker: str,
    include: Optional[str] = Query(None, description="Include related data: profile, commitments, sources, all"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get company by ticker symbol.

    Useful for looking up companies by their stock ticker.
    """
    # Normalize ticker to uppercase
    ticker = ticker.upper()

    # Build select query based on include parameter
    if include == "all":
        select_query = '''
            *,
            profiles!inner(
                *,
                commitments(count),
                controversies(count),
                events(count)
            )
        '''
    elif include == "profile":
        select_query = '''
            *,
            profiles!inner(*)
        '''
    else:
        select_query = '*'

    result = db.table('companies') \
        .select(select_query) \
        .eq('ticker', ticker) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Company with ticker '{ticker}' not found"
        )

    return {"data": result.data[0]}


@router.get("/search/autocomplete", response_model=dict)
@cached(
    "companies:autocomplete",
    ttl=300,
    key_builder=lambda q, limit, db, key_validation: f"companies:autocomplete:{q.lower()}:{limit}"
)
async def autocomplete_companies(
    q: str = Query(..., min_length=1, description="Search query for autocomplete"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Autocomplete endpoint for company search.

    Returns a lightweight list of companies matching the query,
    optimized for autocomplete dropdowns. Searches by name and ticker.
    """
    # Search by name or ticker with case-insensitive matching
    result = db.table('companies').select(
        'id, name, ticker, industry, hq_country, hq_city'
    ).or_(
        f'name.ilike.%{q}%,ticker.ilike.%{q}%'
    ).order('name').limit(limit).execute()

    return {
        "data": result.data,
        "count": len(result.data)
    }


@router.get("/filters/options", response_model=dict)
@cached("companies:filters:options", ttl=600)
async def get_filter_options(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get unique filter option values for industries, countries, and states.

    Returns distinct values for each filter type, optimized for dropdown menus.
    Results are cached for 10 minutes.
    """
    # Get all companies with only the fields we need for filters
    result = db.table('companies').select('industry, hq_country, hq_state').execute()

    # Extract unique values using sets for efficiency
    industries = set()
    countries = set()
    states = set()

    for company in result.data:
        if company.get('industry'):
            industries.add(company['industry'])
        if company.get('hq_country'):
            countries.add(company['hq_country'])
        if company.get('hq_state'):
            states.add(company['hq_state'])

    return {
        "data": {
            "industries": sorted(list(industries)),
            "countries": sorted(list(countries)),
            "states": sorted(list(states))
        }
    }


@router.get("/search/advanced", response_model=dict)
async def advanced_search(
    q: Optional[str] = Query(None, description="Search query"),
    industries: Optional[List[str]] = Query(None, description="Filter by multiple industries"),
    countries: Optional[List[str]] = Query(None, description="Filter by multiple countries"),
    has_commitments: Optional[bool] = Query(None, description="Only companies with active commitments"),
    min_sources: Optional[int] = Query(None, description="Minimum number of sources"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Advanced search with multiple criteria.

    Supports complex filtering by multiple industries, countries,
    commitment status, and minimum source requirements.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('companies').select(
        '''
        *,
        profiles!inner(id, source_count)
        ''',
        count='exact'
    )

    # Apply filters
    if q:
        query = query.or_(f'name.ilike.%{q}%,ticker.ilike.%{q}%')

    if industries and len(industries) > 0:
        industry_filter = ','.join([f'industry.eq.{ind}' for ind in industries])
        query = query.or_(industry_filter)

    if countries and len(countries) > 0:
        country_filter = ','.join([f'hq_country.eq.{c}' for c in countries])
        
        query = query.or_(country_filter)

    # Get results
    count_result = query.execute()
    total_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)

    query = query.range(offset, offset + per_page - 1)
    result = query.execute()

    # Post-process for min_sources filter
    companies_data = result.data
    if min_sources:
        companies_data = [
            c for c in companies_data
            if c.get('profiles', [{}])[0].get('source_count', 0) >= min_sources
        ]
        total_count = len(companies_data)

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

    return {
        "data": companies_data,
        "pagination": pagination.dict()
    }

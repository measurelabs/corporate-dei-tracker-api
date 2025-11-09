"""Profiles API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import Optional
from supabase import Client
from app.database import get_db
from app.schemas import Profile, FullProfile, PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key
from app.config import get_settings
from app.utils.cache import cached

settings = get_settings()
router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/", response_model=dict)
@cached("profiles:list", ttl=300)
async def list_profiles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    min_sources: Optional[int] = Query(None, description="Minimum source count"),
    is_latest: bool = Query(True, description="Only show latest profiles"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all DEI profiles with optional filtering.

    Returns profile metadata with company information.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('profiles').select(
        '''
        id,
        company_id,
        schema_version,
        profile_type,
        generated_at,
        research_captured_at,
        research_notes,
        source_count,
        is_latest,
        created_at,
        companies!inner(id, name, ticker, industry)
        ''',
        count='exact'
    )

    # Apply filters
    if company_id:
        query = query.eq('company_id', company_id)
    if is_latest:
        query = query.eq('is_latest', True)
    if min_sources:
        query = query.gte('source_count', min_sources)

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
    profiles_data = []
    for profile in result.data:
        profile_dict = dict(profile)
        companies = profile_dict.pop('companies', None)
        if companies:
            profile_dict['company'] = companies
        profiles_data.append(profile_dict)

    return {
        "data": profiles_data,
        "pagination": pagination.dict()
    }


@router.get("/{profile_id}", response_model=dict)
async def get_profile(
    profile_id: str,
    full: bool = Query(True, description="Return full profile with all components (default: true)"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get detailed DEI profile.

    By default, returns the complete profile with all components including
    AI analysis, DEI posture, commitments, controversies, and all related data.
    Set full=false for a lighter response with just basic profile info.
    """
    # Default to full profile
    if full:
        return await get_full_profile(profile_id, db, key_validation)

    # Lightweight version
    result = db.table('profiles') \
        .select('''
            id,
            company_id,
            schema_version,
            profile_type,
            generated_at,
            research_captured_at,
            research_notes,
            source_count,
            is_latest,
            created_at,
            companies!inner(id, name, ticker, industry, hq_city, hq_state, hq_country)
        ''') \
        .eq('id', profile_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = result.data[0]

    # Transform company data
    if 'companies' in profile_data:
        profile_data['company'] = profile_data.pop('companies')

    return {"data": profile_data}


@router.get("/{profile_id}/full", response_model=dict)
@cached(
    "profile:full",
    ttl=900,  # Cache for 15 minutes
    key_builder=lambda profile_id, db, key_validation: f"profile:full:{profile_id}"
)
async def get_full_profile(
    profile_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get complete DEI profile with all components.

    This endpoint returns the comprehensive profile including:
    - Company information
    - AI analysis (context, insights, strategic implications)
    - DEI posture
    - CDO role information
    - Reporting practices
    - Supplier diversity
    - Risk assessment
    - Data quality flags
    - All related commitments, controversies, events, and sources

    Results are cached for 15 minutes.
    """
    # Get base profile
    profile_result = db.table('profiles') \
        .select('''
            id,
            company_id,
            schema_version,
            profile_type,
            generated_at,
            research_captured_at,
            research_notes,
            source_count,
            is_latest,
            created_at,
            companies!inner(id, name, ticker, industry, hq_city, hq_state, hq_country)
        ''') \
        .eq('id', profile_id) \
        .execute()

    if not profile_result.data or len(profile_result.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = profile_result.data[0]
    profile_data['company'] = profile_data.pop('companies', None)

    # Get AI Context
    ai_context_result = db.table('ai_contexts') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if ai_context_result.data:
        profile_data['ai_context'] = ai_context_result.data[0]

    # Get AI Key Insights
    insights_result = db.table('ai_key_insights') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .order('insight_order') \
        .execute()
    profile_data['key_insights'] = insights_result.data

    # Get AI Strategic Implications
    implications_result = db.table('ai_strategic_implications') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .order('implication_order') \
        .execute()
    profile_data['strategic_implications'] = implications_result.data

    # Get DEI Posture
    posture_result = db.table('dei_postures') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if posture_result.data:
        profile_data['dei_posture'] = posture_result.data[0]

    # Get CDO Role
    cdo_result = db.table('cdo_roles') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if cdo_result.data:
        profile_data['cdo_role'] = cdo_result.data[0]

    # Get Reporting Practices
    reporting_result = db.table('reporting_practices') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if reporting_result.data:
        profile_data['reporting_practices'] = reporting_result.data[0]

    # Get Supplier Diversity
    supplier_result = db.table('supplier_diversity') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if supplier_result.data:
        profile_data['supplier_diversity'] = supplier_result.data[0]

    # Get Risk Assessment
    risk_result = db.table('risk_assessments') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if risk_result.data:
        profile_data['risk_assessment'] = risk_result.data[0]

    # Get Data Quality Flags
    quality_result = db.table('data_quality_flags') \
        .select('*') \
        .eq('profile_id', profile_id) \
        .execute()
    if quality_result.data:
        profile_data['data_quality_flags'] = quality_result.data[0]

    # Get related data counts and samples
    commitments_result = db.table('commitments') \
        .select('id, commitment_name, commitment_type, current_status, quotes') \
        .eq('profile_id', profile_id) \
        .execute()

    # Fetch sources for each commitment via junction table
    commitments_data = []
    for commitment in commitments_result.data:
        commitment_dict = dict(commitment)
        sources_result = db.table('commitment_sources') \
            .select('data_sources(id, source_id, source_type, title, url, date, reliability_score)') \
            .eq('commitment_id', commitment['id']) \
            .execute()
        if sources_result.data:
            commitment_dict['sources'] = [s['data_sources'] for s in sources_result.data if s.get('data_sources')]
        else:
            commitment_dict['sources'] = []
        commitments_data.append(commitment_dict)

    profile_data['commitments'] = commitments_data
    profile_data['commitment_count'] = len(commitments_data)

    controversies_result = db.table('controversies') \
        .select('id, type, status, description, date, case_name, quotes') \
        .eq('profile_id', profile_id) \
        .execute()

    # Fetch sources for each controversy via junction table
    controversies_data = []
    for controversy in controversies_result.data:
        controversy_dict = dict(controversy)
        sources_result = db.table('controversy_sources') \
            .select('data_sources(id, source_id, source_type, title, url, date, reliability_score)') \
            .eq('controversy_id', controversy['id']) \
            .execute()
        if sources_result.data:
            controversy_dict['sources'] = [s['data_sources'] for s in sources_result.data if s.get('data_sources')]
        else:
            controversy_dict['sources'] = []
        controversies_data.append(controversy_dict)

    profile_data['controversies'] = controversies_data
    profile_data['controversy_count'] = len(controversies_data)

    events_result = db.table('events') \
        .select('id, date, event_type, headline, sentiment, impact, impact_magnitude, impact_direction, event_category, summary, quotes') \
        .eq('profile_id', profile_id) \
        .execute()

    # Fetch sources for each event via junction table
    events_data = []
    for event in events_result.data:
        event_dict = dict(event)
        sources_result = db.table('event_sources') \
            .select('data_sources(id, source_id, source_type, title, url, date, reliability_score)') \
            .eq('event_id', event['id']) \
            .execute()
        if sources_result.data:
            event_dict['sources'] = [s['data_sources'] for s in sources_result.data if s.get('data_sources')]
        else:
            event_dict['sources'] = []
        events_data.append(event_dict)

    profile_data['events'] = events_data
    profile_data['event_count'] = len(events_data)

    sources_result = db.table('data_sources') \
        .select('id, source_id, source_type, title, url, date, reliability_score, notes, publisher, author, doc_type') \
        .eq('profile_id', profile_id) \
        .order('date', desc=True) \
        .execute()

    # Transform notes to summary for frontend compatibility
    sources_data = []
    for source in sources_result.data:
        source_dict = dict(source)
        if 'notes' in source_dict:
            source_dict['summary'] = source_dict.get('notes')
        sources_data.append(source_dict)

    profile_data['sources'] = sources_data

    return {"data": profile_data}


@router.get("/company/{company_id}/latest", response_model=dict)
async def get_latest_profile_for_company(
    company_id: str,
    full: bool = Query(True, description="Return full profile with all components (default: true)"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get the latest DEI profile for a specific company.

    By default returns the complete profile with all components.
    Set full=false for a lighter response.
    """
    # Get latest profile
    result = db.table('profiles') \
        .select('id') \
        .eq('company_id', company_id) \
        .eq('is_latest', True) \
        .limit(1) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found for company {company_id}"
        )

    profile_id = result.data[0]['id']

    # Redirect to get_profile which handles full parameter
    return await get_profile(profile_id, full, db, key_validation)


@router.get("/ranked/at-risk", response_model=dict)
@cached(
    "profiles:ranked:at-risk",
    ttl=300,  # Cache for 5 minutes
    key_builder=lambda limit, db, key_validation: f"profiles:ranked:at-risk:{limit}"
)
async def get_at_risk_profiles(
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get companies ranked by risk score (highest first).

    Uses profiles_full view for efficient querying.
    Returns profiles with highest DEI-related risk scores.
    Cached for 5 minutes.
    """
    result = db.table('profiles_full') \
        .select('*') \
        .eq('is_latest', True) \
        .not_.is_('overall_risk_score', 'null') \
        .order('overall_risk_score', desc=True) \
        .limit(limit) \
        .execute()

    return {
        "data": result.data,
        "count": len(result.data)
    }


@router.get("/ranked/top-committed", response_model=dict)
@cached(
    "profiles:ranked:committed",
    ttl=300,  # Cache for 5 minutes
    key_builder=lambda limit, db, key_validation: f"profiles:ranked:committed:{limit}"
)
async def get_top_committed_profiles(
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get companies ranked by commitment count (highest first).

    Queries profiles_full and joins with profiles_with_commitment_counts.
    Returns profiles with most DEI commitments.
    Cached for 5 minutes.
    """
    # Get commitment counts directly from the database
    # Using a more efficient approach: get all commitments and count them
    commitments_result = db.table('commitments') \
        .select('profile_id') \
        .execute()

    if not commitments_result.data:
        return {"data": [], "count": 0}

    # Count commitments by profile_id
    commitment_counts = {}
    for c in commitments_result.data:
        pid = str(c['profile_id'])  # Ensure string format
        commitment_counts[pid] = commitment_counts.get(pid, 0) + 1

    # Sort by count and get top profiles
    sorted_profiles = sorted(commitment_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    if not sorted_profiles:
        return {"data": [], "count": 0}

    # Get the profile IDs with highest commitment counts
    profile_ids = [p[0] for p in sorted_profiles]
    commitment_counts_dict = {p[0]: p[1] for p in sorted_profiles}

    # Guard against empty profile_ids
    if not profile_ids:
        return {"data": [], "count": 0}

    # Get full profile data from profiles_full using batching if needed
    # PostgREST has limits on IN clause size, so we'll fetch individually or use a different approach
    # For small limits (20-50), we can fetch one by one or in small batches
    all_profiles = []

    # Fetch in batches of 10 to avoid PostgREST IN clause limits
    batch_size = 10
    for i in range(0, len(profile_ids), batch_size):
        batch = profile_ids[i:i + batch_size]

        batch_result = db.table('profiles_full') \
            .select('*') \
            .in_('profile_id', batch) \
            .eq('is_latest', True) \
            .execute()

        all_profiles.extend(batch_result.data)

    profiles_result = type('obj', (object,), {'data': all_profiles})

    # Add commitment_count to each profile and sort
    for profile in profiles_result.data:
        profile_id_str = str(profile['profile_id'])
        profile['commitment_count'] = commitment_counts_dict.get(profile_id_str, 0)

    # Sort by commitment count (since .in_ doesn't preserve order)
    sorted_profiles = sorted(profiles_result.data, key=lambda p: p['commitment_count'], reverse=True)

    return {
        "data": sorted_profiles,
        "count": len(sorted_profiles)
    }

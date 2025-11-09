"""Events API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import Optional
from supabase import Client
from app.database import get_db
from app.schemas import Event, EventWithCompany, PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=dict)
async def list_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (positive, negative, neutral)"),
    impact: Optional[str] = Query(None, description="Filter by impact level"),
    impact_magnitude: Optional[str] = Query(None, description="Filter by impact magnitude"),
    impact_direction: Optional[str] = Query(None, description="Filter by impact direction"),
    event_category: Optional[str] = Query(None, description="Filter by event category"),
    search: Optional[str] = Query(None, description="Search in headline or summary"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all events with filtering and pagination.

    Events represent significant occurrences related to company DEI initiatives,
    including announcements, milestones, setbacks, and changes.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('events').select(
        '''
        id,
        profile_id,
        date,
        headline,
        event_type,
        sentiment,
        impact,
        summary,
        quotes,
        provenance_ids,
        impact_magnitude,
        impact_direction,
        event_category,
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
    if event_type:
        query = query.eq('event_type', event_type)
    if sentiment:
        query = query.eq('sentiment', sentiment)
    if impact:
        query = query.eq('impact', impact)
    if impact_magnitude:
        query = query.eq('impact_magnitude', impact_magnitude)
    if impact_direction:
        query = query.eq('impact_direction', impact_direction)
    if event_category:
        query = query.eq('event_category', event_category)
    if search:
        query = query.or_(f'headline.ilike.%{search}%,summary.ilike.%{search}%')
    if company_id:
        query = query.eq('profiles.company_id', company_id)

    # Order by date descending (most recent first)
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
    events_data = []
    for event in result.data:
        event_dict = dict(event)
        profiles = event_dict.pop('profiles', None)
        if profiles and 'companies' in profiles:
            event_dict['company'] = profiles['companies']
        events_data.append(event_dict)

    return {
        "data": events_data,
        "pagination": pagination.dict()
    }


@router.get("/{event_id}", response_model=dict)
async def get_event(
    event_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get detailed information about a specific event.
    """
    result = db.table('events') \
        .select('''
            *,
            profiles!inner(
                id,
                company_id,
                companies!inner(id, name, ticker, industry)
            )
        ''') \
        .eq('id', event_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    event_data = result.data[0]

    # Transform company data
    profiles = event_data.pop('profiles', None)
    if profiles and 'companies' in profiles:
        event_data['company'] = profiles['companies']

    # Fetch sources via junction table
    sources_result = db.table('event_sources') \
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
        .eq('event_id', event_id) \
        .execute()

    if sources_result.data:
        event_data['sources'] = [s['data_sources'] for s in sources_result.data if s.get('data_sources')]
    else:
        event_data['sources'] = []

    return {"data": event_data}


@router.get("/types/stats", response_model=dict)
async def get_event_type_stats(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get statistics for all event types.

    Returns count and sentiment breakdown for each event type.
    """
    # Get all events with relevant fields
    result = db.table('events') \
        .select('event_type, sentiment, impact, event_category') \
        .execute()

    # Calculate statistics
    type_stats = {}
    for event in result.data:
        etype = event.get('event_type', 'unknown')
        if etype not in type_stats:
            type_stats[etype] = {
                'event_type': etype,
                'count': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'high_impact': 0
            }

        type_stats[etype]['count'] += 1

        sentiment = event.get('sentiment')
        if sentiment == 'positive':
            type_stats[etype]['positive'] += 1
        elif sentiment == 'negative':
            type_stats[etype]['negative'] += 1
        elif sentiment == 'neutral':
            type_stats[etype]['neutral'] += 1

        if event.get('impact') in ['high', 'major', 'significant']:
            type_stats[etype]['high_impact'] += 1

    # Convert to list
    stats_list = list(type_stats.values())

    # Sort by count descending
    stats_list.sort(key=lambda x: x['count'], reverse=True)

    return {"data": stats_list}

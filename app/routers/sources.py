"""Data sources API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security, BackgroundTasks
from typing import Optional
from supabase import Client
from app.database import get_db
from app.schemas import DataSource, DataSourceWithCompany, SourceTypeStats, PaginationMeta
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key
from app.utils.fetch_title import fetch_titles_batch, fetch_page_title
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=dict)
async def list_sources(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    source_type: Optional[str] = Query(None, description="Filter by type"),
    min_reliability: Optional[int] = Query(None, ge=1, le=5, description="Minimum reliability score"),
    publisher: Optional[str] = Query(None, description="Filter by publisher"),
    search: Optional[str] = Query(None, description="Search in title and notes"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    List all data sources with filtering.

    Sources document the evidence and research behind DEI profiles.
    """
    offset = (page - 1) * per_page

    # Build query
    query = db.table('data_sources').select(
        '''
        id,
        profile_id,
        source_id,
        source_type,
        publisher,
        author,
        url,
        date,
        title,
        reliability_score,
        doc_type,
        notes,
        profiles!inner(
            id,
            company_id,
            companies!inner(id, name, ticker)
        )
        ''',
        count='exact'
    )

    # Apply filters
    if profile_id:
        query = query.eq('profile_id', profile_id)
    if source_type:
        query = query.eq('source_type', source_type)
    if min_reliability:
        query = query.gte('reliability_score', min_reliability)
    if publisher:
        query = query.ilike('publisher', f'%{publisher}%')
    if search:
        query = query.or_(f'title.ilike.%{search}%,notes.ilike.%{search}%')
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
    sources_data = []
    for source in result.data:
        source_dict = dict(source)
        profiles = source_dict.pop('profiles', None)
        if profiles and 'companies' in profiles:
            source_dict['company'] = profiles['companies']
        sources_data.append(source_dict)

    return {
        "data": sources_data,
        "pagination": pagination.dict()
    }


@router.get("/{source_id}", response_model=dict)
async def get_source(
    source_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get detailed information about a specific data source.
    """
    result = db.table('data_sources') \
        .select('''
            *,
            profiles!inner(
                id,
                company_id,
                companies!inner(id, name, ticker, industry)
            )
        ''') \
        .eq('id', source_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Data source not found")

    source_data = result.data[0]

    # Transform company data
    profiles = source_data.pop('profiles', None)
    if profiles and 'companies' in profiles:
        source_data['company'] = profiles['companies']

    return {"data": source_data}


@router.get("/types/stats", response_model=dict)
async def get_source_type_stats(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get statistics for all source types.

    Returns count and average reliability score for each source type.
    """
    # Get all sources
    result = db.table('data_sources') \
        .select('source_type, reliability_score') \
        .execute()

    # Calculate statistics
    type_stats = {}
    for source in result.data:
        stype = source['source_type']
        if stype not in type_stats:
            type_stats[stype] = {
                'source_type': stype,
                'count': 0,
                'total_reliability': 0,
                'reliability_count': 0
            }

        type_stats[stype]['count'] += 1
        if source.get('reliability_score'):
            type_stats[stype]['total_reliability'] += source['reliability_score']
            type_stats[stype]['reliability_count'] += 1

    # Convert to list and calculate averages
    stats_list = []
    for stype, stats in type_stats.items():
        avg_reliability = None
        if stats['reliability_count'] > 0:
            avg_reliability = round(
                stats['total_reliability'] / stats['reliability_count'],
                2
            )

        stats_list.append({
            'source_type': stats['source_type'],
            'count': stats['count'],
            'avg_reliability': avg_reliability
        })

    # Sort by count descending
    stats_list.sort(key=lambda x: x['count'], reverse=True)

    return {"data": stats_list}


@router.post("/fetch-titles", response_model=dict)
async def fetch_and_update_titles(
    limit: Optional[int] = Query(None, description="Limit number of sources to update (for testing)"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Fetch page titles from URLs and update the database.

    This endpoint fetches HTML page meta titles for all sources that have a URL
    but are missing the title field.
    """
    # Get all sources with missing titles but valid URLs
    query = db.table('data_sources').select('id, url').is_('title', 'null').not_.is_('url', 'null')

    if limit:
        query = query.limit(limit)

    result = query.execute()
    sources = result.data

    if not sources:
        return {
            "message": "No sources found with missing titles",
            "updated": 0
        }

    logger.info(f"Found {len(sources)} sources with missing titles")

    # Extract URLs
    url_to_id = {source['url']: source['id'] for source in sources}
    urls = list(url_to_id.keys())

    # Fetch titles
    try:
        logger.info(f"Fetching titles for {len(urls)} URLs")
        titles_dict = await fetch_titles_batch(urls)

        # Update database
        updated_count = 0
        failed_count = 0

        for url, title in titles_dict.items():
            if title:
                try:
                    source_id = url_to_id[url]
                    db.table('data_sources').update({
                        'title': title
                    }).eq('id', source_id).execute()
                    updated_count += 1
                    logger.info(f"Updated title for source {source_id}: {title[:50]}")
                except Exception as e:
                    logger.error(f"Failed to update source for URL {url}: {str(e)}")
                    failed_count += 1
            else:
                failed_count += 1
                logger.warning(f"No title fetched for URL: {url}")

        return {
            "message": f"Successfully fetched and updated titles",
            "total_sources": len(sources),
            "updated": updated_count,
            "failed": failed_count,
            "success_rate": f"{(updated_count / len(sources) * 100):.1f}%" if len(sources) > 0 else "0%"
        }

    except Exception as e:
        logger.error(f"Error fetching titles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching titles: {str(e)}")


@router.patch("/{source_id}/title", response_model=dict)
async def update_source_title(
    source_id: str,
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Fetch and update the title for a specific source.
    """
    # Get the source
    result = db.table('data_sources') \
        .select('id, url, title') \
        .eq('id', source_id) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Source not found")

    source = result.data[0]

    if not source.get('url'):
        raise HTTPException(status_code=400, detail="Source has no URL to fetch title from")

    # Fetch title
    try:
        title = await fetch_page_title(source['url'])

        if not title:
            raise HTTPException(status_code=404, detail="Could not fetch title from URL")

        # Update database
        db.table('data_sources').update({
            'title': title
        }).eq('id', source_id).execute()

        return {
            "message": "Title updated successfully",
            "id": source_id,
            "title": title,
            "url": source['url']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching title for source {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching title: {str(e)}")

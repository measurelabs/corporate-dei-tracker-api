from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_supabase_client
from schemas.source import SourceResponse

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=dict)
async def list_sources(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = None,
    source_type: Optional[str] = None,
    min_reliability: Optional[int] = Query(None, ge=1, le=5),
    publisher: Optional[str] = None,
    search: Optional[str] = None
):
    """List all data sources with filtering"""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page
    query = supabase.table('data_sources').select('*', count='exact')

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

    query = query.order('date', desc=True)
    query = query.range(offset, offset + per_page - 1)

    result = query.execute()

    total_count = result.count if result.count else 0
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    return {
        "data": result.data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    }


@router.get("/types", response_model=dict)
async def get_source_types():
    """Get all source types with statistics"""
    supabase = get_supabase_client()

    # Get all sources
    result = supabase.table('data_sources').select('source_type, reliability_score').execute()

    # Calculate stats
    type_stats = {}
    for row in result.data:
        source_type = row['source_type']
        if source_type not in type_stats:
            type_stats[source_type] = {
                'count': 0,
                'total_reliability': 0
            }
        type_stats[source_type]['count'] += 1
        type_stats[source_type]['total_reliability'] += row['reliability_score']

    # Format response
    data = []
    for source_type, stats in type_stats.items():
        data.append({
            'source_type': source_type,
            'count': stats['count'],
            'avg_reliability': round(stats['total_reliability'] / stats['count'], 2)
        })

    # Sort by count
    data.sort(key=lambda x: x['count'], reverse=True)

    return {"data": data}


@router.get("/{source_id}", response_model=dict)
async def get_source(source_id: str):
    """Get detailed information about a specific source"""
    supabase = get_supabase_client()

    result = supabase.table('data_sources') \
        .select('*, profiles(*, companies(*))') \
        .eq('id', source_id) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Source not found")

    source_data = result.data[0]

    response = {
        "id": source_data["id"],
        "profile_id": source_data["profile_id"],
        "source_id": source_data["source_id"],
        "source_type": source_data["source_type"],
        "publisher": source_data["publisher"],
        "author": source_data.get("author"),
        "url": source_data["url"],
        "date": source_data["date"],
        "title": source_data["title"],
        "reliability_score": source_data["reliability_score"],
        "doc_type": source_data["doc_type"],
        "notes": source_data.get("notes")
    }

    # Add company info if available
    if 'profiles' in source_data and source_data['profiles']:
        profile = source_data['profiles'] if isinstance(source_data['profiles'], dict) else source_data['profiles'][0]
        if 'companies' in profile and profile['companies']:
            company = profile['companies'] if isinstance(profile['companies'], dict) else profile['companies'][0]
            response['company'] = {
                "id": company.get("id"),
                "name": company.get("name"),
                "ticker": company.get("ticker")
            }

    return {"data": response}

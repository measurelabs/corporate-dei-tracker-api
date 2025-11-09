from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_supabase_client
from schemas.commitment import CommitmentResponse

router = APIRouter(prefix="/commitments", tags=["commitments"])


@router.get("/", response_model=dict)
async def list_commitments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    profile_id: Optional[str] = None,
    commitment_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    changed_only: bool = Query(False, description="Only show commitments with status changes")
):
    """List all DEI commitments and initiatives"""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page
    query = supabase.table('commitments').select('*, profiles(*, companies(*))', count='exact')

    if profile_id:
        query = query.eq('profile_id', profile_id)
    if commitment_type:
        query = query.eq('commitment_type', commitment_type)
    if status:
        query = query.eq('current_status', status)
    if search:
        query = query.ilike('commitment_name', f'%{search}%')
    if changed_only:
        query = query.not_.is_('previous_status', 'null')

    query = query.order('commitment_name')
    query = query.range(offset, offset + per_page - 1)

    result = query.execute()

    total_count = result.count if result.count else 0
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    # Transform data
    commitments_data = []
    for row in result.data:
        commitment = {
            "id": row["id"],
            "profile_id": row["profile_id"],
            "commitment_name": row["commitment_name"],
            "commitment_type": row["commitment_type"],
            "current_status": row["current_status"],
            "quotes": row.get("quotes", []),
            "provenance_ids": row.get("provenance_ids", []),
            "status_changed_at": row.get("status_changed_at"),
            "previous_status": row.get("previous_status"),
            "quote_count": len(row.get("quotes", [])),
            "source_count": len(row.get("provenance_ids", []))
        }

        # Add company info
        if 'profiles' in row and row['profiles']:
            profile = row['profiles'] if isinstance(row['profiles'], dict) else row['profiles'][0]
            if 'companies' in profile and profile['companies']:
                company = profile['companies'] if isinstance(profile['companies'], dict) else profile['companies'][0]
                commitment['company'] = {
                    "id": company.get("id"),
                    "name": company.get("name"),
                    "ticker": company.get("ticker")
                }

        commitments_data.append(commitment)

    return {
        "data": commitments_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    }


@router.get("/types", response_model=dict)
async def get_commitment_types():
    """Get all commitment types with statistics"""
    supabase = get_supabase_client()

    result = supabase.table('commitments').select('commitment_type, current_status, profile_id').execute()

    # Calculate stats
    type_stats = {}
    for row in result.data:
        commitment_type = row['commitment_type']
        if commitment_type not in type_stats:
            type_stats[commitment_type] = {
                'count': 0,
                'active_count': 0,
                'profile_ids': set()
            }
        type_stats[commitment_type]['count'] += 1
        if row['current_status'] == 'active':
            type_stats[commitment_type]['active_count'] += 1
        type_stats[commitment_type]['profile_ids'].add(row['profile_id'])

    # Format response
    data = []
    for commitment_type, stats in type_stats.items():
        data.append({
            'commitment_type': commitment_type,
            'count': stats['count'],
            'active_count': stats['active_count'],
            'companies_count': len(stats['profile_ids'])
        })

    data.sort(key=lambda x: x['count'], reverse=True)

    return {"data": data}


@router.get("/changes", response_model=dict)
async def get_commitment_changes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    change_type: Optional[str] = Query(None, description="Filter by change: discontinued, reactivated")
):
    """Get commitments that have changed status"""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page
    query = supabase.table('commitments') \
        .select('*, profiles(*, companies(*))', count='exact') \
        .not_.is_('previous_status', 'null')

    # Filter by change type
    if change_type == 'discontinued':
        query = query.eq('current_status', 'discontinued')
    elif change_type == 'reactivated':
        query = query.eq('current_status', 'active').eq('previous_status', 'discontinued')

    query = query.order('status_changed_at', desc=True)
    query = query.range(offset, offset + per_page - 1)

    result = query.execute()

    total_count = result.count if result.count else 0
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0

    # Transform data
    changes_data = []
    for row in result.data:
        change = {
            "id": row["id"],
            "commitment_name": row["commitment_name"],
            "commitment_type": row["commitment_type"],
            "previous_status": row.get("previous_status"),
            "current_status": row["current_status"],
            "status_changed_at": row.get("status_changed_at"),
            "change_direction": "removed" if row["current_status"] == "discontinued" else "restored"
        }

        # Add company info
        if 'profiles' in row and row['profiles']:
            profile = row['profiles'] if isinstance(row['profiles'], dict) else row['profiles'][0]
            if 'companies' in profile and profile['companies']:
                company = profile['companies'] if isinstance(profile['companies'], dict) else profile['companies'][0]
                change['company'] = {
                    "id": company.get("id"),
                    "name": company.get("name"),
                    "ticker": company.get("ticker")
                }

        changes_data.append(change)

    return {
        "data": changes_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    }


@router.get("/{commitment_id}", response_model=dict)
async def get_commitment(commitment_id: str):
    """Get detailed information about a specific commitment"""
    supabase = get_supabase_client()

    result = supabase.table('commitments') \
        .select('*, profiles(*, companies(*))') \
        .eq('id', commitment_id) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Commitment not found")

    commitment_data = result.data[0]

    response = {
        "id": commitment_data["id"],
        "profile_id": commitment_data["profile_id"],
        "commitment_name": commitment_data["commitment_name"],
        "commitment_type": commitment_data["commitment_type"],
        "current_status": commitment_data["current_status"],
        "quotes": commitment_data.get("quotes", []),
        "provenance_ids": commitment_data.get("provenance_ids", []),
        "status_changed_at": commitment_data.get("status_changed_at"),
        "previous_status": commitment_data.get("previous_status")
    }

    # Add company info
    if 'profiles' in commitment_data and commitment_data['profiles']:
        profile = commitment_data['profiles'] if isinstance(commitment_data['profiles'], dict) else commitment_data['profiles'][0]
        if 'companies' in profile and profile['companies']:
            company = profile['companies'] if isinstance(profile['companies'], dict) else profile['companies'][0]
            response['company'] = {
                "id": company.get("id"),
                "name": company.get("name"),
                "ticker": company.get("ticker"),
                "industry": company.get("industry")
            }

    # Get sources for this commitment
    if response.get("provenance_ids"):
        sources_result = supabase.table('data_sources') \
            .select('source_id, url, reliability_score, title') \
            .in_('source_id', response["provenance_ids"]) \
            .execute()
        response['sources'] = sources_result.data

    return {"data": response}

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_supabase_client
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=dict)
async def get_overview():
    """Get overall platform statistics"""
    supabase = get_supabase_client()

    # Get counts
    companies_result = supabase.table('companies').select('*', count='exact').execute()
    profiles_result = supabase.table('profiles').select('*', count='exact').execute()
    sources_result = supabase.table('data_sources').select('source_type', count='exact').execute()
    commitments_result = supabase.table('commitments').select('current_status', count='exact').execute()

    total_companies = companies_result.count or 0
    total_profiles = profiles_result.count or 0
    total_sources = sources_result.count or 0
    total_commitments = commitments_result.count or 0

    # Source type breakdown
    source_type_breakdown = {}
    for source in sources_result.data:
        source_type = source.get('source_type')
        if source_type:
            source_type_breakdown[source_type] = source_type_breakdown.get(source_type, 0) + 1

    # Commitment status breakdown
    commitment_status_breakdown = {}
    for commitment in commitments_result.data:
        status = commitment.get('current_status')
        if status:
            commitment_status_breakdown[status] = commitment_status_breakdown.get(status, 0) + 1

    # Get industries
    industries_result = supabase.table('companies').select('industry').execute()
    industries_covered = len(set(row['industry'] for row in industries_result.data if row.get('industry')))

    # Get countries
    countries_result = supabase.table('companies').select('hq_country').execute()
    countries_covered = len(set(row['hq_country'] for row in countries_result.data if row.get('hq_country')))

    # Calculate averages
    avg_sources = round(total_sources / total_companies, 1) if total_companies > 0 else 0
    avg_commitments = round(total_commitments / total_companies, 1) if total_companies > 0 else 0

    return {
        "data": {
            "total_companies": total_companies,
            "total_profiles": total_profiles,
            "total_sources": total_sources,
            "total_commitments": total_commitments,
            "avg_sources_per_company": avg_sources,
            "avg_commitments_per_company": avg_commitments,
            "industries_covered": industries_covered,
            "countries_covered": countries_covered,
            "source_type_breakdown": source_type_breakdown,
            "commitment_status_breakdown": commitment_status_breakdown
        }
    }


@router.get("/industries", response_model=dict)
async def get_industries_stats():
    """Get DEI statistics by industry"""
    supabase = get_supabase_client()

    # Get all data
    companies_result = supabase.table('companies').select('id, industry').execute()
    profiles_result = supabase.table('profiles').select('company_id, source_count').execute()
    commitments_result = supabase.table('commitments').select('profile_id, current_status').execute()

    # Build profile lookup
    profile_by_company = {}
    for profile in profiles_result.data:
        profile_by_company[profile['company_id']] = profile

    # Build commitment lookup
    commitments_by_profile = defaultdict(list)
    for commitment in commitments_result.data:
        commitments_by_profile[commitment['profile_id']].append(commitment)

    # Aggregate by industry
    industry_stats = defaultdict(lambda: {
        'company_count': 0,
        'total_sources': 0,
        'total_commitments': 0,
        'active_commitments': 0
    })

    for company in companies_result.data:
        industry = company.get('industry')
        if not industry:
            continue

        company_id = company['id']
        stats = industry_stats[industry]
        stats['company_count'] += 1

        # Add sources
        if company_id in profile_by_company:
            profile = profile_by_company[company_id]
            stats['total_sources'] += profile.get('source_count', 0)

            # Add commitments
            profile_id = profile.get('id')
            if profile_id in commitments_by_profile:
                commitments = commitments_by_profile[profile_id]
                stats['total_commitments'] += len(commitments)
                stats['active_commitments'] += sum(1 for c in commitments if c.get('current_status') == 'active')

    # Format response
    data = []
    for industry, stats in industry_stats.items():
        company_count = stats['company_count']
        data.append({
            'industry': industry,
            'company_count': company_count,
            'avg_sources': round(stats['total_sources'] / company_count, 1) if company_count > 0 else 0,
            'avg_commitments': round(stats['total_commitments'] / company_count, 1) if company_count > 0 else 0,
            'total_commitments': stats['total_commitments'],
            'active_commitments': stats['active_commitments']
        })

    # Sort by company count
    data.sort(key=lambda x: x['company_count'], reverse=True)

    return {"data": data}


@router.get("/compare", response_model=dict)
async def compare_companies(
    company_ids: str = Query(..., description="Comma-separated company IDs (2-5)")
):
    """Compare multiple companies side-by-side"""
    supabase = get_supabase_client()

    # Parse company IDs
    ids = [id.strip() for id in company_ids.split(',')]

    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 company IDs required")
    if len(ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 companies can be compared")

    # Get companies
    companies_result = supabase.table('companies').select('*').in_('id', ids).execute()

    if len(companies_result.data) != len(ids):
        raise HTTPException(status_code=404, detail="One or more companies not found")

    # Get profiles
    profiles_result = supabase.table('profiles').select('*').in_('company_id', ids).execute()
    profile_by_company = {p['company_id']: p for p in profiles_result.data}

    # Get sources and commitments for each profile
    profile_ids = [p['id'] for p in profiles_result.data]

    sources_result = supabase.table('data_sources').select('profile_id, reliability_score').in_('profile_id', profile_ids).execute()
    commitments_result = supabase.table('commitments').select('profile_id, current_status, commitment_type').in_('profile_id', profile_ids).execute()

    # Organize by profile
    sources_by_profile = defaultdict(list)
    commitments_by_profile = defaultdict(list)

    for source in sources_result.data:
        sources_by_profile[source['profile_id']].append(source)

    for commitment in commitments_result.data:
        commitments_by_profile[commitment['profile_id']].append(commitment)

    # Build comparison
    comparison_data = []
    for company in companies_result.data:
        company_id = company['id']
        profile = profile_by_company.get(company_id, {})
        profile_id = profile.get('id')

        sources = sources_by_profile.get(profile_id, [])
        commitments = commitments_by_profile.get(profile_id, [])

        company_data = {
            "id": company['id'],
            "name": company['name'],
            "ticker": company['ticker'],
            "industry": company['industry'],
            "metrics": {
                "source_count": len(sources),
                "commitment_count": len(commitments),
                "active_commitments": sum(1 for c in commitments if c.get('current_status') == 'active'),
                "discontinued_commitments": sum(1 for c in commitments if c.get('current_status') == 'discontinued'),
                "pledge_count": sum(1 for c in commitments if c.get('commitment_type') == 'pledge'),
                "industry_initiatives": sum(1 for c in commitments if c.get('commitment_type') == 'industry_initiative'),
                "avg_source_reliability": round(sum(s.get('reliability_score', 0) for s in sources) / len(sources), 2) if sources else 0,
                "latest_research": profile.get('research_captured_at')
            }
        }
        comparison_data.append(company_data)

    return {"data": {"companies": comparison_data}}


@router.get("/stance-changes", response_model=dict)
async def get_stance_changes(
    days: int = Query(90, description="Look back period in days"),
    change_type: Optional[str] = Query(None, description="Filter: all, increased, decreased")
):
    """Track changes in DEI stances over time"""
    supabase = get_supabase_client()

    # Get all commitments with status changes
    query = supabase.table('commitments') \
        .select('*, profiles(*, companies(*))') \
        .not_.is_('previous_status', 'null')

    result = query.execute()

    changes = []
    for commitment in result.data:
        prev_status = commitment.get('previous_status')
        curr_status = commitment.get('current_status')

        # Determine change direction
        if prev_status == 'active' and curr_status == 'discontinued':
            direction = 'decreased'
        elif prev_status == 'discontinued' and curr_status == 'active':
            direction = 'increased'
        else:
            direction = 'changed'

        # Apply filter
        if change_type and change_type != 'all' and direction != change_type:
            continue

        # Get company info
        company = None
        if 'profiles' in commitment and commitment['profiles']:
            profile = commitment['profiles'] if isinstance(commitment['profiles'], dict) else commitment['profiles'][0]
            if 'companies' in profile and profile['companies']:
                comp = profile['companies'] if isinstance(profile['companies'], dict) else profile['companies'][0]
                company = {
                    "id": comp.get("id"),
                    "name": comp.get("name"),
                    "ticker": comp.get("ticker"),
                    "industry": comp.get("industry")
                }

        changes.append({
            "commitment_name": commitment['commitment_name'],
            "commitment_type": commitment['commitment_type'],
            "previous_status": prev_status,
            "current_status": curr_status,
            "changed_at": commitment.get('status_changed_at'),
            "change_direction": direction,
            "company": company
        })

    # Sort by change date
    changes.sort(key=lambda x: x.get('changed_at') or '', reverse=True)

    # Stats
    total_changes = len(changes)
    increased = sum(1 for c in changes if c['change_direction'] == 'increased')
    decreased = sum(1 for c in changes if c['change_direction'] == 'decreased')

    return {
        "data": {
            "changes": changes,
            "stats": {
                "total_changes": total_changes,
                "increased": increased,
                "decreased": decreased,
                "net_change": increased - decreased
            }
        }
    }


@router.get("/industry-trends", response_model=dict)
async def get_industry_trends():
    """Analyze DEI trends by industry"""
    supabase = get_supabase_client()

    # Get all commitments with company/industry info
    result = supabase.table('commitments') \
        .select('current_status, previous_status, profiles(*, companies(*))') \
        .execute()

    industry_trends = defaultdict(lambda: {
        'total_commitments': 0,
        'active': 0,
        'discontinued': 0,
        'increased': 0,
        'decreased': 0,
        'companies': set()
    })

    for commitment in result.data:
        # Get industry
        industry = None
        if 'profiles' in commitment and commitment['profiles']:
            profile = commitment['profiles'] if isinstance(commitment['profiles'], dict) else commitment['profiles'][0]
            if 'companies' in profile and profile['companies']:
                company = profile['companies'] if isinstance(profile['companies'], dict) else profile['companies'][0]
                industry = company.get('industry')
                industry_trends[industry]['companies'].add(company.get('id'))

        if not industry:
            continue

        trends = industry_trends[industry]
        trends['total_commitments'] += 1

        curr_status = commitment.get('current_status')
        prev_status = commitment.get('previous_status')

        if curr_status == 'active':
            trends['active'] += 1
        elif curr_status == 'discontinued':
            trends['discontinued'] += 1

        # Track changes
        if prev_status:
            if prev_status == 'discontinued' and curr_status == 'active':
                trends['increased'] += 1
            elif prev_status == 'active' and curr_status == 'discontinued':
                trends['decreased'] += 1

    # Format response
    data = []
    for industry, trends in industry_trends.items():
        company_count = len(trends['companies'])
        data.append({
            'industry': industry,
            'company_count': company_count,
            'total_commitments': trends['total_commitments'],
            'active_commitments': trends['active'],
            'discontinued_commitments': trends['discontinued'],
            'recent_increases': trends['increased'],
            'recent_decreases': trends['decreased'],
            'net_trend': trends['increased'] - trends['decreased'],
            'trend_direction': 'positive' if trends['increased'] > trends['decreased'] else 'negative' if trends['decreased'] > trends['increased'] else 'stable'
        })

    data.sort(key=lambda x: x['company_count'], reverse=True)

    return {"data": data}

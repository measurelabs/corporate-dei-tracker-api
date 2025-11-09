"""Analytics and aggregation API endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends, Security
from typing import List, Optional
from datetime import datetime
from supabase import Client
from app.database import get_db
from app.schemas import (
    OverviewStats,
    IndustryStats,
    CompanyMetrics,
    CompanyComparison,
    ComparisonResponse
)
from app.schemas.api_key import APIKeyValidation
from app.middleware.auth import verify_api_key
from app.utils.cache import cached, build_query_cache_key

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=dict)
@cached("analytics:overview", ttl=600, key_builder=lambda db, key_validation: "analytics:overview")  # Cache for 10 minutes
async def get_overview_stats(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get overall platform statistics.

    Returns comprehensive statistics including totals, averages,
    and breakdowns by source type, commitment status, and risk level.

    Results are cached for 10 minutes.
    """
    # Get basic counts
    companies_result = db.table('companies').select('id', count='exact').execute()
    profiles_result = db.table('profiles').select('id', count='exact').execute()
    sources_result = db.table('data_sources').select('id, source_type', count='exact').execute()
    commitments_result = db.table('commitments').select('id, current_status', count='exact').execute()
    controversies_result = db.table('controversies').select('id', count='exact').execute()
    events_result = db.table('events').select('id', count='exact').execute()

    total_companies = companies_result.count if hasattr(companies_result, 'count') else len(companies_result.data)
    total_profiles = profiles_result.count if hasattr(profiles_result, 'count') else len(profiles_result.data)
    total_sources = sources_result.count if hasattr(sources_result, 'count') else len(sources_result.data)
    total_commitments = commitments_result.count if hasattr(commitments_result, 'count') else len(commitments_result.data)
    total_controversies = controversies_result.count if hasattr(controversies_result, 'count') else len(controversies_result.data)
    total_events = events_result.count if hasattr(events_result, 'count') else len(events_result.data)

    # Calculate averages
    avg_sources_per_company = round(total_sources / total_companies, 1) if total_companies > 0 else 0
    avg_commitments_per_company = round(total_commitments / total_companies, 1) if total_companies > 0 else 0

    # Get unique industries and countries
    companies_data = db.table('companies').select('industry, hq_country').execute()
    industries = set(c['industry'] for c in companies_data.data if c.get('industry'))
    countries = set(c['hq_country'] for c in companies_data.data if c.get('hq_country'))

    # Source type breakdown
    source_type_breakdown = {}
    for source in sources_result.data:
        stype = source.get('source_type', 'unknown')
        source_type_breakdown[stype] = source_type_breakdown.get(stype, 0) + 1

    # Commitment status breakdown
    commitment_status_breakdown = {}
    for commitment in commitments_result.data:
        status = commitment.get('current_status', 'unknown')
        commitment_status_breakdown[status] = commitment_status_breakdown.get(status, 0) + 1

    # Risk level breakdown
    risk_result = db.table('risk_assessments').select('risk_level').execute()
    risk_level_breakdown = {}
    for risk in risk_result.data:
        level = risk.get('risk_level', 'unknown')
        risk_level_breakdown[level] = risk_level_breakdown.get(level, 0) + 1

    # AI Recommendation (Grade) breakdown - from latest profiles only
    recommendation_result = db.table('profiles_full') \
        .select('recommendation') \
        .eq('is_latest', True) \
        .execute()
    recommendation_breakdown = {}
    for rec in recommendation_result.data:
        recommendation = rec.get('recommendation', 'unknown')
        if recommendation:
            recommendation_breakdown[recommendation] = recommendation_breakdown.get(recommendation, 0) + 1

    # DEI Status breakdown - from latest profiles only
    dei_status_result = db.table('profiles_full') \
        .select('dei_status') \
        .eq('is_latest', True) \
        .execute()
    dei_status_breakdown = {}
    for status in dei_status_result.data:
        dei_stat = status.get('dei_status', 'unknown')
        if dei_stat:
            dei_status_breakdown[dei_stat] = dei_status_breakdown.get(dei_stat, 0) + 1

    # Transparency Rating distribution - from latest profiles only
    transparency_result = db.table('profiles_full') \
        .select('transparency_rating') \
        .eq('is_latest', True) \
        .execute()
    transparency_distribution = {}
    for transp in transparency_result.data:
        rating = transp.get('transparency_rating')
        if rating is not None:
            # Group into ranges: 1-3 (Low), 4-6 (Medium), 7-10 (High)
            if rating <= 3:
                range_key = 'low'
            elif rating <= 6:
                range_key = 'medium'
            else:
                range_key = 'high'
            transparency_distribution[range_key] = transparency_distribution.get(range_key, 0) + 1

    # Get latest research date
    latest_profile = db.table('profiles') \
        .select('research_captured_at') \
        .order('research_captured_at', desc=True) \
        .limit(1) \
        .execute()

    latest_research_date = None
    if latest_profile.data and latest_profile.data[0].get('research_captured_at'):
        latest_research_date = latest_profile.data[0]['research_captured_at']

    return {
        "data": {
            "total_companies": total_companies,
            "total_profiles": total_profiles,
            "total_sources": total_sources,
            "total_commitments": total_commitments,
            "total_controversies": total_controversies,
            "total_events": total_events,
            "avg_sources_per_company": avg_sources_per_company,
            "avg_commitments_per_company": avg_commitments_per_company,
            "industries_covered": len(industries),
            "countries_covered": len(countries),
            "latest_research_date": latest_research_date,
            "source_type_breakdown": source_type_breakdown,
            "commitment_status_breakdown": commitment_status_breakdown,
            "risk_level_breakdown": risk_level_breakdown,
            "recommendation_breakdown": recommendation_breakdown,
            "dei_status_breakdown": dei_status_breakdown,
            "transparency_distribution": transparency_distribution
        }
    }


@router.get("/industries", response_model=dict)
@cached("analytics:industries", ttl=600, key_builder=lambda db, key_validation: "analytics:industries")  # Cache for 10 minutes
async def get_industry_stats(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get DEI statistics by industry.

    Returns metrics for each industry including company count,
    average sources, commitments, controversies, and CDO presence.

    Results are cached for 10 minutes.
    """
    # Get all companies
    companies = db.table('companies') \
        .select('id, industry') \
        .execute()

    # Get latest profile data for each company from profiles_full
    profiles_full = db.table('profiles_full') \
        .select('company_id, profile_id, source_count, cdo_exists') \
        .eq('is_latest', True) \
        .execute()

    # Get all commitments
    commitments = db.table('commitments') \
        .select('profile_id, current_status') \
        .execute()

    # Get all controversies
    controversies = db.table('controversies') \
        .select('profile_id') \
        .execute()

    # Build lookup dictionaries
    profile_full_by_company = {p['company_id']: p for p in profiles_full.data}

    # Count commitments by profile_id
    commitments_by_profile = {}
    active_commitments_by_profile = {}
    for c in commitments.data:
        profile_id = c['profile_id']
        commitments_by_profile[profile_id] = commitments_by_profile.get(profile_id, 0) + 1
        if c.get('current_status') == 'active':
            active_commitments_by_profile[profile_id] = active_commitments_by_profile.get(profile_id, 0) + 1

    # Count controversies by profile_id
    controversies_by_profile = {}
    for c in controversies.data:
        profile_id = c['profile_id']
        controversies_by_profile[profile_id] = controversies_by_profile.get(profile_id, 0) + 1

    # Group by industry
    industry_data = {}
    for company in companies.data:
        industry = company.get('industry', 'Unknown')
        if industry not in industry_data:
            industry_data[industry] = {
                'industry': industry,
                'company_count': 0,
                'total_sources': 0,
                'total_commitments': 0,
                'active_commitments': 0,
                'total_controversies': 0,
                'companies_with_cdo': 0
            }

        industry_data[industry]['company_count'] += 1

        company_id = company['id']

        # Get profile_full data
        profile_full = profile_full_by_company.get(company_id)
        if profile_full:
            profile_id = profile_full.get('profile_id')

            industry_data[industry]['total_sources'] += profile_full.get('source_count', 0)

            # Count commitments for this profile
            total_commits = commitments_by_profile.get(profile_id, 0)
            active_commits = active_commitments_by_profile.get(profile_id, 0)
            industry_data[industry]['total_commitments'] += total_commits
            industry_data[industry]['active_commitments'] += active_commits

            # Count controversies for this profile
            total_controv = controversies_by_profile.get(profile_id, 0)
            industry_data[industry]['total_controversies'] += total_controv

            if profile_full.get('cdo_exists'):
                industry_data[industry]['companies_with_cdo'] += 1

    # Calculate averages and format results
    results = []
    for industry, data in industry_data.items():
        count = data['company_count']
        results.append({
            'industry': industry,
            'company_count': count,
            'avg_sources': round(data['total_sources'] / count, 1) if count > 0 else 0,
            'avg_commitments': round(data['total_commitments'] / count, 1) if count > 0 else 0,
            'total_commitments': data['total_commitments'],
            'active_commitments': data['active_commitments'],
            'total_controversies': data['total_controversies'],
            'companies_with_cdo': data['companies_with_cdo']
        })

    # Sort by company count descending
    results.sort(key=lambda x: x['company_count'], reverse=True)

    return {"data": results}


@router.get("/compare", response_model=dict)
@cached(
    "analytics:compare",
    ttl=300,  # Cache for 5 minutes
    key_builder=lambda company_ids, db, key_validation: f"analytics:compare:{'_'.join(sorted(company_ids))}"
)
async def compare_companies(
    company_ids: List[str] = Query(..., description="List of company IDs to compare (2-5 companies)"),
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Compare multiple companies side-by-side.

    Accepts 2-5 company IDs and returns detailed metrics for comparison.

    Results are cached for 5 minutes.
    """
    if len(company_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 companies required for comparison"
        )
    if len(company_ids) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 companies allowed for comparison"
        )

    comparisons = []

    for company_id in company_ids:
        # Get company with full data
        company_result = db.table('companies') \
            .select('''
                id,
                name,
                ticker,
                industry,
                profiles!inner(
                    id,
                    source_count,
                    research_captured_at,
                    data_sources(reliability_score),
                    commitments(id, commitment_type, current_status),
                    controversies(id),
                    events(id),
                    cdo_roles(exists),
                    risk_assessments(overall_risk_score, risk_level),
                    ai_contexts(commitment_strength_rating, transparency_rating, recommendation)
                )
            ''') \
            .eq('id', company_id) \
            .limit(1) \
            .execute()

        if not company_result.data:
            continue

        company = company_result.data[0]
        profiles = company.get('profiles', [])

        if not profiles:
            continue

        profile = profiles[0] if isinstance(profiles, list) else profiles

        # Calculate metrics
        sources = profile.get('data_sources', [])
        avg_reliability = None
        if sources:
            reliabilities = [s.get('reliability_score', 0) for s in sources if s.get('reliability_score')]
            if reliabilities:
                avg_reliability = round(sum(reliabilities) / len(reliabilities), 2)

        commitments = profile.get('commitments', [])
        commitment_count = len(commitments) if isinstance(commitments, list) else 0
        active_commitments = sum(1 for c in commitments if c.get('current_status') == 'active') if isinstance(commitments, list) else 0

        pledge_count = sum(1 for c in commitments if c.get('commitment_type') == 'pledge') if isinstance(commitments, list) else 0
        industry_initiatives = sum(1 for c in commitments if c.get('commitment_type') == 'industry_initiative') if isinstance(commitments, list) else 0

        controversies = profile.get('controversies', [])
        controversy_count = len(controversies) if isinstance(controversies, list) else 0

        events = profile.get('events', [])
        event_count = len(events) if isinstance(events, list) else 0

        cdo_roles = profile.get('cdo_roles', [])
        has_cdo = False
        if cdo_roles:
            cdo = cdo_roles[0] if isinstance(cdo_roles, list) else cdo_roles
            has_cdo = cdo.get('exists', False)

        risk_assessments = profile.get('risk_assessments', [])
        risk_score = None
        risk_level = None
        if risk_assessments:
            risk = risk_assessments[0] if isinstance(risk_assessments, list) else risk_assessments
            risk_score = risk.get('overall_risk_score')
            risk_level = risk.get('risk_level')

        ai_contexts = profile.get('ai_contexts', [])
        transparency_rating = None
        commitment_strength_rating = None
        recommendation = None
        if ai_contexts:
            ai_context = ai_contexts[0] if isinstance(ai_contexts, list) else ai_contexts
            transparency_rating = ai_context.get('transparency_rating')
            commitment_strength_rating = ai_context.get('commitment_strength_rating')
            recommendation = ai_context.get('recommendation')

        metrics = {
            "source_count": profile.get('source_count', 0),
            "commitment_count": commitment_count,
            "active_commitments": active_commitments,
            "controversy_count": controversy_count,
            "event_count": event_count,
            "pledge_count": pledge_count,
            "industry_initiatives": industry_initiatives,
            "avg_source_reliability": avg_reliability,
            "latest_research": profile.get('research_captured_at'),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "has_cdo": has_cdo,
            "transparency_rating": transparency_rating,
            "commitment_strength_rating": commitment_strength_rating,
            "recommendation": recommendation
        }

        comparisons.append({
            "id": company['id'],
            "name": company['name'],
            "ticker": company['ticker'],
            "industry": company.get('industry'),
            "metrics": metrics
        })

    return {
        "data": {
            "companies": comparisons,
            "comparison_date": datetime.utcnow().isoformat()
        }
    }


@router.get("/risks", response_model=dict)
@cached("analytics:risks", ttl=600, key_builder=lambda db, key_validation: "analytics:risks")  # Cache for 10 minutes
async def get_risk_distribution(
    db: Client = Depends(get_db),
    key_validation: APIKeyValidation = Security(verify_api_key)
):
    """
    Get risk level distribution across all companies.

    Returns statistics for each risk level including counts and averages.

    Results are cached for 10 minutes.
    """
    # Get all risk assessments
    risk_result = db.table('risk_assessments') \
        .select('''
            risk_level,
            overall_risk_score,
            ongoing_lawsuits,
            settled_cases,
            negative_events
        ''') \
        .execute()

    # Group by risk level
    risk_data = {}
    total_companies = len(risk_result.data)

    for risk in risk_result.data:
        level = risk.get('risk_level', 'unknown')
        if level not in risk_data:
            risk_data[level] = {
                'risk_level': level,
                'count': 0,
                'total_lawsuits': 0,
                'total_controversies': 0
            }

        risk_data[level]['count'] += 1
        risk_data[level]['total_lawsuits'] += risk.get('ongoing_lawsuits', 0) + risk.get('settled_cases', 0)

    # Calculate percentages and averages
    results = []
    for level, data in risk_data.items():
        count = data['count']
        results.append({
            'risk_level': level,
            'count': count,
            'percentage': round((count / total_companies * 100), 1) if total_companies > 0 else 0,
            'avg_lawsuits': round(data['total_lawsuits'] / count, 1) if count > 0 else 0,
            'avg_controversies': round(data['total_controversies'] / count, 1) if count > 0 else 0
        })

    # Sort by count descending
    results.sort(key=lambda x: x['count'], reverse=True)

    return {"data": results}

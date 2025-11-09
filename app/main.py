"""
DEI Tracker API - Main Application

Comprehensive API for tracking corporate DEI (Diversity, Equity, and Inclusion)
stances, commitments, and actions over time.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import (
    companies,
    profiles,
    commitments,
    controversies,
    sources,
    analytics,
    api_keys,
    events,
    supplier_diversity
)
from app.redis_client import redis_client, clear_cache_pattern

settings = get_settings()

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description=settings.app_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
if settings.enable_cors:
    cors_origins = settings.parsed_cors_origins
    print(f"🔧 CORS Configuration:")
    print(f"   - Raw value: {settings.cors_origins}")
    print(f"   - Parsed origins: {cors_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers with version prefix
api_prefix = f"/{settings.api_version}"

app.include_router(companies.router, prefix=api_prefix)
app.include_router(profiles.router, prefix=api_prefix)
app.include_router(commitments.router, prefix=api_prefix)
app.include_router(controversies.router, prefix=api_prefix)
app.include_router(sources.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)
app.include_router(events.router, prefix=api_prefix)
app.include_router(supplier_diversity.router, prefix=api_prefix)
app.include_router(api_keys.router, prefix=api_prefix)


@app.get("/")
async def root():
    """
    Root endpoint with API information and available endpoints.
    """
    return {
        "message": "DEI Tracker API",
        "version": settings.api_version,
        "description": "Track corporate DEI stances, commitments, and changes",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "companies": f"{api_prefix}/companies",
            "profiles": f"{api_prefix}/profiles",
            "commitments": f"{api_prefix}/commitments",
            "controversies": f"{api_prefix}/controversies",
            "events": f"{api_prefix}/events",
            "supplier_diversity": f"{api_prefix}/supplier-diversity",
            "sources": f"{api_prefix}/sources",
            "analytics": f"{api_prefix}/analytics",
            "api_keys": f"{api_prefix}/api-keys"
        },
        "key_features": [
            "Browse companies with DEI profiles",
            "Access detailed DEI research and AI insights",
            "Track commitments and monitor changes",
            "Review controversies and lawsuits",
            "Analyze trends and compare companies",
            "Evaluate DEI-related risks"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "version": settings.api_version,
        "service": "DEI Tracker API"
    }


@app.get(f"{api_prefix}/")
async def api_root():
    """
    API version root endpoint.
    """
    return {
        "version": settings.api_version,
        "endpoints": {
            "companies": {
                "list": f"{api_prefix}/companies",
                "get_by_id": f"{api_prefix}/companies/{{id}}",
                "get_by_ticker": f"{api_prefix}/companies/ticker/{{ticker}}",
                "search": f"{api_prefix}/companies/search/advanced"
            },
            "profiles": {
                "list": f"{api_prefix}/profiles",
                "get_by_id": f"{api_prefix}/profiles/{{id}}",
                "get_full": f"{api_prefix}/profiles/{{id}}/full",
                "get_latest_for_company": f"{api_prefix}/profiles/company/{{company_id}}/latest"
            },
            "commitments": {
                "list": f"{api_prefix}/commitments",
                "get_by_id": f"{api_prefix}/commitments/{{id}}",
                "stats": f"{api_prefix}/commitments/types/stats"
            },
            "controversies": {
                "list": f"{api_prefix}/controversies",
                "get_by_id": f"{api_prefix}/controversies/{{id}}"
            },
            "events": {
                "list": f"{api_prefix}/events",
                "get_by_id": f"{api_prefix}/events/{{id}}",
                "stats": f"{api_prefix}/events/types/stats"
            },
            "supplier_diversity": {
                "list": f"{api_prefix}/supplier-diversity",
                "get_by_profile": f"{api_prefix}/supplier-diversity/{{profile_id}}",
                "stats": f"{api_prefix}/supplier-diversity/stats/overview"
            },
            "sources": {
                "list": f"{api_prefix}/sources",
                "get_by_id": f"{api_prefix}/sources/{{id}}",
                "stats": f"{api_prefix}/sources/types/stats",
                "fetch_titles": f"{api_prefix}/sources/fetch-titles",
                "update_title": f"{api_prefix}/sources/{{id}}/title"
            },
            "analytics": {
                "overview": f"{api_prefix}/analytics/overview",
                "by_industry": f"{api_prefix}/analytics/industries",
                "compare": f"{api_prefix}/analytics/compare",
                "risks": f"{api_prefix}/analytics/risks"
            },
            "api_keys": {
                "create": f"{api_prefix}/api-keys",
                "list": f"{api_prefix}/api-keys",
                "verify": f"{api_prefix}/api-keys/verify/current"
            }
        }
    }


@app.post("/cache/clear")
async def clear_cache(pattern: str = "*"):
    """
    Clear cache entries matching a pattern.

    Args:
        pattern: Redis key pattern (default: "*" clears all)
                 Examples: "analytics:*", "profile:full:*"

    Returns:
        Status message
    """
    try:
        success = await clear_cache_pattern(pattern)
        if success:
            return {
                "status": "success",
                "message": f"Cache cleared for pattern: {pattern}"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to clear cache"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clearing cache: {str(e)}"
        }


@app.get("/cache/stats")
async def cache_stats():
    """
    Get Redis cache statistics.

    Returns basic information about the cache state.
    """
    try:
        # Get all keys
        all_keys = redis_client.keys("*")
        key_count = len(all_keys) if all_keys else 0

        # Group by prefix
        prefixes = {}
        if all_keys:
            for key in all_keys:
                prefix = key.split(":")[0] if ":" in key else "other"
                prefixes[prefix] = prefixes.get(prefix, 0) + 1

        return {
            "status": "connected",
            "total_keys": key_count,
            "keys_by_prefix": prefixes
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting cache stats: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

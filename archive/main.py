from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routers import companies, profiles, sources, commitments, analytics

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="""
    API for tracking corporate DEI stances, commitments, and changes.

    ## Features

    * **Companies** - Browse and search companies with DEI profiles
    * **Profiles** - Access detailed DEI research profiles
    * **Sources** - Explore documented sources with reliability scores
    * **Commitments** - Track DEI pledges and initiatives
    * **Analytics** - Analyze trends and compare companies

    ## Use Cases

    * Track which companies are backing DEI vs. quietly rolling back
    * Monitor commitment status changes (active → discontinued)
    * Compare DEI stances across industries
    * Research with cited, reliability-scored sources
    """
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router, prefix=f"/{settings.api_version}")
app.include_router(profiles.router, prefix=f"/{settings.api_version}")
app.include_router(sources.router, prefix=f"/{settings.api_version}")
app.include_router(commitments.router, prefix=f"/{settings.api_version}")
app.include_router(analytics.router, prefix=f"/{settings.api_version}")


@app.get("/")
async def root():
    return {
        "message": "DEI Tracker API",
        "version": settings.api_version,
        "description": "Track corporate DEI stances and commitment changes",
        "docs": "/docs",
        "endpoints": {
            "companies": f"/{settings.api_version}/companies",
            "profiles": f"/{settings.api_version}/profiles",
            "sources": f"/{settings.api_version}/sources",
            "commitments": f"/{settings.api_version}/commitments",
            "analytics": f"/{settings.api_version}/analytics"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.api_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

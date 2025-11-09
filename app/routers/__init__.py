"""API routers for all endpoints."""
from app.routers import companies
from app.routers import profiles
from app.routers import commitments
from app.routers import controversies
from app.routers import sources
from app.routers import analytics
from app.routers import events
from app.routers import supplier_diversity

__all__ = [
    "companies",
    "profiles",
    "commitments",
    "controversies",
    "sources",
    "analytics",
    "events",
    "supplier_diversity",
]

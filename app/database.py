"""Database connection and utilities."""
from supabase import create_client, Client
from functools import lru_cache
from app.config import get_settings

settings = get_settings()


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.

    Returns:
        Client: Supabase client configured with service role key
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )


def get_db() -> Client:
    """
    Dependency for FastAPI routes to get database client.

    Yields:
        Client: Supabase client instance
    """
    return get_supabase_client()

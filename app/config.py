"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
import json
from typing import Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str

    # Redis Configuration
    upstash_redis_rest_url: str
    upstash_redis_rest_token: str
    redis_cache_ttl: int = 300  # 5 minutes default cache TTL

    api_version: str = "v1"
    app_name: str = "DEI Tracker API"
    app_description: str = """
    Comprehensive API for tracking corporate DEI (Diversity, Equity, and Inclusion)
    stances, commitments, and changes over time.

    ## Key Features

    * **Companies** - Browse and search companies with DEI profiles
    * **Profiles** - Access detailed DEI research profiles with AI insights
    * **Commitments** - Track DEI pledges and initiatives
    * **Controversies** - Monitor lawsuits and controversies
    * **CDO Roles** - Track Chief Diversity Officer appointments
    * **Analytics** - Analyze trends and compare companies
    * **Risk Assessment** - Evaluate DEI-related risks

    ## Use Cases

    * Track which companies are backing DEI vs. quietly rolling back
    * Monitor commitment status changes (active → discontinued)
    * Compare DEI stances across industries
    * Research with cited, reliability-scored sources
    * Investor due diligence and risk assessment
    """

    # API Configuration
    enable_cors: bool = True
    cors_origins: Union[str, list] = '["*"]'

    @property
    def parsed_cors_origins(self) -> list:
        """Parse CORS origins from string or list."""
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        if isinstance(self.cors_origins, str):
            try:
                return json.loads(self.cors_origins)
            except json.JSONDecodeError:
                return [self.cors_origins]
        return ["*"]

    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100

    # API Authentication
    require_api_key: bool = False  # Set to True to require API key for all endpoints
    initial_admin_key: str = ""  # Initial admin key for bootstrapping (set in .env)

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

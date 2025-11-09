-- Migration: Add performance indexes for companies and profiles tables
-- Description: Adds indexes on frequently filtered/searched columns to improve query performance
-- Created: 2025-11-09
-- Note: Using regular CREATE INDEX (not CONCURRENTLY) to allow running in transaction

-- Enable pg_trgm extension for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Add index on companies.industry for filtering
CREATE INDEX IF NOT EXISTS idx_companies_industry
ON companies(industry);

-- Add index on companies.hq_country for filtering
CREATE INDEX IF NOT EXISTS idx_companies_hq_country
ON companies(hq_country);

-- Add index on companies.hq_state for filtering
CREATE INDEX IF NOT EXISTS idx_companies_hq_state
ON companies(hq_state);

-- Add index on companies.name for text search (using trigram for ILIKE queries)
CREATE INDEX IF NOT EXISTS idx_companies_name_trgm
ON companies USING gin (name gin_trgm_ops);

-- Add index on companies.ticker for text search
CREATE INDEX IF NOT EXISTS idx_companies_ticker_trgm
ON companies USING gin (ticker gin_trgm_ops);

-- Add composite index on profiles for efficient company_id + is_latest lookups
CREATE INDEX IF NOT EXISTS idx_profiles_company_id_latest
ON profiles(company_id, is_latest)
WHERE is_latest = true;

-- Add comment explaining the indexes
COMMENT ON INDEX idx_companies_industry IS 'Improves performance of industry filter queries';
COMMENT ON INDEX idx_companies_hq_country IS 'Improves performance of country filter queries';
COMMENT ON INDEX idx_companies_hq_state IS 'Improves performance of state filter queries';
COMMENT ON INDEX idx_companies_name_trgm IS 'Improves performance of ILIKE searches on company name';
COMMENT ON INDEX idx_companies_ticker_trgm IS 'Improves performance of ILIKE searches on ticker';
COMMENT ON INDEX idx_profiles_company_id_latest IS 'Improves performance of latest profile lookups by company_id';

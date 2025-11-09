-- API Keys Table
-- Stores API keys for authentication with admin-level key management

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL, -- Store first few chars for identification
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false, -- Admin keys can create other keys
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID, -- References the API key that created this key (NULL for initial admin key)
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}', -- Additional metadata like rate limits, scopes, etc.

    CONSTRAINT valid_expiry CHECK (expires_at IS NULL OR expires_at > created_at)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);
CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);

-- Enable Row Level Security (optional, depending on your Supabase setup)
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Comment on table
COMMENT ON TABLE api_keys IS 'API keys for authentication with hierarchical admin key system';
COMMENT ON COLUMN api_keys.key_hash IS 'SHA-256 hash of the API key';
COMMENT ON COLUMN api_keys.key_prefix IS 'First 8 characters of the key for display purposes';
COMMENT ON COLUMN api_keys.is_admin IS 'Admin keys can create and manage other API keys';
COMMENT ON COLUMN api_keys.metadata IS 'Additional configuration like rate limits, allowed endpoints, etc.';

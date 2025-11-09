# API Key Authentication

This document describes the API key authentication system for the DEI Tracker API.

## Overview

The API uses API key authentication with a hierarchical admin key system:
- **Admin keys** can create and manage other API keys
- **Regular keys** can only access API endpoints
- All keys are stored securely as SHA-256 hashes

## Your Admin API Key

Your initial admin API key has been created:

```
Ec0dzulxsDeBxpsVX9dyMO6QdeN6nLj4Evvm-cCAwBQ
```

**IMPORTANT:** Save this key securely. It will not be shown again.

## Using API Keys

Include the API key in the `X-API-Key` header with all requests:

```bash
curl -H "X-API-Key: Ec0dzulxsDeBxpsVX9dyMO6QdeN6nLj4Evvm-cCAwBQ" \
  https://your-api.com/v1/companies
```

### Python Example

```python
import requests

headers = {
    "X-API-Key": "Ec0dzulxsDeBxpsVX9dyMO6QdeN6nLj4Evvm-cCAwBQ"
}

response = requests.get("https://your-api.com/v1/companies", headers=headers)
print(response.json())
```

### JavaScript/Fetch Example

```javascript
const response = await fetch('https://your-api.com/v1/companies', {
  headers: {
    'X-API-Key': 'Ec0dzulxsDeBxpsVX9dyMO6QdeN6nLj4Evvm-cCAwBQ'
  }
});
const data = await response.json();
```

## API Key Management Endpoints

All key management endpoints require an admin API key.

### Create a New API Key

**POST** `/v1/api-keys`

```bash
curl -X POST https://your-api.com/v1/api-keys \
  -H "X-API-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "is_admin": false,
    "expires_at": "2025-12-31T23:59:59Z",
    "metadata": {
      "environment": "production",
      "rate_limit": 1000
    }
  }'
```

Response:
```json
{
  "id": "uuid",
  "name": "Production API Key",
  "key": "NEW_API_KEY_HERE",
  "key_prefix": "abc12345",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-11-02T23:41:10Z",
  "expires_at": "2025-12-31T23:59:59Z",
  "metadata": {
    "environment": "production",
    "rate_limit": 1000
  }
}
```

**Note:** The `key` field is only shown once when creating a key.

### List All API Keys

**GET** `/v1/api-keys`

```bash
curl https://your-api.com/v1/api-keys \
  -H "X-API-Key: YOUR_ADMIN_KEY"
```

Optional parameters:
- `include_inactive=true` - Include deactivated keys

### Get API Key Details

**GET** `/v1/api-keys/{key_id}`

```bash
curl https://your-api.com/v1/api-keys/c059beaa-0343-4004-826d-16afebb009cb \
  -H "X-API-Key: YOUR_ADMIN_KEY"
```

### Update API Key

**PATCH** `/v1/api-keys/{key_id}`

```bash
curl -X PATCH https://your-api.com/v1/api-keys/c059beaa-0343-4004-826d-16afebb009cb \
  -H "X-API-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "metadata": {
      "rate_limit": 2000
    }
  }'
```

### Deactivate API Key

**POST** `/v1/api-keys/{key_id}/deactivate`

```bash
curl -X POST https://your-api.com/v1/api-keys/c059beaa-0343-4004-826d-16afebb009cb/deactivate \
  -H "X-API-Key: YOUR_ADMIN_KEY"
```

### Activate API Key

**POST** `/v1/api-keys/{key_id}/activate`

```bash
curl -X POST https://your-api.com/v1/api-keys/c059beaa-0343-4004-826d-16afebb009cb/activate \
  -H "X-API-Key: YOUR_ADMIN_KEY"
```

### Delete API Key

**DELETE** `/v1/api-keys/{key_id}`

```bash
curl -X DELETE https://your-api.com/v1/api-keys/c059beaa-0343-4004-826d-16afebb009cb \
  -H "X-API-Key: YOUR_ADMIN_KEY"
```

**Warning:** This permanently deletes the key and cannot be undone.

### Verify Current API Key

**GET** `/v1/api-keys/verify/current`

Test if your API key is valid and get its information:

```bash
curl https://your-api.com/v1/api-keys/verify/current \
  -H "X-API-Key: YOUR_API_KEY"
```

## Protecting Endpoints

To protect specific endpoints with API key authentication, add the `verify_api_key` dependency:

```python
from fastapi import APIRouter, Security
from app.middleware.auth import verify_api_key, APIKeyValidation

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(
    api_key: APIKeyValidation = Security(verify_api_key)
):
    return {
        "message": "This endpoint requires authentication",
        "key_id": str(api_key.id),
        "is_admin": api_key.is_admin
    }
```

For admin-only endpoints:

```python
from app.middleware.auth import require_admin_key

@router.post("/admin-only")
async def admin_endpoint(
    admin_key: APIKeyValidation = Security(require_admin_key)
):
    return {"message": "Admin access granted"}
```

## Configuration

In your `.env` file:

```env
# Set to true to require API keys for ALL endpoints
REQUIRE_API_KEY=false

# Optional: Set an initial admin key for bootstrapping
INITIAL_ADMIN_KEY=your-secure-key-here
```

## Security Best Practices

1. **Never commit API keys to version control**
2. **Rotate keys regularly** - Create new keys and delete old ones
3. **Use different keys for different environments** (dev, staging, production)
4. **Set expiration dates** for keys when possible
5. **Monitor key usage** via the `last_used_at` field
6. **Deactivate compromised keys immediately**
7. **Use metadata** to track key purpose and ownership

## Creating Additional Admin Keys

To create another admin key (requires existing admin key):

```bash
curl -X POST https://your-api.com/v1/api-keys \
  -H "X-API-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Secondary Admin Key",
    "is_admin": true
  }'
```

## Database Schema

The `api_keys` table structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `name` | VARCHAR(255) | Descriptive name |
| `key_hash` | VARCHAR(255) | SHA-256 hash of the key |
| `key_prefix` | VARCHAR(20) | First 8 chars for display |
| `is_active` | BOOLEAN | Whether the key is active |
| `is_admin` | BOOLEAN | Admin privileges |
| `created_at` | TIMESTAMP | When created |
| `created_by` | UUID | Key that created this key |
| `last_used_at` | TIMESTAMP | Last usage timestamp |
| `expires_at` | TIMESTAMP | Expiration date (optional) |
| `metadata` | JSONB | Additional configuration |

## Troubleshooting

### 401 Unauthorized
- Check that the `X-API-Key` header is present
- Verify the key is correct (no extra spaces)
- Check if the key has been deactivated
- Check if the key has expired

### 403 Forbidden
- The operation requires an admin key
- Your key doesn't have sufficient privileges

### Creating a New Admin Key (Bootstrap)

If you need to create a fresh admin key:

```bash
python3 -m app.scripts.create_admin_key --name "New Admin Key"
```

Optional expiration:
```bash
python3 -m app.scripts.create_admin_key \
  --name "Temporary Admin" \
  --expires "2025-12-31T23:59:59Z"
```

## API Documentation

Full interactive API documentation is available at:
- Swagger UI: `https://your-api.com/docs`
- ReDoc: `https://your-api.com/redoc`

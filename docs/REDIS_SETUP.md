# Redis Caching Setup

## Overview

Redis caching has been successfully integrated into the DEI Tracker API using Upstash Redis. This dramatically improves performance for expensive analytics queries.

## Performance Improvement

**Before caching:**
- Analytics overview endpoint: ~1.66 seconds

**After caching:**
- Analytics overview endpoint: ~0.24 seconds (7x faster!)

## What's Been Implemented

### 1. Redis Client (`app/redis_client.py`)
- Upstash Redis connection using REST API
- Helper functions: `get_cache()`, `set_cache()`, `delete_cache()`, `clear_cache_pattern()`
- Automatic JSON serialization/deserialization
- Error handling with graceful fallback

### 2. Caching Decorator (`app/utils/cache.py`)
- `@cached` decorator for easy caching of any function
- Customizable TTL (time-to-live)
- Flexible key building with custom key_builder functions
- Automatic cache key generation from function parameters

### 3. Cached Endpoints

#### Analytics Endpoints (all cached for 10 minutes)
- `GET /v1/analytics/overview` - Platform statistics
- `GET /v1/analytics/industries` - Industry breakdowns
- `GET /v1/analytics/risks` - Risk distribution
- `GET /v1/analytics/compare` - Company comparison (5 min TTL)

#### Profile Endpoints (cached for 15 minutes)
- `GET /v1/profiles/{id}/full` - Full profile with all components
- `GET /v1/profiles/{id}` - Profile by ID (when full=true)

### 4. Cache Management Endpoints

#### Get Cache Statistics
```bash
GET /cache/stats
```

Returns:
```json
{
  "status": "connected",
  "total_keys": 3,
  "keys_by_prefix": {
    "analytics": 2,
    "profile": 1
  }
}
```

#### Clear Cache
```bash
POST /cache/clear?pattern=analytics:*
```

Examples:
- `pattern=*` - Clear all cache
- `pattern=analytics:*` - Clear all analytics cache
- `pattern=profile:full:*` - Clear all full profile cache

## Configuration

### Environment Variables (.env)
```env
UPSTASH_REDIS_REST_URL=https://your-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token
```

### Settings (app/config.py)
```python
redis_cache_ttl: int = 300  # Default 5 minutes
```

## Cache Keys Pattern

The caching system uses structured key patterns:

- **Analytics Overview**: `analytics:overview`
- **Analytics Industries**: `analytics:industries`
- **Analytics Risks**: `analytics:risks`
- **Analytics Compare**: `analytics:compare:{sorted_company_ids}`
- **Full Profile**: `profile:full:{profile_id}`

## Usage Examples

### Adding Cache to a New Endpoint

Simple caching with default TTL:
```python
from app.utils.cache import cached

@router.get("/my-endpoint")
@cached("my:endpoint", ttl=300)
async def my_endpoint():
    # Your expensive operation
    return result
```

Custom key builder:
```python
@router.get("/companies/{company_id}")
@cached(
    "company",
    ttl=600,
    key_builder=lambda company_id, db: f"company:{company_id}"
)
async def get_company(company_id: str, db: Client = Depends(get_db)):
    # Your operation
    return result
```

### Manual Cache Operations

```python
from app.redis_client import get_cache, set_cache, delete_cache

# Set cache
await set_cache("my:key", {"data": "value"}, ttl=300)

# Get cache
value = await get_cache("my:key")

# Delete cache
await delete_cache("my:key")
```

## Testing

### Test Redis Connection
```bash
python test_redis.py
```

### Test Cached Endpoint Performance
```bash
# First request (not cached)
time curl http://localhost:8000/v1/analytics/overview

# Second request (cached - should be much faster)
time curl http://localhost:8000/v1/analytics/overview
```

### Check Cache Stats
```bash
curl http://localhost:8000/cache/stats | python3 -m json.tool
```

### Clear Cache
```bash
curl -X POST "http://localhost:8000/cache/clear?pattern=analytics:*"
```

## Cache TTL Strategy

Current TTL settings:
- **Analytics endpoints**: 600 seconds (10 minutes)
- **Company comparisons**: 300 seconds (5 minutes)
- **Full profiles**: 900 seconds (15 minutes)
- **Default**: 300 seconds (5 minutes)

Adjust these based on:
- How frequently your data updates
- How stale data can be
- Redis memory constraints

## Best Practices

1. **Cache expensive operations**: Focus on endpoints with multiple DB queries
2. **Use appropriate TTL**: Balance freshness vs. performance
3. **Monitor cache hit rates**: Use `/cache/stats` endpoint
4. **Clear cache after updates**: If you add write endpoints, clear relevant cache
5. **Handle cache failures gracefully**: The system falls back to DB if Redis fails

## Future Enhancements

Potential improvements:
- [ ] Cache hit/miss metrics
- [ ] Automatic cache warming
- [ ] Redis Pub/Sub for cache invalidation
- [ ] Background task for cache preloading
- [ ] Cache compression for large responses
- [ ] Rate limiting with Redis
- [ ] Session storage with Redis

## Dependencies

```txt
redis>=5.0.0
upstash-redis>=0.15.0
```

## Troubleshooting

### Redis connection errors
- Verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` in `.env`
- Check Upstash dashboard for instance status
- API will continue to work (slower) if Redis is unavailable

### Cache not updating
- Wait for TTL to expire, or
- Use `/cache/clear` endpoint to force refresh

### High memory usage
- Reduce TTL values
- Use more specific cache patterns
- Clear unused cache regularly

## Monitoring

Check Redis usage in Upstash dashboard:
- Memory usage
- Request count
- Latency metrics
- Storage used

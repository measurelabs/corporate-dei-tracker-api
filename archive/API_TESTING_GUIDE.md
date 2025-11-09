# DEI Tracker API - Testing Guide

## API Status: ✅ LIVE

**Base URL**: `http://localhost:8000`
**API Version**: `v1`
**Interactive Docs**: http://localhost:8000/docs

---

## Quick Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "v1"
}
```

---

## Companies Endpoints

### 1. List All Companies
```bash
curl "http://localhost:8000/v1/companies/?per_page=5&page=1"
```

**Filter by Industry:**
```bash
curl "http://localhost:8000/v1/companies/?industry=Information%20Technology"
```

**Search by Name:**
```bash
curl "http://localhost:8000/v1/companies/?search=Apple"
```

**Sort by Ticker:**
```bash
curl "http://localhost:8000/v1/companies/?sort=ticker&order=asc"
```

### 2. Get Company by ID
```bash
curl "http://localhost:8000/v1/companies/0a4545e1-f3c5-48f6-bf08-e3854524869f"
```

**Include Profile Data:**
```bash
curl "http://localhost:8000/v1/companies/0a4545e1-f3c5-48f6-bf08-e3854524869f?include=profile"
```

### 3. Get Company by Ticker
```bash
curl "http://localhost:8000/v1/companies/ticker/AAPL"
```

---

## Profiles Endpoints

### 1. List All Profiles
```bash
curl "http://localhost:8000/v1/profiles/?per_page=10"
```

**Get Latest Profiles Only:**
```bash
curl "http://localhost:8000/v1/profiles/?is_latest=true"
```

### 2. Get Profile with Full Details
```bash
# Replace {profile_id} with actual ID
curl "http://localhost:8000/v1/profiles/{profile_id}?include=sources,commitments"
```

---

## Sources Endpoints

### 1. List All Sources
```bash
curl "http://localhost:8000/v1/sources/?per_page=10"
```

**Filter by Source Type:**
```bash
curl "http://localhost:8000/v1/sources/?source_type=regulatory_filing"
```

**Filter by Reliability:**
```bash
curl "http://localhost:8000/v1/sources/?min_reliability=4"
```

**Search Sources:**
```bash
curl "http://localhost:8000/v1/sources/?search=diversity"
```

### 2. Get Source Types Statistics
```bash
curl "http://localhost:8000/v1/sources/types"
```
**Response shows source type breakdown with counts and average reliability.**

---

## Commitments Endpoints

### 1. List All Commitments
```bash
curl "http://localhost:8000/v1/commitments/?per_page=10"
```

**Filter by Status:**
```bash
# Active commitments
curl "http://localhost:8000/v1/commitments/?status=active"

# Discontinued commitments
curl "http://localhost:8000/v1/commitments/?status=discontinued"

# Inactive commitments
curl "http://localhost:8000/v1/commitments/?status=inactive"
```

**Filter by Type:**
```bash
curl "http://localhost:8000/v1/commitments/?commitment_type=pledge"
```

**Search Commitments:**
```bash
curl "http://localhost:8000/v1/commitments/?search=equity"
```

**Only Show Changed Commitments:**
```bash
curl "http://localhost:8000/v1/commitments/?changed_only=true"
```

### 2. Get Commitment Changes
```bash
curl "http://localhost:8000/v1/commitments/changes"
```

**Filter by Change Type:**
```bash
# Only discontinued
curl "http://localhost:8000/v1/commitments/changes?change_type=discontinued"

# Only reactivated
curl "http://localhost:8000/v1/commitments/changes?change_type=reactivated"
```

### 3. Get Commitment Types Statistics
```bash
curl "http://localhost:8000/v1/commitments/types"
```

---

## Analytics Endpoints

### 1. Platform Overview
```bash
curl "http://localhost:8000/v1/analytics/overview"
```
**Returns:**
- Total companies, profiles, sources, commitments
- Average sources/commitments per company
- Industries and countries covered
- Source type breakdown
- Commitment status breakdown

### 2. Industry Statistics
```bash
curl "http://localhost:8000/v1/analytics/industries"
```
**Returns DEI metrics by industry:**
- Company count
- Average sources/commitments
- Total and active commitments

### 3. Compare Companies
```bash
curl "http://localhost:8000/v1/analytics/compare?company_ids=0a4545e1-f3c5-48f6-bf08-e3854524869f,e3770756-f606-4436-8355-beb5774590e9"
```
**Compares 2-5 companies side-by-side.**

### 4. Stance Changes Over Time
```bash
curl "http://localhost:8000/v1/analytics/stance-changes"
```

**Filter by change type:**
```bash
curl "http://localhost:8000/v1/analytics/stance-changes?change_type=decreased"
```

### 5. Industry Trends
```bash
curl "http://localhost:8000/v1/analytics/industry-trends"
```
**Shows:**
- Total/active/discontinued commitments by industry
- Recent increases/decreases
- Net trend direction (positive/negative/stable)

---

## Real-World Use Case Examples

### Use Case 1: Find Companies Backing Away from DEI
```bash
# Get all discontinued commitments
curl "http://localhost:8000/v1/commitments/?status=discontinued"

# Get companies with the most discontinued commitments
curl "http://localhost:8000/v1/analytics/stance-changes?change_type=decreased"
```

### Use Case 2: Research a Specific Company
```bash
# 1. Get company by ticker
curl "http://localhost:8000/v1/companies/ticker/AAPL"

# 2. Get their profile with commitments
COMPANY_ID="0a4545e1-f3c5-48f6-bf08-e3854524869f"
curl "http://localhost:8000/v1/companies/$COMPANY_ID?include=profile"

# 3. Get all their sources
curl "http://localhost:8000/v1/sources/?profile_id={profile_id}"

# 4. Get all their commitments
curl "http://localhost:8000/v1/commitments/?profile_id={profile_id}"
```

### Use Case 3: Industry Comparison
```bash
# Compare all tech companies
curl "http://localhost:8000/v1/companies/?industry=Information%20Technology"

# Get industry trends
curl "http://localhost:8000/v1/analytics/industries"

# See which industries are backing away from DEI
curl "http://localhost:8000/v1/analytics/industry-trends"
```

### Use Case 4: Find Most Credible Sources
```bash
# Get highest reliability sources (5/5)
curl "http://localhost:8000/v1/sources/?min_reliability=5&per_page=20"

# Get regulatory filings (most reliable)
curl "http://localhost:8000/v1/sources/?source_type=regulatory_filing"
```

### Use Case 5: Track Commitment Changes
```bash
# Get all commitments with status changes
curl "http://localhost:8000/v1/commitments/?changed_only=true"

# Get stance changes stats
curl "http://localhost:8000/v1/analytics/stance-changes"
```

---

## Response Format

All endpoints return JSON with consistent structure:

### List Endpoints
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "total_count": 47,
    "has_next": true,
    "has_prev": false
  }
}
```

### Single Resource Endpoints
```json
{
  "data": {...}
}
```

---

## Common Query Parameters

**Pagination (all list endpoints):**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Sorting (companies):**
- `sort`: Field to sort by (name, ticker, industry, created_at)
- `order`: Sort order (asc, desc)

**Filtering:**
- `industry`: Filter by industry
- `country`: Filter by country
- `status`: Filter by status (commitments)
- `source_type`: Filter by source type
- `min_reliability`: Minimum reliability score (1-5)
- `search`: Text search

**Including Related Data:**
- `include`: Comma-separated list (profile, sources, commitments, all)

---

## Testing with Python

```python
import requests

# Get all companies
response = requests.get('http://localhost:8000/v1/companies/')
companies = response.json()
print(f"Found {companies['pagination']['total_count']} companies")

# Get Apple's data
apple = requests.get('http://localhost:8000/v1/companies/ticker/AAPL').json()
print(f"Company: {apple['data']['name']}")

# Get active commitments
commitments = requests.get(
    'http://localhost:8000/v1/commitments/',
    params={'status': 'active', 'per_page': 5}
).json()
print(f"Active commitments: {len(commitments['data'])}")

# Get analytics overview
overview = requests.get('http://localhost:8000/v1/analytics/overview').json()
print(f"Total companies: {overview['data']['total_companies']}")
print(f"Total commitments: {overview['data']['total_commitments']}")
```

---

## Current Data Summary

Based on `/v1/analytics/overview`:

- **47 companies** tracked
- **361 sources** documented
- **196 commitments** tracked
- **188 active** commitments
- **7 inactive** commitments
- **33 industries** covered
- **5 countries** represented

### Source Types:
- Corporate websites: 108
- Press releases: 74
- News articles: 73
- Third-party reports: 39
- Regulatory filings: 14
- Trade press: 11
- And more...

### Top Industries:
- Information Technology (5 companies)
- Utilities (5 companies)
- Health Care (3 companies)
- Financials (3 companies)

---

## Interactive API Documentation

Visit **http://localhost:8000/docs** for:
- Full API schema
- Interactive testing interface
- Request/response examples
- Try out endpoints directly in browser

---

## Next Steps

1. **Add more companies** to expand coverage
2. **Track status changes** by updating `status_changed_at` and `previous_status` fields
3. **Build frontend** to visualize the data
4. **Deploy to production** (Railway, Render, Vercel)
5. **Add authentication** for write operations
6. **Set up webhooks** for change notifications

---

**API is ready to use!** Start exploring corporate DEI stances with cited, reliability-scored evidence.

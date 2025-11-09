# DEI Tracker API Architecture

## Overview
This document outlines the API architecture for a comprehensive DEI (Diversity, Equity, and Inclusion) tracking platform that helps users understand companies' DEI stances, commitments, and performance.

---

## Database Schema

### Tables Overview

#### 1. `companies` (47 rows)
Core company information and identification.

**Columns:**
- `id` (UUID, PK): Unique company identifier
- `ticker` (string): Stock ticker symbol
- `name` (string): Company legal name
- `cik` (string): SEC Central Index Key
- `industry` (string): Industry classification
- `hq_city` (string): Headquarters city
- `hq_state` (string): Headquarters state/province
- `hq_country` (string): Headquarters country
- `created_at` (timestamp): Record creation time
- `updated_at` (timestamp): Record last update time

#### 2. `profiles` (47 rows)
DEI profile metadata for each company (1:1 with companies).

**Columns:**
- `id` (UUID, PK): Unique profile identifier
- `company_id` (UUID, FK): References companies.id
- `schema_version` (string): Profile schema version
- `profile_type` (string): Type of profile (e.g., "company_dei_profile")
- `generated_at` (timestamp): When profile was generated
- `research_captured_at` (timestamp): When research was conducted
- `research_notes` (text): Notes about the research process
- `source_count` (int): Number of sources used
- `is_latest` (boolean): Flag for most recent profile version
- `created_at` (timestamp): Record creation time

#### 3. `data_sources` (361 rows)
Source materials documenting DEI information (Many:1 with profiles).

**Columns:**
- `id` (UUID, PK): Unique source identifier
- `profile_id` (UUID, FK): References profiles.id
- `source_id` (string): Human-readable source identifier
- `source_type` (string): Type of source (corporate_website, news_article, regulatory_filing, trade_press)
- `publisher` (string): Publisher/organization
- `author` (string, nullable): Author name
- `url` (string): Source URL
- `date` (date): Publication/update date
- `title` (string): Document/article title
- `reliability_score` (int): 1-5 reliability rating
- `doc_type` (string): Document classification
- `notes` (text): Additional context about the source

#### 4. `commitments` (196 rows)
DEI commitments, pledges, and initiatives (Many:1 with profiles).

**Columns:**
- `id` (UUID, PK): Unique commitment identifier
- `profile_id` (UUID, FK): References profiles.id
- `commitment_name` (string): Name of the commitment/initiative
- `commitment_type` (string): Type (pledge, industry_initiative, etc.)
- `current_status` (string): Current status (active, completed, discontinued)
- `quotes` (array): Supporting quotes from sources
- `provenance_ids` (array): References to source_id values in data_sources

---

## API Endpoints Architecture

### Base URL
```
https://api.deitracker.com/v1
```

### Authentication
All endpoints require API key authentication via header:
```
Authorization: Bearer {API_KEY}
```

---

## Core Endpoints

### 1. Companies

#### `GET /companies`
List all companies with optional filtering and pagination.

**Query Parameters:**
- `page` (int, default: 1): Page number
- `per_page` (int, default: 20, max: 100): Results per page
- `industry` (string): Filter by industry
- `country` (string): Filter by headquarters country
- `state` (string): Filter by headquarters state
- `search` (string): Search by company name or ticker
- `sort` (string): Sort field (name, ticker, industry, created_at)
- `order` (string): Sort order (asc, desc)

**Response:**
```json
{
  "data": [
    {
      "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "cik": "0000320193",
      "industry": "Information Technology",
      "headquarters": {
        "city": "Cupertino",
        "state": "California",
        "country": "United States"
      },
      "created_at": "2025-11-01T22:21:55.332578Z",
      "updated_at": "2025-11-01T22:21:55.332578Z",
      "profile_id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "has_profile": true
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "total_count": 47
  }
}
```

#### `GET /companies/{id}`
Get detailed information for a specific company.

**Path Parameters:**
- `id` (UUID): Company ID

**Query Parameters:**
- `include` (string): Comma-separated list of related data to include (profile, sources, commitments, all)

**Response:**
```json
{
  "data": {
    "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "cik": "0000320193",
    "industry": "Information Technology",
    "headquarters": {
      "city": "Cupertino",
      "state": "California",
      "country": "United States"
    },
    "created_at": "2025-11-01T22:21:55.332578Z",
    "updated_at": "2025-11-01T22:21:55.332578Z",
    "profile": {
      "id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "generated_at": "2025-11-01T20:44:40.852451Z",
      "research_captured_at": "2025-11-01T13:15:00Z",
      "source_count": 13,
      "commitment_count": 4
    }
  }
}
```

#### `GET /companies/search`
Advanced search with multiple criteria.

**Query Parameters:**
- `q` (string): Search query
- `industries[]` (array): Filter by multiple industries
- `countries[]` (array): Filter by multiple countries
- `has_commitments` (boolean): Only companies with active commitments
- `min_sources` (int): Minimum number of sources
- `page` (int): Page number
- `per_page` (int): Results per page

---

### 2. DEI Profiles

#### `GET /profiles`
List all DEI profiles.

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Results per page
- `company_id` (UUID): Filter by company
- `min_sources` (int): Minimum source count
- `from_date` (date): Filter profiles generated after date
- `to_date` (date): Filter profiles generated before date

**Response:**
```json
{
  "data": [
    {
      "id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "company": {
        "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
        "name": "Apple Inc.",
        "ticker": "AAPL"
      },
      "schema_version": "1.0",
      "profile_type": "company_dei_profile",
      "generated_at": "2025-11-01T20:44:40.852451Z",
      "research_captured_at": "2025-11-01T13:15:00Z",
      "source_count": 13,
      "commitment_count": 4,
      "is_latest": true
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "total_count": 47
  }
}
```

#### `GET /profiles/{id}`
Get detailed DEI profile with all related data.

**Path Parameters:**
- `id` (UUID): Profile ID

**Query Parameters:**
- `include` (string): Related data to include (sources, commitments, company, all)

**Response:**
```json
{
  "data": {
    "id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
    "company": {
      "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
      "name": "Apple Inc.",
      "ticker": "AAPL",
      "industry": "Information Technology"
    },
    "schema_version": "1.0",
    "profile_type": "company_dei_profile",
    "generated_at": "2025-11-01T20:44:40.852451Z",
    "research_captured_at": "2025-11-01T13:15:00Z",
    "research_notes": "Comprehensive DEI research for Apple Inc. covering posture, leadership, reporting...",
    "source_count": 13,
    "is_latest": true,
    "created_at": "2025-11-01T22:21:55.332578Z",
    "sources": [...],
    "commitments": [...]
  }
}
```

---

### 3. Data Sources

#### `GET /sources`
List all data sources with filtering.

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Results per page
- `profile_id` (UUID): Filter by profile
- `company_id` (UUID): Filter by company
- `source_type` (string): Filter by type (corporate_website, news_article, regulatory_filing, trade_press)
- `min_reliability` (int): Minimum reliability score (1-5)
- `publisher` (string): Filter by publisher
- `from_date` (date): Sources published after date
- `to_date` (date): Sources published before date
- `search` (string): Search in title and notes

**Response:**
```json
{
  "data": [
    {
      "id": "10375cab-ee19-4f66-be3e-fde154c8e28e",
      "profile_id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "source_id": "apple_diversity_website_2025",
      "source_type": "corporate_website",
      "publisher": "Apple Inc.",
      "author": null,
      "url": "https://www.apple.com/diversity/",
      "date": "2025-04-15",
      "title": "Inclusion & Diversity - Apple",
      "reliability_score": 5,
      "doc_type": "Corporate website",
      "notes": "Official Apple diversity and inclusion page...",
      "company": {
        "name": "Apple Inc.",
        "ticker": "AAPL"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 19,
    "total_count": 361
  }
}
```

#### `GET /sources/{id}`
Get detailed information about a specific source.

**Response:**
```json
{
  "data": {
    "id": "10375cab-ee19-4f66-be3e-fde154c8e28e",
    "profile_id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
    "source_id": "apple_diversity_website_2025",
    "source_type": "corporate_website",
    "publisher": "Apple Inc.",
    "author": null,
    "url": "https://www.apple.com/diversity/",
    "date": "2025-04-15",
    "title": "Inclusion & Diversity - Apple",
    "reliability_score": 5,
    "doc_type": "Corporate website",
    "notes": "Official Apple diversity and inclusion page with programs, initiatives, and commitment statements",
    "profile": {
      "id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "company_id": "0a4545e1-f3c5-48f6-bf08-e3854524869f"
    },
    "company": {
      "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
      "name": "Apple Inc.",
      "ticker": "AAPL"
    }
  }
}
```

#### `GET /sources/types`
Get all available source types with counts.

**Response:**
```json
{
  "data": [
    {
      "source_type": "corporate_website",
      "count": 156,
      "avg_reliability": 4.8
    },
    {
      "source_type": "news_article",
      "count": 120,
      "avg_reliability": 4.2
    },
    {
      "source_type": "regulatory_filing",
      "count": 48,
      "avg_reliability": 5.0
    },
    {
      "source_type": "trade_press",
      "count": 37,
      "avg_reliability": 3.5
    }
  ]
}
```

---

### 4. Commitments

#### `GET /commitments`
List all DEI commitments and initiatives.

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Results per page
- `profile_id` (UUID): Filter by profile
- `company_id` (UUID): Filter by company
- `commitment_type` (string): Filter by type (pledge, industry_initiative)
- `status` (string): Filter by status (active, completed, discontinued)
- `search` (string): Search in commitment name and quotes

**Response:**
```json
{
  "data": [
    {
      "id": "68fe422b-469e-4d15-933e-1d3224343248",
      "profile_id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "commitment_name": "Racial Equity and Justice Initiative (REJI)",
      "commitment_type": "pledge",
      "current_status": "active",
      "quote_count": 1,
      "source_count": 1,
      "company": {
        "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
        "name": "Apple Inc.",
        "ticker": "AAPL"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 10,
    "total_count": 196
  }
}
```

#### `GET /commitments/{id}`
Get detailed information about a specific commitment.

**Response:**
```json
{
  "data": {
    "id": "68fe422b-469e-4d15-933e-1d3224343248",
    "profile_id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
    "commitment_name": "Racial Equity and Justice Initiative (REJI)",
    "commitment_type": "pledge",
    "current_status": "active",
    "quotes": [
      "Apple's REJI has surpassed $200 million in investments focusing on education, economic empowerment..."
    ],
    "provenance_ids": ["apple_reji_website_2025"],
    "sources": [
      {
        "source_id": "apple_reji_website_2025",
        "url": "https://www.apple.com/reji/",
        "reliability_score": 5
      }
    ],
    "company": {
      "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
      "name": "Apple Inc.",
      "ticker": "AAPL",
      "industry": "Information Technology"
    }
  }
}
```

#### `GET /commitments/types`
Get all commitment types with statistics.

**Response:**
```json
{
  "data": [
    {
      "commitment_type": "pledge",
      "count": 98,
      "active_count": 92,
      "companies_count": 35
    },
    {
      "commitment_type": "industry_initiative",
      "count": 98,
      "active_count": 95,
      "companies_count": 42
    }
  ]
}
```

---

### 5. Analytics & Aggregations

#### `GET /analytics/overview`
Get overall platform statistics.

**Response:**
```json
{
  "data": {
    "total_companies": 47,
    "total_profiles": 47,
    "total_sources": 361,
    "total_commitments": 196,
    "avg_sources_per_company": 7.7,
    "avg_commitments_per_company": 4.2,
    "industries_covered": 15,
    "countries_covered": 8,
    "latest_research_date": "2025-11-01T13:15:00Z",
    "source_type_breakdown": {
      "corporate_website": 156,
      "news_article": 120,
      "regulatory_filing": 48,
      "trade_press": 37
    },
    "commitment_status_breakdown": {
      "active": 187,
      "completed": 6,
      "discontinued": 3
    }
  }
}
```

#### `GET /analytics/industries`
Get DEI statistics by industry.

**Response:**
```json
{
  "data": [
    {
      "industry": "Information Technology",
      "company_count": 12,
      "avg_sources": 9.2,
      "avg_commitments": 5.1,
      "total_commitments": 61,
      "active_commitments": 58
    },
    {
      "industry": "Health Care",
      "company_count": 8,
      "avg_sources": 7.5,
      "avg_commitments": 4.2,
      "total_commitments": 34,
      "active_commitments": 32
    }
  ]
}
```

#### `GET /analytics/trends`
Get trends over time.

**Query Parameters:**
- `metric` (string): Metric to track (profiles_created, sources_added, commitments_added)
- `interval` (string): Time interval (day, week, month, quarter, year)
- `from_date` (date): Start date
- `to_date` (date): End date

**Response:**
```json
{
  "data": {
    "metric": "profiles_created",
    "interval": "day",
    "period": {
      "from": "2025-10-01",
      "to": "2025-11-01"
    },
    "data_points": [
      {
        "date": "2025-11-01",
        "count": 47
      }
    ]
  }
}
```

#### `GET /analytics/compare`
Compare multiple companies side-by-side.

**Query Parameters:**
- `company_ids[]` (array): Company IDs to compare (2-5 companies)

**Response:**
```json
{
  "data": {
    "companies": [
      {
        "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "industry": "Information Technology",
        "metrics": {
          "source_count": 13,
          "commitment_count": 4,
          "active_commitments": 4,
          "pledge_count": 2,
          "industry_initiatives": 2,
          "avg_source_reliability": 4.6,
          "latest_research": "2025-11-01T13:15:00Z"
        }
      },
      {
        "id": "e3770756-f606-4436-8355-beb5774590e9",
        "name": "AbbVie Inc.",
        "ticker": "ABBV",
        "industry": "Health Care",
        "metrics": {
          "source_count": 10,
          "commitment_count": 3,
          "active_commitments": 3,
          "pledge_count": 1,
          "industry_initiatives": 2,
          "avg_source_reliability": 4.3,
          "latest_research": "2025-11-01T00:00:00Z"
        }
      }
    ]
  }
}
```

---

### 6. Search

#### `GET /search`
Universal search across all entities.

**Query Parameters:**
- `q` (string, required): Search query
- `entity_types[]` (array): Limit to specific types (companies, profiles, sources, commitments)
- `page` (int): Page number
- `per_page` (int): Results per page

**Response:**
```json
{
  "data": {
    "query": "diversity initiative",
    "results": {
      "companies": [
        {
          "type": "company",
          "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
          "name": "Apple Inc.",
          "ticker": "AAPL",
          "relevance_score": 0.95,
          "match_context": "...diversity and inclusion page..."
        }
      ],
      "commitments": [
        {
          "type": "commitment",
          "id": "68fe422b-469e-4d15-933e-1d3224343248",
          "commitment_name": "Racial Equity and Justice Initiative (REJI)",
          "company": "Apple Inc.",
          "relevance_score": 0.92,
          "match_context": "...justice initiative has surpassed..."
        }
      ],
      "sources": [
        {
          "type": "source",
          "id": "10375cab-ee19-4f66-be3e-fde154c8e28e",
          "title": "Inclusion & Diversity - Apple",
          "company": "Apple Inc.",
          "relevance_score": 0.88,
          "match_context": "...diversity page with programs..."
        }
      ]
    },
    "total_results": 42
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

---

## Error Handling

All endpoints follow consistent error response format:

**Error Response Structure:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "request_id": "unique-request-id"
  }
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting

**Default Limits:**
- Anonymous: 10 requests/minute
- Authenticated (Free): 60 requests/minute
- Authenticated (Pro): 600 requests/minute
- Authenticated (Enterprise): Custom

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1635724800
```

---

## Pagination

All list endpoints support pagination with consistent parameters:

**Query Parameters:**
- `page` (int, default: 1): Page number
- `per_page` (int, default: 20, max: 100): Items per page

**Response Structure:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "total_count": 47,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

---

## Filtering & Sorting

### Common Filter Parameters
Most list endpoints support:
- Field-specific filters (e.g., `industry=`, `country=`)
- Range filters (e.g., `from_date=`, `to_date=`, `min_sources=`)
- Array filters (e.g., `industries[]=Tech&industries[]=Healthcare`)
- Search (e.g., `search=` for text search)

### Sorting
- `sort`: Field to sort by
- `order`: `asc` or `desc`

Example:
```
GET /companies?sort=name&order=asc&industry=Technology
```

---

## Advanced Features

### 1. Field Selection
Reduce payload size by requesting specific fields:

```
GET /companies/{id}?fields=id,name,ticker,industry
```

### 2. Embedding Related Resources
Include related data in a single request:

```
GET /companies/{id}?include=profile,commitments,sources
```

### 3. Bulk Operations
Get multiple resources in one request:

```
GET /companies/bulk?ids[]=uuid1&ids[]=uuid2&ids[]=uuid3
```

### 4. Webhooks (Future)
Subscribe to events:
- `company.created`
- `profile.updated`
- `commitment.added`
- `source.added`

---

## Technology Stack Recommendations

### Backend Framework Options
1. **FastAPI (Python)** - Recommended
   - Native async support
   - Auto-generated OpenAPI docs
   - Type hints and validation
   - Great Supabase integration

2. **Express.js (Node.js)**
   - Good Supabase SDK
   - Large ecosystem
   - Fast development

3. **Django REST Framework (Python)**
   - Robust ORM
   - Admin panel
   - Mature ecosystem

### Database Layer
- **Supabase** (already in use)
  - Built-in REST API
  - Real-time subscriptions
  - Row-level security
  - Authentication

### Caching
- **Redis** for caching frequent queries
- Cache analytics aggregations
- Cache search results

### Documentation
- **OpenAPI/Swagger** for API docs
- **Postman Collections** for testing

---

## Implementation Phases

### Phase 1: Core API (MVP)
- [x] Database schema (existing)
- [ ] Companies CRUD endpoints
- [ ] Profiles read endpoints
- [ ] Sources read endpoints
- [ ] Commitments read endpoints
- [ ] Basic filtering and pagination
- [ ] Authentication

### Phase 2: Analytics
- [ ] Analytics endpoints
- [ ] Aggregation queries
- [ ] Comparison features
- [ ] Trend analysis

### Phase 3: Search & Discovery
- [ ] Full-text search
- [ ] Advanced filtering
- [ ] Recommendation engine
- [ ] Related companies

### Phase 4: Advanced Features
- [ ] Webhooks
- [ ] Real-time updates
- [ ] Bulk operations
- [ ] Export capabilities (CSV, JSON, PDF)
- [ ] Public vs private data access

---

## Security Considerations

### Authentication
- API Key-based authentication
- JWT tokens for user sessions
- OAuth2 for third-party integrations

### Authorization
- Role-based access control (RBAC)
- Public data vs premium data tiers
- Supabase Row Level Security (RLS)

### Data Protection
- HTTPS only
- Input validation and sanitization
- SQL injection prevention (use parameterized queries)
- XSS protection
- CORS configuration

### Privacy
- No PII collection in sources
- Compliance with data retention policies
- GDPR/CCPA compliance considerations

---

## Performance Optimization

### Database
1. **Indexes:**
   - `companies(ticker)` - for ticker lookups
   - `companies(industry)` - for industry filtering
   - `profiles(company_id, is_latest)` - for latest profile queries
   - `data_sources(profile_id)` - for profile source lookups
   - `commitments(profile_id, current_status)` - for active commitment queries
   - Full-text search indexes on `companies(name)`, `commitments(commitment_name)`

2. **Views:**
   - `company_summary_view` - Pre-joined company + profile data
   - `commitment_stats_view` - Aggregated commitment statistics

### API
1. **Caching Strategy:**
   - Cache GET requests for 5-15 minutes
   - Cache analytics for 1 hour
   - Invalidate on data updates

2. **Query Optimization:**
   - Use `select` parameter to limit fields
   - Implement cursor-based pagination for large datasets
   - Use database connection pooling

3. **Response Compression:**
   - Enable gzip compression
   - Minify JSON responses

---

## Monitoring & Observability

### Metrics to Track
- Request rate and response times
- Error rates by endpoint
- Cache hit/miss ratios
- Database query performance
- Rate limit hits

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking (Sentry, Rollbar)
- Audit logs for data changes

### Tools
- Application monitoring: Datadog, New Relic
- Error tracking: Sentry
- Uptime monitoring: Pingdom, UptimeRobot
- Analytics: Custom dashboard

---

## API Versioning

### Strategy: URL Path Versioning
```
https://api.deitracker.com/v1/companies
https://api.deitracker.com/v2/companies
```

### Version Lifecycle
- v1: Current stable version
- v2: Beta/preview available via header: `X-API-Version: 2.0-beta`
- Deprecation notice: 6 months before sunset
- Support overlap: 12 months minimum

---

## Example Use Cases

### Use Case 1: Company Dashboard
**Goal:** Display comprehensive DEI overview for a single company

**API Calls:**
```
1. GET /companies/{id}?include=profile
2. GET /commitments?company_id={id}&status=active
3. GET /sources?company_id={id}&source_type=corporate_website&min_reliability=4
```

### Use Case 2: Industry Comparison
**Goal:** Compare DEI commitment levels across industries

**API Calls:**
```
1. GET /analytics/industries
2. GET /commitments/types
3. GET /analytics/trends?metric=commitments_added&interval=month
```

### Use Case 3: Research Platform
**Goal:** Find all companies with specific DEI initiatives

**API Calls:**
```
1. GET /search?q=racial equity initiative
2. GET /commitments?commitment_type=pledge&status=active
3. GET /companies?has_commitments=true&min_sources=5
```

### Use Case 4: Investor Due Diligence
**Goal:** Assess DEI posture of potential investment targets

**API Calls:**
```
1. GET /analytics/compare?company_ids[]={id1}&company_ids[]={id2}
2. GET /sources?company_id={id}&source_type=regulatory_filing
3. GET /commitments?company_id={id}
```

---

## Next Steps

1. **Choose Technology Stack:** FastAPI recommended for Python + Supabase
2. **Set up Development Environment:** Local Supabase instance, API framework
3. **Implement Phase 1 Endpoints:** Start with read-only endpoints
4. **Create OpenAPI Documentation:** Auto-generate from code
5. **Build Sample Frontend:** Simple React dashboard to test API
6. **Add Authentication:** API key management system
7. **Deploy to Production:** Vercel, Railway, or AWS
8. **Monitor and Iterate:** Gather usage data and improve

---

## Appendix

### Sample Request/Response Examples

#### Getting Company with Full DEI Profile
**Request:**
```bash
curl -X GET "https://api.deitracker.com/v1/companies/0a4545e1-f3c5-48f6-bf08-e3854524869f?include=all" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "data": {
    "id": "0a4545e1-f3c5-48f6-bf08-e3854524869f",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "cik": "0000320193",
    "industry": "Information Technology",
    "headquarters": {
      "city": "Cupertino",
      "state": "California",
      "country": "United States"
    },
    "profile": {
      "id": "fe9d9d74-e604-4608-aac4-e7ae7258c7c4",
      "research_captured_at": "2025-11-01T13:15:00Z",
      "source_count": 13,
      "commitment_count": 4
    },
    "commitments": [
      {
        "id": "68fe422b-469e-4d15-933e-1d3224343248",
        "commitment_name": "Racial Equity and Justice Initiative (REJI)",
        "commitment_type": "pledge",
        "current_status": "active"
      }
    ],
    "sources": [
      {
        "id": "10375cab-ee19-4f66-be3e-fde154c8e28e",
        "title": "Inclusion & Diversity - Apple",
        "source_type": "corporate_website",
        "reliability_score": 5,
        "url": "https://www.apple.com/diversity/"
      }
    ]
  }
}
```

---

**End of API Architecture Document**

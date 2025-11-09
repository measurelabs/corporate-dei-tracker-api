# DEI Tracker API - Implementation Quick Start Guide

## Database Schema Diagram

```
┌─────────────────────────────┐
│        companies            │
├─────────────────────────────┤
│ id (PK)          UUID       │
│ ticker           STRING     │
│ name             STRING     │
│ cik              STRING     │
│ industry         STRING     │
│ hq_city          STRING     │
│ hq_state         STRING     │
│ hq_country       STRING     │
│ created_at       TIMESTAMP  │
│ updated_at       TIMESTAMP  │
└─────────────────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────────────────┐
│         profiles            │
├─────────────────────────────┤
│ id (PK)          UUID       │
│ company_id (FK)  UUID       │────┐
│ schema_version   STRING     │    │
│ profile_type     STRING     │    │
│ generated_at     TIMESTAMP  │    │
│ research_captured_at  TS    │    │
│ research_notes   TEXT       │    │
│ source_count     INTEGER    │    │
│ is_latest        BOOLEAN    │    │
│ created_at       TIMESTAMP  │    │
└─────────────────────────────┘    │
         │                          │
         │ 1:N                      │
         ├──────────────────────────┼────────┐
         │                          │        │
         ▼                          ▼        ▼
┌──────────────────────┐  ┌─────────────────────────────┐
│    data_sources      │  │       commitments           │
├──────────────────────┤  ├─────────────────────────────┤
│ id (PK)      UUID    │  │ id (PK)          UUID       │
│ profile_id   UUID    │  │ profile_id (FK)  UUID       │
│ source_id    STRING  │  │ commitment_name  STRING     │
│ source_type  STRING  │  │ commitment_type  STRING     │
│ publisher    STRING  │  │ current_status   STRING     │
│ author       STRING  │  │ quotes           ARRAY      │
│ url          STRING  │  │ provenance_ids   ARRAY      │
│ date         DATE    │  └─────────────────────────────┘
│ title        STRING  │
│ reliability  INTEGER │
│ doc_type     STRING  │
│ notes        TEXT    │
└──────────────────────┘
```

## Key Relationships

- **companies → profiles**: One-to-One (each company has one current DEI profile)
- **profiles → data_sources**: One-to-Many (each profile has multiple source citations)
- **profiles → commitments**: One-to-Many (each profile has multiple DEI commitments)

## FastAPI Implementation Example

### 1. Project Structure

```
measure_api/
├── .env
├── requirements.txt
├── main.py
├── config.py
├── database.py
├── models/
│   ├── __init__.py
│   ├── company.py
│   ├── profile.py
│   ├── source.py
│   └── commitment.py
├── schemas/
│   ├── __init__.py
│   ├── company.py
│   ├── profile.py
│   ├── source.py
│   └── commitment.py
├── routers/
│   ├── __init__.py
│   ├── companies.py
│   ├── profiles.py
│   ├── sources.py
│   ├── commitments.py
│   └── analytics.py
├── services/
│   ├── __init__.py
│   ├── company_service.py
│   └── analytics_service.py
└── tests/
    ├── __init__.py
    ├── test_companies.py
    └── test_analytics.py
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn supabase python-dotenv pydantic
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.3
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

### 3. Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    api_version: str = "v1"
    app_name: str = "DEI Tracker API"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### 4. Database Connection (`database.py`)

```python
from supabase import create_client, Client
from config import get_settings

settings = get_settings()

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
```

### 5. Pydantic Schemas (`schemas/company.py`)

```python
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    ticker: str
    name: str
    cik: Optional[str] = None
    industry: str
    hq_city: str
    hq_state: Optional[str] = None
    hq_country: str

class CompanyResponse(CompanyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyWithProfile(CompanyResponse):
    profile_id: Optional[UUID4] = None
    has_profile: bool = False
    source_count: Optional[int] = 0
    commitment_count: Optional[int] = 0
```

### 6. Router Example (`routers/companies.py`)

```python
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from supabase import Client
from database import get_supabase_client
from schemas.company import CompanyResponse, CompanyWithProfile

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    supabase: Client = Depends(get_supabase_client)
):
    """List all companies with optional filtering"""

    # Calculate offset
    offset = (page - 1) * per_page

    # Build query
    query = supabase.table('companies').select('*')

    # Apply filters
    if industry:
        query = query.eq('industry', industry)
    if country:
        query = query.eq('hq_country', country)
    if search:
        query = query.or_(f'name.ilike.%{search}%,ticker.ilike.%{search}%')

    # Apply pagination
    query = query.range(offset, offset + per_page - 1)

    # Execute query
    result = query.execute()

    return result.data

@router.get("/{company_id}", response_model=CompanyWithProfile)
async def get_company(
    company_id: str,
    include: Optional[str] = None,
    supabase: Client = Depends(get_supabase_client)
):
    """Get a single company by ID"""

    # Build base query
    select_fields = '*'

    if include and 'profile' in include:
        # Join with profiles table
        result = supabase.table('companies') \
            .select('*, profiles(*)') \
            .eq('id', company_id) \
            .execute()
    else:
        result = supabase.table('companies') \
            .select(select_fields) \
            .eq('id', company_id) \
            .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")

    return result.data[0]

@router.get("/ticker/{ticker}", response_model=CompanyResponse)
async def get_company_by_ticker(
    ticker: str,
    supabase: Client = Depends(get_supabase_client)
):
    """Get company by ticker symbol"""

    result = supabase.table('companies') \
        .select('*') \
        .eq('ticker', ticker.upper()) \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail=f"Company with ticker {ticker} not found")

    return result.data[0]
```

### 7. Main Application (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routers import companies, profiles, sources, commitments, analytics

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="API for tracking corporate DEI stances and commitments"
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
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 8. Run the Application

```bash
# Development
uvicorn main:app --reload --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 9. Access API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example API Calls

### Get All Companies
```bash
curl http://localhost:8000/v1/companies
```

### Get Company by ID
```bash
curl http://localhost:8000/v1/companies/0a4545e1-f3c5-48f6-bf08-e3854524869f
```

### Filter by Industry
```bash
curl http://localhost:8000/v1/companies?industry=Information%20Technology
```

### Search Companies
```bash
curl http://localhost:8000/v1/companies?search=apple
```

## Database Indexes to Add

For optimal performance, add these indexes to your Supabase database:

```sql
-- Companies table indexes
CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_country ON companies(hq_country);
CREATE INDEX idx_companies_name ON companies USING gin(to_tsvector('english', name));

-- Profiles table indexes
CREATE INDEX idx_profiles_company_id ON profiles(company_id);
CREATE INDEX idx_profiles_is_latest ON profiles(company_id, is_latest) WHERE is_latest = true;

-- Data sources table indexes
CREATE INDEX idx_sources_profile_id ON data_sources(profile_id);
CREATE INDEX idx_sources_type ON data_sources(source_type);
CREATE INDEX idx_sources_date ON data_sources(date);
CREATE INDEX idx_sources_reliability ON data_sources(reliability_score);

-- Commitments table indexes
CREATE INDEX idx_commitments_profile_id ON commitments(profile_id);
CREATE INDEX idx_commitments_type ON commitments(commitment_type);
CREATE INDEX idx_commitments_status ON commitments(current_status);
```

## Supabase Row Level Security (RLS)

Enable RLS policies for public API access:

```sql
-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE commitments ENABLE ROW LEVEL SECURITY;

-- Allow public read access (adjust as needed)
CREATE POLICY "Public read access on companies"
ON companies FOR SELECT
USING (true);

CREATE POLICY "Public read access on profiles"
ON profiles FOR SELECT
USING (true);

CREATE POLICY "Public read access on sources"
ON data_sources FOR SELECT
USING (true);

CREATE POLICY "Public read access on commitments"
ON commitments FOR SELECT
USING (true);
```

## Environment Variables

Ensure your `.env` file has:

```env
SUPABASE_URL=https://izjhjmzltmbtqlwdvdvd.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Testing

Create test files to verify endpoints:

```python
# tests/test_companies.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_companies():
    response = client.get("/v1/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_company():
    response = client.get("/v1/companies/0a4545e1-f3c5-48f6-bf08-e3854524869f")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["name"] == "Apple Inc."
```

Run tests:
```bash
pip install pytest httpx
pytest tests/
```

## Deployment Options

### 1. Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway init
railway up
```

### 2. Render
```yaml
# render.yaml
services:
  - type: web
    name: dei-tracker-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3. Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t dei-tracker-api .
docker run -p 8000:8000 --env-file .env dei-tracker-api
```

## Next Steps

1. **Implement remaining routers** (profiles, sources, commitments, analytics)
2. **Add authentication** using API keys or JWT
3. **Implement caching** with Redis for frequently accessed data
4. **Add rate limiting** to prevent abuse
5. **Create frontend** using React, Vue, or Next.js
6. **Set up monitoring** with Sentry and logging
7. **Write comprehensive tests**
8. **Deploy to production**

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Supabase Python Docs**: https://supabase.com/docs/reference/python/introduction
- **Pydantic Docs**: https://docs.pydantic.dev/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

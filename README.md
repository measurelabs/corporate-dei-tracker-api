# MEASURE Labs API

**Making Corporate Accountability Transparent and Accessible**

The MEASURE Labs API provides programmatic access to comprehensive corporate DEI (Diversity, Equity, and Inclusion) intelligence. Track commitments, controversies, and accountability metrics across 360+ companies with AI-powered analysis and verified data sources.

🔗 **Production API**: [api.measurelabs.org](https://api.measurelabs.org)  
📚 **Documentation**: [measurelabs.org/api-docs](https://measurelabs.org/docs)  
🌐 **Platform**: [measurelabs.org](https://measurelabs.org)  
📧 **Contact**: contribute@measurelabs.org

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Response Format](#response-format)
- [Caching](#caching)
- [Rate Limits](#rate-limits)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Use Cases](#use-cases)
- [Data Methodology](#data-methodology)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Overview

MEASURE Labs API enables developers, researchers, journalists, and organizations to integrate corporate DEI intelligence into their applications, research, and decision-making workflows.

### What You Can Build

- **Consumer Tools** - Help users make values-aligned purchasing decisions
- **Investment Platforms** - Assess DEI risk and ESG alignment
- **Research Dashboards** - Analyze corporate accountability trends
- **Journalism Tools** - Investigate gaps between rhetoric and action
- **HR Applications** - Evaluate company cultures for job seekers
- **Advocacy Platforms** - Track corporate commitments and hold companies accountable

### Key Features

- ✅ **360+ Companies** - Comprehensive S&P 500 coverage with high-profile additions
- 🤖 **AI-Powered Insights** - Executive summaries synthesizing multiple data sources
- ⚡ **Real-Time Data** - Continuously updated commitments and controversies
- 🔍 **Multi-Source Verification** - 3,486+ sources with reliability scores
- 📊 **Industry Analytics** - Benchmarking across 11+ sectors
- ⚠️ **Risk Scoring** - Automated assessment of DEI-related risks
- 🚀 **Performance Optimized** - Redis caching for 7x faster responses
- 📈 **Historical Tracking** - Monitor changes in commitments over time

---

## Quick Start

### Base URL

**Production**: `https://api.measurelabs.org/v1`  
**Development**: `http://localhost:8000/v1`

### Example Request

```bash
# Get all companies
curl https://api.measurelabs.org/v1/companies

# Get company by ticker
curl https://api.measurelabs.org/v1/companies/ticker/AAPL

# Get analytics overview
curl https://api.measurelabs.org/v1/analytics/overview
```

### Example Response

```json
{
  "data": {
    "id": "uuid",
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "industry": "Information Technology",
    "headquarters_location": "Cupertino, California, United States",
    "website": "https://www.apple.com"
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "total_count": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

## Authentication

### Free Tier (Public Access)

API key required for basic endpoints. Rate limited to:
- **50 requests/hour**
- **100 requests/day**

### Premium Tier

For higher rate limits and advanced features, contact: **contribute@measurelabs.org**

Premium benefits:
- **10,000 requests/hour**
- **Unlimited daily requests**
- **Webhook support** (coming soon)
- **Priority support**
- **Custom data exports**

---

## API Endpoints

### Companies

#### List Companies
```http
GET /v1/companies?page=1&per_page=20&industry=Technology&country=United%20States
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `per_page` - Results per page (default: 20, max: 100)
- `industry` - Filter by industry name
- `country` - Filter by country
- `search` - Search by name or ticker

#### Get Company by ID
```http
GET /v1/companies/{company_id}
```

#### Get Company by Ticker
```http
GET /v1/companies/ticker/{ticker}
```

**Example:**
```bash
curl https://api.measurelabs.org/v1/companies/ticker/TSLA
```

#### Advanced Search
```http
GET /v1/companies/search/advanced?query=tech&filters=committed
```

**Query Parameters:**
- `query` - Search term
- `filters` - Commitment status, risk level, etc.
- `sort_by` - Sort field (name, ticker, industry)
- `sort_order` - asc or desc

---

### Profiles

#### Get Latest Profile for Company
```http
GET /v1/profiles/company/{company_id}/latest
```

Returns the most recent comprehensive DEI profile including:
- AI executive summary
- Key insights and strategic implications
- Commitment strength and transparency scores
- Risk assessment
- CDO information
- All commitments and controversies

**Example:**
```bash
curl https://api.measurelabs.org/v1/profiles/company/abc123/latest
```

#### Get Full Profile by ID
```http
GET /v1/profiles/{profile_id}/full
```

#### List All Profiles
```http
GET /v1/profiles?page=1&per_page=20
```

---

### Commitments

#### List Commitments
```http
GET /v1/commitments?company_id={id}&status=active&page=1
```

**Query Parameters:**
- `company_id` - Filter by company
- `status` - active, inactive, partial
- `commitment_type` - Filter by type (e.g., "CEO Pledge", "Coalition")

#### Get Commitment by ID
```http
GET /v1/commitments/{commitment_id}
```

#### Commitment Type Statistics
```http
GET /v1/commitments/types/stats
```

Returns distribution of commitment types across all companies.

---

### Controversies

#### List Controversies
```http
GET /v1/controversies?company_id={id}&type=lawsuit&page=1
```

**Query Parameters:**
- `company_id` - Filter by company
- `type` - discrimination lawsuit, class action, etc.
- `date_from` - Start date (ISO format)
- `date_to` - End date (ISO format)

#### Get Controversy by ID
```http
GET /v1/controversies/{controversy_id}
```

---

### Data Sources

#### List Sources
```http
GET /v1/sources?company_id={id}&source_type=news&page=1
```

**Query Parameters:**
- `company_id` - Filter by company
- `source_type` - corporate website, news article, press release, sec filing, etc.
- `min_reliability` - Minimum reliability score (0-10)

#### Get Source by ID
```http
GET /v1/sources/{source_id}
```

#### Source Type Statistics
```http
GET /v1/sources/types/stats
```

---

### Analytics

#### Overview Statistics
```http
GET /v1/analytics/overview
```

Returns platform-wide statistics:
- Total companies tracked
- Total commitments
- Total controversies
- Average scores by metric
- Distribution breakdowns

**Cached for 10 minutes**

#### Industry Statistics
```http
GET /v1/analytics/industries
```

Returns statistics grouped by industry:
- Company count per industry
- Average commitment strength
- CDO presence percentage
- Risk distribution

**Cached for 10 minutes**

#### Compare Companies
```http
GET /v1/analytics/compare?company_ids={id1}&company_ids={id2}&company_ids={id3}
```

Compare up to 5 companies side-by-side across all metrics.

**Cached for 5 minutes**

#### Risk Distribution
```http
GET /v1/analytics/risks
```

Returns breakdown of companies by risk level (Low/Medium/High).

**Cached for 10 minutes**

---

### Cache Management

#### Get Cache Statistics
```http
GET /cache/stats
```

Returns cache hit rates, memory usage, and key counts.

#### Clear Cache
```http
POST /cache/clear?pattern=analytics:*
```

**Query Parameters:**
- `pattern` - Redis pattern to match (default: `*` for all)

**Note:** Cache clearing requires admin authentication (coming soon).

---

## Response Format

All API endpoints return JSON with a consistent structure:

### Successful Response

```json
{
  "data": {
    // Response data (object or array)
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_count": 94,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response

```json
{
  "detail": "Error message",
  "status_code": 404,
  "type": "not_found"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

## Caching

MEASURE Labs API uses Redis caching for optimal performance:

### Cache Strategy

- **Analytics endpoints**: 10-minute TTL
- **Company comparisons**: 5-minute TTL
- **Static data**: 1-hour TTL
- **Dynamic data**: No caching

### Cache Headers

Responses include cache information:

```http
X-Cache-Status: HIT
X-Cache-TTL: 598
```

### Performance Impact

- **Without cache**: ~500-1000ms average response time
- **With cache**: ~70-100ms average response time
- **7x faster** for cached responses

---

## Rate Limits

### Free Tier
- **100 requests/hour**
- **1,000 requests/day**
- Burst allowance: 10 requests

### Premium Tier
- **10,000 requests/hour**
- **Unlimited daily requests**
- Burst allowance: 100 requests

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1635724800
```

### Handling Rate Limits

When rate limited, you'll receive:

```json
{
  "detail": "Rate limit exceeded. Try again in 42 seconds.",
  "status_code": 429,
  "retry_after": 42
}
```

Implement exponential backoff in your client code.

---

## Tech Stack

- **Framework**: FastAPI (Python 3.12+)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis (Upstash)
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI)
- **Documentation**: OpenAPI/Swagger

### Key Libraries

```
fastapi==0.104.1
pydantic==2.5.0
supabase==2.0.0
redis==5.0.1
uvicorn==0.24.0
```

---

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL (or Supabase account)
- Redis (or Upstash account)

### Setup

1. **Clone repository**
```bash
git clone https://github.com/measurelabs/dei-tracker-api.git
cd dei-tracker-api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**

Create `.env` file:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (Upstash)
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token

# API Configuration
API_V1_PREFIX=/v1
PROJECT_NAME=MEASURE Labs API
VERSION=1.0.0
```

4. **Run development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Production Deployment

```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Run with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or use Docker
docker build -t measurelabs-api .
docker run -p 8000:8000 --env-file .env measurelabs-api
```

---

## Use Cases

### 1. Consumer Decision Tool

Build a browser extension that shows DEI scores when shopping online:

```javascript
// Check company DEI status
async function checkCompany(ticker) {
  const response = await fetch(
    `https://api.measurelabs.org/v1/companies/ticker/${ticker}`
  );
  const data = await response.json();
  
  // Display commitment score and controversies
  displayDEIBadge(data.commitment_score, data.controversies);
}
```

### 2. Investment Research Platform

Integrate DEI risk assessment into portfolio analysis:

```python
import requests

def assess_portfolio_dei_risk(tickers):
    risk_scores = {}
    for ticker in tickers:
        response = requests.get(
            f"https://api.measurelabs.org/v1/companies/ticker/{ticker}"
        )
        company = response.json()['data']
        risk_scores[ticker] = company['risk_level']
    return risk_scores
```

### 3. Journalism Data Pipeline

Automate monitoring of corporate DEI changes:

```python
# Daily script to check for new controversies
import requests
from datetime import datetime, timedelta

yesterday = (datetime.now() - timedelta(days=1)).isoformat()

response = requests.get(
    "https://api.measurelabs.org/v1/controversies",
    params={"date_from": yesterday}
)

new_controversies = response.json()['data']
if new_controversies:
    send_alert_to_newsroom(new_controversies)
```

### 4. Job Seeker Tool

Help candidates evaluate company culture:

```javascript
async function evaluateEmployer(companyName) {
  const profile = await fetch(
    `https://api.measurelabs.org/v1/profiles/company/${companyId}/latest`
  ).then(r => r.json());
  
  return {
    hasCDO: profile.cdo_info !== null,
    commitmentScore: profile.commitment_strength,
    recentControversies: profile.controversies.filter(
      c => new Date(c.date) > Date.now() - 365*24*60*60*1000
    )
  };
}
```

### 5. Academic Research

Export data for longitudinal analysis:

```python
import pandas as pd
import requests

# Get all companies with full profiles
companies = requests.get(
    "https://api.measurelabs.org/v1/companies",
    params={"per_page": 100}
).json()['data']

# Build dataset
df = pd.DataFrame([
    {
        'ticker': c['ticker'],
        'industry': c['industry'],
        'commitment_score': c['commitment_strength'],
        'has_cdo': c['has_cdo']
    }
    for c in companies
])

df.to_csv('dei_research_dataset.csv')
```

---

## Data Methodology

### Data Collection

We aggregate information from:
- Corporate websites and DEI pages
- ESG and sustainability reports
- Press releases and announcements
- SEC filings and proxy statements
- News articles from verified outlets
- Legal databases (PACER, CourtListener)
- Advocacy group reports

### Source Verification

Each source receives a **reliability score (0-10)** based on:
- Publisher credibility
- Recency of publication
- Primary vs. secondary sourcing
- Corroboration across sources

### AI Analysis

AI executive summaries are generated using:
- GPT-4 for text synthesis
- Retrieval-augmented generation (RAG)
- Multi-source cross-referencing
- Human review for accuracy

**All AI summaries cite underlying sources** to prevent hallucination.

### Scoring Methodology

**Commitment Strength (0-10)**
- 8-10: Binding commitments with structural accountability
- 5-7: Moderate commitments with transparency
- 2-4: Vague commitments without accountability
- 0-1: No commitment or active scaling back

**Transparency (0-10)**
- 8-10: Detailed public metrics, EEO-1 data shared
- 5-7: Annual diversity reports with some metrics
- 2-4: Vague statements without data
- 0-1: No public information

**Risk Level**
- **Low**: No controversies, strong commitments, transparent
- **Medium**: Minor controversies or mixed signals
- **High**: Active lawsuits, major controversies, rollbacks

---

## Contributing

MEASURE Labs welcomes contributions from developers, researchers, and data enthusiasts.

### Ways to Contribute

#### 🐛 **Report Bugs**
Found an API issue? [Open an issue](https://github.com/measurelabs/api/issues) with:
- Endpoint and parameters used
- Expected vs. actual behavior
- Request/response examples
- Environment details

#### 📊 **Submit Data**
Found missing information or inaccuracies? Email:  
**contribute@measurelabs.org**

Include:
- Company name and ticker
- Data type (commitment, controversy, source)
- URL or document reference
- Description

#### 💻 **Code Contributions**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/api-improvement`)
3. Write tests for new functionality
4. Follow code style (Black, Flake8)
5. Submit a pull request

**Code Style:**
```bash
# Format code
black app/

# Check linting
flake8 app/

# Run tests
pytest tests/
```

#### 📚 **Documentation**

Improve API docs, add examples, or clarify confusing sections:
- Update endpoint descriptions
- Add code samples in multiple languages
- Create integration guides
- Translate documentation

#### 🔬 **Research Collaboration**

Academic institutions and research organizations can request:
- Full database exports
- Custom API endpoints
- Co-publishing opportunities

Contact: **contribute@measurelabs.org**

---

## License

**MEASURE Labs API** is licensed under a **Proprietary Source-Available License**.

### Usage Rights

✅ **You CAN:**
- Access and use the API through official endpoints
- View the source code for reference and learning
- Augment the codebase for internal use
- Use the data in research and publications (with attribution)

❌ **You CANNOT:**
- Distribute the source code
- Host competing API instances
- Redistribute the data outside our platform
- Remove attribution

⚠️ **You MUST:**
- Attribute MEASURE Labs when using data: "Data provided by MEASURE Labs (measurelabs.org)"
- Comply with API Terms of Service
- Respect rate limits
- Maintain proper citations in publications

### Commercial Licensing

For commercial API usage, premium access, or custom deployments:  
**contribute@measurelabs.org**

**Full License**: [LICENSE](./LICENSE)

---

## Support

### Documentation

- **API Docs**: [measurelabs.org/api-docs](https://measurelabs.org/api-docs)
- **Swagger UI**: [api.measurelabs.org/docs](https://api.measurelabs.org/docs)
- **Methodology**: [measurelabs.org/methodology](https://measurelabs.org/methodology)

### Contact

- **Email**: contribute@measurelabs.org
- **GitHub**: [github.com/measurelabs](https://github.com/measurelabs/)
- **Platform**: [measurelabs.org](https://measurelabs.org)

---

## Disclaimer

MEASURE Labs provides information for educational and research purposes. While we strive for accuracy:

- Data aggregates publicly available information
- AI summaries may contain errors—verify with original sources
- We are not legal or financial advisors
- Information may be incomplete or outdated
- Users should verify data for critical decisions

For corrections: **contribute@measurelabs.org**

---

**Making Corporate Accountability Transparent and Accessible**

MEASURE Labs API empowers developers, researchers, and organizations to build tools that hold institutions accountable. We believe transparency starts with accessible data.

⭐ **Star this repository** if you support corporate accountability!

---

*Last Updated: November 2025*
# Postman Collection Guide

## Overview

The `DEI_Tracker_API.postman_collection.json` file contains an exhaustive collection of 80+ API requests covering all endpoints and use cases.

## How to Import

### Method 1: Import via Postman App
1. Open Postman Desktop or Web
2. Click **Import** button (top left)
3. Select **File** tab
4. Choose `DEI_Tracker_API.postman_collection.json`
5. Click **Import**

### Method 2: Drag and Drop
1. Open Postman
2. Drag the JSON file into the Postman window
3. Collection will be imported automatically

## Collection Structure

The collection is organized into **7 main folders**:

### 1. Health & Info (3 requests)
- Root endpoint
- Health check
- API documentation

### 2. Companies (16 requests)
- List all companies (with pagination)
- Filter by industry, country, state
- Search by name or ticker
- Sort by various fields
- Get by ID or ticker
- Advanced search with multiple criteria

### 3. Profiles (7 requests)
- List all profiles
- Filter by company, latest version
- Get profile with sources, commitments, or everything

### 4. Sources (12 requests)
- List all sources
- Filter by type (corporate_website, news_article, regulatory_filing, etc.)
- Filter by reliability score (1-5)
- Filter by publisher
- Search sources
- Get source type statistics

### 5. Commitments (14 requests) ⭐ CORE VALUE
- List all commitments
- Filter by status (active, discontinued, inactive)
- Filter by type (pledge, industry_initiative)
- Search commitments
- Get changed commitments only
- Track commitment changes
- Get commitment type statistics

### 6. Analytics (9 requests)
- Platform overview
- Industry statistics
- Compare 2-5 companies
- Stance changes tracking
- Industry trends

### 7. Real-World Use Cases (9 requests)
- Complete workflows for common scenarios
- Find companies backing away from DEI
- Research specific companies
- Compare industries
- Track recent changes
- Investor due diligence

## Collection Variables

The collection includes pre-configured variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `api_version` | `v1` | API version |
| `company_id` | `0a4545e1-f3c5-48f6-bf08-e3854524869f` | Apple Inc. ID (example) |
| `profile_id` | `fe9d9d74-e604-4608-aac4-e7ae7258c7c4` | Apple profile ID (example) |

### Updating Variables

1. Click on the collection name
2. Go to **Variables** tab
3. Update values as needed
4. Save

## Request Examples

### Basic Request
```
GET {{base_url}}/{{api_version}}/companies/
```
Uses variables to construct: `http://localhost:8000/v1/companies/`

### Request with Parameters
```
GET {{base_url}}/{{api_version}}/companies/?industry=Information Technology&sort=name
```

### Request with Variable
```
GET {{base_url}}/{{api_version}}/companies/{{company_id}}
```

## Key Features

### 📊 Comprehensive Coverage
- **80+ requests** covering all endpoints
- Multiple examples per endpoint
- Different filter combinations

### 🎯 Use Case Driven
- Organized by real-world scenarios
- Step-by-step workflows
- Business context in descriptions

### 🔍 Search & Filter Examples
- Every filterable field has examples
- Combined filter demonstrations
- Search query examples

### 📈 Analytics Ready
- All analytics endpoints
- Comparison requests
- Trend tracking

### 🏷️ Well Documented
- Clear descriptions for each request
- Query parameter explanations
- Expected use cases

## Quick Start

### 1. Import Collection
Import the JSON file into Postman (see above)

### 2. Test Basic Endpoints
Start with **Health & Info** folder:
- Root Endpoint → See API info
- Health Check → Verify API is running

### 3. Explore Companies
Go to **Companies** folder:
- List All Companies → Browse all companies
- Get Company by Ticker - AAPL → Get Apple's data

### 4. Track DEI Changes
Go to **Commitments** folder:
- Filter by Status - Active → See active commitments
- Filter by Status - Discontinued → Companies backing away
- Get Commitment Changes → Track all changes

### 5. Run Analytics
Go to **Analytics** folder:
- Platform Overview → Get statistics
- Industry Trends → See which industries backing away

### 6. Try Use Cases
Go to **Real-World Use Cases** folder:
- Run complete workflows
- See how endpoints work together

## Common Workflows

### Research a Company
1. **Companies** → Get Company by Ticker - AAPL
2. Copy the `id` from response
3. **Profiles** → Get Profile by ID (use copied ID)
4. **Commitments** → Get Commitments for Profile

### Track Industry Changes
1. **Analytics** → Industry Trends
2. **Companies** → Filter by Industry (pick from trends)
3. **Commitments** → Get Commitment Changes
4. Filter results by companies in that industry

### Find Companies Backing Away
1. **Commitments** → Get Commitment Changes
2. **Commitments** → Filter by Status - Discontinued
3. **Analytics** → Stance Changes - Decreased Only
4. **Analytics** → Industry Trends (see which sectors)

## Tips & Tricks

### 1. Save Response Data
- Click **Save Response** to keep examples
- Use for documentation
- Share with team

### 2. Use Environments
- Create different environments (dev, staging, prod)
- Switch `base_url` per environment
- Keep same collection for all environments

### 3. Run Collections
- Use **Collection Runner** to test all endpoints
- Verify API health
- Catch breaking changes

### 4. Extract Variables
- Use **Tests** tab to extract IDs from responses
- Auto-populate variables
- Chain requests together

### Example Test Script
```javascript
// Save company ID to variable
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

var jsonData = pm.response.json();
pm.environment.set("company_id", jsonData.data[0].id);
```

### 5. Organize with Folders
- Create your own folders for specific projects
- Duplicate requests and customize
- Keep original collection as reference

## Request Categories

### By HTTP Method
- **GET**: All requests (read-only API)

### By Response Type
- **List**: Returns array with pagination
- **Single**: Returns single object
- **Stats**: Returns aggregated statistics
- **Comparison**: Returns side-by-side data

### By Complexity
- **Simple**: No parameters
- **Filtered**: Query parameters
- **Complex**: Multiple filters + sorting
- **Nested**: Includes related data

## Endpoint Summary

| Folder | Endpoints | Key Features |
|--------|-----------|--------------|
| Companies | 16 | Search, filter, sort, ticker lookup |
| Profiles | 7 | Include sources/commitments |
| Sources | 12 | Reliability filtering, type stats |
| Commitments | 14 | Status tracking, change detection |
| Analytics | 9 | Trends, comparisons, insights |

## Response Formats

### List Endpoints
All return consistent pagination:
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

### Single Resource
```json
{
  "data": {...}
}
```

### Statistics
```json
{
  "data": {
    "total_companies": 47,
    "total_commitments": 196,
    ...
  }
}
```

## Troubleshooting

### API Not Responding
1. Check API is running: `GET /health`
2. Verify `base_url` variable is correct
3. Ensure no trailing slashes in URLs

### 307 Redirects
- FastAPI redirects URLs without trailing slash
- Add `/` to the end: `/companies/` not `/companies`

### No Data in Response
- Check if database has data
- Verify filters aren't too restrictive
- Try pagination: `page=1&per_page=100`

### Variable Not Working
- Ensure variable name matches: `{{company_id}}`
- Check variable is set in collection or environment
- Variables are case-sensitive

## Advanced Usage

### Export for Team
1. Click collection **...** menu
2. Select **Export**
3. Choose **Collection v2.1**
4. Share JSON file with team

### Generate Code
1. Click any request
2. Click **</>** (Code) button
3. Select language (curl, Python, JavaScript, etc.)
4. Copy generated code

### Mock Servers
1. Right-click collection
2. **Mock Collection**
3. Get mock URL
4. Use for frontend development before API is ready

### API Testing
1. Add tests to requests
2. Use Collection Runner
3. Set up CI/CD integration
4. Automated regression testing

## Next Steps

1. **Import the collection** and explore
2. **Run health check** to verify API is up
3. **Try use cases** to see real workflows
4. **Customize** for your specific needs
5. **Share** with your team
6. **Automate** testing with Newman (Postman CLI)

## Newman (CLI) Usage

Run collection from command line:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run DEI_Tracker_API.postman_collection.json

# Run with environment
newman run DEI_Tracker_API.postman_collection.json -e production.json

# Generate HTML report
newman run DEI_Tracker_API.postman_collection.json --reporters html
```

---

**Collection Version**: 1.0
**Total Requests**: 80+
**Last Updated**: November 2025
**API Version**: v1

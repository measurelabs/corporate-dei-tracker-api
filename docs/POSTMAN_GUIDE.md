# Postman Collection Guide - DEI Tracker API

## Overview

This guide explains how to use the DEI Tracker API Postman collection to test and interact with the API endpoints.

## Import the Collection

1. Open Postman
2. Click "Import" button
3. Select the file: `DEI_Tracker_API.postman_collection.json`
4. The collection will be imported with all endpoints organized into folders

## Collection Variables

The collection includes two variables that you can customize:

- **base_url**: Default is `http://localhost:8000` (change if your API is hosted elsewhere)
- **api_version**: Default is `v1`

To edit variables:
1. Click on the collection name
2. Go to the "Variables" tab
3. Update the "Current Value" column
4. Save changes

## Collection Structure

The collection is organized into the following folders:

### 1. Health & Info
Basic endpoints to check API status and get information.

- **Health Check**: Verify API is running
- **API Root**: Get API overview and feature list
- **API Version Info**: Get all available endpoints

### 2. Companies
Endpoints for browsing and searching companies.

- **List Companies**: Paginated list with filtering options
- **Get Company by ID**: Detailed company information
- **Get Company by Ticker**: Look up by stock ticker (e.g., AAPL)
- **Advanced Search**: Complex filtering with multiple criteria

**Example Filters** (enable in query params):
- `industry=Information Technology`
- `country=United States`
- `search=apple`
- `sort=name&order=asc`

### 3. Profiles
Endpoints for accessing complete DEI profiles.

**Key Feature**: Profile endpoints now return FULL profile data by default, including:
- AI analysis (executive summary, insights, strategic implications)
- DEI posture
- CDO role information
- Reporting practices
- Supplier diversity
- Risk assessment
- All related commitments, controversies, events, and sources

**Available Endpoints**:
- **List Profiles**: Browse all profiles with filtering
- **Get Profile (Full by Default)**: Returns complete profile with all components
- **Get Profile (Lightweight)**: Use `?full=false` for basic data only
- **Get Full Profile (Explicit)**: Direct `/full` endpoint
- **Get Latest Profile for Company**: Get most recent profile for a company

**Example Usage**:
```
GET /v1/profiles/{profile_id}
→ Returns full profile by default

GET /v1/profiles/{profile_id}?full=false
→ Returns lightweight version

GET /v1/profiles/company/{company_id}/latest
→ Returns latest full profile for company
```

### 4. Commitments
Track DEI commitments and initiatives.

- **List Commitments**: Filter by type, status, company
- **Get Commitment by ID**: Detailed commitment info
- **Get Commitment Type Stats**: Statistics by commitment type

**Example Filters**:
- `status=active` - Only active commitments
- `commitment_type=pledge` - Only pledges
- `search=equity` - Search commitment names

### 5. Controversies
Monitor DEI-related lawsuits and controversies.

- **List Controversies**: Filter by type, status
- **Get Controversy by ID**: Detailed controversy information

**Example Filters**:
- `status=ongoing` - Active lawsuits
- `type=lawsuit` - Filter by type
- `search=discrimination` - Search descriptions

### 6. Data Sources
Explore documented sources with reliability scores.

- **List Sources**: Filter by type, reliability, publisher
- **Get Source by ID**: Detailed source information
- **Get Source Type Stats**: Statistics by source type

**Example Filters**:
- `source_type=corporate_website`
- `min_reliability=4` - Only high-reliability sources
- `search=diversity` - Search titles and notes

### 7. Analytics
Comprehensive analytics and company comparisons.

- **Overview Statistics**: Platform-wide stats
- **Industry Statistics**: Metrics by industry
- **Compare Companies**: Side-by-side comparison (2-5 companies)
- **Risk Distribution**: Risk level breakdown

**Example - Compare Companies**:
```
GET /v1/analytics/compare?company_ids={id1}&company_ids={id2}&company_ids={id3}
```

## Common Query Parameters

Most endpoints support these parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | int | Page number | 1 |
| `per_page` | int | Items per page (max 100) | 20 |
| `full` | boolean | Return full data (profiles only) | true |

## Response Format

All endpoints return JSON in a consistent format:

```json
{
  "data": {
    // Response data
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_count": 100,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

## Tips for Testing

### 1. Start with Health Check
Always verify the API is running first:
```
GET /health
```

### 2. Explore Companies
Get a list of companies to find IDs for other requests:
```
GET /v1/companies/?per_page=10
```

### 3. Get Full Company Profile
Use ticker for easy lookup:
```
GET /v1/companies/ticker/AAPL
```

Then get the full DEI profile:
```
GET /v1/profiles/company/{company_id}/latest
```

### 4. Filter Effectively
Use query parameters to narrow results:
```
GET /v1/commitments/?status=active&per_page=5
GET /v1/sources/?min_reliability=4&source_type=corporate_website
```

### 5. Compare Companies
Get company IDs first, then compare:
```
GET /v1/analytics/compare?company_ids={id1}&company_ids={id2}
```

## Example Workflows

### Workflow 1: Research a Company's DEI Stance

1. **Find the company**:
   ```
   GET /v1/companies/ticker/AAPL
   ```

2. **Get full DEI profile** (includes AI analysis):
   ```
   GET /v1/profiles/company/{company_id}/latest
   ```

3. **View their commitments**:
   ```
   GET /v1/commitments/?company_id={company_id}
   ```

4. **Check for controversies**:
   ```
   GET /v1/controversies/?company_id={company_id}
   ```

### Workflow 2: Industry Analysis

1. **Get industry statistics**:
   ```
   GET /v1/analytics/industries
   ```

2. **List companies in specific industry**:
   ```
   GET /v1/companies/?industry=Information%20Technology
   ```

3. **Compare top companies**:
   ```
   GET /v1/analytics/compare?company_ids={id1}&company_ids={id2}
   ```

### Workflow 3: Track Active Commitments

1. **List all active commitments**:
   ```
   GET /v1/commitments/?status=active&per_page=50
   ```

2. **Get commitment statistics by type**:
   ```
   GET /v1/commitments/types/stats
   ```

3. **Search for specific initiatives**:
   ```
   GET /v1/commitments/?search=equity&status=active
   ```

## Key Features

### Full Profile Data by Default
**Important**: As of the latest version, profile endpoints return complete profile data by default, including:
- ✅ AI Context (executive summary, trend analysis, ratings)
- ✅ Key Insights (ordered list)
- ✅ Strategic Implications
- ✅ DEI Posture
- ✅ CDO Role Information
- ✅ Reporting Practices
- ✅ Supplier Diversity Programs
- ✅ Risk Assessments
- ✅ Data Quality Flags
- ✅ All Commitments
- ✅ All Controversies
- ✅ All Events
- ✅ Data Sources

**To get lightweight version**: Add `?full=false` parameter

### Pagination
All list endpoints support pagination:
- Use `page` and `per_page` parameters
- Check `pagination.has_next` to see if more results exist
- Use `pagination.next_page` for next page number

### Filtering
Most endpoints support multiple filter options:
- Combine filters with `&`
- Disable filters you don't need in query params
- Use `search` parameter for text search

## Troubleshooting

### 404 Not Found
- Check that the ID exists
- Verify the endpoint path is correct
- Make sure to include trailing slash for list endpoints

### 307 Temporary Redirect
- FastAPI may redirect URLs without trailing slashes
- Add trailing slash to list endpoints: `/companies/` not `/companies`

### Empty Results
- Check your filters - they may be too restrictive
- Verify the database has data for your query
- Try removing filters one by one

## API Documentation

For complete API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For questions or issues:
- Check the main README.md
- Review the API documentation at `/docs`
- Examine response error messages for details

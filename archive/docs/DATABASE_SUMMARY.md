# Database Summary - DEI Tracker

## Overview
Your Supabase database contains a comprehensive DEI (Diversity, Equity, and Inclusion) tracking system with data on **47 companies** across various industries.

## Database Statistics

| Table | Row Count | Description |
|-------|-----------|-------------|
| **companies** | 47 | Core company information and identification |
| **profiles** | 47 | DEI profile metadata (1:1 with companies) |
| **data_sources** | 361 | Source materials and citations (~7.7 sources per company) |
| **commitments** | 196 | DEI commitments and initiatives (~4.2 per company) |

**Total Records**: 651

## Table Details

### 1. Companies Table
**Purpose**: Store fundamental company information

**Key Fields**:
- Company identifiers (ticker, name, CIK)
- Industry classification
- Headquarters location (city, state, country)

**Sample Companies**:
- Apple Inc. (AAPL) - Information Technology
- AbbVie Inc. (ABBV) - Health Care
- Airbnb, Inc. (ABNB) - Consumer Discretionary
- Abbott Laboratories (ABT) - Health Care

**Industries Represented**:
- Information Technology
- Health Care
- Consumer Discretionary
- Financials
- And more...

### 2. Profiles Table
**Purpose**: Track DEI research and profile versions for each company

**Key Features**:
- Links to parent company (1:1 relationship)
- Tracks when research was conducted
- Version control with `is_latest` flag
- Counts of associated sources

**Profile Metadata**:
- Schema version tracking (currently v1.0)
- Profile type: "company_dei_profile"
- Research notes and context
- Generated and captured timestamps

### 3. Data Sources Table
**Purpose**: Document all sources used in DEI research

**Source Types** (361 total sources):
1. **Corporate Website** (~156 sources)
   - Official DEI pages
   - Diversity reports
   - Company statements
   - Average reliability: 4.8/5

2. **News Articles** (~120 sources)
   - Major news outlets (CNN, Fortune, etc.)
   - Coverage of DEI initiatives
   - Average reliability: 4.2/5

3. **Regulatory Filings** (~48 sources)
   - SEC filings
   - Government settlements
   - Official disclosures
   - Average reliability: 5.0/5

4. **Trade Press** (~37 sources)
   - Industry publications
   - Specialized DEI coverage
   - Average reliability: 3.5/5

**Reliability Scoring**:
- Scale: 1-5 (5 being most reliable)
- Helps users assess source quality
- Regulatory filings score highest (5.0 avg)

**Example Sources**:
- Apple's official Diversity page (reliability: 5)
- CNN Business articles on DEI (reliability: 4)
- DOJ settlement documents (reliability: 5)

### 4. Commitments Table
**Purpose**: Track DEI pledges, initiatives, and programs

**Commitment Types** (196 total):
1. **Pledges** (~98 commitments)
   - Specific DEI goals
   - Financial commitments
   - Policy changes
   - Example: Apple's REJI ($200M+ investment)

2. **Industry Initiatives** (~98 commitments)
   - Cross-company programs
   - Coalition memberships
   - Certification programs
   - Example: CEO Action for Diversity & Inclusion

**Status Tracking**:
- **Active**: 187 commitments (95%)
- **Completed**: 6 commitments
- **Discontinued**: 3 commitments

**Data Points per Commitment**:
- Name and type
- Current status
- Supporting quotes from sources
- Provenance (links to specific source IDs)

**Example Commitments**:
- Racial Equity and Justice Initiative (REJI) - Apple
- Gender Pay Equity programs
- Supplier Diversity Programs
- Diversity Network Associations (DNAs)

## Data Relationships

```
companies (47)
    │
    └── profiles (47) [1:1]
            ├── data_sources (361) [1:Many]
            │       - Corporate websites
            │       - News articles
            │       - Regulatory filings
            │       - Trade press
            │
            └── commitments (196) [1:Many]
                    - Pledges
                    - Industry initiatives
```

## Key Insights

### Coverage
- **47 companies** tracked across multiple industries
- Average **7.7 sources per company** (strong documentation)
- Average **4.2 commitments per company** (active DEI engagement)
- Data captured as of **November 1, 2025**

### Source Quality
- **48% regulatory/primary sources** (high reliability)
- **33% news coverage** (good reliability)
- **43% corporate sources** (official statements)
- **10% trade press** (industry context)

### DEI Activity
- **95% of commitments are active** (187/196)
- Strong focus on **racial equity** and **gender equity**
- Many companies participate in **industry-wide initiatives**
- Evidence of **supplier diversity programs**

### Geographic Distribution
- Primary focus: **United States**
- Some international companies (e.g., Bermuda HQ)
- State distribution: California, Illinois, etc.

## Data Quality Observations

### Strengths
1. **Comprehensive source documentation** - Every claim backed by sources
2. **Reliability scoring** - Users can assess source quality
3. **Provenance tracking** - Clear lineage of information
4. **Version control** - Profile versioning with `is_latest` flag
5. **Structured data** - Well-organized, normalized schema

### Opportunities
1. **Time series data** - Could track changes over time
2. **Quantitative metrics** - Could add numerical DEI metrics
3. **Employee data** - Could include workforce demographics
4. **Board diversity** - Could track board composition
5. **Rating system** - Could add overall DEI scores

## Use Cases

This database supports multiple use cases:

### 1. Investor Due Diligence
- Research company DEI stances before investing
- Compare companies within industries
- Track commitment fulfillment

### 2. Consumer Awareness
- Understand company values
- Make informed purchasing decisions
- Track corporate accountability

### 3. Research & Analysis
- Academic research on corporate DEI
- Trend analysis across industries
- Policy effectiveness studies

### 4. Competitive Intelligence
- Benchmark against competitors
- Identify industry best practices
- Track emerging DEI trends

### 5. ESG Reporting
- Environmental, Social, Governance analysis
- Corporate responsibility assessment
- Stakeholder reporting

## Sample Data Examples

### Apple Inc. Profile
- **13 sources** including:
  - Official diversity website
  - CNN coverage of DEI defense
  - Black Enterprise articles on leadership
  - DOJ settlement documents

- **4 active commitments**:
  - Racial Equity and Justice Initiative ($200M+)
  - Diversity Network Associations (60K+ members)
  - Gender Pay Equity (achieved since 2017)
  - Supplier Diversity Program (since 1993)

### AbbVie Inc. Profile
- **10 sources** covering DEI posture
- **Multiple commitments** including CEO Action pledge
- **Health Care industry** focus

## Technical Notes

### Database Platform
- **Supabase** (PostgreSQL-based)
- Real-time capabilities available
- Built-in authentication
- Row-level security ready

### Schema Design
- **Normalized structure** (minimal redundancy)
- **UUID primary keys** (globally unique)
- **Foreign key relationships** (referential integrity)
- **Timestamp tracking** (created_at, updated_at)

### Data Types
- **UUIDs** for IDs
- **Strings** for text fields
- **Arrays** for multi-value fields (quotes, provenance_ids)
- **Timestamps** with timezone
- **Integers** for counts and scores

## Recommended Indexes

For optimal query performance:

```sql
-- Frequently filtered fields
CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_industry ON companies(industry);

-- Foreign key relationships
CREATE INDEX idx_profiles_company_id ON profiles(company_id);
CREATE INDEX idx_sources_profile_id ON data_sources(profile_id);
CREATE INDEX idx_commitments_profile_id ON commitments(profile_id);

-- Status and type filtering
CREATE INDEX idx_commitments_status ON commitments(current_status);
CREATE INDEX idx_sources_type ON data_sources(source_type);
```

## Next Steps

1. **API Development**: See `API_ARCHITECTURE.md`
2. **Implementation**: See `IMPLEMENTATION_GUIDE.md`
3. **Data Expansion**: Add more companies and sources
4. **Feature Enhancement**: Add metrics, ratings, trends
5. **Frontend Development**: Build user-facing application

---

**Generated**: November 1, 2025
**Database**: Supabase PostgreSQL
**Tables**: 4
**Total Records**: 651

# Schema Update Proposal: Add AI Analysis Content

## Problem

**Current State**: The `profiles` table only contains metadata (when profile was generated, source count, etc.)

**Missing**: The actual AI-generated DEI analysis content that users need!

When someone queries `/profiles/{id}`, they get:
- ❌ Profile metadata (useless)
- ❌ List of sources (just citations)
- ❌ List of commitments (just pledges)

But they DON'T get:
- ❌ The actual DEI stance assessment
- ❌ Analysis of leadership
- ❌ Summary of controversies
- ❌ Key findings
- ❌ Overall evaluation

## Solution

Add analysis content fields to the `profiles` table:

### New Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `dei_posture` | TEXT | Full narrative DEI assessment | "Apple maintains a publicly supportive DEI stance..." |
| `dei_posture_summary` | TEXT | Executive summary (2-3 sentences) | "Supportive with active programs but facing scrutiny..." |
| `key_findings` | JSONB | Structured bullet points | `["$200M REJI investment", "Pay equity since 2017", ...]` |
| `leadership_analysis` | TEXT | DEI leadership assessment | "CDO Cynthia Bowman leads diversity efforts..." |
| `reporting_transparency` | TEXT | Transparency assessment | "Apple publishes annual diversity reports..." |
| `controversies_summary` | TEXT | Controversies overview | "2023: $25M DOJ settlement for discrimination..." |
| `overall_assessment` | TEXT | Qualitative evaluation | "Generally supportive with mixed execution..." |
| `stance_direction` | ENUM | Current stance | `'supportive'`, `'neutral'`, `'reducing'`, `'unclear'` |
| `stance_trend` | ENUM | Trend over time | `'increasing'`, `'stable'`, `'decreasing'`, `'mixed'` |

## Proposed Profile Response Structure

### Current (Bad):
```json
{
  "id": "...",
  "company_id": "...",
  "generated_at": "...",
  "source_count": 13
}
```
→ **Useless!** Just metadata.

### Proposed (Good):
```json
{
  "id": "...",
  "company": {
    "name": "Apple Inc.",
    "ticker": "AAPL",
    "industry": "Information Technology"
  },

  "analysis": {
    "summary": "Apple maintains publicly supportive DEI stance with active programs but faces ongoing scrutiny...",

    "stance": {
      "direction": "supportive",
      "trend": "stable"
    },

    "key_findings": [
      "$200M+ Racial Equity and Justice Initiative (REJI)",
      "Gender pay equity achieved and maintained since 2017",
      "81+ Diversity Network Associations with 60K+ members",
      "2023: $25M DOJ settlement for citizenship discrimination"
    ],

    "assessment": {
      "posture": "Apple publicly champions diversity and inclusion... [full narrative]",
      "leadership": "CDO Cynthia Bowman (since 2024) leads diversity efforts...",
      "transparency": "Publishes annual diversity reports with demographic breakdowns...",
      "controversies": "2023 DOJ settlement for $25M over citizenship-based hiring discrimination..."
    }
  },

  "commitments": [
    {
      "name": "Racial Equity and Justice Initiative",
      "status": "active",
      "quotes": ["..."]
    }
  ],

  "sources": [
    {
      "title": "Inclusion & Diversity - Apple",
      "type": "corporate_website",
      "reliability": 5,
      "url": "..."
    }
  ],

  "metadata": {
    "generated_at": "2025-11-01T20:44:40Z",
    "research_period": "2020-2025",
    "source_count": 13,
    "is_latest": true
  }
}
```

## User Flow

### What Users Want:

1. **GET /profiles/{id}** → Start with **AI ANALYSIS**
   - Summary (2-3 sentences)
   - Key findings (bullets)
   - Stance direction & trend
   - Full narrative assessment

2. **Drill down** → Specific commitments
   - What pledges they made
   - Which ones are active vs discontinued
   - Quotes from companies

3. **Verify** → Sources
   - Where did this info come from?
   - How reliable are the sources?
   - Links to original documents

### What They DON'T Want:

❌ "This profile has 13 sources and was generated on Nov 1"
→ Who cares! Show me the analysis!

## Implementation Steps

### 1. Update Database Schema
```sql
ALTER TABLE profiles ADD COLUMN dei_posture TEXT;
ALTER TABLE profiles ADD COLUMN dei_posture_summary TEXT;
ALTER TABLE profiles ADD COLUMN key_findings JSONB;
ALTER TABLE profiles ADD COLUMN leadership_analysis TEXT;
ALTER TABLE profiles ADD COLUMN reporting_transparency TEXT;
ALTER TABLE profiles ADD COLUMN controversies_summary TEXT;
ALTER TABLE profiles ADD COLUMN overall_assessment TEXT;
ALTER TABLE profiles ADD COLUMN stance_direction TEXT;
ALTER TABLE profiles ADD COLUMN stance_trend TEXT;
```

### 2. Update API Response Schema

**NEW**: `schemas/analysis.py`
```python
class DEIAnalysis(BaseModel):
    summary: str  # Executive summary
    posture: str  # Full assessment
    key_findings: List[str]  # Bullet points
    leadership: Optional[str]
    transparency: Optional[str]
    controversies: Optional[str]
    stance_direction: str  # supportive/neutral/reducing/unclear
    stance_trend: str  # increasing/stable/decreasing/mixed

class ProfileResponseEnhanced(BaseModel):
    id: str
    company: CompanyBasic
    analysis: DEIAnalysis  # ← THE ACTUAL CONTENT
    commitments: List[CommitmentSummary]
    sources: List[SourceSummary]
    metadata: ProfileMetadata
```

### 3. Update Router

**`routers/profiles.py`** - Return analysis first:
```python
@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    # Get profile with analysis
    profile = get_profile_with_analysis(profile_id)

    return {
        "data": {
            "id": profile.id,
            "company": {...},
            "analysis": {  # ← LEAD WITH THIS
                "summary": profile.dei_posture_summary,
                "key_findings": profile.key_findings,
                "stance": {
                    "direction": profile.stance_direction,
                    "trend": profile.stance_trend
                },
                "assessment": {
                    "posture": profile.dei_posture,
                    "leadership": profile.leadership_analysis,
                    "transparency": profile.reporting_transparency,
                    "controversies": profile.controversies_summary
                }
            },
            "commitments": [...],  # Drill down
            "sources": [...],      # Evidence
            "metadata": {...}      # Last
        }
    }
```

## Migration Plan

### Option A: Add Fields Now (Recommended)
1. Run SQL to add columns
2. Populate with AI-generated analysis for existing profiles
3. Update API to return new structure
4. Deprecate old metadata-only endpoint

### Option B: New Table
Create `profile_analysis` table:
- One-to-one with profiles
- All analysis fields
- Cleaner separation

## Benefits

✅ **Useful responses** - Get actual analysis, not metadata
✅ **Better UX** - Lead with insights, drill to details
✅ **Clearer value** - Immediately see DEI assessment
✅ **Structured data** - Machine-readable stance/trend
✅ **Flexibility** - Can add more analysis types later

## Example Use Case

**Investor researching Apple:**

```bash
GET /profiles/{apple_profile_id}
```

**Current Response** (Bad):
```json
{
  "id": "...",
  "generated_at": "...",
  "source_count": 13
}
```
→ Investor: "OK... so what's their DEI stance?" 🤷

**New Response** (Good):
```json
{
  "company": {"name": "Apple Inc.", "ticker": "AAPL"},
  "analysis": {
    "summary": "Apple maintains supportive stance with $200M+ REJI investment but faced $25M DOJ discrimination settlement in 2023.",
    "stance": {"direction": "supportive", "trend": "stable"},
    "key_findings": [
      "$200M+ Racial Equity and Justice Initiative",
      "Gender pay equity since 2017",
      "$25M DOJ settlement (2023)"
    ]
  }
}
```
→ Investor: "Perfect! They're supportive but have compliance issues." ✅

## Decision Needed

**Should we:**
1. ✅ Add analysis fields to `profiles` table (simpler)
2. ⚠️ Create separate `profile_analysis` table (cleaner but more complex)

**And should we:**
1. ✅ Make analysis the default response (always included)
2. ⚠️ Make it opt-in with `?include=analysis` (more requests)

## Recommendation

**Add fields to `profiles` table + always return analysis by default.**

Why?
- Simpler implementation
- Analysis IS the profile (not optional metadata)
- One less table to join
- Faster queries
- User gets what they actually want without extra params

---

**Ready to implement?** Let me know and I'll:
1. Run the SQL migration
2. Update the schemas
3. Restructure the profile response
4. Update Postman collection

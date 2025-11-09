#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

print("Finding ALL tables in the database...")
print("=" * 80)

# Try to query information_schema through PostgREST
# Supabase exposes pg_catalog views

# Method 1: Try common table names
common_table_prefixes = ['', 'dei_', 'company_', 'profile_', 'ai_', 'analysis_', 'assessment_']
common_table_names = [
    'companies', 'profiles', 'data_sources', 'commitments',
    'sources', 'insights', 'analysis', 'assessments', 'stances',
    'postures', 'findings', 'narratives', 'summaries', 'reports',
    'evaluations', 'measurements', 'metrics', 'indicators',
    'dei_profiles', 'dei_analysis', 'dei_assessments', 'dei_stances',
    'profile_analysis', 'profile_content', 'profile_insights',
    'ai_analysis', 'ai_insights', 'ai_content', 'ai_assessments',
    'company_analysis', 'company_insights', 'company_assessments'
]

# Build exhaustive list
all_possible_names = set(common_table_names)
for prefix in common_table_prefixes:
    for name in common_table_names:
        all_possible_names.add(f"{prefix}{name}")

print(f"Checking {len(all_possible_names)} potential table names...")
print()

found_tables = []

for table_name in sorted(all_possible_names):
    try:
        result = supabase.table(table_name).select('*', count='exact').limit(0).execute()
        found_tables.append({
            'name': table_name,
            'count': result.count
        })
        print(f"✓ {table_name:<40} ({result.count} rows)")
    except Exception:
        pass

print("\n" + "=" * 80)
print(f"FOUND {len(found_tables)} TABLES")
print("=" * 80)

for table in found_tables:
    print(f"  {table['name']:<40} {table['count']:>6} rows")

# Now get the schema for each found table
print("\n" + "=" * 80)
print("DETAILED SCHEMA FOR EACH TABLE")
print("=" * 80)

for table_info in found_tables:
    table_name = table_info['name']
    print(f"\n{table_name.upper()}")
    print("-" * 80)

    try:
        result = supabase.table(table_name).select('*').limit(1).execute()

        if result.data:
            fields = list(result.data[0].keys())
            print(f"Fields ({len(fields)}): {', '.join(fields)}")

            # Show any text/jsonb fields with content
            for field in fields:
                value = result.data[0][field]
                if isinstance(value, str) and len(value) > 50:
                    print(f"\n  {field} (TEXT, {len(value)} chars):")
                    print(f"    {value[:200]}...")
                elif isinstance(value, (dict, list)):
                    print(f"\n  {field} (JSONB):")
                    print(f"    {json.dumps(value, indent=4)[:300]}...")
        else:
            print("  (empty table)")

    except Exception as e:
        print(f"  Error reading table: {e}")

print("\n" + "=" * 80)
print("COMPLETE!")
print("=" * 80)

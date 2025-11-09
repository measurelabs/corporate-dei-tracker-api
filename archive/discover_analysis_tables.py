#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Try to find tables with analysis/assessment content
potential_tables = [
    'profiles', 'companies', 'data_sources', 'commitments',
    'analysis', 'assessments', 'stances', 'posture', 'dei_analysis',
    'insights', 'findings', 'summary', 'evaluation', 'report',
    'content', 'narrative', 'overview'
]

print("Searching for tables with AI analysis content...")
print("=" * 80)

found_tables = []
for table_name in potential_tables:
    try:
        result = supabase.table(table_name).select('*', count='exact').limit(1).execute()
        found_tables.append(table_name)
        print(f"✓ Found: {table_name} ({result.count} rows)")

        if result.data:
            print(f"  Sample columns: {list(result.data[0].keys())}")
    except Exception:
        pass

print(f"\n{'=' * 80}")
print(f"Total tables found: {len(found_tables)}")
print(f"Tables: {', '.join(found_tables)}")

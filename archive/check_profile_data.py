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

# Get a full profile with all fields
result = supabase.table('profiles').select('*').limit(1).execute()

if result.data:
    profile = result.data[0]
    print("Profile Fields:")
    print("=" * 80)
    for key, value in profile.items():
        if isinstance(value, str) and len(value) > 200:
            print(f"{key}: {value[:200]}...")
        else:
            print(f"{key}: {value}")

    print("\n" + "=" * 80)
    print("\nChecking for AI analysis content...")
    print("=" * 80)

    # Check if there are other tables with analysis
    print("\nAll table names:")
    tables = ['profiles', 'companies', 'data_sources', 'commitments']
    for table in tables:
        count = supabase.table(table).select('*', count='exact').limit(0).execute()
        print(f"  {table}: {count.count} rows")

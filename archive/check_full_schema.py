#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Try direct PostgreSQL connection to see full schema
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("Checking profiles table for all columns...")
    print("=" * 80)

    cur.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'profiles'
        ORDER BY ordinal_position;
    """)

    columns = cur.fetchall()
    for col in columns:
        print(f"{col['column_name']:<30} {col['data_type']:<20} {col.get('character_maximum_length', '')}")

    print("\n" + "=" * 80)
    print("Checking for JSONB or TEXT columns that might contain analysis...")
    print("=" * 80)

    cur.execute("""
        SELECT *
        FROM profiles
        LIMIT 1;
    """)

    row = cur.fetchone()
    if row:
        for key, value in row.items():
            if value and isinstance(value, str) and len(value) > 100:
                print(f"\n{key}:")
                print(f"  Type: {type(value)}")
                print(f"  Length: {len(value)} chars")
                print(f"  Preview: {value[:300]}...")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Direct connection failed: {e}")
    print("\nFalling back to Supabase client...")

    from supabase import create_client
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )

    # Check if there are any text/jsonb fields we're missing
    result = supabase.table('profiles').select('*').limit(1).execute()
    if result.data:
        print("\nAll profile fields:")
        for key in result.data[0].keys():
            print(f"  - {key}")

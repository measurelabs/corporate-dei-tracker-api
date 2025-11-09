#!/usr/bin/env python3
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def inspect_supabase():
    """Connect to Supabase and inspect all tables"""
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        print("=" * 80)
        print("SUPABASE DATABASE INSPECTION")
        print("=" * 80)

        # Use PostgREST API to get schema information
        # Query the information_schema to get all tables
        result = supabase.rpc('get_table_info').execute()

        # If that doesn't work, try getting tables directly
        # Let's try a different approach - use the REST API to list tables

        # First, let's see what tables we can access by trying common table names
        # and checking for errors

        print("\nAttempting to discover tables...\n")

        # Try to query pg_catalog to get table names using SQL
        response = supabase.table('pg_tables').select('*').limit(5).execute()

        print("Response:", response)

    except Exception as e:
        print(f"Error with RPC approach: {e}")
        print("\nTrying alternative approach using raw SQL query...")

        try:
            # Use the Supabase client to execute raw SQL
            # This requires using the PostgREST RPC function

            # Let's try accessing common tables that might exist
            print("\nSearching for tables by trying common names...\n")

            # Common table names for a DEI tracking app
            potential_tables = [
                'companies',
                'company',
                'organizations',
                'organization',
                'dei_metrics',
                'metrics',
                'diversity_data',
                'employees',
                'reports',
                'stances',
                'dei_stances',
                'policies',
                'initiatives',
                'demographics',
                'ratings',
                'reviews'
            ]

            found_tables = []

            for table_name in potential_tables:
                try:
                    result = supabase.table(table_name).select('*', count='exact').limit(0).execute()
                    found_tables.append({
                        'name': table_name,
                        'count': result.count
                    })
                    print(f"✓ Found table: {table_name} ({result.count} rows)")
                except Exception as e:
                    # Table doesn't exist or we don't have access
                    pass

            print(f"\n{'=' * 80}")
            print(f"Found {len(found_tables)} accessible tables")
            print('=' * 80)

            # Now get detailed info for each found table
            for table_info in found_tables:
                table_name = table_info['name']
                print(f"\n{'=' * 80}")
                print(f"TABLE: {table_name}")
                print('=' * 80)
                print(f"Total rows: {table_info['count']}")

                # Get sample data
                try:
                    result = supabase.table(table_name).select('*').limit(3).execute()
                    data = result.data

                    if data:
                        print(f"\nSample data (up to 3 rows):")
                        print("-" * 80)

                        # Get column names from first row
                        if len(data) > 0:
                            columns = list(data[0].keys())
                            print(f"\nColumns: {', '.join(columns)}\n")

                            for i, row in enumerate(data, 1):
                                print(f"Row {i}:")
                                for key, value in row.items():
                                    # Truncate long values
                                    str_value = str(value)
                                    if len(str_value) > 100:
                                        str_value = str_value[:97] + "..."
                                    print(f"  {key}: {str_value}")
                                print()
                    else:
                        print("\nNo data in this table")

                except Exception as e:
                    print(f"Error fetching data: {e}")

            if not found_tables:
                print("\n⚠️  No tables found. The database might be empty or table names are different.")
                print("You may need to create tables first or check your database permissions.")

        except Exception as e2:
            print(f"Error: {e2}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    inspect_supabase()

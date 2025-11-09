#!/usr/bin/env python3
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def discover_all_tables():
    """Systematically discover all tables in Supabase"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        print("=" * 80)
        print("COMPREHENSIVE TABLE DISCOVERY")
        print("=" * 80)

        # Expanded list of potential table names
        potential_tables = [
            # Company related
            'companies', 'company', 'organizations', 'organization', 'firms', 'corporations',

            # DEI metrics and data
            'dei_metrics', 'metrics', 'diversity_data', 'dei_data', 'dei_scores',
            'diversity_metrics', 'inclusion_metrics', 'equity_metrics',
            'stances', 'dei_stances', 'positions', 'statements',

            # Employee/demographic data
            'employees', 'workforce', 'demographics', 'workforce_demographics',
            'employee_demographics', 'diversity_breakdown',

            # Reports and disclosures
            'reports', 'disclosures', 'dei_reports', 'eeo_reports', 'esg_reports',
            'annual_reports', 'diversity_reports',

            # Policies and initiatives
            'policies', 'dei_policies', 'initiatives', 'programs', 'dei_initiatives',
            'diversity_initiatives', 'inclusion_programs',

            # Ratings and assessments
            'ratings', 'scores', 'assessments', 'evaluations', 'rankings',
            'dei_ratings', 'diversity_scores',

            # Reviews and feedback
            'reviews', 'feedback', 'comments', 'notes',

            # Leadership and governance
            'leadership', 'executives', 'board', 'board_members', 'directors',
            'board_diversity', 'leadership_diversity',

            # Data sources
            'sources', 'data_sources', 'citations', 'references',

            # Categories and classifications
            'categories', 'tags', 'labels', 'types',

            # Time-series data
            'history', 'historical_data', 'trends', 'time_series',

            # User/auth related
            'users', 'profiles', 'accounts', 'auth_users',

            # Measurements and indicators
            'indicators', 'measures', 'kpis', 'benchmarks',

            # Actions and commitments
            'commitments', 'pledges', 'actions', 'goals', 'targets',

            # External data
            'news', 'articles', 'press_releases', 'announcements'
        ]

        found_tables = []

        print(f"\nScanning {len(potential_tables)} potential table names...\n")

        for table_name in potential_tables:
            try:
                result = supabase.table(table_name).select('*', count='exact').limit(0).execute()
                found_tables.append({
                    'name': table_name,
                    'count': result.count
                })
                print(f"✓ Found: {table_name:<30} ({result.count} rows)")
            except Exception:
                # Table doesn't exist or we don't have access
                pass

        print(f"\n{'=' * 80}")
        print(f"DISCOVERED {len(found_tables)} TABLES")
        print('=' * 80)

        # Display full schema for each table
        for table_info in found_tables:
            table_name = table_info['name']
            print(f"\n{'=' * 80}")
            print(f"TABLE: {table_name}")
            print('=' * 80)
            print(f"Total rows: {table_info['count']}")

            # Get sample data to understand schema
            try:
                result = supabase.table(table_name).select('*').limit(5).execute()
                data = result.data

                if data and len(data) > 0:
                    # Display schema
                    print(f"\nSchema:")
                    print("-" * 80)
                    first_row = data[0]
                    for key, value in first_row.items():
                        value_type = type(value).__name__
                        sample_val = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"  {key:<30} {value_type:<15} Example: {sample_val}")

                    # Display sample rows
                    print(f"\nSample rows ({min(5, len(data))} of {table_info['count']}):")
                    print("-" * 80)
                    for i, row in enumerate(data, 1):
                        print(f"\nRow {i}:")
                        for key, value in row.items():
                            str_value = str(value)
                            if len(str_value) > 100:
                                str_value = str_value[:97] + "..."
                            print(f"  {key}: {str_value}")
                else:
                    print("\nTable is empty")

            except Exception as e:
                print(f"Error inspecting table: {e}")

        # Summary
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print('=' * 80)
        print(f"\nTotal tables found: {len(found_tables)}")
        print(f"\nTables by row count:")
        sorted_tables = sorted(found_tables, key=lambda x: x['count'], reverse=True)
        for table in sorted_tables:
            print(f"  {table['name']:<30} {table['count']:>6} rows")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    discover_all_tables()

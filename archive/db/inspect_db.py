#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def inspect_database():
    """Connect to database and inspect all tables"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        print("=" * 80)
        print("DATABASE SCHEMA INSPECTION")
        print("=" * 80)

        # Get all tables in public schema
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()

        print(f"\nFound {len(tables)} tables in public schema:\n")

        for table_row in tables:
            table_name = table_row['table_name']
            print(f"\n{'=' * 80}")
            print(f"TABLE: {table_name}")
            print('=' * 80)

            # Get columns for this table
            cur.execute("""
                SELECT
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            columns = cur.fetchall()

            print(f"\nColumns ({len(columns)}):")
            print("-" * 80)
            for col in columns:
                max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  {col['column_name']:<30} {col['data_type']}{max_len:<20} {nullable:<10} {default}")

            # Get row count
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name};")
            count = cur.fetchone()['count']
            print(f"\nRow count: {count}")

            # Show sample data if available
            if count > 0:
                cur.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                samples = cur.fetchall()
                print(f"\nSample data (up to 3 rows):")
                print("-" * 80)
                for i, row in enumerate(samples, 1):
                    print(f"\nRow {i}:")
                    for key, value in row.items():
                        # Truncate long values
                        str_value = str(value)
                        if len(str_value) > 100:
                            str_value = str_value[:97] + "..."
                        print(f"  {key}: {str_value}")

            # Get foreign key constraints
            cur.execute("""
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND tc.table_name = %s;
            """, (table_name,))

            fks = cur.fetchall()
            if fks:
                print(f"\nForeign Keys:")
                print("-" * 80)
                for fk in fks:
                    print(f"  {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")

        cur.close()
        conn.close()

        print("\n" + "=" * 80)
        print("INSPECTION COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_database()
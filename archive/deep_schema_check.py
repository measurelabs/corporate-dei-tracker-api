#!/usr/bin/env python3
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

print("Deep search for AI fields across all tables...")
print("=" * 80)

tables = ['profiles', 'companies', 'data_sources', 'commitments']

for table_name in tables:
    print(f"\n{table_name.upper()}")
    print("-" * 80)

    try:
        # Get first row
        result = supabase.table(table_name).select('*').limit(1).execute()

        if result.data:
            all_fields = list(result.data[0].keys())

            # Look for AI-related fields
            ai_fields = [f for f in all_fields if any(keyword in f.lower() for keyword in ['ai', 'insight', 'analysis', 'context', 'assessment', 'finding', 'posture', 'narrative'])]

            print(f"Total fields: {len(all_fields)}")
            print(f"All fields: {', '.join(all_fields)}")

            if ai_fields:
                print(f"\n✓ AI-related fields found: {ai_fields}")

                for field in ai_fields:
                    value = result.data[0][field]
                    if value:
                        print(f"\n  {field}:")
                        if isinstance(value, str):
                            print(f"    Type: string ({len(value)} chars)")
                            print(f"    Preview: {value[:200]}")
                        else:
                            print(f"    Value: {value}")
            else:
                print("  ❌ No AI-related fields")

    except Exception as e:
        print(f"  Error: {e}")

# Try explicitly selecting ai_context and ai_key_insights
print("\n" + "=" * 80)
print("Trying to explicitly select ai_context and ai_key_insights...")
print("=" * 80)

try:
    result = supabase.table('profiles').select('ai_context, ai_key_insights').limit(1).execute()
    print(f"✓ Success! Found fields:")
    print(result.data)
except Exception as e:
    print(f"❌ Error: {e}")

# Try selecting everything with rpc
print("\n" + "=" * 80)
print("Checking if there's a view or different schema...")
print("=" * 80)

# List all possible field names
possible_ai_fields = [
    'ai_context', 'ai_key_insights', 'ai_analysis', 'ai_summary',
    'context', 'key_insights', 'insights', 'analysis', 'assessment',
    'dei_analysis', 'dei_context', 'dei_insights', 'dei_assessment',
    'narrative', 'posture', 'findings', 'summary'
]

for field_name in possible_ai_fields:
    try:
        result = supabase.table('profiles').select(field_name).limit(1).execute()
        if result.data and result.data[0].get(field_name) is not None:
            print(f"✓ Found: {field_name}")
            value = result.data[0][field_name]
            if isinstance(value, str):
                print(f"  Preview: {value[:150]}")
    except:
        pass

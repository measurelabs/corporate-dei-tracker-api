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

print("Fetching actual profile schema from database...")
print("=" * 80)

# Get a profile with ALL fields using select *
result = supabase.table('profiles').select('*').limit(1).execute()

if result.data:
    profile = result.data[0]

    print(f"\nAll fields in profiles table ({len(profile)} fields):")
    print("=" * 80)

    for key, value in sorted(profile.items()):
        value_type = type(value).__name__

        if value is None:
            print(f"{key:<40} {value_type:<15} NULL")
        elif isinstance(value, str):
            preview = value[:100] + "..." if len(value) > 100 else value
            print(f"{key:<40} {value_type:<15} {len(value)} chars - {preview}")
        elif isinstance(value, (list, dict)):
            print(f"{key:<40} {value_type:<15} {json.dumps(value)[:100]}")
        else:
            print(f"{key:<40} {value_type:<15} {value}")

    # Check if ai_context or ai_key_insights exist
    print("\n" + "=" * 80)
    print("Checking for AI fields...")
    print("=" * 80)

    ai_fields = [k for k in profile.keys() if 'ai' in k.lower() or 'insight' in k.lower() or 'analysis' in k.lower() or 'context' in k.lower()]

    if ai_fields:
        print(f"\nFound AI-related fields: {ai_fields}")
        for field in ai_fields:
            value = profile[field]
            print(f"\n{field}:")
            if isinstance(value, str):
                print(f"  Length: {len(value)} characters")
                print(f"  Content: {value[:500]}")
            else:
                print(f"  Value: {value}")
    else:
        print("\n⚠️  No AI-related fields found!")

# Also check what we're actually selecting in the API
print("\n" + "=" * 80)
print("Full profile data structure:")
print("=" * 80)
print(json.dumps(profile, indent=2, default=str))

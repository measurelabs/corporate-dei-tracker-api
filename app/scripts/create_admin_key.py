#!/usr/bin/env python3
"""
Bootstrap script to create an initial admin API key.

This script creates the first admin API key that can be used to create other API keys.
Run this script once during initial setup.

Usage:
    python -m app.scripts.create_admin_key --name "Initial Admin Key"
"""
import argparse
import sys
from datetime import datetime
from app.database import get_db
from app.middleware.auth import generate_api_key, hash_api_key


def create_admin_key(name: str = "Initial Admin Key", expires_at: str = None):
    """
    Create an initial admin API key.

    Args:
        name: Descriptive name for the API key
        expires_at: Optional expiration date (ISO format)
    """
    db = get_db()

    # Generate a new admin key
    admin_key = generate_api_key()
    key_hash = hash_api_key(admin_key)
    key_prefix = admin_key[:8]

    try:
        # Check if any admin keys already exist
        existing = db.table("api_keys").select("id").eq("is_admin", True).execute()

        if existing.data and len(existing.data) > 0:
            print("⚠️  Warning: Admin API keys already exist in the database.")
            response = input("Do you want to create another admin key? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted.")
                return

        # Insert the admin key
        response = db.table("api_keys").insert({
            "name": name,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "is_admin": True,
            "is_active": True,
            "expires_at": expires_at,
            "metadata": {"created_by_script": True}
        }).execute()

        if not response.data or len(response.data) == 0:
            print("❌ Failed to create admin API key")
            sys.exit(1)

        created_key = response.data[0]

        # Display the key information
        print("\n" + "="*70)
        print("✅ ADMIN API KEY CREATED SUCCESSFULLY")
        print("="*70)
        print(f"\nKey ID:      {created_key['id']}")
        print(f"Name:        {created_key['name']}")
        print(f"Created:     {created_key['created_at']}")
        print(f"Expires:     {created_key.get('expires_at', 'Never')}")
        print("\n" + "-"*70)
        print("API KEY (save this - it will not be shown again):")
        print("-"*70)
        print(f"\n{admin_key}\n")
        print("-"*70)
        print("\n⚠️  IMPORTANT:")
        print("   - Save this API key in a secure location")
        print("   - It will NOT be shown again")
        print("   - Use it in the 'X-API-Key' header for API requests")
        print("   - This key can create and manage other API keys")
        print("="*70 + "\n")

        # Save to .env reminder
        print("💡 To use this key, add it to your .env file or use it directly:")
        print(f"   X-API-Key: {admin_key}")
        print()

    except Exception as e:
        print(f"❌ Error creating admin API key: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Create an initial admin API key for the DEI Tracker API"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="Initial Admin Key",
        help="Descriptive name for the API key"
    )
    parser.add_argument(
        "--expires",
        type=str,
        default=None,
        help="Expiration date in ISO format (e.g., 2024-12-31T23:59:59Z)"
    )

    args = parser.parse_args()

    print("\n🔑 Creating Admin API Key...")
    print(f"Name: {args.name}")
    if args.expires:
        print(f"Expires: {args.expires}")
    else:
        print("Expires: Never")
    print()

    create_admin_key(name=args.name, expires_at=args.expires)


if __name__ == "__main__":
    main()

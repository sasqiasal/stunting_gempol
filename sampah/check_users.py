#!/usr/bin/env python3
"""
Check existing users in the database
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Checking users in database...\n")

try:
    response = supabase.table("users").select("id, email, role, is_active").execute()
    
    if response.data:
        print(f"Found {len(response.data)} users:\n")
        for user in response.data:
            print(f"  ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
            print(f"  Active: {user['is_active']}")
            print()
    else:
        print("❌ No users found in database. You need to create one first.")
        print("\nYou can register a user via the /auth/register endpoint or add one manually.")
        
except Exception as e:
    print(f"❌ Error: {e}")

#!/usr/bin/env python3
"""
Test koneksi ke Supabase database
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

print("🔄 Testing Supabase connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:10]}...")

try:
    # Create client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Test connection dengan query sederhana
    response = supabase.table("users").select("count", count="exact").execute()

    print("✅ Connection successful!")
    print(f"Users table accessible. Total users: {response.count}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)
#!/usr/bin/env python3
"""
Test menggunakan Supabase Auth untuk login
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")  # PUBLIC KEY

print("=" * 80)
print("TESTING SUPABASE AUTH LOGIN")
print("=" * 80)

# Create client dengan PUBLIC KEY
client: Client = create_client(supabase_url, supabase_key)

# Test login dengan Supabase Auth
test_cases = [
    ("admin@gempol.id", "admin123"),
    ("kaderceria@gempol.id", "KADER123"),
    ("kader@gempol.id", "kader123"),
]

for email, password in test_cases:
    try:
        print(f"\n🔓 Testing: {email} / {password}")
        
        # Try Supabase Auth login
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            print(f"   ✅ AUTH SUCCESS!")
            print(f"   User ID: {response.user.id}")
            print(f"   Email: {response.user.email}")
        else:
            print(f"   ❌ Auth failed (no user)")
            
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg or "400" in error_msg:
            print(f"   ❌ Auth FAILED: Invalid credentials")
        else:
            print(f"   ❌ Error: {error_msg}")

print("\n" + "=" * 80)
print("NOTE: If auth works here, use Supabase Auth in your API!")
print("=" * 80)

#!/usr/bin/env python3
"""
Reset semua user passwords ke default yang sama
"""

import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from supabase import create_client

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Default password untuk semua user
DEFAULT_PASSWORD = "Password123!"  # CHANGE THIS!
hashed = pwd_context.hash(DEFAULT_PASSWORD)

print("=" * 70)
print(f"RESET ALL USERS PASSWORD TO: {DEFAULT_PASSWORD}")
print(f"HASHED: {hashed}")
print("=" * 70)

# Get all users
users_response = supabase.table("users").select("id, email").execute()

if users_response.data:
    print(f"\n📋 Found {len(users_response.data)} users\n")
    
    for user in users_response.data:
        user_id = user['id']
        email = user['email']
        
        try:
            # Update password
            response = supabase.table("users").update({
                "hashed_password": hashed
            }).eq("id", user_id).execute()
            
            if response.data:
                print(f"✅ {email}")
            else:
                print(f"❌ {email} - Update failed")
                
        except Exception as e:
            print(f"❌ {email} - Error: {e}")
    
    print(f"\n{'=' * 70}")
    print(f"✅ All users password reset to: {DEFAULT_PASSWORD}")
    print(f"{'=' * 70}")
else:
    print("No users found!")

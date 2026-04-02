#!/usr/bin/env python3
"""
Debug script - Cek status user di database dengan detail
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 70)
print("CHECKING USERS TABLE")
print("=" * 70)

# Ambil semua users
try:
    response = supabase.table("users").select("*").execute()
    
    if response.data:
        print(f"\n✅ Found {len(response.data)} user(s):\n")
        
        for user in response.data:
            print(f"📋 Email: {user.get('email')}")
            print(f"   ID: {user.get('id')}")
            print(f"   Role: {user.get('role')}")
            print(f"   Is Active: {user.get('is_active')}")
            
            hash_val = user.get('hashed_password')
            if hash_val:
                print(f"   Password Hash: {hash_val[:30]}...")
            else:
                print(f"   ❌ Password Hash: NONE/NULL")
            print()
    else:
        print("❌ No users found in database!")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Specific check for admin@gempol.id
print("=" * 70)
print("CHECKING admin@gempol.id SPECIFICALLY")
print("=" * 70)

try:
    response = supabase.table("users").select("*").eq("email", "admin@gempol.id").execute()
    
    if response.data:
        user = response.data[0]
        print(f"\n✅ Admin user FOUND")
        print(f"   Email: {user.get('email')}")
        print(f"   ID: {user.get('id')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Is Active: {user.get('is_active')}")
        
        hash_val = user.get('hashed_password')
        if hash_val:
            print(f"   Password Hash: {hash_val}")
            
            # Test verify
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            test_passwords = ["admin123", "password", "admin"]
            print(f"\n   Testing passwords:")
            for pwd in test_passwords:
                try:
                    match = pwd_context.verify(pwd, hash_val)
                    status = "✅ MATCH" if match else "❌ NO MATCH"
                    print(f"   - '{pwd}': {status}")
                except Exception as e:
                    print(f"   - '{pwd}': Error - {e}")
        else:
            print(f"   ❌ Password Hash: NONE/NULL (This is the problem!)")
    else:
        print(f"❌ Admin user NOT FOUND (admin@gempol.id)")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)

#!/usr/bin/env python3
"""
Test script untuk debug login flow step by step
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

print("=" * 60)
print("LOGIN TROUBLESHOOTING CHECKLIST")
print("=" * 60)

# 1. Check Environment Variables
print("\n1️⃣  CHECKING ENVIRONMENT VARIABLES...")
print("-" * 60)

REQUIRED_VARS = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "SUPABASE_SERVICE_KEY",
    "SECRET_KEY",
    "DATABASE_URL"
]

missing_vars = []
for var in REQUIRED_VARS:
    value = os.getenv(var)
    if value:
        # Show only first 20 chars for security
        masked = value[:20] + "..." if len(value) > 20 else value
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: MISSING!")
        missing_vars.append(var)

if missing_vars:
    print(f"\n❌ ERROR: Missing variables: {', '.join(missing_vars)}")
    print("⚠️  These must be set as Environment Variables in Vercel!")
    sys.exit(1)

# 2. Test Database Connection
print("\n2️⃣  TESTING DATABASE CONNECTION...")
print("-" * 60)

try:
    from supabase import create_client, Client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase: Client = create_client(supabase_url, supabase_service_key)
    
    # Try to fetch users table
    response = supabase.table("users").select("id, email").limit(1).execute()
    
    print(f"✅ Database connection successful!")
    print(f"   Users found: {len(response.data) if response.data else 0}")
    
except Exception as e:
    print(f"❌ Database connection failed: {str(e)}")
    sys.exit(1)

# 3. Check admin user exists
print("\n3️⃣  CHECKING ADMIN USER...")
print("-" * 60)

try:
    admin_response = supabase.table("users").select("*").eq("email", "admin@gempol.id").execute()
    
    if admin_response.data:
        user = admin_response.data[0]
        print(f"✅ Admin user found!")
        print(f"   Email: {user.get('email')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Is Active: {user.get('is_active')}")
        
        # Check if password hash exists
        if user.get('hashed_password'):
            hash_preview = user.get('hashed_password')[:20] + "..."
            print(f"   Password Hash: {hash_preview}")
        else:
            print(f"   ❌ Password Hash: MISSING! (This is the problem)")
    else:
        print(f"❌ Admin user NOT found (admin@gempol.id)")
        
except Exception as e:
    print(f"❌ Failed to check user: {str(e)}")
    sys.exit(1)

# 4. Test password verification
print("\n4️⃣  TESTING PASSWORD VERIFICATION...")
print("-" * 60)

try:
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    test_password = "admin123"
    admin_user = admin_response.data[0]
    db_hash = admin_user.get('hashed_password')
    
    if not db_hash:
        print(f"❌ Cannot test: Password hash is missing in database!")
    else:
        is_correct = pwd_context.verify(test_password, db_hash)
        
        if is_correct:
            print(f"✅ Password verification: CORRECT!")
            print(f"   Test password 'admin123' matches the hash in database")
        else:
            print(f"❌ Password verification: FAILED!")
            print(f"   Test password 'admin123' does NOT match the hash in database")
            print(f"   This means the password is wrong or needs to be reset")
            
except Exception as e:
    print(f"❌ Password verification test failed: {str(e)}")
    sys.exit(1)

# 5. Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if not missing_vars:
    print("✅ All checks passed!")
    print("\nIf login is still failing on Vercel:")
    print("1. Make sure User's SUPABASE_SERVICE_KEY is correct (copy from Supabase Dashboard)")
    print("2. Check Vercel deployment logs: https://vercel.com/dashboard/stunting-gempol/logs")
    print("3. Verify database has the user with correct email and password hash")
else:
    print("❌ Fix missing environment variables in Vercel first!")

print("=" * 60)

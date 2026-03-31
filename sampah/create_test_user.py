#!/usr/bin/env python3
"""
Create a test user for authentication testing
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import sys
sys.path.insert(0, "d:\\development\\stunting_gempol\\api")

from app.utils.auth import hash_password

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test credentials
TEST_EMAIL = "testuser@gempol.id"
TEST_PASSWORD = "testpass123"

print(f"Creating test user: {TEST_EMAIL}")
print(f"Password: {TEST_PASSWORD}\n")

try:
    # Check if user already exists
    check = supabase.table("users").select("email").eq("email", TEST_EMAIL).execute()
    
    if check.data:
        print(f"✅ User already exists: {TEST_EMAIL}")
        print("You can use this email to log in with password: testpass123")
    else:
        # Create new user
        hashed_password = hash_password(TEST_PASSWORD)
        
        user_data = {
            "email": TEST_EMAIL,
            "hashed_password": hashed_password,
            "role": "admin",
            "is_active": True,
            "nama_lengkap": "Test User"
        }
        
        response = supabase.table("users").insert(user_data).execute()
        
        if response.data:
            print(f"✅ User created successfully!")
            print(f"Email: {TEST_EMAIL}")
            print(f"Password: {TEST_PASSWORD}")
            print(f"Role: admin")
        else:
            print(f"❌ Failed to create user")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Script untuk reset password user di Supabase
"""

from passlib.context import CryptContext
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Init
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Password yang mau di-set
NEW_PASSWORD = "admin123"  # GANTI SESUAI KEBUTUHAN
EMAIL = "admin@gempol.id"  # GANTI SESUAI KEBUTUHAN

# Hash password
hashed = pwd_context.hash(NEW_PASSWORD)
print(f"Email: {EMAIL}")
print(f"New Password: {NEW_PASSWORD}")
print(f"Hashed: {hashed}")

# Update di database
try:
    response = supabase.table("users").update({
        "hashed_password": hashed
    }).eq("email", EMAIL).execute()
    
    if response.data:
        print(f"✅ Password updated successfully!")
        print(f"User: {response.data[0]['email']}")
    else:
        print("❌ User tidak ditemukan atau error")
        
except Exception as e:
    print(f"❌ Error: {e}")

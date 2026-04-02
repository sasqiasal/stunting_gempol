#!/usr/bin/env python3
"""
Analisa hash algorithm yang digunakan untuk setiap user
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import re

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

print("=" * 80)
print("ANALYZING PASSWORD HASH TYPES")
print("=" * 80)

response = supabase.table("users").select("email, hashed_password").execute()

if response.data:
    for user in response.data:
        email = user['email']
        hash_val = user['hashed_password']
        
        print(f"\n📧 {email}")
        print(f"   Hash: {hash_val[:50]}...")
        
        # Identify hash type by prefix
        if hash_val.startswith('$2a$') or hash_val.startswith('$2b$') or hash_val.startswith('$2y$'):
            print(f"   Type: bcrypt (passlib)")
        elif hash_val.startswith('$argon2'):
            print(f"   Type: Argon2")
        elif hash_val.startswith('$pbkdf2-sha256$'):
            print(f"   Type: PBKDF2-SHA256")
        elif len(hash_val) == 60 and hash_val.startswith('$'):
            print(f"   Type: Unknown bcrypt variant")
        elif len(hash_val) == 64 and all(c in '0123456789abcdef' for c in hash_val):
            print(f"   Type: SHA256 hex")
        else:
            print(f"   Type: UNKNOWN!")
            
print("\n" + "=" * 80)
print("⚠️  Check if hashes start with $2a$, $2b$, $2y$ (bcrypt)")
print("    Or other algorithm signature (argon2, pbkdf2, etc)")
print("=" * 80)

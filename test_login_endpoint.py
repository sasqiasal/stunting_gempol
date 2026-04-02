#!/usr/bin/env python3
"""
Test login endpoint locally
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.routes.auth import login
from app.models.user import UserLogin
from app.database import get_supabase
from fastapi import Depends

print("=" * 80)
print("TESTING LOGIN ENDPOINT")
print("=" * 80)

async def test_login():
    # Test credentials
    test_email = "admin@gempol.id"
    test_password = "admin123"
    
    print(f"\nTesting login for: {test_email} / {test_password}")
    
    try:
        credentials = UserLogin(email=test_email, password=test_password)
        supabase_client = get_supabase()
        
        # Call login function directly
        result = await login(credentials, supabase_client)
        print(f"✅ Login SUCCESS!")
        print(f"   Token: {result['access_token'][:50]}...")
        print(f"   Type: {result['token_type']}")
        print(f"   User: {result['user']['email']}")
        
    except Exception as e:
        print(f"❌ Login FAILED!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_login())

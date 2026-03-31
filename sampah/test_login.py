#!/usr/bin/env python3
"""Test script to check users in database"""
import sys
sys.path.insert(0, '/development/stunting_gempol/backend')

from app.database import get_supabase

try:
    client = get_supabase()
    
    print("=" * 60)
    print("CHECKING USERS IN DATABASE")
    print("=" * 60)
    
    users = client.table('users').select('id, email, role, is_active, hashed_password').execute()
    
    if users.data:
        print(f"\n✅ Found {len(users.data)} user(s):")
        for u in users.data:
            has_pwd = "✅" if u.get('hashed_password') else "❌"
            print(f"  {has_pwd} Email: {u['email']}")
            print(f"     Role: {u['role']}, Active: {u['is_active']}")
            print()
    else:
        print("\n❌ No users found in database!")
        print("\nCreating test users...")
        
        from app.utils.auth import hash_password
        
        test_users = [
            {
                "email": "admin@gempol.id",
                "nama_lengkap": "Admin Gempol",
                "role": "admin",
                "hashed_password": hash_password("admin123"),
                "is_active": True
            },
            {
                "email": "kader@gempol.id",
                "nama_lengkap": "Kader Gempol",
                "role": "kader",
                "hashed_password": hash_password("kader123"),
                "posyandu_id": 1,
                "is_active": True
            }
        ]
        
        for user in test_users:
            result = client.table('users').insert(user).execute()
            if result.data:
                print(f"  ✅ Created: {user['email']}")
            else:
                print(f"  ❌ Failed to create: {user['email']}")
                
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()

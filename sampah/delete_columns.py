import sys
sys.path.insert(0, 'backend')

from app.database import get_supabase

try:
    supabase = get_supabase()
    
    print("⚠️  DELETING COLUMNS FROM TABLE posyandu...")
    print("=" * 70)
    print()
    
    # Drop columns using raw SQL
    # Note: Supabase doesn't directly support DROP COLUMN via SDK,
    # so we need to use PostgreSQL client or admin API
    
    print("❌ Cannot drop columns from Supabase UI directly via SDK")
    print()
    print("Opsi untuk delete:")
    print("1. Gunakan Supabase SQL Editor (direct)")
    print("2. Gunakan psql command")
    print("3. Gunakan admin API")
    print()
    print("SQL yang perlu dijalankan:")
    print("-" * 70)
    print("""
    ALTER TABLE posyandu DROP COLUMN latitude;
    ALTER TABLE posyandu DROP COLUMN longitude;
    ALTER TABLE posyandu DROP COLUMN geom;
    """)
    print("-" * 70)
    print()
    print("📍 Cara paling mudah:")
    print("1. Buka Supabase Dashboard")
    print("2. Navigate ke SQL Editor")
    print("3. Paste SQL di atas")
    print("4. Click 'Run'")
    
except Exception as e:
    print(f"Error: {e}")

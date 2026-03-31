#!/usr/bin/env python
"""
فحص البيانات الفعلية - Check actual pengukuran data to understand why k_comparisons might not be working
"""
import sys
sys.path.insert(0, 'd:\\development\\stunting_gempol\\api')

import os
from dotenv import load_dotenv

# Load env
dotenv_path = 'd:\\development\\stunting_gempol\\.env'
load_dotenv(dotenv_path)

print("[1] Loading environment...")
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("✗ Missing Supabase credentials in .env")
    sys.exit(1)

print(f"✓ Supabase URL: {SUPABASE_URL[:30]}...")

print("\n[2] Creating Supabase client...")
from supabase import create_client
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n[3] Fetching pengukuran data...")
pengukuran_response = supabase_client.table("pengukuran").select("count").execute()
print(f"✓ Pengukuran table size: {len(pengukuran_response.data)} records")

# Get first 5 records to see the structure
print("\n[4] Fetching first 5 pengukuran records...")
try:
    sample_response = supabase_client.table("pengukuran")\
        .select("jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, zscore_tbu, status_gizi")\
        .limit(5)\
        .execute()
   
    if sample_response.data:
        print(f"✓ Found {len(sample_response.data)} sample records")
        for i, record in enumerate(sample_response.data[:3], 1):
            print(f"\nRecord {i}:")
            print(f"  jenis_kelamin={record.get('jenis_kelamin')}, usia_bulan={record.get('usia_bulan')}")
            print(f"  tinggi_badan={record.get('tinggi_badan')}, berat_badan={record.get('berat_badan')}")
            print(f"  zscore_tbu={record.get('zscore_tbu')}, status_gizi={record.get('status_gizi')}")
    else:
        print("✗ No sample records found - pengukuran table might be empty!")
except Exception as e:
    print(f"✗ Error fetching samples: {e}")

# Check if zscore_tbu column has values
print("\n[5] Checking zscore_tbu values...")
try:
    zscore_response = supabase_client.table("pengukuran")\
        .select("zscore_tbu")\
        .not_("zscore_tbu", "is", None)\
        .limit(10)\
        .execute()
    
    if zscore_response.data:
        print(f"✓ Found {len(zscore_response.data)} records with zscore_tbu")
        zscores = [float(r.get('zscore_tbu', 0)) for r in zscore_response.data]
        stunting_count = sum(1 for z in zscores if z < -2.0)
        normal_count = len(zscores) - stunting_count
        print(f"  Stunting (score < -2.0): {stunting_count}")
        print(f"  Normal (score >= -2.0): {normal_count}")
    else:
        print("⚠️  No zscore_tbu values found")
except Exception as e:
    print(f"✗ Error checking zscore: {e}")

print("\n[Done]")

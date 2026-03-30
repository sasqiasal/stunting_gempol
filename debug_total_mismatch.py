"""
Script untuk debug mengapa total admin evaluation tidak selaras dengan total pengukuran
"""
import asyncio
from supabase import create_client
import os
from datetime import datetime

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jxvhiuxvbvvdvtlvbqyc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp4dmhpdXh2YnZ2ZHZ0bHZicXljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDM0NDAzNjQsImV4cCI6MjAxOTAxNjM2NH0.xBYq8kG7qEIY2Yd5jVFzoxGqWCBMHu2T5ZW0jZJVCv0")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def debug_totals():
    """Debug: Bandingkan total di berbagai kondisi"""
    
    print("=" * 80)
    print("DEBUG: Total Data Mismatch")
    print("=" * 80)
    
    # 1. Total records NO FILTER
    print("\n[1] TOTAL RECORDS (NO FILTER)")
    print("-" * 80)
    response = supabase.table("pengukuran").select("id").execute()
    total_all = len(response.data)
    print(f"✅ Total records di tabel pengukuran: {total_all}")
    
    # 2. Total records HAS status_gizi
    print("\n[2] RECORDS WITH status_gizi (NOT NULL)")
    print("-" * 80)
    response = supabase.table("pengukuran").select("id,status_gizi").execute()
    records_with_status = [r for r in response.data if r.get("status_gizi")]
    print(f"✅ Records dengan status_gizi: {len(records_with_status)}")
    print(f"❌ Records tanpa status_gizi: {total_all - len(records_with_status)}")
    
    # 3. Total records HAS zscore_tbu dan zscore_bbu
    print("\n[3] RECORDS WITH zscore_tbu AND zscore_bbu")
    print("-" * 80)
    response = supabase.table("pengukuran").select("id,zscore_tbu,zscore_bbu").execute()
    records_with_zscores = [
        r for r in response.data 
        if r.get("zscore_tbu") is not None and r.get("zscore_bbu") is not None
    ]
    print(f"✅ Records dengan kedua z-score: {len(records_with_zscores)}")
    print(f"❌ Records tanpa lengkap z-score: {total_all - len(records_with_zscores)}")
    
    # 4. Total records COMPLETE (has status_gizi + both z-scores)
    print("\n[4] RECORDS COMPLETE (status_gizi + zscore_tbu + zscore_bbu)")
    print("-" * 80)
    response = supabase.table("pengukuran").select(
        "id,status_gizi,zscore_tbu,zscore_bbu,tanggal_pengukuran"
    ).execute()
    complete_records = [
        r for r in response.data 
        if (r.get("status_gizi") and 
            r.get("zscore_tbu") is not None and 
            r.get("zscore_bbu") is not None)
    ]
    print(f"✅ Complete records: {len(complete_records)}")
    print(f"❌ Incomplete records: {total_all - len(complete_records)}")
    
    # 5. Check tanggal_pengukuran (some might have NULL date)
    print("\n[5] RECORDS WITH tanggal_pengukuran (NOT NULL)")
    print("-" * 80)
    response = supabase.table("pengukuran").select("id,tanggal_pengukuran").execute()
    records_with_date = [r for r in response.data if r.get("tanggal_pengukuran")]
    print(f"✅ Records dengan tanggal_pengukuran: {len(records_with_date)}")
    print(f"❌ Records tanpa tanggal_pengukuran: {total_all - len(records_with_date)}")
    
    # 6. Check for duplicate IDs
    print("\n[6] CHECK DUPLICATE IDs")
    print("-" * 80)
    response = supabase.table("pengukuran").select("id").execute()
    ids = [r["id"] for r in response.data]
    unique_ids = set(ids)
    print(f"ℹ️ Total records: {len(ids)}")
    print(f"ℹ️ Unique IDs: {len(unique_ids)}")
    if len(ids) != len(unique_ids):
        print(f"⚠️ DUPLICATE IDs FOUND: {len(ids) - len(unique_ids)}")
    
    # 7. Summary for admin evaluation
    print("\n[7] EXPECTED ADMIN EVALUATION TOTAL")
    print("-" * 80)
    print(f"Expected: {len(complete_records)} records")
    print("(Only complete records with all required fields)")
    
    # 8. Check some NULL values
    print("\n[8] SAMPLE OF RECORDS WITH NULL VALUES")
    print("-" * 80)
    response = supabase.table("pengukuran").select(
        "id,status_gizi,zscore_tbu,zscore_bbu,tanggal_pengukuran"
    ).limit(1000).execute()
    
    null_patterns = {}
    for r in response.data:
        pattern = []
        if not r.get("status_gizi"):
            pattern.append("status_gizi=NULL")
        if r.get("zscore_tbu") is None:
            pattern.append("zscore_tbu=NULL")
        if r.get("zscore_bbu") is None:
            pattern.append("zscore_bbu=NULL")
        if not r.get("tanggal_pengukuran"):
            pattern.append("tanggal_pengukuran=NULL")
        
        if pattern:
            pattern_str = ", ".join(pattern)
            null_patterns[pattern_str] = null_patterns.get(pattern_str, 0) + 1
    
    if null_patterns:
        print("Pattern of NULL values found:")
        for pattern, count in sorted(null_patterns.items(), key=lambda x: -x[1]):
            print(f"  - {pattern}: {count} records")
    else:
        print("✅ No NULL values found in sample")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(debug_totals())

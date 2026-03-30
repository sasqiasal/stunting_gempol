"""
Check pengukuran table count dan quality dari dalam environment app
"""
import asyncio
import sys
import os

# Add backend path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def check_data():
    from app.database import get_supabase
    from app.services.evaluation_service import evaluation_service, STATUS_GIZI_MAPPING
    
    supabase = get_supabase()
    evaluation_service.set_supabase_client(supabase)
    
    print("=" * 80)
    print("CHECK: Pengukuran Data Quality & Total Count Analysis")
    print("=" * 80)
    
    # 1. Total records (NO FILTER)
    print("\n[1] TOTAL RECORDS di tabel pengukuran")
    print("-" * 80)
    response = supabase.table("pengukuran").select("count", count="exact").execute()
    print(f"Total records: {response.count}")
    
    # 2. Fetch semua data untuk analisis
    print("\n[2] Fetching all records untuk analisis...")
    print("-" * 80)
    response = supabase.table("pengukuran").select(
        "id,status_gizi,zscore_tbu,zscore_bbu,tanggal_pengukuran,created_at"
    ).execute()
    
    all_records = response.data
    print(f"Records fetched: {len(all_records)}")
    
    # 3. Analyze missing fields
    print("\n[3] DATA QUALITY ANALYSIS")
    print("-" * 80)
    
    missing_status_gizi = [r for r in all_records if not r.get("status_gizi")]
    missing_zscore_tbu = [r for r in all_records if r.get("zscore_tbu") is None]
    missing_zscore_bbu = [r for r in all_records if r.get("zscore_bbu") is None]
    missing_tanggal = [r for r in all_records if not r.get("tanggal_pengukuran")]
    
    print(f"✅ COMPLETE records (all fields): {len(all_records) - (len(missing_status_gizi) | len(missing_zscore_tbu) | len(missing_zscore_bbu))}")
    print(f"❌ Missing status_gizi: {len(missing_status_gizi)}")
    print(f"❌ Missing zscore_tbu: {len(missing_zscore_tbu)}")
    print(f"❌ Missing zscore_bbu: {len(missing_zscore_bbu)}")
    print(f"❌ Missing tanggal_pengukuran: {len(missing_tanggal)}")
    
    # 4. Check evaluation_service fetchdata
    print("\n[4] EVALUASI SERVICE: Fetch ALL data (admin, no bulan filter)")
    print("-" * 80)
    evaluation_data = await evaluation_service.fetch_pengukuran_data(
        bulan=None,
        role="admin",
        posyandu_id=None
    )
    print(f"Data dari evaluation_service: {len(evaluation_data)} records")
    
    # 5. Compare status_gizi mapping
    print("\n[5] STATUS_GIZI MAPPING CHECK")
    print("-" * 80)
    status_gizi_values = set([r.get("status_gizi") for r in all_records if r.get("status_gizi")])
    print(f"Unique status_gizi values dalam database:")
    for status in sorted(status_gizi_values):
        count = len([r for r in all_records if r.get("status_gizi") == status])
        mapped = STATUS_GIZI_MAPPING.get(status, "NOT MAPPED")
        print(f"  - '{status}' → {mapped} ({count} records)")
    
    # 6. Unmapped values (if any)
    unmapped = []
    for r in all_records:
        status = r.get("status_gizi")
        if status and status not in STATUS_GIZI_MAPPING:
            unmapped.append(status)
    
    if unmapped:
        print(f"\n⚠️ UNMAPPED status_gizi values:")
        for status in set(unmapped):
            count = len([s for s in unmapped if s == status])
            print(f"  - '{status}': {count} records")
    
    # 7. Check evaluation result
    print("\n[6] ACTUAL EVALUATION RESULT")
    print("-" * 80)
    result = await evaluation_service.evaluate_model(
        bulan=None,
        role="admin",
        posyandu_id=None
    )
    
    if result.get("success"):
        total_evaluated = result.get("metadata", {}).get("total_data", 0)
        print(f"Total evaluated: {total_evaluated}")
        if total_evaluated < len(all_records):
            missing = len(all_records) - total_evaluated
            print(f"⚠️ DISCREPANCY: {missing} records not evaluated")
            print(f"Reason: Likely have NULL/missing values in critical fields")
    else:
        print(f"❌ Evaluation failed: {result.get('message')}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(check_data())

"""
Debug: Cek apakah ada discrepancy antara pengukuran dan evaluasi_model_knn
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def check_evaluasi_table():
    from app.database import get_supabase
    
    supabase = get_supabase()
    
    print("=" * 80)
    print("CHECK: Discrepancy antara pengukuran vs evaluasi_model_knn")
    print("=" * 80)
    
    # 1. Count pengukuran
    pengukuran_response = supabase.table("pengukuran").select("count", count="exact").execute()
    pengukuran_total = pengukuran_response.count
    print(f"\n[1] Total di tabel PENGUKURAN: {pengukuran_total}")
    
    # 2. Count evaluasi_model_knn
    evaluasi_response = supabase.table("evaluasi_model_knn").select("count", count="exact").execute()
    evaluasi_total = evaluasi_response.count
    print(f"[2] Total di tabel EVALUASI_MODEL_KNN: {evaluasi_total}")
    
    # 3. Find pengukuran yang TIDAK punya evaluasi
    print(f"\n[3] ANALYSIS:")
    print("-" * 80)
    if pengukuran_total == evaluasi_total:
        print(f"✅ SELARAS: Semua {pengukuran_total} records memiliki evaluasi")
    else:
        diff = abs(pengukuran_total - evaluasi_total)
        print(f"⚠️ DISKREPANSI: {diff} records berbeda")
        
        # Get IDs yang exist di pengukuran
        pengukuran_ids_response = supabase.table("pengukuran").select("id").execute()
        pengukuran_ids = set([r["id"] for r in pengukuran_ids_response.data])
        
        # Get IDs yang exist di evaluasi_model_knn (pengukuran_id)
        evaluasi_ids_response = supabase.table("evaluasi_model_knn").select("pengukuran_id").execute()
        evaluasi_ids = set([r["pengukuran_id"] for r in evaluasi_ids_response.data])
        
        # Find missing
        missing_in_evaluasi = pengukuran_ids - evaluasi_ids
        orphaned_in_evaluasi = evaluasi_ids - pengukuran_ids
        
        if missing_in_evaluasi:
            print(f"\n❌ Pengukuran yang TIDAK punya evaluasi: {len(missing_in_evaluasi)}")
            print(f"   IDs: {sorted(list(missing_in_evaluasi))[:10]}...")  # Show first 10
        
        if orphaned_in_evaluasi:
            print(f"\n❌ Evaluasi dengan pengukuran_id yang tidak ada: {len(orphaned_in_evaluasi)}")
            print(f"   IDs: {sorted(list(orphaned_in_evaluasi))[:10]}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(check_evaluasi_table())

"""
Buat evaluasi_model_knn entry untuk pengukuran yang orphaned
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def create_missing_evaluasi():
    from app.database import get_supabase
    from app.services.evaluation_service import EvaluationService
    
    supabase = get_supabase()
    eval_service = EvaluationService()
    eval_service.set_supabase_client(supabase)
    
    print("=" * 80)
    print("CREATE MISSING EVALUASI_MODEL_KNN ENTRIES")
    print("=" * 80)
    
    # Get pengukuran yang tidak punya evaluasi
    pengukuran_response = supabase.table("pengukuran").select("id").execute()
    pengukuran_ids = set([r["id"] for r in pengukuran_response.data])
    
    evaluasi_response = supabase.table("evaluasi_model_knn").select("pengukuran_id").execute()
    evaluasi_ids = set([r["pengukuran_id"] for r in evaluasi_response.data])
    
    missing_pengukuran_ids = list(pengukuran_ids - evaluasi_ids)
    
    if not missing_pengukuran_ids:
        print("✅ Semua pengukuran sudah punya evaluasi! Tidak ada yang perlu diperbaiki.")
        return
    
    print(f"\n❌ Ditemukan {len(missing_pengukuran_ids)} pengukuran tanpa evaluasi:")
    print(f"   IDs: {missing_pengukuran_ids}")
    
    print("\n🔧 Membuat evaluasi_model_knn entries...")
    print("-" * 80)
    
    created_count = 0
    error_count = 0
    
    for pengukuran_id in missing_pengukuran_ids:
        try:
            # Get pengukuran data
            peng_response = supabase.table("pengukuran").select("*").eq("id", pengukuran_id).execute()
            
            if not peng_response.data:
                print(f"⚠️  Pengukuran #{pengukuran_id}: Not found")
                error_count += 1
                continue
            
            pengukuran = peng_response.data[0]
            
            # Create evaluasi entry dengan neighbors kosong (akan dihitung nanti jika perlu)
            evaluasi_entry = {
                "pengukuran_id": pengukuran_id,
                "k_value": 5,
                "algorithm": "KNN",
                "nearest_neighbors": []  # Empty array, akan dipopulate dengan fungsi lain jika perlu
                # Let the database handle created_at/updated_at automatically
            }
            
            # Insert ke evaluasi_model_knn
            insert_response = supabase.table("evaluasi_model_knn").insert(evaluasi_entry).execute()
            
            if insert_response.data:
                print(f"✅ Evaluasi #{pengukuran_id} dibuat")
                created_count += 1
            else:
                print(f"⚠️  Evaluasi #{pengukuran_id}: Insert failed")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error pada pengukuran #{pengukuran_id}: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"✅ Created: {created_count}")
    print(f"❌ Errors: {error_count}")
    print("=" * 80)
    
    # Verify totals sekarang
    print("\nVERIFICATION:")
    peng_verify = supabase.table("pengukuran").select("count", count="exact").execute()
    eval_verify = supabase.table("evaluasi_model_knn").select("count", count="exact").execute()
    
    print(f"Pengukuran: {peng_verify.count}")
    print(f"Evaluasi: {eval_verify.count}")
    
    if peng_verify.count == eval_verify.count:
        print("\n✅ SELARAS! Semua records sekarang match.")
    else:
        print(f"\n⚠️ Masih ada discrepancy: {abs(peng_verify.count - eval_verify.count)} records")


if __name__ == "__main__":
    asyncio.run(create_missing_evaluasi())

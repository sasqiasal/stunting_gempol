"""
Cek detail record pengukuran yang hilang di evaluasi_model_knn
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def check_orphaned_record():
    from app.database import get_supabase
    
    supabase = get_supabase()
    
    print("=" * 80)
    print("DETAIL: Pengukuran Record yang Hilang di Evaluasi")
    print("=" * 80)
    
    # Cek record 1119
    response = supabase.table("pengukuran").select(
        "id,balita_id,status_gizi,zscore_tbu,zscore_bbu,tanggal_pengukuran,created_at"
    ).eq("id", 1119).execute()
    
    if response.data:
        record = response.data[0]
        print(f"\n📋 RECORD PENGUKURAN #1119:")
        print("-" * 80)
        print(f"ID: {record['id']}")
        print(f"Balita ID: {record['balita_id']}")
        print(f"Status Gizi: {record['status_gizi']}")
        print(f"Z-Score TBU (Tunggal): {record['zscore_tbu']}")
        print(f"Z-Score BBU (Berat): {record['zscore_bbu']}")
        print(f"Tanggal Pengukuran: {record['tanggal_pengukuran']}")
        print(f"Created At: {record['created_at']}")
        
        # Cek apakah ada di evaluasi_model_knn
        evaluasi_response = supabase.table("evaluasi_model_knn").select("*").eq("pengukuran_id", 1119).execute()
        if evaluasi_response.data:
            print(f"\n✅ Ada entry di evaluasi_model_knn")
        else:
            print(f"\n❌ TIDAK ada entry di evaluasi_model_knn")
            print("\nKemungkinan penyebab:")
            print("1. Record ditambah AFTER pengukuran tanpa trigger evaluasi")
            print("2. Ada error saat create evaluasi_model_knn")
            print("3. Entry evaluasi dihapus tapi pengukuran tetap ada")
    else:
        print("❌ Record 1119 not found!")
    
    print("\n" + "=" * 80)
    print("\nSOLUSI:")
    print("-" * 80)
    print("Pilihan:")
    print("1. DELETE pengukuran #1119 (jika record ini invalid)")
    print("2. CREATE evaluasi_model_knn entry untuk record #1119")
    print("3. INVESTIGATE: Cek kenapa record ini tidak punya evaluasi")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(check_orphaned_record())

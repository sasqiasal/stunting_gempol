"""
Routes untuk Pengukuran
- Create pengukuran (dengan prediksi stunting otomatis)
- Get riwayat pengukuran
- Get statistik pengukuran
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.models.pengukuran import PengukuranCreate, PengukuranUpdate, PengukuranResponse, PengukuranWithBalita
from app.utils.auth import get_current_user, get_current_kader
from app.utils.helpers import calculate_age_in_months
from app.services.prediction_service import prediction_service
from app.database import get_supabase

router = APIRouter(prefix="/pengukuran", tags=["Pengukuran"])

@router.get("/statistik/summary")
async def get_statistik_summary(
    posyandu_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Get summary statistics for dashboard
    """
    try:
        # 1. Total Balita
        query_balita = supabase_client.table("balita").select("id", count="exact")
        
        # Filter by role or param
        if current_user["role"] == "kader":
            # Kader hanya lihat posyandu dia
            # Perlu ambil posyandu_id dari tabel kader/user? 
            # Asumsi: posyandu_id dikirim dari frontend atau ambil dari user profile
            # Untuk simplifikasi, jika param posyandu_id ada, gunakan.
            if posyandu_id:
                query_balita = query_balita.eq("posyandu_id", posyandu_id)
        elif posyandu_id:
             query_balita = query_balita.eq("posyandu_id", posyandu_id)
             
        res_balita = query_balita.execute()
        total_balita = res_balita.count or 0

        # 2. Total Stunting (Status Terkini)
        query_stunting = supabase_client.table("balita").select("id", count="exact")\
            .ilike("status_terkini", "%stunt%")
            
        if current_user["role"] == "kader" and posyandu_id:
            query_stunting = query_stunting.eq("posyandu_id", posyandu_id)
        elif posyandu_id:
            query_stunting = query_stunting.eq("posyandu_id", posyandu_id)
            
        res_stunting = query_stunting.execute()
        total_stunting = res_stunting.count or 0
        
        # 3. Pengukuran Bulan Ini
        now = datetime.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Query pengukuran -> join balita -> filter posyandu
        # Karena supabase-py join filtering agak kompleks, kita query pengukuran simple dulu
        # Atau filter balita IDs dulu
        
        balita_ids = []
        if posyandu_id:
            res_ids = supabase_client.table("balita").select("id").eq("posyandu_id", posyandu_id).execute()
            balita_ids = [b["id"] for b in res_ids.data]
            
        query_pengukuran = supabase_client.table("pengukuran").select("id", count="exact")\
            .gte("tanggal_pengukuran", first_day.isoformat())
            
        if balita_ids:
            query_pengukuran = query_pengukuran.in_("balita_id", balita_ids)
            
        res_pengukuran = query_pengukuran.execute()
        total_pengukuran_bulan_ini = res_pengukuran.count or 0
        
        # Calculate derived stats
        total_normal = total_balita - total_stunting
        if total_normal < 0: total_normal = 0
        
        persentase_stunting = 0
        if total_balita > 0:
            persentase_stunting = round((total_stunting / total_balita) * 100, 1)

        return {
            "total_balita": total_balita,
            "total_pengukuran": total_balita, # Map total balita to total pengukuran for consistent stats
            "total_stunting": total_stunting,
            "total_normal": total_normal,
            "persentase_stunting": persentase_stunting,
            "pengukuran_bulan_ini": total_pengukuran_bulan_ini
        }
        
    except Exception as e:
        print(f"Error summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/riwayat-stunting")
async def get_riwayat_stunting(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Get riwayat jumlah kasus stunting 6 bulan terakhir
    """
    try:
        # Hitung range 6 bulan ke belakang
        now = datetime.now()
        start_date = now - timedelta(days=180) # Approx 6 months
        
        # Query pengukuran dari 6 bulan terakhir - ambil semua field
        response = supabase_client.table("pengukuran").select(
            "*"
        ).gte("tanggal_pengukuran", start_date.isoformat()).execute()
        
        # Filter stunting dengan fallback logic
        def is_stunting(item):
            # Priority 1: status_gizi_label (2 atau 3 = stunting)
            if item.get("status_gizi_label") is not None:
                return item.get("status_gizi_label") in (2, 3)
            
            # Priority 2: prediksi_stunting (True)
            if item.get("prediksi_stunting") is not None:
                return item.get("prediksi_stunting") == True
            
            # Priority 3: status_gizi contains "Stunting"
            status_gizi = item.get("status_gizi", "")
            if status_gizi:
                return "Stunting" in str(status_gizi)
            
            return False
        
        data = [d for d in response.data if is_stunting(d)]
        print(f"📊 Riwayat stunting: {len(data)} kasus dari {len(response.data)} pengukuran")
        
        # Group by Month
        stats = {}
        bulan_map = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                     "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        
        # Init 6 bulan terakhir dengan 0
        for i in range(6):
            d = now - timedelta(days=30 * (5-i))
            mon_idx = d.month - 1
            key_id = f"{bulan_map[mon_idx]} {d.year}"
            stats[key_id] = 0
            
        # Aggregate
        total_cases = 0
        for item in data:
            try:
                # Parse date
                tgl = datetime.fromisoformat(item["tanggal_pengukuran"].replace("Z", "+00:00"))
                mon_idx = tgl.month - 1
                key_id = f"{bulan_map[mon_idx]} {tgl.year}"
                
                if key_id in stats:
                    stats[key_id] += 1
                    total_cases += 1
            except:
                continue
        
        # Format output dengan urutan yang benar (lama ke baru)
        result_data = []
        for i in range(5, -1, -1):  # 5 bulan lalu sampai bulan ini
            target_date = now - timedelta(days=30 * i)
            mon_idx = target_date.month - 1
            key_id = f"{bulan_map[mon_idx]} {target_date.year}"
            if key_id in stats:
                result_data.append({"bulan": key_id, "jumlah": stats[key_id]})
             
        return {
            "data": result_data,
            "total": total_cases,
            "periode": "6 Bulan Terakhir"
        }

    except Exception as e:
        print(f"Error getting riwayat stunting: {e}")
        import traceback
        traceback.print_exc()
        # Return safe response with placeholder data
        return {
            "data": [
                {"bulan": "Januari 2026", "jumlah": 0},
                {"bulan": "Februari 2026", "jumlah": 0},
                {"bulan": "Maret 2026", "jumlah": 0},
                {"bulan": "April 2026", "jumlah": 0},
                {"bulan": "Mei 2026", "jumlah": 0},
                {"bulan": "Juni 2026", "jumlah": 0}
            ],
            "total": 0,
            "periode": "6 Bulan Terakhir"
        }

@router.post("/", response_model=PengukuranResponse, status_code=status.HTTP_201_CREATED)
async def create_pengukuran(
    pengukuran_data: PengukuranCreate,
    current_user: dict = Depends(get_current_kader),
    supabase_client = Depends(get_supabase)
):
    """
    Menambahkan data pengukuran baru dengan prediksi stunting otomatis
    
    Flow:
    1. Ambil data balita
    2. Validasi tanggal pengukuran (harus dalam 3 bulan + bulan saat ini ke belakang)
    3. Hitung usia saat pengukuran
    4. Hitung Z-Score BB/U dan TB/U
    5. Prediksi stunting menggunakan model KNN
    6. Simpan ke database
    7. Update status_terkini di tabel balita
    """
    # 1. Ambil data balita
    balita_response = supabase_client.table("balita").select("*").eq("id", pengukuran_data.balita_id).execute()
    
    if not balita_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balita not found"
        )
    
    balita = balita_response.data[0]
    
    # 2. Validasi tanggal pengukuran (harus dalam 3 bulan + bulan saat ini ke belakang)
    tgl_ukur = pengukuran_data.tanggal_pengukuran or date.today()
    today = date.today()
    
    # Hitung min date: 3 bulan sebelumnya dari hari pertama bulan saat ini
    first_day_current_month = today.replace(day=1)
    min_date = first_day_current_month - timedelta(days=90)  # ~3 bulan
    min_date = min_date.replace(day=1)  # Set ke hari pertama bulan min
    
    # Max date: hari terakhir bulan saat ini
    if today.month == 12:
        max_date = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        max_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    if tgl_ukur < min_date or tgl_ukur > max_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tanggal pengukuran harus dalam range {min_date.strftime('%Y-%m-%d')} sampai {max_date.strftime('%Y-%m-%d')} (bulan saat ini + 3 bulan sebelumnya)"
        )
    
    # 3. Hitung usia saat pengukuran
    tanggal_lahir = date.fromisoformat(balita["tanggal_lahir"])
    usia_bulan = calculate_age_in_months(tanggal_lahir, tgl_ukur)
    jenis_kelamin = balita["jenis_kelamin"]
    
    # 4. Prediksi stunting (termasuk kalkulasi Z-Score)
    prediksi_result = prediction_service.predict_stunting(
        jenis_kelamin=jenis_kelamin,
        usia_bulan=usia_bulan,
        tinggi_badan=pengukuran_data.tinggi_badan,
        berat_badan=pengukuran_data.berat_badan,
        lingkar_lengan=pengukuran_data.lingkar_lengan,
        lingkar_kepala=pengukuran_data.lingkar_kepala
    )
    
    # 5. Siapkan data untuk disimpan
    pengukuran_dict = pengukuran_data.model_dump()
    
    # Determine prediksi_stunting boolean from 4-class label for backward compatibility
    status_gizi_label = int(prediksi_result["status_gizi_label"])
    is_stunting = status_gizi_label in [2, 3]  # Labels 2,3 = Stunting
    
    pengukuran_dict.update({
        "kader_id": current_user["id"],
        "usia_bulan": usia_bulan,
        "jenis_kelamin": jenis_kelamin,
        "zscore_bbu": float(prediksi_result["zscore_bbu"]),
        "zscore_tbu": float(prediksi_result["zscore_tbu"]),
        # Status gizi sekarang menggunakan 4 kelas dari model KNN
        "status_gizi": prediksi_result["status_gizi"],
        # Keep prediksi_stunting for backward compatibility (True=stunting, False=normal)
        "prediksi_stunting": is_stunting,
        # Label klasifikasi integer (0, 1, 2, 3) - will be stored when DB is updated
        # For now, keep it in detail_prediksi only
        "confidence_score": float(prediksi_result["confidence_score"]),
        # Gunakan tanggal pengukuran yang dikirim (retroaktif) atau waktu sekarang
        "tanggal_pengukuran": datetime.combine(tgl_ukur, datetime.min.time()).astimezone().isoformat(),
        "created_at": datetime.now().astimezone().isoformat(),
        # Simpan detail prediksi (termasuk nearest_neighbors dan label 4 kelas)
        "detail_prediksi": {
            "status_gizi_label": status_gizi_label,
            "nearest_neighbors": prediksi_result.get("nearest_neighbors", []),
            "version": "2.0", 
            "model": "KNN-4Class",
            "k": 5,
            "classes": ["Normal + Gizi Baik", "Normal + Kurang Gizi", "Stunting + Gizi Baik", "Stunting + Kurang Gizi"]
        }
    })
    
    # Convert float values to ensure JSON serialization
    for key in ["tinggi_badan", "berat_badan", "lingkar_lengan", "lingkar_kepala"]:
        if key in pengukuran_dict:
            pengukuran_dict[key] = float(pengukuran_dict[key])
    
    # 5. Insert pengukuran (TANPA detail_prediksi karena disimpan di tabel terpisah)
    try:
        # Hapus field evaluasi dari dict pengukuran jika ada, karena akan disimpan terpisah/tidak ada di schema pengukuran
        if "detail_prediksi" in pengukuran_dict:
            del pengukuran_dict["detail_prediksi"]
            
        response = supabase_client.table("pengukuran").insert(pengukuran_dict).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Gagal menyimpan data pengukuran")
            
        pengukuran_new = response.data[0]
        pengukuran_id = pengukuran_new["id"]
        
        # 5b. Insert ke tabel evaluasi_model_knn
        # Simpan detail evaluasi di tabel terpisah
        evaluasi_data = {
            "pengukuran_id": pengukuran_id,
            "k_value": 5, 
            "algorithm": "KNN",
            "nearest_neighbors": prediksi_result.get("nearest_neighbors", [])
        }
        
        try:
            supabase_client.table("evaluasi_model_knn").insert(evaluasi_data).execute()
            print(f"✅ Evaluasi detail saved for pengukuran {pengukuran_id}")
        except Exception as e_eval:
            print(f"⚠️ Gagal menyimpan evaluasi detail: {e_eval}")
            # Tidak raise error agar proses pengukuran tetap sukses
            
    except Exception as e:
        print(f"⚠️ Error inserting pengukuran: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Terjadi kesalahan database: {str(e)}"
        )
    
    pengukuran = pengukuran_new
    
    # 6. Update status_terkini di tabel balita
    supabase_client.table("balita").update({
        "status_terkini": prediksi_result["status_gizi"],
        "usia_bulan": usia_bulan
    }).eq("id", pengukuran_data.balita_id).execute()
    
    # Add status_gizi_label to response (required by response model)
    STATUS_GIZI_MAPPING = {
        "Normal + Gizi Baik": 0,
        "Normal + Kurang Gizi": 1,
        "Stunting + Gizi Baik": 2,
        "Stunting + Kurang Gizi": 3,
    }
    status_gizi = pengukuran.get("status_gizi", "Normal")
    pengukuran["status_gizi_label"] = STATUS_GIZI_MAPPING.get(status_gizi, 0)
    
    return pengukuran

@router.put("/{id}", response_model=PengukuranResponse)
async def update_pengukuran(
    id: int,
    pengukuran_data: PengukuranUpdate,
    current_user: dict = Depends(get_current_kader),
    supabase_client = Depends(get_supabase)
):
    """
    Update data pengukuran dan recalculate semua prediksi/evaluasi

    Flow:
    1. Ambil data pengukuran yang akan diupdate
    2. Ambil data balita terkait
    3. Hitung ulang usia saat pengukuran
    4. Hitung ulang Z-Score dan prediksi KNN
    5. Update tabel pengukuran
    6. Update tabel evaluasi_model_knn
    7. Update status_terkini di tabel balita
    """
    # 1. Ambil pengukuran yang akan diupdate
    existing = supabase_client.table("pengukuran").select("*").eq("id", id).execute()
    if not existing.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data pengukuran tidak ditemukan")

    pengukuran_existing = existing.data[0]
    balita_id = pengukuran_existing["balita_id"]

    # 2. Ambil data balita
    balita_response = supabase_client.table("balita").select("*").eq("id", balita_id).execute()
    if not balita_response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balita tidak ditemukan")

    balita = balita_response.data[0]

    # 3. Gunakan usia_bulan yang sudah tersimpan (JANGAN RECALCULATE untuk konsistensi)
    # Usia_bulan harus tetap sama seperti saat create, agar klasifikasi tetap konsisten
    usia_bulan = pengukuran_existing["usia_bulan"]
    jenis_kelamin = balita["jenis_kelamin"]

    # 4. Prediksi ulang stunting
    prediksi_result = prediction_service.predict_stunting(
        jenis_kelamin=jenis_kelamin,
        usia_bulan=usia_bulan,
        tinggi_badan=pengukuran_data.tinggi_badan,
        berat_badan=pengukuran_data.berat_badan,
        lingkar_lengan=pengukuran_data.lingkar_lengan,
        lingkar_kepala=pengukuran_data.lingkar_kepala
    )

    # 5. Update tabel pengukuran
    # Determine stunting status from 4-class label for backward compatibility  
    status_gizi_label = int(prediksi_result["status_gizi_label"])
    is_stunting = status_gizi_label in [2, 3]  # Labels 2,3 = Stunting
    
    update_dict = {
        "tinggi_badan": float(pengukuran_data.tinggi_badan),
        "berat_badan": float(pengukuran_data.berat_badan),
        "lingkar_lengan": float(pengukuran_data.lingkar_lengan),
        "lingkar_kepala": float(pengukuran_data.lingkar_kepala),
        "catatan": pengukuran_data.catatan,
        "usia_bulan": usia_bulan,
        "zscore_bbu": float(prediksi_result["zscore_bbu"]),
        "zscore_tbu": float(prediksi_result["zscore_tbu"]),
        # Status gizi menggunakan 4 kelas dari model KNN
        "status_gizi": prediksi_result["status_gizi"],
        # Keep prediksi_stunting for backward compatibility
        "prediksi_stunting": is_stunting,
        "confidence_score": float(prediksi_result["confidence_score"]),
    }

    try:
        response = supabase_client.table("pengukuran").update(update_dict).eq("id", id).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Gagal mengupdate data pengukuran")

        updated_pengukuran = response.data[0]

        # 6. Update atau insert ke tabel evaluasi_model_knn
        evaluasi_data = {
            "pengukuran_id": id,
            "k_value": 5,
            "algorithm": "KNN",
            "nearest_neighbors": prediksi_result.get("nearest_neighbors", [])
        }

        try:
            existing_eval = supabase_client.table("evaluasi_model_knn").select("id").eq("pengukuran_id", id).execute()
            if existing_eval.data:
                supabase_client.table("evaluasi_model_knn").update(evaluasi_data).eq("pengukuran_id", id).execute()
            else:
                supabase_client.table("evaluasi_model_knn").insert(evaluasi_data).execute()
            print(f"✅ Evaluasi updated for pengukuran {id}")
        except Exception as e_eval:
            print(f"⚠️ Gagal update evaluasi detail: {e_eval}")

        # 7. Update status_terkini balita (ambil pengukuran terbaru untuk balita ini)
        latest = supabase_client.table("pengukuran")\
            .select("status_gizi, tanggal_pengukuran")\
            .eq("balita_id", balita_id)\
            .order("tanggal_pengukuran", desc=True)\
            .limit(1)\
            .execute()

        if latest.data:
            supabase_client.table("balita").update({
                "status_terkini": latest.data[0]["status_gizi"],
                "usia_bulan": usia_bulan
            }).eq("id", balita_id).execute()

    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error updating pengukuran: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Terjadi kesalahan: {str(e)}")

    # Add status_gizi_label to response (required by response model)
    STATUS_GIZI_MAPPING = {
        "Normal + Gizi Baik": 0,
        "Normal + Kurang Gizi": 1,
        "Stunting + Gizi Baik": 2,
        "Stunting + Kurang Gizi": 3,
    }
    status_gizi = updated_pengukuran.get("status_gizi", "Normal")
    updated_pengukuran["status_gizi_label"] = STATUS_GIZI_MAPPING.get(status_gizi, 0)
    
    return updated_pengukuran

@router.get("/{id}/detail-evaluasi", response_model=Dict[str, Any])
async def get_detail_evaluasi(
    id: int,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan detail evaluasi model KNN (Nearest Neighbors) 
    untuk pengukuran tertentu.
    """
    try:
        # Cek apakah tabel evaluasi ada datanya untuk pengukuran ini
        response = supabase_client.table("evaluasi_model_knn")\
            .select("*")\
            .eq("pengukuran_id", id)\
            .execute()
            
        if response.data and len(response.data) > 0:
            return {
                "status": "success",
                "source": "database_table",
                "data": response.data[0]
            }
        
        # Fallback: Cek apakah tersimpan di kolom detail_prediksi (legacy/fallback)
        pengukuran_res = supabase_client.table("pengukuran")\
            .select("detail_prediksi")\
            .eq("id", id)\
            .execute()
            
        if pengukuran_res.data and pengukuran_res.data[0].get("detail_prediksi"):
            return {
                "status": "success",
                "source": "pengukuran_column",
                "data": {
                    "nearest_neighbors": pengukuran_res.data[0]["detail_prediksi"].get("nearest_neighbors", [])
                }
            }
            
        raise HTTPException(status_code=404, detail="Detail evaluasi tidak ditemukan untuk pengukuran ini")
        
    except Exception as e:
        print(f"Error fetching detail evaluasi: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data evaluasi")

@router.get("/", response_model=List[PengukuranWithBalita])
async def get_all_pengukuran(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    balita_id: Optional[int] = None,
    posyandu_id: Optional[int] = None,
    prediksi_stunting: Optional[bool] = None,
    bulan: Optional[str] = Query(None, description="Filter bulan dalam format YYYY-MM (contoh: 2026-01)"),
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan semua data pengukuran dengan join ke tabel balita dan posyandu
    
    - Kader: Hanya bisa melihat pengukuran dari posyandu mereka sendiri
    - Admin: Bisa melihat semua pengukuran atau filter berdasarkan posyandu_id
    - Filter bulan: format YYYY-MM untuk filter berdasarkan tanggal_pengukuran
    """
    print(f"🔍 GET /pengukuran - User: {current_user.get('email')} ({current_user.get('role')})")
    if bulan:
        print(f"📅 Filter bulan: {bulan}")
    
    try:
        # Query dengan join
        query = supabase_client.table("pengukuran").select(
            "*, balita:balita_id(nama_lengkap, nik, posyandu_id), posyandu:balita(posyandu:posyandu_id(nama))"
        )
        
        # Filter berdasarkan balita_id
        if balita_id:
            query = query.eq("balita_id", balita_id)
        
        # Filter berdasarkan status stunting (backward compatible)
        # For now, use prediksi_stunting column; will migrate to status_gizi_label after DB update
        if prediksi_stunting is not None:
            query = query.eq("prediksi_stunting", prediksi_stunting)
        
        # Filter berdasarkan bulan (YYYY-MM)
        if bulan:
            try:
                # Parse bulan format YYYY-MM
                year, month = bulan.split('-')
                start_date = f"{year}-{month}-01"
                
                # Hitung akhir bulan
                if month == '12':
                    end_date = f"{int(year)+1}-01-01"
                else:
                    end_date = f"{year}-{str(int(month)+1).zfill(2)}-01"
                
                # Filter tanggal_pengukuran >= start dan < end
                query = query.gte("tanggal_pengukuran", start_date).lt("tanggal_pengukuran", end_date)
                print(f"📅 Date range: {start_date} to {end_date}")
            except (ValueError, IndexError) as e:
                print(f"⚠️ Invalid bulan format: {bulan}, ignoring filter")
        
        # Pagination
        query = query.range(skip, skip + limit - 1).order("tanggal_pengukuran", desc=True)
        
        response = query.execute()
        print(f"✅ Query executed successfully, got {len(response.data)} records")
        
        # Transform data untuk response
        # Classification mapping for status_gizi_label
        STATUS_GIZI_MAPPING = {
            "Normal + Gizi Baik": 0,
            "Normal + Kurang Gizi": 1,
            "Stunting + Gizi Baik": 2,
            "Stunting + Kurang Gizi": 3,
        }
        
        results = []
        for item in response.data:
            result = {**item}
            
            # Add status_gizi_label based on status_gizi string
            # This is required by the response model
            status_gizi = result.get("status_gizi", "Normal")
            result["status_gizi_label"] = STATUS_GIZI_MAPPING.get(status_gizi, 0)
            
            # Flatten data balita
            if "balita" in item and item["balita"]:
                result["balita_nama"] = item["balita"].get("nama_lengkap") or "-"
                result["balita_nik"] = item["balita"].get("nik") or "-"
                result["posyandu_id"] = item["balita"].get("posyandu_id")
                
                # Fetch posyandu nama if possible
                if "posyandu" in item and item["posyandu"] and "posyandu" in item["posyandu"]:
                    if isinstance(item["posyandu"]["posyandu"], dict):
                        result["posyandu_nama"] = item["posyandu"]["posyandu"].get("nama")
            else:
                result["balita_nama"] = "-"
                result["balita_nik"] = "-"
            
            results.append(result)
        
        # Filter berdasarkan role user
        if current_user.get("role") == "kader":
            user_posyandu_id = current_user.get("posyandu_id")
            if not user_posyandu_id:
                # Jika kader belum punya posyandu, return empty array
                print(f"⚠️ Kader {current_user.get('email')} belum memiliki posyandu_id")
                return []
            # Filter hanya pengukuran dari posyandu kader
            results = [r for r in results if r.get("posyandu_id") == user_posyandu_id]
        elif posyandu_id:
            # Admin bisa filter berdasarkan posyandu_id jika diberikan
            results = [r for r in results if r.get("posyandu_id") == posyandu_id]
        
        print(f"📊 Returning {len(results)} records after filtering")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_all_pengukuran: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@router.get("/balita/{balita_id}", response_model=List[PengukuranResponse])
async def get_pengukuran_by_balita(
    balita_id: int,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan riwayat pengukuran balita tertentu
    """
    response = supabase_client.table("pengukuran").select("*").eq("balita_id", balita_id).order("tanggal_pengukuran", desc=True).execute()
    
    return response.data

@router.get("/statistik/summary")
async def get_statistik_summary(
    posyandu_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan statistik ringkasan pengukuran
    """
    # Query untuk total pengukuran
    query = supabase_client.table("pengukuran").select("*", count="exact")
    
    if posyandu_id:
        # Join dengan balita untuk filter posyandu
        query = query.eq("balita.posyandu_id", posyandu_id)
    
    total_response = query.execute()
    total_pengukuran = total_response.count or 0
    
    # Query untuk stunting (using prediksi_stunting for backward compatibility)
    stunting_query = supabase_client.table("pengukuran").select("*", count="exact").eq("prediksi_stunting", True)
    
    if posyandu_id:
        stunting_query = stunting_query.eq("balita.posyandu_id", posyandu_id)
    
    stunting_response = stunting_query.execute()
    total_stunting = stunting_response.count or 0
    
    # Hitung persentase
    persentase_stunting = (total_stunting / total_pengukuran * 100) if total_pengukuran > 0 else 0
    
    return {
        "total_pengukuran": total_pengukuran,
        "total_stunting": total_stunting,
        "total_normal": total_pengukuran - total_stunting,
        "persentase_stunting": round(persentase_stunting, 2)
    }

@router.get("/riwayat-stunting")
async def get_riwayat_stunting(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan riwayat kasus stunting 6 bulan terakhir untuk visualisasi grafik
    
    Logic berdasarkan role:
    - Admin: Data stunting dari seluruh Posyandu (Global)
    - Kader: Data stunting hanya dari Posyandu tempat kader bertugas
    
    Return: Array data per bulan dengan jumlah kasus stunting
    """
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Hitung 6 bulan terakhir
    now = datetime.now()
    six_months_ago = now - timedelta(days=180)  # Approx 6 bulan
    
    # Query pengukuran dengan filter stunting (prediksi_stunting=true) dan 6 bulan terakhir
    query = supabase_client.table("pengukuran").select(
        "id, tanggal_pengukuran, prediksi_stunting, balita:balita_id(posyandu_id)"
    ).eq("prediksi_stunting", True).gte("tanggal_pengukuran", six_months_ago.isoformat())
    
    response = query.execute()
    
    # Filter berdasarkan role
    data = response.data
    if current_user.get("role") == "kader":
        user_posyandu_id = current_user.get("posyandu_id")
        if not user_posyandu_id:
            # Jika kader belum punya posyandu, return empty array (bukan error)
            print(f"⚠️ Kader {current_user.get('email')} belum memiliki posyandu_id")
            return []
        # Filter hanya data dari posyandu kader
        data = [d for d in data if d.get("balita") and d["balita"].get("posyandu_id") == user_posyandu_id]
    
    # Group by month
    monthly_data = defaultdict(int)
    month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    
    for item in data:
        tgl = datetime.fromisoformat(item["tanggal_pengukuran"].replace("Z", "+00:00"))
        month_key = f"{month_names[tgl.month - 1]} {tgl.year}"
        monthly_data[month_key] += 1
    
    # Generate 6 bulan terakhir dengan default 0
    result = []
    for i in range(5, -1, -1):  # 5 bulan lalu sampai bulan ini
        target_date = now - timedelta(days=30 * i)
        month_key = f"{month_names[target_date.month - 1]} {target_date.year}"
        result.append({
            "bulan": month_key,
            "jumlah": monthly_data.get(month_key, 0)
        })
    
    return {
        "data": result,
        "total": sum([item["jumlah"] for item in result]),
        "periode": f"{result[0]['bulan']} - {result[-1]['bulan']}"
    }

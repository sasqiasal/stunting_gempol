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
    supabase_client = Depends(get_supabase)
):
    """
    Get summary statistics for dashboard
    """
    try:
        # 1. Total Balita
        query_balita = supabase_client.table("balita").select("id", count="exact")
        
        # Filter by posyandu_id if provided
        if posyandu_id:
            query_balita = query_balita.eq("posyandu_id", posyandu_id)
             
        res_balita = query_balita.execute()
        total_balita = res_balita.count or 0

        # 2. Total Stunting (Status Terkini)
        query_stunting = supabase_client.table("balita").select("id", count="exact")\
            .ilike("status_terkini", "%stunt%")
            
        if posyandu_id:
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
    supabase_client = Depends(get_supabase)
):
    """
    Get riwayat jumlah kasus stunting 6 bulan terakhir
    """
    try:
        # Hitung range 6 bulan ke belakang
        now = datetime.now()
        start_date = now - timedelta(days=180) # Approx 6 months
        
        # Query pengukuran yang stunting
        # Kita cari pengukuran dengan status_gizi stunting
        query = supabase_client.table("pengukuran").select(
            "tanggal_pengukuran, status_gizi, balita_id, balita(posyandu_id)"
        ).gte("tanggal_pengukuran", start_date.isoformat())\
         .ilike("status_gizi", "%stunt%")
        
        response = query.execute()
        data = response.data
        
        # Return all data (client can filter if needed)
        
        # Group by Month
        stats = {}
        # Init 6 bulan terakhir dengan 0
        for i in range(6):
            d = now - timedelta(days=30 * (5-i))
            key = d.strftime("%B %Y") # ex: "August 2025" (English? Locale default)
            # Kita pakai format sederhana dulu
            # Untuk konsistensi, gunakan nama bulan Indonesia manual atau library
            import calendar
            # Simple mapping or rely on frontend formatting? 
            # Doc says: "Agustus 2025"
            bulan_map = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                         "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            mon_idx = d.month - 1
            key_id = f"{bulan_map[mon_idx]} {d.year}"
            stats[key_id] = 0
            
        # Aggregate
        total_cases = 0
        for item in data:
            # Parse date
            tgl = datetime.fromisoformat(item["tanggal_pengukuran"].replace("Z", "+00:00"))
            mon_idx = tgl.month - 1
            key_id = f"{bulan_map[mon_idx]} {tgl.year}"
            
            if key_id in stats:
                stats[key_id] += 1
                total_cases += 1
        
        # Format output
        result_data = []
        for key, val in stats.items():
             result_data.append({"bulan": key, "jumlah": val})
             
        return {
            "data": result_data,
            "summary": {
                "total_kasus": total_cases,
                "periode": "6 Bulan Terakhir"
            }
        }

    except Exception as e:
        print(f"Error creating riwayat stunting: {e}")
        # Return empty safe response instead of 500
        return {"data": [], "summary": {"total_kasus": 0, "periode": "Error"}}

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
    2. Hitung usia saat pengukuran
    3. Hitung Z-Score BB/U dan TB/U
    4. Prediksi stunting menggunakan model KNN
    5. Simpan ke database
    6. Update status_terkini di tabel balita
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
    # Gunakan usia_bulan dari frontend jika ada, atau hitung dari tanggal_lahir
    if pengukuran_data.usia_bulan is not None:
        usia_bulan = pengukuran_data.usia_bulan
    else:
        # Gunakan tanggal pengukuran yang dikirim (untuk input retroaktif), default hari ini
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
    
    try:
        print(f"DEBUG CREATE: Preparing data for balita {pengukuran_data.balita_id}")
        print(f"  Prediction result keys: {prediksi_result.keys()}")
        print(f"  prediksi_stunting type: {type(prediksi_result['prediksi_stunting'])}, value: {prediksi_result['prediksi_stunting']}")
        
        prediksi_stunting_bool = int(prediksi_result["prediksi_stunting"]) >= 2
        print(f"  Converted to boolean: {prediksi_stunting_bool}")
        
        pengukuran_dict.update({
            "kader_id": current_user["id"],
            "usia_bulan": usia_bulan,
            "jenis_kelamin": jenis_kelamin,
            "zscore_bbu": float(prediksi_result["zscore_bbu"]),
            "zscore_tbu": float(prediksi_result["zscore_tbu"]),
            "status_gizi": prediksi_result["status_gizi"],
            "prediksi_stunting": prediksi_stunting_bool,  # Convert to boolean for DB
            "confidence_score": float(prediksi_result["confidence_score"]),
            # Gunakan tanggal pengukuran yang dikirim (retroaktif) atau waktu sekarang
            "tanggal_pengukuran": datetime.combine(tgl_ukur, datetime.min.time()).astimezone().isoformat(),
            "created_at": datetime.now().astimezone().isoformat(),
            # Simpan detail prediksi (termasuk nearest_neighbors)
            "detail_prediksi": {
                "nearest_neighbors": prediksi_result.get("nearest_neighbors", []),
                "version": "1.0", 
                "model": "KNN",
                "k": 5
            }
        })
        print(f"  Updated dict with all fields")
    except Exception as e:
        print(f"ERROR in data preparation: {e}")
        raise HTTPException(status_code=500, detail=f"Error preparing data: {str(e)}")
    
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
    try:
        supabase_client.table("balita").update({
            "status_terkini": prediksi_result["status_gizi"],
            "usia_bulan": usia_bulan
        }).eq("id", pengukuran_data.balita_id).execute()
        print(f"✅ Updated balita status_terkini for balita {pengukuran_data.balita_id}")
    except Exception as e:
        print(f"⚠️ Error updating balita: {e}")
        # Tidak raise error, balita update adalah secondary action
    
    print(f"✅ Successfully created pengukuran ID {pengukuran_id}")
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
    update_dict = {
        "tinggi_badan": float(pengukuran_data.tinggi_badan),
        "berat_badan": float(pengukuran_data.berat_badan),
        "lingkar_lengan": float(pengukuran_data.lingkar_lengan),
        "lingkar_kepala": float(pengukuran_data.lingkar_kepala),
        "catatan": pengukuran_data.catatan,
        "usia_bulan": usia_bulan,
        "zscore_bbu": float(prediksi_result["zscore_bbu"]),
        "zscore_tbu": float(prediksi_result["zscore_tbu"]),
        "status_gizi": prediksi_result["status_gizi"],
        "prediksi_stunting": int(prediksi_result["prediksi_stunting"]) >= 2,  # Convert to boolean for DB
        "confidence_score": float(prediksi_result["confidence_score"]),
    }

    try:
        print(f"DEBUG UPDATE: Updating pengukuran ID {id}")
        print(f"  prediksi_stunting raw: {prediksi_result['prediksi_stunting']} (type: {type(prediksi_result['prediksi_stunting'])})")
        print(f"  update_dict keys: {update_dict.keys()}")
        
        response = supabase_client.table("pengukuran").update(update_dict).eq("id", id).execute()
        
        if not response.data:
            print(f"ERROR UPDATE: No data returned from update. Response: {response}")
            raise HTTPException(status_code=500, detail="Gagal mengupdate data pengukuran")

        updated_pengukuran = response.data[0]
        print(f"✅ Update successful for ID {id}")
        print(f"  Returned fields: {updated_pengukuran.keys() if isinstance(updated_pengukuran, dict) else 'not a dict'}")

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
    limit: int = Query(100, ge=1, le=99999),
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
        
        # Filter berdasarkan prediksi stunting
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
        
        # Pagination & Ordering
        # Sort by: 1) tanggal_pengukuran DESC, 2) created_at DESC (untuk data same-day)
        query = query.range(skip, skip + limit - 1).order("tanggal_pengukuran", desc=True).order("created_at", desc=True)
        
        response = query.execute()
        print(f"✅ Query executed successfully, got {len(response.data)} records")
        
        # Transform data untuk response
        results = []
        for item in response.data:
            result = {**item}
            
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
    
    # Query untuk stunting
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
    
    # Query pengukuran dengan filter stunting = true dan 6 bulan terakhir
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

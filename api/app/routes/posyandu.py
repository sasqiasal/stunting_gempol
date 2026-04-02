"""
Routes untuk Posyandu
- CRUD Posyandu
- Get data spasial GeoJSON
- Get statistik per posyandu
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.posyandu import (
    PosyanduCreate,
    PosyanduUpdate,
    PosyanduResponse,
    PosyanduGeoJSONCollection
)
from app.utils.auth import get_current_user, get_current_admin
from app.database import get_supabase

router = APIRouter(prefix="/posyandu", tags=["Posyandu"])

@router.post("/", response_model=PosyanduResponse, status_code=status.HTTP_201_CREATED)
async def create_posyandu(
    posyandu_data: PosyanduCreate,
    current_user: dict = Depends(get_current_admin),
    supabase_client = Depends(get_supabase)
):
    """
    Menambahkan posyandu baru (hanya Admin)
    """
    # Insert posyandu
    posyandu_dict = posyandu_data.model_dump()
    
    # Buat point geometry untuk PostGIS
    posyandu_dict["geom"] = f"POINT({posyandu_dict['longitude']} {posyandu_dict['latitude']})"
    
    response = supabase_client.table("posyandu").insert(posyandu_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create posyandu"
        )
    
    return response.data[0]

@router.get("/", response_model=List[PosyanduResponse])
async def get_all_posyandu(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=99999),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan semua data posyandu dengan statistik (Public access untuk peta)
    
    LOGIKA PENGHITUNGAN STUNTING:
    1. Prioritas: Hitung dari pengukuran BULAN TERKINI (April 2024)
    2. Fallback: Jika tidak ada pengukuran bulan ini, gunakan status_terkini
    
    Contoh:
    - Posyandu Ceria Maret: 2 stunting
    - April: Belum ada pengukuran → Tampil 2 (fallback)
    - April: Ada 1 pengukuran stunting baru → Tampil 1 (dari data April saja)
    """
    from datetime import datetime
    
    # Query posyandu dengan count balita
    query = supabase_client.table("posyandu").select(
        "*, balita(count)"
    ).range(skip, skip + limit - 1).order("nama")
    
    response = query.execute()
    
    # Hitung awal bulan terkini
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Tambahkan statistik stunting per posyandu
    results = []
    for posyandu in response.data:
        posyandu_id = posyandu["id"]
        
        # Count total balita di posyandu ini
        balita_response = supabase_client.table("balita").select(
            "id", count="exact"
        ).eq("posyandu_id", posyandu_id).execute()
        
        jumlah_balita = balita_response.count or 0
        
        # Get all balita_id dari posyandu ini
        balita_ids_response = supabase_client.table("balita").select(
            "id, status_terkini"
        ).eq("posyandu_id", posyandu_id).execute()
        balita_ids = [b["id"] for b in balita_ids_response.data] if balita_ids_response.data else []
        balita_data = {b["id"]: b["status_terkini"] for b in balita_ids_response.data} if balita_ids_response.data else {}
        
        jumlah_stunting = 0
        jumlah_pengukuran_bulan_ini = 0
        
        if balita_ids:
            # PRIORITAS 1: Cek pengukuran bulan terkini
            try:
                pengukuran_response = supabase_client.table("pengukuran").select(
                    "*"
                ).in_("balita_id", balita_ids).gte("tanggal_pengukuran", first_day_of_month.isoformat()).execute()
                
                jumlah_pengukuran_bulan_ini = len(pengukuran_response.data) if pengukuran_response.data else 0
                
                if jumlah_pengukuran_bulan_ini > 0 and pengukuran_response.data:
                    # Ada pengukuran bulan ini → hitung stunting dari sini saja
                    # Stunting = status_gizi_label in (2, 3) atau prediksi_stunting = true
                    balita_stunting_bulan_ini = set()
                    for pengukuran in pengukuran_response.data:
                        # Priority: status_gizi_label (2, 3) = stunting
                        if pengukuran.get("status_gizi_label") in (2, 3):
                            balita_stunting_bulan_ini.add(pengukuran["balita_id"])
                        # Fallback: prediksi_stunting = true
                        elif pengukuran.get("prediksi_stunting") == True:
                            balita_stunting_bulan_ini.add(pengukuran["balita_id"])
                    
                    jumlah_stunting = len(balita_stunting_bulan_ini)
                else:
                    # FALLBACK: Tidak ada pengukuran bulan ini → gunakan status_terkini
                    for balita_id, status in balita_data.items():
                        if status and "stunt" in status.lower():
                            jumlah_stunting += 1
            except Exception as e:
                # Fallback jika ada error query
                print(f"⚠️ Error querying pengukuran: {e}")
                for balita_id, status in balita_data.items():
                    if status and "stunt" in status.lower():
                        jumlah_stunting += 1
        
        result = {**posyandu}
        result["jumlah_balita"] = jumlah_balita
        result["jumlah_stunting"] = jumlah_stunting
        result["jumlah_pengukuran_bulan_ini"] = jumlah_pengukuran_bulan_ini
        
        results.append(result)
    
    return results

@router.get("/geojson", response_model=PosyanduGeoJSONCollection)
async def get_posyandu_geojson(
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan data posyandu dalam format GeoJSON untuk peta (Public access)
    
    LOGIKA PENGHITUNGAN STUNTING:
    1. Prioritas: Hitung dari pengukuran BULAN TERKINI (April 2024)
    2. Fallback: Jika tidak ada pengukuran bulan ini, gunakan status_terkini
    """
    from datetime import datetime
    
    # Query posyandu dengan statistik
    response = supabase_client.table("posyandu").select("*").execute()
    
    # Hitung awal bulan terkini
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    features = []
    
    for posyandu in response.data:
        # Count total balita di posyandu ini
        balita_response = supabase_client.table("balita").select(
            "id, status_terkini", count="exact"
        ).eq("posyandu_id", posyandu["id"]).execute()
        
        jumlah_balita = balita_response.count or 0
        balita_ids = [b["id"] for b in balita_response.data] if balita_response.data else []
        balita_data = {b["id"]: b["status_terkini"] for b in balita_response.data} if balita_response.data else {}
        
        jumlah_stunting = 0
        
        if balita_ids:
            # PRIORITAS 1: Cek pengukuran bulan terkini
            try:
                pengukuran_response = supabase_client.table("pengukuran").select(
                    "*"
                ).in_("balita_id", balita_ids).gte("tanggal_pengukuran", first_day_of_month.isoformat()).execute()
                
                jumlah_pengukuran_bulan_ini = len(pengukuran_response.data) if pengukuran_response.data else 0
                
                if jumlah_pengukuran_bulan_ini > 0 and pengukuran_response.data:
                    # Ada pengukuran bulan ini → hitung stunting dari sini saja
                    balita_stunting_bulan_ini = set()
                    for pengukuran in pengukuran_response.data:
                        # Priority: status_gizi_label (2, 3) = stunting
                        if pengukuran.get("status_gizi_label") in (2, 3):
                            balita_stunting_bulan_ini.add(pengukuran["balita_id"])
                        # Fallback: prediksi_stunting = true
                        elif pengukuran.get("prediksi_stunting") == True:
                            balita_stunting_bulan_ini.add(pengukuran["balita_id"])
                    
                    jumlah_stunting = len(balita_stunting_bulan_ini)
                else:
                    # FALLBACK: Tidak ada pengukuran bulan ini → gunakan status_terkini
                    for balita_id, status in balita_data.items():
                        if status and "stunt" in status.lower():
                            jumlah_stunting += 1
            except Exception as e:
                # Fallback jika ada error query
                print(f"⚠️ Error querying pengukuran: {e}")
                for balita_id, status in balita_data.items():
                    if status and "stunt" in status.lower():
                        jumlah_stunting += 1
        
        persentase_stunting = (jumlah_stunting / jumlah_balita * 100) if jumlah_balita > 0 else 0
        
        # Buat GeoJSON Feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [posyandu["longitude"], posyandu["latitude"]]
            },
            "properties": {
                "id": posyandu["id"],
                "nama": posyandu["nama"],
                "alamat": posyandu["alamat"],
                "kelurahan": posyandu["kelurahan"],
                "kecamatan": posyandu["kecamatan"],
                "kader_penanggungjawab": posyandu.get("kader_penanggungjawab"),
                "jumlah_balita": jumlah_balita,
                "jumlah_stunting": jumlah_stunting,
                "persentase_stunting": round(persentase_stunting, 2)
            }
        }
        
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/{posyandu_id}", response_model=PosyanduResponse)
async def get_posyandu(
    posyandu_id: int,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan detail posyandu berdasarkan ID
    
    LOGIKA PENGHITUNGAN STUNTING:
    1. Prioritas: Hitung dari pengukuran BULAN TERKINI
    2. Fallback: Jika tidak ada pengukuran bulan ini, gunakan status_terkini
    """
    from datetime import datetime
    
    response = supabase_client.table("posyandu").select("*").eq("id", posyandu_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posyandu not found"
        )
    
    posyandu = response.data[0]
    
    # Hitung awal bulan terkini
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get balita di posyandu ini
    balita_response = supabase_client.table("balita").select(
        "id, status_terkini", count="exact"
    ).eq("posyandu_id", posyandu_id).execute()
    
    jumlah_balita = balita_response.count or 0
    balita_ids = [b["id"] for b in balita_response.data] if balita_response.data else []
    balita_data = {b["id"]: b["status_terkini"] for b in balita_response.data} if balita_response.data else {}
    
    jumlah_stunting = 0
    
    if balita_ids:
        # PRIORITAS 1: Cek pengukuran bulan terkini
        try:
            pengukuran_response = supabase_client.table("pengukuran").select(
                "*"
            ).in_("balita_id", balita_ids).gte("tanggal_pengukuran", first_day_of_month.isoformat()).execute()
            
            jumlah_pengukuran_bulan_ini = len(pengukuran_response.data) if pengukuran_response.data else 0
            
            if jumlah_pengukuran_bulan_ini > 0 and pengukuran_response.data:
                # Ada pengukuran bulan ini → hitung stunting dari sini saja
                balita_stunting_bulan_ini = set()
                for pengukuran in pengukuran_response.data:
                    # Priority: status_gizi_label (2, 3) = stunting
                    if pengukuran.get("status_gizi_label") in (2, 3):
                        balita_stunting_bulan_ini.add(pengukuran["balita_id"])
                    # Fallback: prediksi_stunting = true
                    elif pengukuran.get("prediksi_stunting") == True:
                        balita_stunting_bulan_ini.add(pengukuran["balita_id"])
                
                jumlah_stunting = len(balita_stunting_bulan_ini)
            else:
                # FALLBACK: Tidak ada pengukuran bulan ini → gunakan status_terkini
                for balita_id, status in balita_data.items():
                    if status and "stunt" in status.lower():
                        jumlah_stunting += 1
        except Exception as e:
            # Fallback jika ada error query
            print(f"⚠️ Error querying pengukuran: {e}")
            for balita_id, status in balita_data.items():
                if status and "stunt" in status.lower():
                    jumlah_stunting += 1
    
    posyandu["jumlah_balita"] = jumlah_balita
    posyandu["jumlah_stunting"] = jumlah_stunting
    
    return posyandu

@router.put("/{posyandu_id}", response_model=PosyanduResponse)
async def update_posyandu(
    posyandu_id: int,
    posyandu_data: PosyanduUpdate,
    current_user: dict = Depends(get_current_admin),
    supabase_client = Depends(get_supabase)
):
    """
    Update data posyandu (hanya Admin)
    """
    # Cek apakah posyandu exists
    existing = supabase_client.table("posyandu").select("*").eq("id", posyandu_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posyandu not found"
        )
    
    # Update hanya field yang dikirim
    update_dict = posyandu_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Update geometry jika latitude/longitude berubah
    if "latitude" in update_dict or "longitude" in update_dict:
        old_data = existing.data[0]
        lat = update_dict.get("latitude", old_data["latitude"])
        lon = update_dict.get("longitude", old_data["longitude"])
        update_dict["geom"] = f"POINT({lon} {lat})"
    
    response = supabase_client.table("posyandu").update(update_dict).eq("id", posyandu_id).execute()
    
    return response.data[0]

@router.delete("/{posyandu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_posyandu(
    posyandu_id: int,
    current_user: dict = Depends(get_current_admin),
    supabase_client = Depends(get_supabase)
):
    """
    Hapus posyandu (hanya Admin)
    """
    # Cek apakah posyandu exists
    existing = supabase_client.table("posyandu").select("id").eq("id", posyandu_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posyandu not found"
        )
    
    # Delete
    supabase_client.table("posyandu").delete().eq("id", posyandu_id).execute()
    
    return None

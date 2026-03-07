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
    limit: int = Query(100, ge=1, le=500),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan semua data posyandu dengan statistik (Public access untuk peta)
    """
    # Query posyandu dengan count balita
    query = supabase_client.table("posyandu").select(
        "*, balita(count)"
    ).range(skip, skip + limit - 1).order("nama")
    
    response = query.execute()
    
    # Tambahkan statistik stunting per posyandu
    results = []
    for posyandu in response.data:
        posyandu_id = posyandu["id"]
        
        # Count total balita di posyandu ini
        balita_response = supabase_client.table("balita").select(
            "id", count="exact"
        ).eq("posyandu_id", posyandu_id).execute()
        
        # Count balita stunting di posyandu ini
        # Gunakan %stunt% agar mencakup "Stunting", "Severely Stunted", dll
        stunting_response = supabase_client.table("balita").select(
            "id", count="exact"
        ).eq("posyandu_id", posyandu_id).ilike("status_terkini", "%stunt%").execute()
        
        # Count pengukuran bulan ini
        # Karena pengukuran tidak punya posyandu_id, kita hitung dari balita di posyandu ini
        from datetime import datetime, timedelta
        # Gunakan awal bulan dari waktu saat ini
        now = datetime.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all balita_id dari posyandu ini
        balita_ids_response = supabase_client.table("balita").select("id").eq("posyandu_id", posyandu_id).execute()
        balita_ids = [b["id"] for b in balita_ids_response.data] if balita_ids_response.data else []
        
        # Count pengukuran dari balita-balita tersebut
        jumlah_pengukuran_bulan_ini = 0
        if balita_ids:
            pengukuran_response = supabase_client.table("pengukuran").select(
                "id", count="exact"
            ).in_("balita_id", balita_ids).gte("tanggal_pengukuran", first_day_of_month.isoformat()).execute()
            jumlah_pengukuran_bulan_ini = pengukuran_response.count or 0
        
        jumlah_balita = balita_response.count or 0
        jumlah_stunting = stunting_response.count or 0
        
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
    """
    # Query posyandu dengan statistik
    response = supabase_client.table("posyandu").select("*").execute()
    
    features = []
    
    for posyandu in response.data:
        # Count balita dan stunting
        balita_response = supabase_client.table("balita").select(
            "id", count="exact"
        ).eq("posyandu_id", posyandu["id"]).execute()
        
        stunting_response = supabase_client.table("balita").select(
            "id", count="exact"
        ).eq("posyandu_id", posyandu["id"]).ilike("status_terkini", "%stunting%").execute()
        
        jumlah_balita = balita_response.count or 0
        jumlah_stunting = stunting_response.count or 0
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
    """
    response = supabase_client.table("posyandu").select("*").eq("id", posyandu_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posyandu not found"
        )
    
    posyandu = response.data[0]
    
    # Tambahkan statistik
    balita_response = supabase_client.table("balita").select(
        "id", count="exact"
    ).eq("posyandu_id", posyandu_id).execute()
    
    stunting_response = supabase_client.table("balita").select(
        "id", count="exact"
    ).eq("posyandu_id", posyandu_id).ilike("status_terkini", "%stunting%").execute()
    
    posyandu["jumlah_balita"] = balita_response.count or 0
    posyandu["jumlah_stunting"] = stunting_response.count or 0
    
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

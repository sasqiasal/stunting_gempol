"""
Routes untuk mendapatkan nearest neighbors dengan k value yang berbeda
Endpoint untuk menampilkan tetangga terdekat pada riwayat prediksi dengan k-selector
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.utils.auth import get_current_user
from app.database import get_supabase
from app.ml.knn_model import get_knn_model
import numpy as np

router = APIRouter(prefix="/neighbors", tags=["Neighbors"])


@router.get("/by-k/{pengukuran_id}", response_model=Dict[str, Any])
async def get_neighbors_by_k_value(
    pengukuran_id: int,
    k: int = 5,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    === ENDPOINT GET NEIGHBORS WITH K-VALUE ===
    
    Get nearest neighbors dengan k value tertentu untuk pengukuran yang spesifik
    
    Parameters:
    - pengukuran_id: ID dari pengukuran/prediksi
    - k: K value untuk jumlah tetangga terdekat (3, 5, 7, 9)
    
    Returns:
    - List of k nearest neighbors dengan data lengkap (jenis_kelamin, usia_bulan, dll)
    - Distance dari setiap neighbor
    - Status stunting dari setiap neighbor
    """
    try:
        # Validasi k value
        valid_k_values = [3, 5, 7, 9, 10]
        if k not in valid_k_values:
            raise HTTPException(
                status_code=400,
                detail=f"K value harus salah satu dari {valid_k_values}"
            )
        
        # 1. Fetch pengukuran data
        response = supabase_client.table("pengukuran").select(
            "*,balita(nama,tanggal_lahir),kader(nama)"
        ).eq("id", pengukuran_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Pengukuran dengan ID {pengukuran_id} tidak ditemukan"
            )
        
        pengukuran = response.data[0]
        
        # Role-based access control (kader hanya bisa lihat data posyandunya)
        if current_user.get("role") == "kader":
            balita = pengukuran.get("balita", {})
            if isinstance(balita, dict):
                balita_posyandu_id = balita.get("posyandu_id")
            else:
                balita_posyandu_id = None
            
            kader_posyandu_id = current_user.get("posyandu_id")
            if balita_posyandu_id != kader_posyandu_id:
                raise HTTPException(
                    status_code=403,
                    detail="Anda tidak memiliki akses ke data ini"
                )
        
        # 2. Prepare fitur dari pengukuran
        try:
            jenis_kelamin = pengukuran["jenis_kelamin"]
            usia_bulan = pengukuran["usia_bulan"]
            berat_badan = pengukuran["berat_badan"]
            tinggi_badan = pengukuran["tinggi_badan"]
            lingkar_lengan = pengukuran["lingkar_lengan"]
            lingkar_kepala = pengukuran["lingkar_kepala"]
            
            # Get model
            model = get_knn_model()
            
            # Prepare features
            features = model.prepare_features(
                jenis_kelamin=jenis_kelamin,
                usia_bulan=usia_bulan,
                berat_badan=berat_badan,
                tinggi_badan=tinggi_badan,
                lingkar_lengan=lingkar_lengan,
                lingkar_kepala=lingkar_kepala
            )
            
            # 3. Find nearest neighbors dengan k value yang diberikan
            neighbors = model.find_nearest_neighbors(features, n_neighbors=k)
            
            # 4. Format response
            formatted_neighbors = []
            for idx, neighbor in enumerate(neighbors, 1):
                formatted_neighbors.append({
                    "no": idx,
                    "jenis_kelamin": neighbor.get("jenis_kelamin", ""),
                    "usia_bulan": neighbor.get("usia_bulan", 0),
                    "tinggi_badan": float(neighbor.get("tinggi_badan", 0)),
                    "berat_badan": float(neighbor.get("berat_badan", 0)),
                    "lingkar_lengan": float(neighbor.get("lingkar_lengan", 0)),
                    "lingkar_kepala": float(neighbor.get("lingkar_kepala", 0)),
                    "status_stunting": neighbor.get("label", ""),
                    "distance": float(neighbor.get("distance", 0))
                })
            
            return {
                "status": "success",
                "data": {
                    "pengukuran_id": pengukuran_id,
                    "k_value": k,
                    "neighbors": formatted_neighbors,
                    "total_neighbors": len(formatted_neighbors)
                }
            }
            
        except Exception as e:
            print(f"Error in feature preparation or neighbor finding: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error mencari tetangga terdekat: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR IN /neighbors/by-k ENDPOINT: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil tetangga terdekat: {str(e)}"
        )

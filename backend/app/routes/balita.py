"""
Routes untuk Balita
- CRUD Balita
- Get balita dengan riwayat pengukuran
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from app.models.balita import BalitaCreate, BalitaUpdate, BalitaResponse
from app.utils.auth import get_current_user
from app.utils.helpers import calculate_age_in_months
from app.database import get_supabase

router = APIRouter(prefix="/balita", tags=["Balita"])

@router.post("/", response_model=BalitaResponse, status_code=status.HTTP_201_CREATED)
async def create_balita(
    balita_data: BalitaCreate,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Menambahkan data balita baru
    
    - Kader: Otomatis menggunakan posyandu_id dari akun mereka
    - Admin: Bisa menentukan posyandu_id atau tidak
    """
    # Cek apakah NIK sudah terdaftar
    existing = supabase_client.table("balita").select("nik").eq("nik", balita_data.nik).execute()
    
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NIK already registered"
        )
    
    # Hitung usia saat ini
    usia_bulan = calculate_age_in_months(balita_data.tanggal_lahir)
    
    # Insert balita
    balita_dict = balita_data.model_dump()
    balita_dict["usia_bulan"] = usia_bulan
    
    # Convert date to string for JSON serialization
    if "tanggal_lahir" in balita_dict:
        balita_dict["tanggal_lahir"] = str(balita_dict["tanggal_lahir"])
    
    # Jika user adalah kader, gunakan posyandu_id mereka
    if current_user.get("role") == "kader":
        user_posyandu_id = current_user.get("posyandu_id")
        if not user_posyandu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kader belum memiliki posyandu yang ditugaskan. Silakan hubungi admin untuk set posyandu."
            )
        balita_dict["posyandu_id"] = user_posyandu_id
    
    response = supabase_client.table("balita").insert(balita_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create balita"
        )
    
    return response.data[0]

@router.get("/", response_model=List[BalitaResponse])
async def get_all_balita(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    posyandu_id: Optional[int] = None,
    status_terkini: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan semua data balita dengan pagination dan filter
    
    - Kader: Hanya bisa melihat balita dari posyandu mereka sendiri
    - Admin: Bisa melihat semua balita atau filter berdasarkan posyandu_id
    """
    print(f"🔍 GET /balita - User: {current_user.get('email')} ({current_user.get('role')})")
    
    try:
        query = supabase_client.table("balita").select("*")
        
        # Jika user adalah kader, filter otomatis berdasarkan posyandu_id mereka
        if current_user.get("role") == "kader":
            user_posyandu_id = current_user.get("posyandu_id")
            if not user_posyandu_id:
                # Jika kader belum punya posyandu, return empty array
                print(f"⚠️ Kader {current_user.get('email')} belum memiliki posyandu_id")
                return []
            query = query.eq("posyandu_id", user_posyandu_id)
        else:
            # Admin bisa filter berdasarkan posyandu_id jika diberikan
            if posyandu_id:
                query = query.eq("posyandu_id", posyandu_id)
        
        # Filter berdasarkan status
        if status_terkini:
            query = query.ilike("status_terkini", f"%{status_terkini}%")
        
        # Pagination
        query = query.range(skip, skip + limit - 1).order("created_at", desc=True)
        
        response = query.execute()
        
        # Hitung ulang usia_bulan berdasarkan tanggal_lahir (agar selalu up-to-date)
        today = date.today()
        for balita in response.data:
            if balita.get("tanggal_lahir"):
                balita["usia_bulan"] = calculate_age_in_months(
                    date.fromisoformat(balita["tanggal_lahir"]),
                    today
                )
        
        print(f"✅ Query executed successfully, got {len(response.data)} records")
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_all_balita: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@router.get("/{balita_id}", response_model=BalitaResponse)
async def get_balita(
    balita_id: int,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Mendapatkan detail balita berdasarkan ID
    """
    response = supabase_client.table("balita").select("*").eq("id", balita_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balita not found"
        )
    
    balita = response.data[0]
    
    # Update usia bulan
    usia_bulan = calculate_age_in_months(date.fromisoformat(balita["tanggal_lahir"]))
    balita["usia_bulan"] = usia_bulan
    
    return balita

@router.put("/{balita_id}", response_model=BalitaResponse)
async def update_balita(
    balita_id: int,
    balita_data: BalitaUpdate,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Update data balita
    """
    # Cek apakah balita exists
    existing = supabase_client.table("balita").select("*").eq("id", balita_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balita not found"
        )
    
    # Update hanya field yang dikirim
    update_dict = balita_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    response = supabase_client.table("balita").update(update_dict).eq("id", balita_id).execute()
    
    return response.data[0]

@router.delete("/{balita_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_balita(
    balita_id: int,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Hapus data balita (soft delete dengan mengubah is_active = False)
    """
    # Cek apakah balita exists
    existing = supabase_client.table("balita").select("id").eq("id", balita_id).execute()
    
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Balita not found"
        )
    
    # Soft delete
    supabase_client.table("balita").delete().eq("id", balita_id).execute()
    
    return None

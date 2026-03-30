"""
Routes untuk Manajemen Akun (Admin Only)
- Get Login Logs (Audit Trail)
- Create New User (menggunakan Supabase Admin API)
- Save Login Log
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.auth import get_current_user
from app.database import get_supabase, get_supabase_admin
from app.config import get_settings
from supabase import create_client, Client

router = APIRouter(prefix="/akun", tags=["Akun Management"])
settings = get_settings()

# ============================================================================
# Pydantic Models
# ============================================================================

class LoginLogResponse(BaseModel):
    """Response model untuk login log"""
    id: int
    user_id: int
    user_name: str
    user_email: str
    user_role: str
    login_timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class LoginLogCreate(BaseModel):
    """Model untuk create login log"""
    user_id: int
    user_name: str
    user_email: str
    user_role: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class CreateUserRequest(BaseModel):
    """Model untuk create user baru"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password minimal 6 karakter")
    nama_lengkap: str = Field(..., min_length=3, description="Nama lengkap minimal 3 karakter")
    role: str = Field(..., description="Role: admin atau kader")
    posyandu_id: Optional[int] = Field(None, description="ID Posyandu (wajib jika role=kader)")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['admin', 'kader']:
            raise ValueError('Role harus admin atau kader')
        return v
    
    @field_validator('posyandu_id')
    @classmethod
    def validate_posyandu_id(cls, v, info):
        # Jika role adalah kader, posyandu_id wajib diisi
        if info.data.get('role') == 'kader' and v is None:
            raise ValueError('Posyandu ID wajib diisi untuk role kader')
        return v

class CreateUserResponse(BaseModel):
    """Response model setelah create user"""
    success: bool
    message: str
    user: Dict[str, Any]

# ============================================================================
# Helper Functions
# ============================================================================

def get_supabase_admin() -> Client:
    """
    Get Supabase client dengan Service Key (Admin privileges)
    Untuk operasi admin seperti create user di auth.users
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def verify_admin(current_user: dict):
    """Helper untuk memverifikasi user adalah admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin yang dapat mengakses fitur ini"
        )

# ============================================================================
# Endpoints
# ============================================================================

@router.get("/login-logs", response_model=List[LoginLogResponse])
async def get_login_logs(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """
    Get semua login logs (Admin only)
    
    Returns:
        List of login logs diurutkan dari yang terbaru
    """
    # Verifikasi admin
    verify_admin(current_user)
    
    # Gunakan Service Role client untuk bypass RLS
    supabase_admin = get_supabase_admin()
    
    try:
        # Query login logs dengan admin client
        response = supabase_admin.table("login_logs")\
            .select("*")\
            .order("login_timestamp", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
        
    except Exception as e:
        error_msg = str(e)
        # Jika tabel belum dibuat, return empty list
        if "login_logs" in error_msg.lower() or "does not exist" in error_msg.lower():
            return []
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error mengambil login logs: {str(e)}"
        )

@router.post("/login-logs", status_code=status.HTTP_201_CREATED)
async def save_login_log(
    log_data: LoginLogCreate,
    request: Request
):
    """
    Save login log ke database
    Dipanggil setiap kali user berhasil login
    
    Note: Endpoint ini tidak perlu authentication karena dipanggil saat login
    """
    # Gunakan Service Role client untuk bypass RLS
    supabase_admin = get_supabase_admin()
    
    try:
        # Ambil IP dan User Agent dari request jika tidak disediakan
        if not log_data.ip_address:
            log_data.ip_address = request.client.host if request.client else None
        
        if not log_data.user_agent:
            log_data.user_agent = request.headers.get("user-agent")
        
        # Insert ke database dengan admin client
        log_dict = log_data.model_dump()
        # Gunakan waktu server dengan timezone (aware)
        log_dict["login_timestamp"] = datetime.now().astimezone().isoformat()
        
        response = supabase_admin.table("login_logs").insert(log_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal menyimpan login log"
            )
        
        return {
            "success": True,
            "message": "Login log berhasil disimpan",
            "data": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Jangan fail request jika log gagal
        print(f"Warning: Gagal menyimpan login log: {str(e)}")
        return {
            "success": False,
            "message": "Login log gagal disimpan",
            "error": str(e)
        }

@router.post("/create-user", response_model=CreateUserResponse)
async def create_new_user(
    user_data: CreateUserRequest,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Create user baru (Admin only)
    
    Password disimpan sebagai hashed_password di database
    TIDAK menggunakan Supabase Auth
    """
    # Verifikasi admin
    verify_admin(current_user)
    
    print(f"🔍 CREATE USER Request:")
    print(f"  - Email: {user_data.email}")
    print(f"  - Nama: {user_data.nama_lengkap}")
    print(f"  - Role: {user_data.role}")
    print(f"  - Posyandu ID: {user_data.posyandu_id}")
    
    try:
        # 1. Cek apakah email sudah terdaftar
        existing = supabase_client.table("users")\
            .select("email")\
            .eq("email", user_data.email)\
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user_data.email} sudah terdaftar. Gunakan email lain."
            )
        
        # 2. Jika role=kader, validasi posyandu exists
        if user_data.role == 'kader' and user_data.posyandu_id:
            posyandu = supabase_client.table("posyandu")\
                .select("id, nama")\
                .eq("id", user_data.posyandu_id)\
                .execute()
            
            if not posyandu.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Posyandu dengan ID {user_data.posyandu_id} tidak ditemukan"
                )
        
        # 3. Hash password
        from app.utils.auth import hash_password
        hashed_password = hash_password(user_data.password)
        print(f"🔐 Password hashed successfully")
        
        # 4. Insert user ke database
        user_dict = {
            "email": user_data.email,
            "nama_lengkap": user_data.nama_lengkap,
            "role": user_data.role,
            "hashed_password": hashed_password
        }
        
        # Tambahkan posyandu_id jika role=kader
        if user_data.role == 'kader' and user_data.posyandu_id:
            user_dict["posyandu_id"] = user_data.posyandu_id
        
        print(f"💾 Inserting to database: {user_dict['email']}")
        
        db_response = supabase_client.table("users").insert(user_dict).execute()
        
        print(f"✅ User created successfully in database")
        
        if not db_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal menyimpan user ke database"
            )
        
        created_user = db_response.data[0]
        
        return CreateUserResponse(
            success=True,
            message=f"User {user_data.nama_lengkap} berhasil dibuat",
            user={
                "id": created_user["id"],
                "email": created_user["email"],
                "nama_lengkap": created_user["nama_lengkap"],
                "role": created_user["role"],
                "posyandu_id": created_user.get("posyandu_id"),
                "created_at": created_user["created_at"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in create_new_user: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tidak terduga: {str(e)}"
        )

@router.get("/users")
async def get_all_users(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Get daftar semua user dengan informasi posyandu (Admin only)
    
    Returns:
        List of users dengan detail posyandu
    """
    verify_admin(current_user)
    
    try:
        # Query users dengan join posyandu
        response = supabase_client.table("users")\
            .select("id, email, nama_lengkap, role, posyandu_id, is_active, created_at, posyandu:posyandu_id(id, nama, alamat)")\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error mengambil daftar user: {str(e)}"
        )

class ResetPasswordRequest(BaseModel):
    """Model untuk reset password user"""
    user_id: int = Field(..., description="ID user yang akan direset passwordnya")
    new_password: str = Field(..., min_length=6, description="Password baru minimal 6 karakter")

@router.post("/reset-password")
async def reset_user_password(
    reset_data: ResetPasswordRequest,
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Reset password user (Admin only)
    
    Update hashed_password di database
    """
    verify_admin(current_user)
    
    try:
        # 1. Cek apakah user exists
        user = supabase_client.table("users")\
            .select("id, email, nama_lengkap")\
            .eq("id", reset_data.user_id)\
            .execute()
        
        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User dengan ID {reset_data.user_id} tidak ditemukan"
            )
        
        user_data = user.data[0]
        
        # 2. Hash password baru
        from app.utils.auth import hash_password
        new_hashed_password = hash_password(reset_data.new_password)
        
        # 3. Update hashed_password di database
        update_response = supabase_client.table("users")\
            .update({"hashed_password": new_hashed_password})\
            .eq("id", reset_data.user_id)\
            .execute()
        
        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal update password"
            )
        
        print(f"✅ Password reset successful for user: {user_data['email']}")
        
        return {
            "success": True,
            "message": f"Password untuk {user_data['nama_lengkap']} ({user_data['email']}) berhasil direset"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tidak terduga: {str(e)}"
        )

@router.get("/stats")
async def get_account_stats(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Get statistik akun untuk dashboard admin
    
    Returns:
        - Total users
        - Total admin
        - Total kader
        - Total login hari ini
    """
    verify_admin(current_user)
    
    try:
        # Count total users
        users_response = supabase_client.table("users").select("id, role", count="exact").execute()
        total_users = users_response.count
        
        # Count by role
        users_data = users_response.data
        total_admin = len([u for u in users_data if u["role"] == "admin"])
        total_kader = len([u for u in users_data if u["role"] == "kader"])
        
        # Count login hari ini - gunakan Service Role Key untuk bypass RLS
        login_today = 0
        try:
            from datetime import datetime, timezone
            
            # Get start of today in UTC
            now_utc = datetime.now(timezone.utc)
            today_start = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)
            today_start_iso = today_start.isoformat()
            
            supabase_admin = get_supabase_admin()
            login_response = supabase_admin.table("login_logs")\
                .select("id", count="exact")\
                .gte("login_timestamp", today_start_iso)\
                .execute()
            login_today = login_response.count or 0
        except Exception as e:
            # Tabel login_logs belum ada atau error
            print(f"Warning: Gagal menghitung login hari ini: {str(e)}")
            pass
        
        return {
            "total_users": total_users,
            "total_admin": total_admin,
            "total_kader": total_kader,
            "login_today": login_today
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error mengambil statistik: {str(e)}"
        )


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user account. (Admin Only)"""
    try:
        supabase = get_supabase()
        
        # Check if user exists
        user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")

        # Delete user
        supabase.table('users').delete().eq('id', user_id).execute()

        return {"success": True, "message": "User berhasil dihapus"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}")
async def update_user_admin(user_id: int, user_data: dict):
    """Update user account. (Admin Only)"""
    try:
        supabase = get_supabase()
        
        # Check if user exists
        user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")

        update_data = {
            'nama_lengkap': user_data.get('nama_lengkap'),
            'role': user_data.get('role'),
            'email': user_data.get('email')
        }
        if update_data['role'] == 'kader':
            update_data['posyandu_id'] = user_data.get('posyandu_id')
        else:
            update_data['posyandu_id'] = None

        # Update user
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Gagal mengupdate user")

        return {"success": True, "message": "User berhasil diupdate", "data": result.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

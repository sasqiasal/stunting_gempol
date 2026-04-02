"""
Routes untuk Authentication
- Register
- Login
- Get current user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_supabase
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, supabase_client = Depends(get_supabase)):
    """
    Register user baru (Admin atau Kader)
    """
    # Cek apakah email sudah terdaftar
    existing = supabase_client.table("users").select("email").eq("email", user_data.email).execute()
    
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Insert user baru
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    
    response = supabase_client.table("users").insert(user_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return response.data[0]
@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, supabase_client = Depends(get_supabase)):
    try:
        # 1. Cari user
        response = supabase_client.table("users").select("*").eq("email", credentials.email).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        user = response.data[0]
        
        # 2. Validasi kolom password (Mencegah Error 500 jika kolom kosong/NULL)
        db_password = user.get("hashed_password")
        if not db_password:
            print(f"DEBUG: User {credentials.email} tidak punya hashed_password di DB")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data user tidak lengkap di database (Password NULL)."
            )
        
        # 3. Verifikasi password
        if not verify_password(credentials.password, db_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        # 4. Cek status aktif
        if not user.get("is_active", True):
            raise HTTPException(status_code=403, detail="Akun tidak aktif")

        # 5. Buat token (Pastikan ID dikonversi ke string jika di JWT butuh string)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Tambahkan print debug untuk melihat data sebelum di-encode
        print(f"DEBUG: Login success for user_id: {user['id']}, role: {user['role']}")

        token_payload = {
            "user_id": str(user["id"]), # Konversi ke string untuk keamanan JWT
            "email": user["email"],
            "role": user["role"].lower(), # Paksa huruf kecil sesuai skema DB
            "posyandu_id": user.get("posyandu_id")
        }

        access_token = create_access_token(
            data=token_payload,
            expires_delta=access_token_expires
        )
        
        user_response = {k: v for k, v in user.items() if k != "hashed_password"}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }

    except HTTPException:
        # Re-raise HTTPException tanpa di-wrap (401, 403, dst)
        raise
    except Exception as e:
        # Menangkap error tak terduga (seperti pydantic validation error)
        print(f"ERROR SERIUS DI BACKEND: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan internal: {str(e)}"
        )
        
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Mendapatkan data user yang sedang login
    """
    # Exclude hashed_password
    user_data = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return user_data

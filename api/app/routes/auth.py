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
        print(f"[LOGIN] Attempt for email: {credentials.email}")
        
        # 1. Cari user
        response = supabase_client.table("users").select("*").eq("email", credentials.email).execute()
        print(f"[LOGIN] Query returned {len(response.data) if response.data else 0} user(s)")
        
        if not response.data:
            print(f"[LOGIN] User not found for email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        user = response.data[0]
        print(f"[LOGIN] User found: {user.get('email')}, role: {user.get('role')}")
        
        # 2. Validasi kolom password
        db_password = user.get("hashed_password")
        if not db_password:
            print(f"[LOGIN] ERROR: User {credentials.email} tidak punya hashed_password di DB")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data user tidak lengkap di database (Password NULL)."
            )
        
        print(f"[LOGIN] Found password hash, verifying...")
        
        # 3. Verifikasi password
        if not verify_password(credentials.password, db_password):
            print(f"[LOGIN] Password verification FAILED for {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah"
            )
        
        print(f"[LOGIN] Password verification SUCCESS for {credentials.email}")
        
        # 4. Cek status aktif
        if not user.get("is_active", True):
            print(f"[LOGIN] Account not active for {credentials.email}")
            raise HTTPException(status_code=403, detail="Akun tidak aktif")

        # 5. Buat token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        print(f"[LOGIN] Creating token for user_id: {user['id']}, role: {user['role']}")

        token_payload = {
            "user_id": str(user["id"]),
            "email": user["email"],
            "role": user["role"].lower(),
            "posyandu_id": user.get("posyandu_id")
        }

        access_token = create_access_token(
            data=token_payload,
            expires_delta=access_token_expires
        )
        
        print(f"[LOGIN] Token created successfully")
        
        # Convert user dict to UserResponse model with validation
        try:
            user_response = UserResponse(
                id=user["id"],
                email=user["email"],
                nama_lengkap=user.get("nama_lengkap", ""),
                role=user.get("role", "kader"),
                no_telepon=user.get("no_telepon"),
                alamat=user.get("alamat"),
                posyandu_id=user.get("posyandu_id"),
                is_active=user.get("is_active", True),
                created_at=user.get("created_at"),
                updated_at=user.get("updated_at")
            )
        except Exception as model_error:
            print(f"[LOGIN] ERROR converting to UserResponse: {str(model_error)}")
            raise Exception(f"User data validation error: {str(model_error)}")
        
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

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
    """
    Login user dan mendapatkan JWT token
    Menggunakan hashed_password dari database
    """
    # Cari user berdasarkan email
    response = supabase_client.table("users").select("*").eq("email", credentials.email).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = response.data[0]
    
    # Verifikasi password dengan hashed_password di database
    if not user.get("hashed_password"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User data incomplete. Please contact administrator."
        )
    
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Cek apakah user aktif
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Buat token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "posyandu_id": user.get("posyandu_id")  # Include posyandu_id for kader
        },
        expires_delta=access_token_expires
    )
    
    # Prepare user response (exclude password, include posyandu_id)
    user_response = {k: v for k, v in user.items() if k != "hashed_password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Mendapatkan data user yang sedang login
    """
    # Exclude hashed_password
    user_data = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return user_data

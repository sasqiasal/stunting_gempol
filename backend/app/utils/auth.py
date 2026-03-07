"""
Utilities untuk Authentication dan Authorization
- Hash password
- Verify password
- Create JWT token
- Verify JWT token
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings
from app.models.user import TokenData, UserRole
from app.database import get_supabase

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

def hash_password(password: str) -> str:
    """
    Hash password menggunakan bcrypt
    
    Args:
        password: Password plaintext
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi password
    
    Args:
        plain_password: Password plaintext
        hashed_password: Hashed password dari database
    
    Returns:
        True jika password cocok, False jika tidak
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Membuat JWT access token
    
    Args:
        data: Data yang akan di-encode dalam token
        expires_delta: Waktu kadaluarsa token
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Log untuk debugging
    print(f"Token created at: {datetime.now()}")
    print(f"Token expires at: {expire}")
    print(f"Token lifetime: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes (3 hours)")
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """
    Decode dan verifikasi JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData object
    
    Raises:
        HTTPException jika token tidak valid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None or email is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id, email=email, role=role)
        return token_data
    
    except JWTError:
        raise credentials_exception

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase_client = Depends(get_supabase)
) -> dict:
    """
    Dependency untuk mendapatkan user yang sedang login
    
    Args:
        credentials: HTTP Authorization Bearer token
        supabase_client: Supabase client
    
    Returns:
        User data dictionary
    
    Raises:
        HTTPException jika user tidak valid atau tidak aktif
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    # Get user dari database
    response = supabase_client.table("users").select("*").eq("id", token_data.user_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user = response.data[0]
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency untuk memastikan user adalah Admin
    
    Args:
        current_user: User yang sedang login
    
    Returns:
        User data dictionary
    
    Raises:
        HTTPException jika user bukan admin
    """
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    
    return current_user

async def get_current_kader(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency untuk memastikan user adalah Kader atau Admin
    
    Args:
        current_user: User yang sedang login
    
    Returns:
        User data dictionary
    
    Raises:
        HTTPException jika user bukan kader atau admin
    """
    if current_user.get("role") not in [UserRole.KADER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Kader or Admin access required."
        )
    
    return current_user

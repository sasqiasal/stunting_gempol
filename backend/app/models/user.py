from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """Enum untuk role user"""
    ADMIN = "admin"
    KADER = "kader"

class UserBase(BaseModel):
    """Base model untuk User"""
    email: EmailStr
    nama_lengkap: str
    role: UserRole
    no_telepon: Optional[str] = None
    alamat: Optional[str] = None
    posyandu_id: Optional[int] = None  # ID Posyandu untuk kader

class UserCreate(UserBase):
    """Model untuk registrasi user"""
    password: str

class UserUpdate(BaseModel):
    """Model untuk update user"""
    nama_lengkap: Optional[str] = None
    no_telepon: Optional[str] = None
    alamat: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """Model response user"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Model untuk login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Model untuk JWT token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Model untuk data dalam token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None

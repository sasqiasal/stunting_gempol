from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime

class BalitaBase(BaseModel):
    """Base model untuk Balita"""
    nama_lengkap: str = Field(..., min_length=1, max_length=100)
    nik: str = Field(..., min_length=16, max_length=16)
    jenis_kelamin: Literal["L", "P"] = Field(..., description="L untuk Laki-laki, P untuk Perempuan")
    tanggal_lahir: date
    nama_orang_tua: str
    alamat: str
    posyandu_id: Optional[int] = None
    status: str = Field(default="aktif", description="Status balita: aktif, lulus, pindah")

class BalitaCreate(BalitaBase):
    """Model untuk create balita"""
    pass

class BalitaUpdate(BaseModel):
    """Model untuk update balita"""
    nama_lengkap: Optional[str] = None
    nama_orang_tua: Optional[str] = None
    alamat: Optional[str] = None
    posyandu_id: Optional[int] = None
    status: Optional[Literal["aktif", "lulus", "pindah"]] = None

class BalitaResponse(BalitaBase):
    """Model response balita"""
    id: int
    usia_bulan: int
    status: str = "aktif"
    status_terkini: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

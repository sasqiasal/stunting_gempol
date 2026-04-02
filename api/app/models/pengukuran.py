from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date

class PengukuranBase(BaseModel):
    """Base model untuk Pengukuran"""
    balita_id: int
    tinggi_badan: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    berat_badan: float = Field(..., gt=0, description="Berat badan dalam kg")
    lingkar_lengan: float = Field(..., gt=0, description="Lingkar lengan atas dalam cm")
    lingkar_kepala: float = Field(..., gt=0, description="Lingkar kepala dalam cm")
    catatan: Optional[str] = None

class PengukuranCreate(PengukuranBase):
    """Model untuk create pengukuran"""
    tanggal_pengukuran: Optional[date] = None  # Jika None, pakai tanggal hari ini
    usia_bulan: Optional[int] = None  # Usia saat diukur (opsional, akan dihitung jika tidak ada)

class PengukuranUpdate(BaseModel):
    """Model untuk update pengukuran (hanya field yang bisa diubah)"""
    tinggi_badan: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    berat_badan: float = Field(..., gt=0, description="Berat badan dalam kg")
    lingkar_lengan: float = Field(..., gt=0, description="Lingkar lengan atas dalam cm")
    lingkar_kepala: float = Field(..., gt=0, description="Lingkar kepala dalam cm")
    catatan: Optional[str] = None

class PengukuranResponse(PengukuranBase):
    """Model response pengukuran dengan hasil prediksi"""
    id: int
    kader_id: int
    usia_bulan: Optional[int] = None  # Made optional untuk compatibility dengan older records
    jenis_kelamin: Optional[str] = None  # Made optional untuk compatibility
    zscore_bbu: Optional[float] = None  # Made optional per case
    zscore_tbu: Optional[float] = None  # Made optional per case
    status_gizi: Optional[str] = None  # Made optional per case
    prediksi_stunting: Optional[bool] = None  # Made optional per case
    confidence_score: Optional[float] = None  # Made optional per case
    # Detail prediksi (optional, populated manually or via join if needed)
    # Tidak wajib ada di response standar list, tapi bisa ada di detail
    detail_prediksi: Optional[dict] = None  
    tanggal_pengukuran: Optional[datetime] = None  # Made optional per case
    created_at: Optional[datetime] = None  # Made optional per case


    class Config:
        from_attributes = True
        extra = "allow"  # Allow extra fields from database response

class PengukuranWithBalita(PengukuranResponse):
    """Model response pengukuran dengan data balita"""
    balita_nama: Optional[str] = None
    balita_nik: Optional[str] = None
    posyandu_id: Optional[int] = None
    posyandu_nama: Optional[str] = None

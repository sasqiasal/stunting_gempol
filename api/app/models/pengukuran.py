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

class PengukuranUpdate(BaseModel):
    """Model untuk update pengukuran (hanya field yang bisa diubah)"""
    tinggi_badan: float = Field(..., gt=0, description="Tinggi badan dalam cm")
    berat_badan: float = Field(..., gt=0, description="Berat badan dalam kg")
    lingkar_lengan: float = Field(..., gt=0, description="Lingkar lengan atas dalam cm")
    lingkar_kepala: float = Field(..., gt=0, description="Lingkar kepala dalam cm")
    catatan: Optional[str] = None

class PengukuranResponse(PengukuranBase):
    """Model response pengukuran dengan hasil prediksi (4 kelas)"""
    id: int
    kader_id: int
    usia_bulan: int
    jenis_kelamin: str
    zscore_bbu: float = Field(..., description="Z-Score Berat Badan/Usia")
    zscore_tbu: float = Field(..., description="Z-Score Tinggi Badan/Usia")
    status_gizi: str = Field(..., description="Status Gizi 4 Kelas: Normal+Baik, Normal+Kurang, Stunting+Baik, Stunting+Kurang")
    status_gizi_label: int = Field(..., description="Label integer: 0=Normal+Baik, 1=Normal+Kurang, 2=Stunting+Baik, 3=Stunting+Kurang")
    confidence_score: float
    # Detail prediksi (optional, populated manually or via join if needed)
    # Tidak wajib ada di response standar list, tapi bisa ada di detail
    detail_prediksi: Optional[dict] = None  
    tanggal_pengukuran: datetime
    created_at: datetime
    # Field legacy untuk backward compatibility (deprecated, gunakan status_gizi_label)
    prediksi_stunting: Optional[bool] = None

    class Config:
        from_attributes = True

class PengukuranWithBalita(PengukuranResponse):
    """Model response pengukuran dengan data balita"""
    balita_nama: str
    balita_nik: str
    posyandu_id: Optional[int] = None
    posyandu_nama: Optional[str] = None

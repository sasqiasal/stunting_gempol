"""
COPY-PASTE FILE
File: api/app/routes/laporan.py

Buat file baru dengan nama laporan.py di folder:
api/app/routes/

Kemudian copy-paste semua kode di bawah ini ke file tersebut.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.models import Pengukuran, Balita, Posyandu, User
from app.utils.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/laporan", tags=["Laporan Export"])

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class PengukuranExportSchema(BaseModel):
    """Schema untuk export pengukuran"""
    id: int
    balita_id: int
    balita_nama: str
    balita_nik: str
    jenis_kelamin: str
    tanggal_lahir: str
    posyandu_id: int
    posyandu_nama: str
    tanggal_pengukuran: str
    usia_bulan: int
    tinggi_badan: float
    berat_badan: float
    lingkar_lengan: Optional[float]
    lingkar_kepala: Optional[float]
    zscore_bbu: Optional[float]
    zscore_tbu: Optional[float]
    status_gizi: Optional[str]

    class Config:
        from_attributes = True


class BalitaExportSchema(BaseModel):
    """Schema untuk export balita"""
    id: int
    nama_lengkap: str
    nik: str
    jenis_kelamin: str
    tanggal_lahir: str
    posyandu_id: int

    class Config:
        from_attributes = True


class PosyanduExportSchema(BaseModel):
    """Schema untuk export posyandu"""
    id: int
    nama: str
    alamat: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/pengukuran")
async def get_pengukuran_export(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """
    GET /api/v1/laporan/pengukuran
    
    Kembalikan list pengukuran untuk export laporan
    
    Query Parameters:
    - from_date: Filter dari tanggal (format: YYYY-MM-DD)
    - to_date: Filter sampai tanggal (format: YYYY-MM-DD)
    """
    try:
        query = db.query(Pengukuran).join(Balita).join(Posyandu)
        
        # Filter by posyandu jika user adalah kader
        if current_user.role == "kader" or current_user.role == "Kader":
            query = query.filter(Pengukuran.posyandu_id == current_user.posyandu_id)
        
        # Filter by date range
        if from_date:
            query = query.filter(Pengukuran.tanggal_pengukuran >= from_date)
        if to_date:
            query = query.filter(Pengukuran.tanggal_pengukuran <= to_date)
        
        # Order by tanggal descending
        pengukuran = query.order_by(Pengukuran.tanggal_pengukuran.desc()).all()
        
        # Format response
        result = []
        for p in pengukuran:
            result.append({
                "id": p.id,
                "balita_id": p.balita_id,
                "balita_nama": p.balita.nama_lengkap,
                "balita_nik": p.balita.nik,
                "jenis_kelamin": p.balita.jenis_kelamin,
                "tanggal_lahir": p.balita.tanggal_lahir.strftime("%Y-%m-%d") if p.balita.tanggal_lahir else None,
                "posyandu_id": p.posyandu_id,
                "posyandu_nama": p.posyandu.nama,
                "tanggal_pengukuran": p.tanggal_pengukuran.strftime("%Y-%m-%d") if p.tanggal_pengukuran else None,
                "usia_bulan": p.usia_bulan,
                "tinggi_badan": float(p.tinggi_badan) if p.tinggi_badan else None,
                "berat_badan": float(p.berat_badan) if p.berat_badan else None,
                "lingkar_lengan": float(p.lingkar_lengan) if p.lingkar_lengan else None,
                "lingkar_kepala": float(p.lingkar_kepala) if p.lingkar_kepala else None,
                "zscore_bbu": float(p.zscore_bbu) if p.zscore_bbu else None,
                "zscore_tbu": float(p.zscore_tbu) if p.zscore_tbu else None,
                "status_gizi": p.status_gizi,
            })
        
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balita")
async def get_balita_export(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/v1/laporan/balita
    
    Kembalikan list balita untuk export laporan
    """
    try:
        query = db.query(Balita)
        
        # Filter by posyandu jika user adalah kader
        if current_user.role == "kader" or current_user.role == "Kader":
            query = query.filter(Balita.posyandu_id == current_user.posyandu_id)
        
        balita = query.order_by(Balita.nama_lengkap.asc()).all()
        
        result = []
        for b in balita:
            result.append({
                "id": b.id,
                "nama_lengkap": b.nama_lengkap,
                "nik": b.nik,
                "jenis_kelamin": b.jenis_kelamin,
                "tanggal_lahir": b.tanggal_lahir.strftime("%Y-%m-%d") if b.tanggal_lahir else None,
                "posyandu_id": b.posyandu_id,
            })
        
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posyandu")
async def get_posyandu_export(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/v1/laporan/posyandu
    
    Kembalikan list posyandu untuk export laporan
    """
    try:
        query = db.query(Posyandu)
        
        # Filter by posyandu jika user adalah kader
        if current_user.role == "kader" or current_user.role == "Kader":
            query = query.filter(Posyandu.id == current_user.posyandu_id)
        
        posyandu = query.order_by(Posyandu.nama.asc()).all()
        
        result = []
        for p in posyandu:
            result.append({
                "id": p.id,
                "nama": p.nama,
                "alamat": p.alamat,
            })
        
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

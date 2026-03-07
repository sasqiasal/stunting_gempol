from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PosyanduBase(BaseModel):
    """Base model untuk Posyandu"""
    nama: str = Field(..., min_length=1, max_length=100)
    alamat: str
    kelurahan: str = "Gempol"
    kecamatan: str = "Gempol"
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    kader_penanggungjawab: Optional[str] = None

class PosyanduCreate(PosyanduBase):
    """Model untuk create posyandu"""
    pass

class PosyanduUpdate(BaseModel):
    """Model untuk update posyandu"""
    nama: Optional[str] = None
    alamat: Optional[str] = None
    kelurahan: Optional[str] = None
    kecamatan: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    kader_penanggungjawab: Optional[str] = None

class PosyanduResponse(PosyanduBase):
    """Model response posyandu"""
    id: int
    jumlah_balita: int = 0
    jumlah_stunting: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PosyanduGeoJSON(BaseModel):
    """Model untuk GeoJSON Feature Posyandu"""
    type: str = "Feature"
    geometry: dict
    properties: dict

class PosyanduGeoJSONCollection(BaseModel):
    """Model untuk GeoJSON FeatureCollection"""
    type: str = "FeatureCollection"
    features: List[PosyanduGeoJSON]

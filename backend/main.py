"""
FastAPI Main Application
Sistem Deteksi Dini Stunting Desa Gempol
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes import auth, balita, pengukuran, posyandu, evaluasi, akun
from app.ml.knn_model import knn_model
import os

settings = get_settings()

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="API untuk Sistem Deteksi Dini Stunting dengan Machine Learning KNN",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (untuk frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include Routers
app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(balita.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(pengukuran.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(posyandu.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(evaluasi.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(akun.router, prefix=f"/api/{settings.API_VERSION}")

@app.on_event("startup")
async def startup_event():
    """
    Event yang dijalankan saat aplikasi startup
    Load model KNN jika ada
    """
    print("=" * 60)
    print(f"🚀 Starting {settings.PROJECT_NAME}")
    print(f"📍 Version: {settings.API_VERSION}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print("=" * 60)
    
    # Load model KNN jika file model sudah ada
    model_path = "app/ml/models/knn_stunting_model.pkl"
    if os.path.exists(model_path):
        try:
            knn_model.load_model(model_path)
            print(f"✅ Model KNN berhasil dimuat dari {model_path}")
        except Exception as e:
            print(f"⚠️  Gagal memuat model: {e}")
            print("💡 Model akan menggunakan Z-Score saja untuk prediksi")
    else:
        print(f"⚠️  Model belum tersedia di {model_path}")
        print("💡 Jalankan script train_model.py untuk melatih model")
        print("💡 Sementara, prediksi akan menggunakan Z-Score saja")
    
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Event yang dijalankan saat aplikasi shutdown
    """
    print("=" * 60)
    print("👋 Shutting down application...")
    print("=" * 60)

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Sistem Deteksi Dini Stunting Desa Gempol API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": settings.API_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

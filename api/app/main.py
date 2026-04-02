from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routes import auth, balita, pengukuran, posyandu, evaluasi, akun, knn_global_evaluation
# from app.routes import laporan  # Disabled: SQLAlchemy incompatibility with Python 3.13
from app.ml.knn_model import knn_model
import os

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="API untuk Sistem Deteksi Dini Stunting dengan Machine Learning KNN",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(balita.router, prefix="/api/v1", tags=["Data Balita"])
app.include_router(pengukuran.router, prefix="/api/v1", tags=["Pengukuran & Prediksi"])
app.include_router(posyandu.router, prefix="/api/v1", tags=["Posyandu"])
app.include_router(evaluasi.router, prefix="/api/v1", tags=["Evaluasi Model"])
app.include_router(akun.router, prefix="/api/v1", tags=["Manajemen Akun"])
app.include_router(knn_global_evaluation.router, prefix="/api/v1", tags=["KNN Evaluation"])
# app.include_router(laporan.router, prefix="/api/v1", tags=["Laporan Export"])  # Disabled: SQLAlchemy incompatibility
# app.include_router(k_parameter_evaluation.router)  # Not copied to API folder
# app.include_router(knn_kader_evaluation.router)  # Not copied to API folder

@app.on_event("startup")
async def startup_event():
    print("Starting up KNN Model...")
    # Load model if exists
    try:
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml", "models", "knn_stunting_model.pkl")
        if os.path.exists(model_path):
            knn_model.load_model(model_path)
            print("KNN Model Loaded Successfully.")
        else:
            print("Warning: KNN Model not found. Training might be required.")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Sistem Deteksi Stunting API",
        "docs": "/docs",
        "version": settings.API_VERSION
    }


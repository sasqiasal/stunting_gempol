from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Konfigurasi Aplikasi menggunakan Environment Variables
    """
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180  # 3 jam
    
    # Application
    DEBUG: bool = False
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Sistem Deteksi Dini Stunting Desa Gempol"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Cache settings agar tidak perlu reload setiap request
    """
    return Settings()

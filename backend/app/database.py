from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()

# Supabase Client - GUNAKAN SERVICE_ROLE KEY UNTUK BYPASS RLS
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# Supabase Service Client (untuk operasi admin) - sama dengan supabase
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def get_supabase() -> Client:
    """
    Dependency untuk mendapatkan Supabase client
    Menggunakan SERVICE_ROLE key untuk bypass RLS
    """
    return supabase

def get_supabase_admin() -> Client:
    """
    Dependency untuk mendapatkan Supabase admin client
    """
    return supabase_admin

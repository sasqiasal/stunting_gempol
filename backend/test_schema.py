"""Test script to check database schema"""
from app.database import supabase

try:
    # Check pengukuran columns
    print("=== Pengukuran Table ===")
    resp = supabase.table("pengukuran").select("*").limit(1).execute()
    if resp.data:
        print("Columns:", list(resp.data[0].keys()))
        print("Sample row keys:", resp.data[0])
    
    # Try simple balita query
    print("\n=== Balita Table ===")
    resp = supabase.table("balita").select("*").limit(1).execute()
    if resp.data:
        print("Columns:", list(resp.data[0].keys()))
        print("Sample row:", resp.data[0])
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

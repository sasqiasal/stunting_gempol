#!/usr/bin/env python
"""
Simple test to start the API and show any startup errors
"""
import sys
import os
sys.path.insert(0, 'd:\\development\\stunting_gempol\\api')
os.chdir('d:\\development\\stunting_gempol\\api')

print("[1] Testing app import...")
try:
    from app.main import app
    print("✓ App imported successfully")
    print(f"✓ App has {len(app.routes)} routes")
except Exception as e:
    print(f"✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[2] Importing uvicorn...")
try:
    import uvicorn
    print("✓ Uvicorn imported successfully")
except Exception as e:
    print(f"✗ Error importing uvicorn: {e}")
    sys.exit(1)

print("\n[3] Starting server...")
try:
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
except Exception as e:
    print(f"✗ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

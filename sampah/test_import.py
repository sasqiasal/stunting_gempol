#!/usr/bin/env python
import sys
import os

print(f"Current directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"sys.path entries:")
for p in sys.path:
    print(f"  - {p}")

print("\n--- Attempting import ---")
try:
    import api.app.main as main_module
    print("✅ SUCCESS: api.app.main imported")
    print(f"   App object: {main_module.app}")
    print(f"   Routes count: {len(main_module.app.routes)}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

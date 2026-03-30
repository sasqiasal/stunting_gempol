import sys
import os
sys.path.insert(0, 'd:\\development\\stunting_gempol\\api')
os.chdir('d:\\development\\stunting_gempol\\api')

print("[1] Attempting to import evaluasi...")
try:
    from app.routes import evaluasi
    print("✓ SUCCESS: Evaluasi module imported")
    print(f"✓ Function calculate_k_comparison_from_measurements exists: {hasattr(evaluasi, 'calculate_k_comparison_from_measurements')}")
except SyntaxError as e:
    print(f"✗ SYNTAX ERROR: {e}")
    import traceback
    traceback.print_exc()
except ImportError as e:
    print(f"✗ IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ UNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()

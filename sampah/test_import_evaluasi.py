#!/usr/bin/env python
import sys
sys.path.insert(0, 'd:\\development\\stunting_gempol\\api')

try:
    from app.routes import evaluasi
    print('✓ Evaluasi module imported successfully')
except Exception as e:
    print(f'✗ Error importing evaluasi: {e}')
    import traceback
    traceback.print_exc()

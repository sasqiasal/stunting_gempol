#!/usr/bin/env python
from backend.app.database import get_supabase_service

# Create service
db_service = get_supabase_service()
client = db_service.get_client()

# Count pengukuran records
response = client.table('pengukuran').select('id, balita_id, status_gizi, zscore_tbu, zscore_bbu, created_at').execute()
print(f'Total pengukuran records: {len(response.data)}')

if len(response.data) > 0:
    print('\nFirst 5 records:')
    for i, rec in enumerate(response.data[:5]):
        print(f'\nRecord {i+1}:')
        print(f'  id={rec.get("id")}')
        print(f'  balita_id={rec.get("balita_id")}')
        print(f'  status_gizi={rec.get("status_gizi")}')
        print(f'  zscore_tbu={rec.get("zscore_tbu")}')
        print(f'  zscore_bbu={rec.get("zscore_bbu")}')
else:
    print('No pengukuran data found')

# Count balita records
balita_response = client.table('balita').select('id, nama_lengkap').execute()
print(f'\n\nTotal balita records: {len(balita_response.data)}')

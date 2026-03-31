from app.database import get_supabase

client = get_supabase()

# Check current state
pengukuran = client.table('pengukuran').select('id, status_gizi, zscore_tbu, zscore_bbu').execute()
print(f"Current pengukuran records: {len(pengukuran.data)}")

if len(pengukuran.data) == 0:
    print("\nDatabase kosong. Membuat 1 dummy record untuk testing...")
    
    # Get a balita_id and kader_id for FK
    balita = client.table('balita').select('id').limit(1).execute()
    users = client.table('users').select('id').limit(1).execute()
    
    if balita.data and users.data:
        new_record = {
            'balita_id': balita.data[0]['id'],
            'kader_id': users.data[0]['id'],
            'jenis_kelamin': 'L',
            'usia_bulan': 24,
            'tinggi_badan': 75.5,
            'berat_badan': 12.3,
            'lingkar_lengan': 14.2,
            'lingkar_kepala': 47.5,
            'zscore_tbu': -1.5,  # Normal (>= -2.0)
            'zscore_bbu': -0.5,  # Baik (>= -1.0)
            'status_gizi': 'Normal + Gizi Baik',
            'prediksi_stunting': False,
            'confidence_score': 0.95,
            'catatan': 'Dummy record for evaluation testing'
        }
        
        response = client.table('pengukuran').insert(new_record).execute()
        print(f"Created: {response.data}")
        
        # Verify
        check = client.table('pengukuran').select('id, status_gizi').execute()
        print(f"\nTotal pengukuran now: {len(check.data)}")
    else:
        print("ERROR: No balita or users found!")

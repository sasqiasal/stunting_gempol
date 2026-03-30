"""Create missing evaluasi_model_knn records for existing pengukuran"""
import requests
import json
import sys
sys.path.insert(0, 'd:\\development\\stunting_gempol\\api')

from app.services.prediction_service import prediction_service
from app.database import get_supabase

BASE_URL = 'http://localhost:8000/api/v1'

print("[1] Logging in...")
login_r = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'testuser@gempol.id',
    'password': 'testpass123'
})

if login_r.status_code != 200:
    print(f'❌ Login failed')
    exit(1)

token = login_r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print("✓ Login successful")

# Get all pengukuran
print("\n[2] Fetching all pengukuran...")
pengukuran_r = requests.get(f'{BASE_URL}/pengukuran/?limit=500', headers=headers)
pengukuran_list = pengukuran_r.json()
print(f"✓ Found {len(pengukuran_list)} pengukuran")

# Check which pengukuran don't have evaluasi records
print("\n[3] Checking for missing evaluasi records...")
missing_count = 0
for p in pengukuran_list:
    pengukuran_id = p['id']
    
    # Check if evaluasi exists
    detail_r = requests.get(
        f'{BASE_URL}/pengukuran/{pengukuran_id}/detail-evaluasi',
        headers=headers
    )
    
    if detail_r.status_code != 200:
        missing_count += 1
        print(f"\n  Pengukuran ID {pengukuran_id}: MISSING evaluasi")
        
        # Get the detailed pengukuran data to recalculate prediction
        print(f"    Creating evaluasi for ID {pengukuran_id}...")
        
        # Predict using the same data
        try:
            # Determine gender
            jk_encoded = 1 if p.get('jenis_kelamin') == 'L' else 0
            
            # Make prediction
            prediksi_result = prediction_service.predict_stunting(
                jenis_kelamin=p.get('jenis_kelamin', 'P'),
                usia_bulan=p.get('usia_bulan', 24),
                tinggi_badan=float(p.get('tinggi_badan', 85.0)),
                berat_badan=float(p.get('berat_badan', 12.0)),
                lingkar_lengan=float(p.get('lingkar_lengan', 14.0)),
                lingkar_kepala=float(p.get('lingkar_kepala', 48.0))
            )
            
            # Create evaluasi record in database
            evaluasi_data = {
                "pengukuran_id": pengukuran_id,
                "k_value": 5,
                "algorithm": "KNN",
                "nearest_neighbors": prediksi_result.get("nearest_neighbors", [])
            }
            
            supabase_client = get_supabase()
            response = supabase_client.table("evaluasi_model_knn").insert(evaluasi_data).execute()
            
            if response.data:
                print(f"    ✓ Created evaluasi for pengukuran {pengukuran_id}")
                # Verify it can be fetched
                verify_r = requests.get(
                    f'{BASE_URL}/pengukuran/{pengukuran_id}/detail-evaluasi',
                    headers=headers
                )
                if verify_r.status_code == 200:
                    print(f"    ✓ Verified - evaluasi is now accessible")
                else:
                    print(f"    ? Verification failed: {verify_r.status_code}")
            else:
                print(f"    ❌ Failed to create evaluasi")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")

print(f"\n✓ Summary: {missing_count} evaluasi records were missing")
print("✓ Migration complete! All pengukuran should now have evaluasi records")

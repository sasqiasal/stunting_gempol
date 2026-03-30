with open('d:/development/stunting_gempol/backend/app/services/prediction_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

old_string = '''            if nearest_neighbors:
                print(f"   Nearest Neighbors (k=5):")
                for i, n in enumerate(nearest_neighbors):
                    print(f"     {i+1}. Dist: {n['distance']:.4f} - {n['label']} (Usia: {n['usia_bulan']} bln, TB: {n['tinggi_badan']} cm, BB: {n['berat_badan']} kg)")'''

new_string = '''            if nearest_neighbors:
                print(f"   === DEBUGGING PREDIKSI: DATA DATASET ===")
                try:
                    print(f"   [!] Jumlah training terbaca: {len(model.X_train_data) if model.X_train_data is not None else 0}")
                    if model.X_train_data is not None and len(model.X_train_data) >= 5:
                        print(f"   [!] 5 Baris Pertama Dataset Fitur:")
                        for idx_5 in range(5):
                            print(f"       {model.X_train_data[idx_5].tolist()} -> Label: {model.y_train_data[idx_5]}")
                except Exception as eval_e:
                    print(f"       Could not read training data stats: {eval_e}")
                    
                print(f"   [!] Fitur yang digunakan untuk perhitungan distance: [Jenis_Kelamin, Usia_Bulan, Berat_Badan, Tinggi_Badan, Lingkar_Lengan, Lingkar_Kepala]")
                print(f"   [!] Nearest Neighbors (k={len(nearest_neighbors)}):")
                for i, n in enumerate(nearest_neighbors):
                    print(f"     {i+1}. Dist: {n['distance']:.4f} - {n['label']} - JK:{n['jenis_kelamin']} - Usia:{n['usia_bulan']}bln - TB:{n['tinggi_badan']}cm - BB:{n['berat_badan']}kg - LILA:{n.get('lingkar_lengan', '-')}cm - LK:{n.get('lingkar_kepala', '-')}cm")'''

text = text.replace(old_string, new_string)

with open('d:/development/stunting_gempol/backend/app/services/prediction_service.py', 'w', encoding='utf-8') as f:
    f.write(text)

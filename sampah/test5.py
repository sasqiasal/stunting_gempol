with open('d:/development/stunting_gempol/backend/app/services/prediction_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

old_text = '''                print(f"   [!] Fitur yang digunakan untuk perhitungan distance: [Jenis_Kelamin, Usia_Bulan, Berat_Badan, Tinggi_Badan, Lingkar_Lengan, Lingkar_Kepala]")'''
new_text = '''                print(f"   [!] Data Input : {{features.tolist()}}")\n                print(f"   [!] Fitur yang digunakan untuk perhitungan distance: [Jenis_Kelamin, Usia_Bulan, Berat_Badan, Tinggi_Badan, Lingkar_Lengan, Lingkar_Kepala]")'''

text = text.replace(old_text, new_text)

with open('d:/development/stunting_gempol/backend/app/services/prediction_service.py', 'w', encoding='utf-8') as f:
    f.write(text)

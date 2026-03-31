with open('d:/development/stunting_gempol/backend/app/services/prediction_service.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '''[!] Fitur yang digunakan untuk perhitungan distance: [Jenis_Kelamin, Usia_Bulan, Berat_Badan, Tinggi_Badan, Lingkar_Lengan, Lingkar_Kepala]''', 
    '''[!] Fitur yang digunakan untuk perhitungan distance: [jenis_kelamin, usia_bulan, berat_badan, tinggi_badan, lingkar_lengan, lingkar_kepala]'''
)

with open('d:/development/stunting_gempol/backend/app/services/prediction_service.py', 'w', encoding='utf-8') as f:
    f.write(text)

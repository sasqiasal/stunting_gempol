#!/usr/bin/env python
"""
Test script untuk verifikasi prediksi 4 kelas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from app.services.prediction_service import prediction_service, CLASSIFICATION_MAPPING

print("=" * 70)
print("TEST PREDIKSI 4 KELAS - STUNTING CLASSIFICATION")
print("=" * 70)

# Test cases dengan berbagai input
test_cases = [
    {
        "nama": "Balita Normal, Gizi Baik",
        "jenis_kelamin": "L",
        "usia_bulan": 24,
        "tinggi_badan": 85.0,
        "berat_badan": 13.0,
        "lingkar_lengan": 16.0,
        "lingkar_kepala": 48.0,
    },
    {
        "nama": "Balita Normal, Gizi Kurang",
        "jenis_kelamin": "P",
        "usia_bulan": 18,
        "tinggi_badan": 76.0,
        "berat_badan": 10.5,
        "lingkar_lengan": 14.5,
        "lingkar_kepala": 46.0,
    },
    {
        "nama": "Balita Stunting, Gizi Baik",
        "jenis_kelamin": "L",
        "usia_bulan": 36,
        "tinggi_badan": 85.0,
        "berat_badan": 11.0,
        "lingkar_lengan": 15.0,
        "lingkar_kepala": 47.5,
    },
    {
        "nama": "Balita Stunting, Gizi Kurang",
        "jenis_kelamin": "P",
        "usia_bulan": 30,
        "tinggi_badan": 78.0,
        "berat_badan": 9.0,
        "lingkar_lengan": 13.5,
        "lingkar_kepala": 46.0,
    },
]

print("\nTesting 4-Class Classification System\n")
print("Label Mapping:")
for label, desc in CLASSIFICATION_MAPPING.items():
    print("  {} -> {}".format(label, desc))

print("\n" + "-" * 70)

for i, test in enumerate(test_cases, 1):
    print("\n[Test Case {}] {}".format(i, test['nama']))
    print("   Input: Usia={}bln, JK={}, TB={}cm, BB={}kg".format(
        test['usia_bulan'], test['jenis_kelamin'], test['tinggi_badan'], test['berat_badan']))
    
    try:
        result = prediction_service.predict_stunting(
            jenis_kelamin=test['jenis_kelamin'],
            usia_bulan=test['usia_bulan'],
            tinggi_badan=test['tinggi_badan'],
            berat_badan=test['berat_badan'],
            lingkar_lengan=test['lingkar_lengan'],
            lingkar_kepala=test['lingkar_kepala']
        )
        
        print("\n   HASIL PREDIKSI:")
        print("   + Status Gizi (Text):  {}".format(result['status_gizi']))
        print("   + Status Label (Int):  {}".format(result['status_gizi_label']))
        print("   + Confidence:          {:.2%}".format(result['confidence_score']))
        print("   + Z-Score BB/U:        {:.2f}".format(result['zscore_bbu']))
        print("   + Z-Score TB/U:        {:.2f}".format(result['zscore_tbu']))
        
        # Verify label mapping
        expected = CLASSIFICATION_MAPPING.get(result['status_gizi_label'])
        if expected == result['status_gizi']:
            print("   [OK] Label Mapping: CORRECT")
        else:
            print("   [ERROR] Label Mapping: MISMATCH - Expected '{}', Got '{}'".format(
                expected, result['status_gizi']))
        
    except Exception as e:
        print("   [ERROR] {}".format(e))
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

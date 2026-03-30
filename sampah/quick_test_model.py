#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from app.ml.knn_model import knn_model
import numpy as np

print("Loading KNN model...")
model_path = os.path.join(os.path.dirname(__file__), 'api', 'app', 'ml', 'models', 'knn_stunting_model.pkl')
print("Model path: {}".format(model_path))

try:
    knn_model.load_model(model_path)
    print("Model loaded: {}".format(knn_model.is_trained))
    
    # Test prediction
    from app.services.prediction_service import prediction_service
    
    print("\nTesting 4-class prediction with loaded model...")
    result = prediction_service.predict_stunting(
        jenis_kelamin="L",
        usia_bulan=24,
        tinggi_badan=85.0,
        berat_badan=13.0,
        lingkar_lengan=16.0,
        lingkar_kepala=48.0
    )
    
    print("Status Gizi: {}".format(result['status_gizi']))
    print("Label: {}".format(result['status_gizi_label']))
    print("Confidence: {:.2%}".format(result['confidence_score']))
    
except Exception as e:
    import traceback
    print("Error: {}".format(e))
    traceback.print_exc()

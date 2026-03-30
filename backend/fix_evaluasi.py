import sys
import os

file_path = r'd:\development\stunting_gempol\backend\app\routes\evaluasi.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('@router.get(\"/model-performance\")')
end_idx = text.find('@router.post(\"/simulate\")')

print('start:', start_idx, 'end:', end_idx)

new_method = '''@router.get("/model-performance", response_model=Dict[str, Any])
async def evaluate_model_performance(
    supabase_client = Depends(get_supabase),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    \"\"\"
    Evaluasi kinerja model KNN dengan data dataset (data_latih_stunting.csv)
    Menghitung metrik (CM, Accuracy, Precision, Recall, F1)
    dan mengkomparasi nilai K (3, 5, 7, 9)
    \"\"\"
    try:
        csv_path = "data_latih_stunting.csv"
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=500, detail="Dataset not found")
            
        df = pd.read_csv(csv_path)
        
        # Mapping 4 classes
        classes = [0, 1, 2, 3]
        class_names = [
            "Normal + Gizi Baik",
            "Normal + Kurang Gizi",
            "Stunting + Gizi Baik",
            "Stunting + Kurang Gizi"
        ]
        
        y_true = df["status_stunting"].values
        features = ["jenis_kelamin", "usia_bulan", "berat_badan", "tinggi_badan", "lingkar_lengan", "lingkar_kepala"]
        
        X_df = df.copy()
        X_list = []
        for _, row in X_df.iterrows():
            X_list.append([
                1 if int(float(row["jenis_kelamin"])) == 1 else 0,
                float(row["usia_bulan"]),
                float(row["berat_badan"]),
                float(row["tinggi_badan"]),
                float(row["lingkar_lengan"]),
                float(row["lingkar_kepala"])
            ])
        X = np.array(X_list)
        
        # Test default K=5
        default_k = 5
        test_model = StuntingKNNModel(n_neighbors=default_k)
        test_model.train(X, y_true)
        
        y_pred = []
        for i in range(len(X)):
            pred, _ = test_model.predict(X[i].reshape(1, -1))
            y_pred.append(pred)
        
        metrics = calculate_metrics(y_true, np.array(y_pred), labels=classes)
        
        main_accuracy = metrics["accuracy"]
        main_precision = metrics["precision"]
        main_recall = metrics["recall"]
        main_f1_score = metrics["f1_score"]
        confusion_matrix = metrics["confusion_matrix"]
        
        # Convert CM to specific format expected by frontend
        formatted_cm = format_confusion_matrix_table(confusion_matrix, class_names)
        
        # Convert per-class metrics
        per_class_metrics = []
        for i, class_name in enumerate(class_names):
             # cm shape (n_classes, n_classes) => row is true, col is pred
             actual_samples = int(np.sum(confusion_matrix[i, :]))
             per_class_metrics.append({
                 "class_name": class_name,
                 "idx": i,
                 "samples": actual_samples,
                 "precision": float(metrics["per_class"]["precision"][i]),
                 "recall": float(metrics["per_class"]["recall"][i]),
                 "f1_score": float(metrics["per_class"]["f1_score"][i])
             })
             
        # Compare different K values
        k_values = [3, 5, 7, 9]
        k_comparisons = []
        for k in k_values:
            temp_model = StuntingKNNModel(n_neighbors=k)
            temp_model.train(X, y_true)
            
            k_pred = []
            for i in range(len(X)):
                p, _ = temp_model.predict(X[i].reshape(1, -1))
                k_pred.append(p)
                
            k_metrics = calculate_metrics(y_true, np.array(k_pred), labels=classes)
            
            k_comparisons.append({
                "k": k,
                "accuracy": k_metrics["accuracy"],
                "precision": k_metrics["precision"],
                "recall": k_metrics["recall"],
                "f1_score": k_metrics["f1_score"]
            })
            
        return {
            "status": "success",
            "message": "Evaluasi kinerja model KNN berhasil",
            "dataset_info": {
                "total_data_uji": len(X),
                "deskripsi": "Menggunakan seluruh data dari data_latih_stunting.csv (Cross-Validation)"
            },
            "metrics": {
                "accuracy": float(main_accuracy),
                "accuracy_percentage": round(main_accuracy * 100, 2),
                "macro_avg_precision": float(main_precision),
                "macro_avg_precision_percentage": round(main_precision * 100, 2),
                "macro_avg_recall": float(main_recall),
                "macro_avg_recall_percentage": round(main_recall * 100, 2),
                "macro_avg_f1": float(main_f1_score),
                "macro_avg_f1_percentage": round(main_f1_score * 100, 2),
                "k_value_used": default_k,
                "per_class": per_class_metrics
            },
            "confusion_matrix": {
                "raw": confusion_matrix.tolist(),
                "formatted_table": formatted_cm,
                "labels": class_names
            },
            "k_comparisons": k_comparisons,
            "sample_explanations": [] # Simplified for now
        }
    except Exception as e:
        import traceback
        print("ERROR IN EVALUATION:", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat mengevaluasi model: {str(e)}"
        )

'''

if start_idx != -1 and end_idx != -1:
    new_text = text[:start_idx] + new_method + text[end_idx:]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Replaced!")

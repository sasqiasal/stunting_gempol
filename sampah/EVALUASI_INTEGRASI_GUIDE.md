# Panduan Integrasi Halaman Evaluasi Model KNN

## 📋 Overview

Sistem evaluasi model KNN yang telah dibuat terdiri dari:

### Backend (Python/FastAPI)
- **Endpoint**: `GET /api/v1/evaluasi/realtime`
- **File**: `backend/app/routes/evaluasi.py`
- **Service**: `backend/app/services/evaluation_service.py`

### Frontend (React)
- **Page Component**: `src/pages/EvaluationPage.jsx`
- **Service**: `src/services/evaluationService.js`
- **Styles**: `src/pages/EvaluationPage.css`

---

## 🔌 Integrasi ke Aplikasi Existing

### Step 1: Import Component di App.jsx atau Router

```jsx
// src/App.jsx atau src/pages dalam router Anda
import EvaluationPage from '@/pages/EvaluationPage';

// Option 1: Jika menggunakan React Router
<Route path="/evaluasi" element={<EvaluationPage />} />

// Option 2: Jika tanpa router
<EvaluationPage />
```

### Step 2: Setup Environment Variable (opsional)

Jika menggunakan backend di domain/port berbeda:

```env
# .env atau .env.local
VITE_API_URL=http://localhost:8000/api/v1
```

Service akan fallback ke `http://127.0.0.1:8000/api/v1` jika tidak didefinisikan.

### Step 3: Install Dependencies (jika belum ada)

```bash
npm install axios
```

---

## 📊 Fitur-Fitur

### 1. Real-Time Data Fetching
- Data diambil langsung dari database tabel `pengukuran` (Supabase)
- Tidak menggunakan CSV files
- Automatic conversion dari `status_gizi` (string) ke numeric label

### 2. Binary Classification Metrics
- Metrics untuk Normal vs Stunting (2x2 Confusion Matrix)
- Accuracy, Precision, Recall, Specificity, F1-Score (dalam %)

### 3. Multi-Class Metrics  
- 4x4 Confusion Matrix untuk klasifikasi 4-kelas
- Per-class Precision, Recall, F1-Score

### 4. K-Value Comparison
- Automatic comparison untuk K=3, 5, 7, 9
- Interactive selection dengan click
- Selected K metrics dipilih secara highlight

### 5. Data Distribution
- Menampilkan jumlah dan persentase Normal vs Stunting
- Total data dari database

### 6. Responsive Design
- Mobile-friendly
- Works di semua screen sizes

---

## 🔄 API Specification

### GET `/api/v1/evaluasi/realtime`

**Query Parameters**: Tidak ada

**Response Success** (Status 200):
```json
{
  "status": "success",
  "data": {
    "success": true,
    "message": "Model evaluation completed successfully",
    "metadata": {
      "total_data": 1,
      "evaluation_timestamp": "2026-03-15T14:57:48",
      "note": "Evaluation on all available data (non-k-fold)"
    },
    "binary_classification": {
      "metrics": {
        "confusion_matrix": [[TN, FP], [FN, TP]],
        "tp": 0, "tn": 0, "fp": 1, "fn": 0,
        "accuracy": 0.0, "accuracy_percent": 0.0,
        "precision": 0.0, "precision_percent": 0.0,
        "recall": 0.0, "recall_percent": 0.0,
        "specificity": 0.0, "specificity_percent": 0.0,
        "f1_score": 0.0, "f1_score_percent": 0.0
      }
    },
    "multiclass_classification": {
      "metrics": {
        "confusion_matrix": [[4x4 matrix]],
        "total_samples": 1,
        "accuracy": 0.0, "accuracy_percent": 0.0,
        "macro_precision": 0.0, "macro_precision_percent": 0.0,
        "macro_recall": 0.0, "macro_recall_percent": 0.0,
        "macro_f1": 0.0, "macro_f1_percent": 0.0,
        "per_class_metrics": [
          {
            "class": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0
          },
          ...
        ]
      }
    },
    "k_comparison": [
      {
        "k": 3,
        "accuracy": 0.0, "accuracy_percent": 0.0,
        "precision": 0.0, "precision_percent": 0.0,
        "recall": 0.0, "recall_percent": 0.0,
        "f1_score": 0.0, "f1_score_percent": 0.0,
        "specificity": 0.0, "specificity_percent": 0.0
      },
      ...
    ],
    "distribution": {
      "normal_count": 1,
      "stunting_count": 0,
      "normal_percent": 100.0,
      "stunting_percent": 0.0
    }
  }
}
```

**Response Error** (Status 200 dengan success: false):
```json
{
  "status": "success",
  "data": {
    "success": false,
    "message": "Error during evaluation",
    "error": "Error message detail"
  }
}
```

---

## 🎯 Data Logic

### Ground Truth (Yang Sebenarnya)
```python
# Dari database column zscore_tbu
y_true = 1 if zscore_tbu < -2.0 else 0
# 1 = STUNTING, 0 = NORMAL (WHO Standard)
```

### Prediction (Hasil Model)
```python
# Dari database column status_gizi (string)
# Diconvert ke numeric label (0-3)
status_gizi_mapping = {
    "Normal + Gizi Baik": 0,          # Normal
    "Normal + Kurang Gizi": 1,        # Normal
    "Stunting + Gizi Baik": 2,        # Stunting
    "Stunting + Kurang Gizi": 3       # Stunting
}

# Kemudian convert ke binary
y_pred = 1 if status_gizi_label in (2, 3) else 0
```

### Metrics Calculation

```
TP (True Positive)   = y_true=1 AND y_pred=1 → Benar stunting
TN (True Negative)   = y_true=0 AND y_pred=0 → Benar normal  
FP (False Positive)  = y_true=0 AND y_pred=1 → Salah prediksi stunting
FN (False Negative)  = y_true=1 AND y_pred=0 → Missed stunting

Accuracy   = (TP + TN) / Total
Precision  = TP / (TP + FP)
Recall     = TP / (TP + FN)  ← PALING PENTING untuk medical
Specificity = TN / (TN + FP)
F1-Score   = 2 × (Precision × Recall) / (Precision + Recall)
```

---

## 🚀 Performance Considerations

### Database Optimization
- Hanya fetch kolom yang diperlukan: `status_gizi`, `zscore_tbu`
- Tidak menggunakan CSV files
- Query terpisah/isolated untuk tidak mengganggu fitur lain

### Frontend Optimization
- Separate loading state untuk evaluasi
- Tidak memblock page loading
- Async fetch dengan error handling

### Caching (Optional)
Jika ingin cache hasil evaluasi untuk beberapa waktu:

```jsx
// Di EvaluationPage.jsx
const CACHE_DURATION = 5 * 60 * 1000; // 5 menit

const [lastFetch, setLastFetch] = useState(null);

const shouldRefresh = !lastFetch || 
  Date.now() - lastFetch > CACHE_DURATION;
```

---

## 🔧 Customization

### Mengubah K Values
Di `backend/app/services/evaluation_service.py`:
```python
# Ubah line ini untuk mengubah K values yang dibandingkan
for k in [3, 5, 7, 9]:  # Ganti dengan K yang diinginkan
    k_comparison.append({...})
```

### Mengubah Styling
- Edit `src/pages/EvaluationPage.css`
- Atau customize dengan Tailwind/styling library pilihan

### Menambah Metrik Baru
1. Hitung metrik baru di `backend/app/services/evaluation_service.py`
2. Return dalam response dictionary
3. Display di component dengan state baru

---

## 🐛 Troubleshooting

### Error: "Column pengukuran.status_gizi_label does not exist"
**Solusi**: Service sudah handle ini dengan mapping `status_gizi` string ke numeric label. Pastikan server di-restart.

### Error: Database connection failed
**Solusi**: Pastikan `.env` memiliki konfigurasi Supabase yang benar:
```env
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
```

### Response: "No data available for evaluation"
**Solusi**: Pastikan tabel `pengukuran` memiliki data. Insert test data jika diperlukan.

### Endpoint returns "Not Found" (404)
**Solusi**: 
- Pastikan backend server berjalan di port 8000
- Routes sudah di-include di `backend/app/main.py`
- Gunakan URL yang benar: `/api/v1/evaluasi/realtime`

---

## 📝 File Structure

```
stunting_gempol/
├── backend/
│   └── app/
│       ├── routes/
│       │   └── evaluasi.py          [Updated with /realtime endpoint]
│       ├── services/
│       │   ├── evaluation_service.py [NEW - Evaluation logic]
│       │   └── prediction_service.py [Existing]
│       └── main.py
│
└── src/
    ├── pages/
    │   ├── EvaluationPage.jsx        [NEW - Main component]
    │   └── EvaluationPage.css        [NEW - Styles]
    ├── services/
    │   ├── evaluationService.js      [NEW - API calls]
    │   └── ...
    └── App.jsx                        [Edit to add route]
```

---

## ✅ Testing Checklist

- [ ] Backend server berjalan (`python -m uvicorn main:app --reload`)
- [ ] Endpoint `/api/v1/evaluasi/realtime` accessible
- [ ] Database `pengukuran` memiliki data
- [ ] Frontend component meng-import sesuai path yang benar
- [ ] VITE_API_URL env variable (jika perlu)
- [ ] axios sudah ter-install
- [ ] Component menggunakan EvaluationService untuk fetch
- [ ] CSS file ter-import di component
- [ ] Router/App.jsx sudah di-update dengan route

---

## 📞 Support

Jika ada error atau pertanyaan:
1. Cek console (F12) untuk error details
2. Cek backend terminal untuk server logs
3. Pastikan data flow benar sesuai dokumentasi
4. Database column names sesuai yang di-define

---

**Last Updated**: 15 Maret 2026
**Version**: 1.0.0

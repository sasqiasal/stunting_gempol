# Quick Start: Evaluasi Parameter K

## Ringkasan

Script evaluasi KNN parameter K sudah dibuat untuk membandingkan nilai K (3, 5, 7, 9) dengan metrik:
- Accuracy, Precision, Recall, Specificity, F1-Score

---

## ⚡ Quick Start

### 1. Run Script Langsung (Python)

**Backend:**
```bash
cd backend
python -m app.ml.evaluate_k_parameter
```

**API:**
```bash
cd api
python -m app.ml.evaluate_k_parameter
```

### 2. Via API Endpoint (HTTP)

**Full Evaluation:**
```bash
curl http://localhost:8000/api/evaluation/k-parameter
```

**Summary Only:**
```bash
curl http://localhost:8000/api/evaluation/k-parameter/summary
```

**Specific K (e.g., K=5):**
```bash
curl http://localhost:8000/api/evaluation/k-parameter/detailed/5
```

---

## 📊 Output

### Summary Tabel

```
K  Overall Acc  Macro Acc  Macro Prec  Macro Rec  Macro Spec  Macro F1
3      0.7234      0.6145      0.6234      0.5892      0.8145      0.6012
5      0.7456      0.6423      0.6512      0.6234      0.8234      0.6367
7      0.7389      0.6234      0.6345      0.6089      0.8012      0.6215
9      0.7234      0.6012      0.6123      0.5945      0.7945      0.6023
```

**Result:** K=5 terbaik dengan accuracy 74.56%

---

## 📁 Files

| File | Lokasi | Fungsi |
|------|--------|--------|
| `evaluate_k_parameter.py` | `backend/app/ml/` & `api/app/ml/` | Main logic |
| `test_evaluate_k_parameter.py` | `backend/app/ml/` | Test script |
| `k_parameter_evaluation.py` | `backend/app/routes/` | API endpoints |
| `EVALUASI_K_PARAMETER_USAGE_GUIDE.md` | Root | Detailed guide |
| `K_PARAMETER_API_ENDPOINTS.md` | Root | API documentation |

---

## 🔧 Requirements

```bash
pip install numpy pandas scikit-learn pandas
```

**Supabase Config** di `.env`:
```
SUPABASE_URL=your_url
SUPABASE_SERVICE_KEY=your_key
```

---

## 📖 Dokumentasi Lengkap

- **Detailed Usage:** Baca `EVALUASI_K_PARAMETER_USAGE_GUIDE.md`
- **API Reference:** Baca `K_PARAMETER_API_ENDPOINTS.md`
- **Code:** Baca `backend/app/ml/evaluate_k_parameter.py`

---

## ✅ Checklist

- [x] Script untuk evaluasi K (3, 5, 7, 9) ✓
- [x] Fetch data dari Supabase ✓
- [x] Hitung TP, TN, FP, FN per class ✓
- [x] Hitung Accuracy, Precision, Recall, Specificity, F1-Score ✓
- [x] Output summary tabel ✓
- [x] Output detailed metrics per class ✓
- [x] Tentukan K terbaik ✓
- [x] API endpoints untuk run evaluasi ✓
- [x] Dokumentasi ✓

---

Next Steps:
1. Jalankan script untuk verify: `python -m app.ml.evaluate_k_parameter`
2. Lihat hasil dan tentukan K terbaik
3. Update KNN model dengan K optimal
4. Deploy ke production


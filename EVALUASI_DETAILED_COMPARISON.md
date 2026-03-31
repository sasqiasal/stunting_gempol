# EVALUASI ADMIN vs KADER - DETAILED COMPARISON TABLE

## 1. ENDPOINT & ROUTING

| Aspek | Kader | Admin |
|-------|-------|-------|
| **Endpoint** | `GET /evaluasi/realtime` | `GET /evaluasi/global` |
| **File Route** | `backend/app/routes/evaluasi.py:204-257` | `backend/app/routes/evaluasi.py:270-322` |
| **Frontend Component** | `EvaluasiModelPage.jsx` | `EvaluasiGlobalPage.jsx` |
| **Role Check** | Dalam `current_user` | Admin only (implisit) |
| **Parameter** | `?bulan=2026-01` (optional) | TIDAK ADA |

---

## 2. DATA SOURCE & FILTERING

| Aspek | Kader | Admin |
|-------|-------|-------|
| **Data Source** | ✅ Real-time dari `pengukuran` table | ⚠️ Static dari `data_latih_stunting.csv` |
| **Query** | `SELECT * FROM pengukuran WHERE balita.posyandu_id = kader.posyandu_id` | `pd.read_csv('data_latih_stunting.csv')` |
| **Month Filter** | ✅ Supported `?bulan=2026-01` | ❌ NOT Supported |
| **Posyandu Filter** | ✅ Auto filtered by `current_user.posyandu_id` | ❌ NO filtering (all data) |
| **Data Split** | ❌ NO split (use all data) | ✅ Train-Test Split 80/20 |
| **Data Freshness** | ✅ Real-time (updated setiap ada input) | ⚠️ Static (perlu update manual) |

---

## 3. BUSINESS LOGIC - GROUND TRUTH

| Aspek | Kader | Admin |
|-------|-------|-------|
| **Binary y_true Source** | `zscore_tbu < -2.0` dari DB | CSV `status_stunting` |
| **Multiclass y_true Source** | COMBINATION: `zscore_tbu + zscore_bbu` | CSV `status_stunting` (0-3) |
| **Class Mapping** | Dynamic dari service.convert_zscores_to_class_label() | Hardcoded dalam CSV |
| **WHO Standard** | ✅ Uses zscore_tbu < -2.0 | ⚠️ Uses CSV labels (mungkin outdated?) |

**Important:** Kader dan Admin mungkin punya ground truth yang BERBEDA!

---

## 4. PREDICTION SOURCE

| Aspek | Kader | Admin |
|-------|-------|-------|
| **Prediction Source** | `pengukuran.status_gizi_label` dari DB | KNN model output |
| **Model Used** | Implicit (dari status_gizi_label) | Explicit KNeighborsClassifier |
| **K Value** | Fixed (tidak bervariasi) | Configurable (3,5,7,9) |
| **Real K-Fold?** | ❌ NO - semua K show hasil sama | ✅ YES - actual K-comparison |

---

## 5. METRICS CALCULATION

### Binary Classification (2x2 CM)

| Metric | Kader | Admin | Logic |
|--------|-------|-------|-------|
| **Ground Truth** | `zscore_tbu < -2.0` | CSV label binary | ⚠️ BEDA |
| **Prediction** | `status_gizi_label ∈ (2,3)` | `model.predict()` | ✅ SAMA |
| **Accuracy Formula** | `(TP+TN) / Total` | `(TP+TN) / Total` | ✅ SAMA |
| **Precision** | `TP / (TP+FP)` | `TP / (TP+FP)` | ✅ SAMA |
| **Recall** | `TP / (TP+FN)` | `TP / (TP+FN)` | ✅ SAMA |
| **Specificity** | `TN / (TN+FP)` | `TN / (TN+FP)` | ✅ SAMA |
| **F1-Score** | `2*(P*R)/(P+R)` | `2*(P*R)/(P+R)` | ✅ SAMA |

### Multiclass Classification (4x4 CM)

| Metric | Kader | Admin | Note |
|--------|-------|-------|------|
| **y_true_multiclass** | Dari `convert_zscores_to_class_label()` | Dari CSV | ⚠️ **BERBEDA SUMBER** |
| **y_pred_multiclass** | Dari `status_gizi_label` | Dari model| ✅ SAMA |
| **One-vs-Rest** | Class 3 focus | Class 3 focus | ✅ SAMA |
| **CM Format** | 4x4 matrix | 4x4 matrix | ✅ SAMA |

---

## 6. FRONTEND DISPLAY

### Common Elements (✅ SAMA)

```
┌─────────────────────────────────────────────────┐
│  6 Metric Cards:                                 │
│  ┌─────────┬─────────┬─────────┬─────────┐      │
│  │ Total   │ Accuracy│ Precision│ Recall  │      │
│  │ Sampel  │   92%   │   94%   │  88%    │      │
│  ├─────────┼─────────┼─────────┼─────────┤      │
│  │Specifity│ F1 Score│         │         │      │
│  │  95%    │   91%   │         │         │      │
│  └─────────┴─────────┴─────────┴─────────┘      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  4 Value Cards: TP, TN, FP, FN                  │
│  ┌─────────┬─────────┬─────────┬─────────┐      │
│  │ TP: 45  │ TN: 50  │ FP: 5   │ FN: 8   │      │
│  └─────────┴─────────┴─────────┴─────────┘      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  2x2 Confusion Matrix                            │
│       Predicted                                   │
│       Normal  Stunting                           │
│  A  ┌────────┬────────┐                          │
│  c  │ TN:50  │ FP:5   │                          │
│  t  ├────────┼────────┤                          │
│  u  │ FN:8   │ TP:45  │                          │
│  a  └────────┴────────┘                          │
│  l                                               │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  K Comparison Table                              │
│  K  │ Accuracy │ Precision │ Recall │ F1-Score  │
│  ───┼──────────┼───────────┼────────┼───────────│
│  3  │  92.0%   │   94.0%   │ 88.0%  │  90.9%    │
│  5  │  92.0%   │   94.0%   │ 88.0%  │  90.9%    │
│  7  │  92.0%   │   94.0%   │ 88.0%  │  90.9%    │
│  9  │  92.0%   │   94.0%   │ 88.0%  │  90.9%    │
└─────────────────────────────────────────────────┘
```

### Different Elements (⚠️ BERBEDA)

| Element | Kader | Admin |
|---------|-------|-------|
| **Month Filter** | ✅ `<select>Semua Bulan ▼</select>` | ❌ TIDAK ADA |
| **Filter UI** | `max-w-xs px-3 py-2 border-gray-300` | TIDAK TAMPIL |
| **Data Label** | "Data Kader" | "Test Set" |
| **Refresh Button** | ❌ | ✅ Ada button Refresh |
| **Tabs** | Ringkasan + Riwayat | ❌ NO |
| **Prediction History** | ✅ Lengkap dengan nama balita | ❌ TIDAK ADA |

---

## 7. SERVICE LAYER - evaluation_service.py

### Method: fetch_pengukuran_data()

```python
async def fetch_pengukuran_data(
    bulan: Optional[str],      # Format: YYYY-MM
    role: Optional[str],       # "admin" atau "kader"
    posyandu_id: Optional[int] # Hanya ada jika role="kader"
)
```

**Filter Logic:**
```
IF bulan != None:
    FILTER tanggal_pengukuran LIKE '{bulan}%'

IF role == "kader" AND posyandu_id != None:
    FILTER balita.posyandu_id == posyandu_id

IF role == "admin":
    NO ADDITIONAL FILTERING → SEMUA DATA
```

**Called By:**
- Kader `/evaluasi/realtime`: `evaluation_service.evaluate_model(bulan, "kader", posyandu_id)`
- Admin `/evaluasi/global`: ❌ TIDAK DIPANGGIL (gunakan evaluator lain)

---

## 8. KEY DIFFERENCES SUMMARY

### ✅ SAMA (Logika Evaluasi)
1. Binary metrics calculation (formula)
2. Multiclass metrics calculation (formula)
3. One-vs-Rest approach untuk Class 3
4. UI layout dan styling
5. Metric cards dan displays

### ⚠️ BERBEDA (Scope & Data)
1. **Data Source**: Kader = DB real-time, Admin = CSV static
2. **Month Filter**: Kader = ada, Admin = tidak ada
3. **Posyandu Filter**: Kader = auto, Admin = tidak ada
4. **Ground Truth**: Kader = zscore-based, Admin = CSV-based (mungkin berbeda)
5. **K-Comparison**: Kader = dummy (semua sama), Admin = real K-fold
6. **Tabs/Details**: Kader = ada prediction history, Admin = tidak ada
7. **Data Freshness**: Kader = updated real-time, Admin = static

### ❓ MASALAH POTENSIAL

| No | Masalah | Impact | Severity |
|----|---------|--------|----------|
| 1 | Admin & Kader ground truth BEDA | Metrik tidak bisa dibandingkan | 🔴 HIGH |
| 2 | Admin no month filter | Sulit tracking performa over time | 🟡 MEDIUM |
| 3 | Admin data dari CSV (outdated) | Metrik tidak mencerminkan real performance | 🔴 HIGH |
| 4 | K-comparison logic berbeda | Confusing untuk user | 🟡 MEDIUM |
| 5 | Kader punya history, admin tidak | Asymmetric feature | 🟢 LOW |

---

## 9. REKOMENDASI PERBAIKAN (PRIORITY)

### 🔴 PRIORITY 1 - CRITICAL

**Problem:** Admin menggunakan CSV, Kader menggunakan DB → ground truth beda!

**Solution:** 
```python
# backend/app/routes/evaluasi.py - /evaluasi/global

@router.get("/global")
async def evaluate_model_global(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    # GUNAKAN evaluation_service.evaluate_model() 
    # BUKAN KNNGlobalEvaluator()
    
    evaluation_service.set_supabase_client(supabase_client)
    
    # Evaluasi ALL data (role="admin" → no posyandu filtering)
    result = await evaluation_service.evaluate_model(
        bulan=None,           # Optional: admin bisa pilih bulan
        role="admin",         # Identifier untuk "no filtering"
        posyandu_id=None      # Tidak ada posyandu filtering
    )
    
    return {
        "status": "success",
        "data": result
    }
```

**Benefit:**
- ✅ Consistent ground truth (zscore-based)
- ✅ Real-time data
- ✅ Optional month filter
- ✅ Aligned dengan kader logic

---

### 🟡 PRIORITY 2 - HIGH

**Problem:** Admin no month filter, sulit tracking trend

**Solution:** Add optional bulan parameter ke `/evaluasi/global`

```jsx
// frontend/src/pages/EvaluasiGlobalPage.jsx

const [selectedMonth, setSelectedMonth] = useState(null);
const [availableMonths, setAvailableMonths] = useState([]);

// Fetch months (sama seperti di kader page)
const fetchAvailableMonths = async () => {
  const response = await fetch(`${apiUrl}/evaluasi/available-months`, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
  });
  const months = await response.json();
  setAvailableMonths(months);
};

// Fetch dengan bulan filter
const fetchEvaluasi = async (bulanParam) => {
  const queryString = bulanParam ? `?bulan=${bulanParam}` : '';
  const response = await fetch(`${apiUrl}/evaluasi/global${queryString}`, {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
  });
  setEvaluasi(await response.json());
};
```

---

### 🟢 PRIORITY 3 - MEDIUM

**Problem:** K-comparison logic berbeda (kader dummy, admin real)

**Solution:** Clarify dalam UI dan documentation

```jsx
{/* EvaluasiModelPage.jsx */}
<div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
  <p className="text-sm text-blue-800">
    <span className="font-semibold">ℹ️ Catatan K-Comparison:</span><br/>
    Metrik ditampilkan untuk berbagai K values. Pada evaluasi real-time dengan data terbatas,
    metrik mungkin sama untuk semua K.
  </p>
</div>
```

```jsx
{/* EvaluasiGlobalPage.jsx */}
<div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
  <p className="text-sm text-blue-800">
    <span className="font-semibold">ℹ️ K-Comparison:</span><br/>
    Perbandingan actual K values (3, 5, 7, 9) menggunakan train-test split.
    K optimal dipilih berdasarkan akurasi tertinggi pada test set.
  </p>
</div>
```

---

## 10. VERIFICATION CHECKLIST

- [ ] Test `/evaluasi/realtime?bulan=2026-01` untuk kader
- [ ] Test `/evaluasi/global?bulan=2026-01` untuk admin (belum ada)
- [ ] Verify ground truth adalah sama untuk kader & admin
- [ ] Verify confusion matrix binary sama antara kedua page
- [ ] Verify confusion matrix 4x4 sama antara kedua page
- [ ] Check K-comparison table value sama/berbeda
- [ ] Verify data filter berdasarkan posyandu untuk kader
- [ ] Verify data filter berdasarkan bulan untuk kader
- [ ] Verify admin page menampilkan ALL data
- [ ] Load test dengan banyak data (>1000 records)


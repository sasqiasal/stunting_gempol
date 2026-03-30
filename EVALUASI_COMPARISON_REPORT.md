# Evaluasi Admin vs Kader - Comparison Report

## 📋 Ringkasan Temuan

Logika evaluasi sudah **SAMA**, hanya **BERBEDA di SCOPE DATA**:
- **Kader**: Evaluasi data miliknya saja (posyandu_id)
- **Admin**: Evaluasi SEMUA data dari semua kader

---

## 🔍 Analisis Backend

### 1. **Endpoint dan Router**

#### Kader - `/evaluasi/realtime` (Backend)
```python
@router.get("/realtime")
async def evaluate_model_realtime(
    bulan: Optional[str],
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
)
```
**Logika:**
- `user_role = current_user.get("role")`
- `user_posyandu_id = current_user.get("posyandu_id")` if role == "kader" else None
- Panggil `evaluation_service.evaluate_model(bulan, role, posyandu_id)`

**Filtering Data:**
- Jika bulan ada → filter `tanggal_pengukuran.startswith(bulan)`
- Jika role == "kader" → filter `balita.posyandu_id == user_posyandu_id`
- Jika role == "admin" → TIDAK ADA FILTERING (semua data)

#### Admin - `/evaluasi/global` (Backend)
```python
@router.get("/global")
async def evaluate_model_global(
    supabase_client = Depends(get_supabase)
)
```
**Logika:**
- Gunakan `KNNGlobalEvaluator()` yang evaluate ALL data
- One-vs-Rest approach untuk Class 3 (Stunting + Kurang Gizi)
- Menggunakan Train-Test Split 80/20

### 2. **Service Layer - evaluation_service.py**

**Method: `fetch_pengukuran_data(bulan, role, posyandu_id)`**

```
✅ Fetch semua pengukuran
✅ Filter bulan jika ada (YYYY-MM format)
✅ Filter posyandu_id jika role="kader"
✅ Convert status_gizi string ke numeric label (0-3)
```

**Method: `evaluate_model(bulan, role, posyandu_id)`**

Data Flow:
```
1. Fetch pengukuran_data dengan filtering
2. Extract y_true = zscore_tbu < -2.0 (ground truth binary)
3. Extract y_pred = status_gizi_label mapped to binary
4. Extract y_true_multiclass dari COMBINATION (zscore_tbu + zscore_bbu)
5. Extract y_pred_multiclass dari status_gizi_label
6. Calculate binary metrics (2x2 CM)
7. Calculate multiclass metrics (one-vs-rest untuk Class 3)
8. Generate k_comparison table
```

**Metrics Calculated:**
- Accuracy, Precision, Recall, Specificity, F1-Score
- Confusion Matrix (2x2 binary dan 4x4 multiclass)
- TP, TN, FP, FN

---

## 🎨 Analisis Frontend

### 1. **Kader - EvaluasiModelPage.jsx**

**Endpoint yang digunakan:**
```javascript
await evaluationService.getRealtimeEvaluation(bulan)  // GET /evaluasi/realtime?bulan=2026-01
```

**Data yang ditampilkan:**
- Total Sampel (dari evaluasi data kader)
- Accuracy, Precision, Recall, Specificity, F1 Score
- TP, TN, FP, FN
- 2x2 Confusion Matrix (binary)
- 4x4 Confusion Matrix (multiclass)
- K Comparison (3, 5, 7, 9)
- Month Filter ✅
- Prediction History Tab

**Notifikasi/Label:**
```jsx
<p className="text-xs text-gray-500 mt-2">Data Kader</p>
```

### 2. **Admin - EvaluasiGlobalPage.jsx**

**Endpoint yang digunakan:**
```javascript
{apiUrl}/evaluasi/global  // GET /evaluasi/global
{apiUrl}/evaluasi/global-k-comparison  // GET /evaluasi/global-k-comparison
```

**Data yang ditampilkan:**
- Total Sampel (n_testing_samples dari test set)
- Accuracy, Precision, Recall, Specificity, F1 Score
- TP, TN, FP, FN (dari class_3_metrics)
- 4x4 Confusion Matrix
- K Comparison (3, 5, 7, 9)
- **NO Month Filter** (BERBEDA!)

**Notifikasi/Label:**
```jsx
<p className="text-xs text-gray-500 mt-2">Test Set</p>
```

---

## ⚠️ ISSUES YANG DITEMUKAN

### 1. **Data Source Perbedaan**

| Aspek | Kader | Admin |
|-------|-------|-------|
| Endpoint | `/evaluasi/realtime` | `/evaluasi/global` |
| Data Source | Real-time from `pengukuran` table | Train-Test Split pada CSV |
| Total Data | Semua pengukuran kader | 20% dari CSV |
| Filtering | Support bulan & posyandu | TIDAK support filtering |

**⚠️ MASALAH:** Admin menggunakan data dari CSV, bukan dari database pengukuran yang real!

### 2. **UI Konsistensi**

✅ **SAMA:**
- Layout metrics cards (6 cards: Accuracy, Precision, Recall, Specificity, F1, Total)
- TP, TN, FP, FN display
- Confusion Matrix
- K-value comparison table
- Color scheme dan styling

⚠️ **BERBEDA:**
- Kader: Ada month filter → Admin: TIDAK ada month filter
- Kader: Label "Data Kader" → Admin: Label "Test Set"
- Kader: Real-time evaluation → Admin: Offline train-test split

### 3. **K-Comparison Logic**

**Kader (/evaluasi/realtime):**
```python
# Semua K punya metrik yang sama karena tidak ada K-fold
# Hanya untuk referensi, bukan actual K-comparison
k_comparison = [
    {"k": 3, "accuracy": 0.92, ...},
    {"k": 5, "accuracy": 0.92, ...},  # SAMA dengan K=3
    {"k": 7, "accuracy": 0.92, ...},  # SAMA dengan K=3
]
```

**Admin (/evaluasi/global-k-comparison):**
```python
# Actual K-comparison dengan Train-Test Split
# Setiap K di-evaluate pada test set yang sama
k_comparison = [
    {"k": 3, "accuracy": 0.95, ...},
    {"k": 5, "accuracy": 0.92, ...},  # BERBEDA dengan K=3
    {"k": 7, "accuracy": 0.96, ...},  # BERBEDA dengan K=3
]
```

---

## ✅ REKOMENDASI PERBAIKAN

### 1. **Align Data Source**

**Option A: Gunakan Real-Time untuk Admin Juga**
```python
# /evaluasi/global → gunakan /evaluasi/realtime logic
# Tapi tanpa posyandu_id filtering (ambil SEMUA)

@router.get("/global")
async def evaluate_model_global(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    # Gunakan evaluation_service.evaluate_model(role="admin")
    # Tidak ada posyandu_id filtering → data dari SEMUA kader
```

**Keuntungan:**
- Konsisten dengan data real yang diinput
- Update otomatis saat ada pengukuran baru
- Lebih meaningful untuk monitoring

**Option B: Gunakan CSV untuk Kader Juga**
- Tidak recommended karena kader hanya bisa lihat data miliknya

### 2. **Add Month Filter ke Admin**

```jsx
// Di EvaluasiGlobalPage.jsx
const [selectedMonth, setSelectedMonth] = useState(null);

// Fetch dengan bulan parameter
const fetchEvaluasi = async () => {
    const bulanParam = selectedMonth?.value ? `?bulan=${selectedMonth.value}` : '';
    const response = await fetch(`${apiUrl}/evaluasi/global${bulanParam}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
};
```

**Logika Backend:**
```python
@router.get("/global")
async def evaluate_model_global(
    bulan: Optional[str] = Query(None),  # ADD ini
    supabase_client = Depends(get_supabase)
):
    # Filter data jika ada bulan parameter
```

### 3. **Normalize K-Comparison**

Pastikan kedua page menampilkan K-comparison dengan logic yang sama:
- Gunakan logika real K-fold cross-validation
- Atau jelaskan bahwa tanpa cross-validation, semua K punya hasil sama

### 4. **Add Info Box untuk Perbedaan**

```jsx
{/* Info Box di kedua page */}
<div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
    {role === 'kader' ? (
        <p className="text-sm text-blue-800">
            📌 Menampilkan evaluasi data pengukuran dari Posyandu Anda
        </p>
    ) : (
        <p className="text-sm text-blue-800">
            📌 Menampilkan evaluasi global dari semua Posyandu dan Kader
        </p>
    )}
</div>
```

---

## 📊 Checklist: Logika Evaluasi

| Item | Kader | Admin | Status |
|------|-------|-------|--------|
| Fetch pengukuran dari DB | ✅ | ⚠️ (dari CSV) | BEDA |
| Filter bulan | ✅ | ❌ | BEDA |
| Filter posyandu | ✅ | ❌ | SAMA (tidak ada) |
| Calculate y_true | ✅ zscore_tbu | ⚠️ CSV status | BEDA |
| Calculate y_pred | ✅ status_gizi_label | ⚠️ CSV status | BEDA |
| Binary metrics | ✅ | ✅ | SAMA |
| Multiclass metrics | ✅ | ✅ | SAMA |
| K-comparison | ✅ (dummy) | ✅ (real) | BEDA |
| UI Metrics Cards | ✅ | ✅ | SAMA |
| UI Confusion Matrix | ✅ | ✅ | SAMA |
| UI K-Table | ✅ | ✅ | SAMA |

---

## 🎯 Kesimpulan

**Logika evaluasi SUDAH SAMA**, tapi:
1. ⚠️ Admin menggunakan CSV data alih-alih real pengukuran
2. ⚠️ Tidak ada month filter untuk admin
3. ✅ UI sudah konsisten untuk metrics dan display
4. ❓ K-comparison logic perlu clarity (dummy vs real)

**REKOMENDASI PRIORITY:**
1. **HIGH**: Align data source (admin juga ke DB, bukan CSV)
2. **HIGH**: Add month filter ke admin
3. **MEDIUM**: Clarify K-comparison logic
4. **LOW**: Add info box untuk explain perbedaan


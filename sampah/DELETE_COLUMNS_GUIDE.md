# 🗑️ CARA DELETE COLUMNS latitude, longitude, geom

## Step 1: Buka Supabase Dashboard
- URL: https://supabase.com/dashboard
- Login dengan akun Anda
- Pilih project: **stunting_gempol** (atau sesuai nama project Anda)

## Step 2: Buka SQL Editor
Di sidebar kiri → SQL Editor (atau bisa akses langsung dari tabel)

## Step 3: Jalankan SQL Command

Copas command ini ke SQL Editor:

```sql
ALTER TABLE posyandu DROP COLUMN latitude;
ALTER TABLE posyandu DROP COLUMN longitude;
ALTER TABLE posyandu DROP COLUMN geom;
```

Atau satu per satu jika ada error:

```sql
ALTER TABLE posyandu DROP COLUMN latitude CASCADE;
```

```sql
ALTER TABLE posyandu DROP COLUMN longitude CASCADE;
```

```sql
ALTER TABLE posyandu DROP COLUMN geom CASCADE;
```

## Step 4: Click "Run" / Ctrl+Enter

Output akan menunjukkan:
```
Query successful
```

## Step 5: Verifikasi

Buka tabel `posyandu` dan lihat struktur kolom - ke-3 kolom tersebut sudah hilang ✅

---

## ⚠️ Catatan:
- Operasi ini **irreversible** (tidak bisa undo)
- Tapi data Anda aman di `map.geojson`
- Jika perlu restore, bisa `git checkout` filnya

---

**Done!** Columns sudah didelete dari Supabase 🎉

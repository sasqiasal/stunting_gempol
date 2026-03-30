"""
Check Baby AN data discrepancy - usia_bulan 58 vs 57
"""
import sqlite3

conn = sqlite3.connect('stunting_gempol.db')
cursor = conn.cursor()

# First check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=" * 130)
print("📊 TABEL DI DATABASE:")
print("=" * 130)
print(f"Total tables: {len(tables)}")
for table in tables:
    print(f"  - {table[0]}")

if len(tables) == 0:
    print("\n❌ Database kosong atau tidak ada tabel!")
    conn.close()
    exit()

# Try to find correct table names
print("\n" + "=" * 130)
print("MENCARI DATA BABY AN")
print("=" * 130)

table_names_to_try = [
    ("balita", "pengukuran"),
    ("tabel_balita", "tabel_pengukuran"),
]

results = None
used_tables = None

for balita_table, pengukuran_table in table_names_to_try:
    try:
        cursor.execute(f"""
            SELECT 
                b.id,
                b.nama,
                p.id as pengukuran_id,
                p.usia_bulan,
                p.tinggi_badan,
                p.berat_badan,
                p.lingkar_lengan,
                p.lingkar_kepala,
                p.zscore_bbu,
                p.zscore_tbu,
                p.status_gizi_label,
                p.tanggal_pengukuran
            FROM {balita_table} b
            LEFT JOIN {pengukuran_table} p ON b.id = p.balita_id
            WHERE b.nama LIKE '%AN%'
            ORDER BY p.tanggal_pengukuran DESC
            LIMIT 20
        """)
        results = cursor.fetchall()
        used_tables = (balita_table, pengukuran_table)
        print(f"\n✓ Berhasil menggunakan tabel: {balita_table}, {pengukuran_table}\n")
        break
    except Exception as e:
        print(f"  ✗ Gagal dengan {balita_table}/{pengukuran_table}")
        continue

if results:
    for row in results:
        print(f"\n🔍 Balita ID: {row[0]} | Nama: {row[1]}")
        print(f"   Pengukuran ID: {row[2]}")
        print(f"   Usia Bulan: {row[3]} ⚠️ (USER KATAKAN SEHARUSNYA: 58)")
        print(f"   Tinggi: {row[4]} cm")
        print(f"   Berat: {row[5]} kg")
        print(f"   Lingkar Lengan: {row[6]} cm")
        print(f"   Lingkar Kepala: {row[7]} cm")
        print(f"   ZScore BBU: {row[8]}")
        print(f"   ZScore TBU: {row[9]}")
        
        label_map = {0: "Normal + Gizi Baik", 1: "Normal + Kurang Gizi", 
                    2: "Stunting + Gizi Baik", 3: "Stunting + Kurang Gizi"}
        print(f"   Status: {label_map.get(row[10], f'Unknown ({row[10]})')}")
        print(f"   Tanggal: {row[11]}")
else:
    print("❌ Tidak ditemukan data 'AN'")
    
    # List all balita names
    if used_tables:
        balita_table = used_tables[0]
        cursor.execute(f"SELECT DISTINCT nama FROM {balita_table} ORDER BY nama LIMIT 20")
        print(f"\n\nBalita di database (dari tabel {balita_table}):")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")

conn.close()

from app.database import get_supabase
import pandas as pd

client = get_supabase()

# Check existing balita
balita_response = client.table('balita').select('id, nama_lengkap, jenis_kelamin').execute()
print(f"Total balita records: {len(balita_response.data)}")

if len(balita_response.data) > 0:
    print(f"\nFirst 5 balita:")
    for i, b in enumerate(balita_response.data[:5]):
        print(f"{i+1}. ID={b.get('id')}, Nama={b.get('nama_lengkap')}, JK={b.get('jenis_kelamin')}")
else:
    print("No balita found")

# Create dummy balita records for test data
print("\n" + "="*50)
print("Creating dummy balita for test data...")

# Generate 500 dummy balita records
dummy_balitas = []
for i in range(1, 501):
    dummy_balitas.append({
        'nama_lengkap': f'Test Child {i}',
        'nik': f'TEST{str(i).zfill(6)}',
        'tanggal_lahir': '2022-01-15',  # Birth date required
        'jenis_kelamin': 'L' if i % 2 == 0 else 'P',
    })

# Insert in batches
batch_size = 50
total_inserted = 0

for i in range(0, len(dummy_balitas), batch_size):
    batch = dummy_balitas[i:i+batch_size]
    try:
        response = client.table('balita').insert(batch).execute()
        total_inserted += len(batch)
        print(f"✓ Inserted balita batch {i//batch_size + 1}: {len(batch)} records")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        break

print(f"\nTotal dummy balita created: {total_inserted}")

# Verify new balita count
final_balita = client.table('balita').select('id').execute()
print(f"Final balita records: {len(final_balita.data)}")

# Get first few IDs for mapping
balita_ids = [b['id'] for b in final_balita.data]
print(f"\nFirst 10 balita IDs: {balita_ids[:10]}")

from app.database import get_supabase

client = get_supabase()

# Get all pengukuran records first to see what we have
all_records = client.table('pengukuran').select('id, catatan').execute()
print(f"Total records before delete: {len(all_records.data)}")

# Find records to delete
test_records = [r['id'] for r in all_records.data if r.get('catatan') == 'IMPORTED FROM CSV - TEST DATA']
print(f"Test records to delete: {len(test_records)}")

# Delete each record
if test_records:
    for batch_id in test_records[:100]:  # Delete first 100
        try:
            client.table('pengukuran').delete().eq('id', batch_id).execute()
        except:
            pass
    
    # Delete remaining in batch
    for i in range(100, len(test_records), 100):
        for batch_id in test_records[i:i+100]:
            try:
                client.table('pengukuran').delete().eq('id', batch_id).execute()
            except:
                pass

# Verify
remaining = client.table('pengukuran').select('id, catatan').execute()
print(f"Remaining records after delete: {len(remaining.data)}")
if remaining.data:
    print("\nSample remaining records:")
    for r in remaining.data[:3]:
        print(f"  ID={r['id']}, Catatan={r.get('catatan', 'None')}")

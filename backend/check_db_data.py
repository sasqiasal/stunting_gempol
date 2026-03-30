from app.database import get_supabase

client = get_supabase()

# Check pengukuran table
r = client.table('pengukuran').select('id,status_gizi,zscore_tbu,zscore_bbu').execute()
print(f'Total pengukuran: {len(r.data)}')
if len(r.data) > 0:
    print('\nFirst 5 records:')
    for i, rec in enumerate(r.data[:5]):
        print(f'{i+1}. status={rec.get("status_gizi")}, tbu={rec.get("zscore_tbu")}, bbu={rec.get("zscore_bbu")}')

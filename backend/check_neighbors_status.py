#!/usr/bin/env python
"""Check status of nearest_neighbors in evaluasi_model_knn table"""

import sys
sys.path.insert(0, '.')
from app.database import get_supabase

client = get_supabase()

# Query tabel evaluasi_model_knn
result = client.table('evaluasi_model_knn').select('id, pengukuran_id, nearest_neighbors').order('id', desc=True).limit(30).execute()

if result.data:
    print(f'=== CHECKING {len(result.data)} ROWS (NEWEST FIRST) ===')
    print(f'{"id":<5} | {"pengukuran_id":<12} | {"neighbors_count":<15} | {"status":<10}')
    print('-' * 60)
    
    empty_count = 0
    filled_count = 0
    
    for row in result.data:
        neighbors = row.get('nearest_neighbors', [])
        count = len(neighbors) if isinstance(neighbors, list) else 0
        status = '✅ FILLED' if count > 0 else '❌ EMPTY'
        
        if count > 0:
            filled_count += 1
        else:
            empty_count += 1
            
        print(f'{row["id"]:<5} | {row["pengukuran_id"]:<12} | {count:<15} | {status}')
    
    print('-' * 60)
    print(f'✅ Summary: {filled_count} filled, {empty_count} empty')
    print(f'\n📋 Latest Data:')
    if result.data:
        latest = result.data[0]
        neighbors = latest.get('nearest_neighbors', [])
        print(f'   ID: {latest["id"]}, Pengukuran ID: {latest["pengukuran_id"]}')
        print(f'   Neighbors count: {len(neighbors)}')
        if neighbors:
            print(f'   Sample neighbor 1: {neighbors[0]["label"]} (distance: {neighbors[0]["distance"]})')
else:
    print('❌ No data found')

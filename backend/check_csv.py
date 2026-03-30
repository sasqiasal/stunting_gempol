import pandas as pd

csv_path = "data_latih_stunting.csv"
df = pd.read_csv(csv_path)

print(f"CSV shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst 3 rows:")
print(df.head(3))
print(f"\njenis_kelamin unique values: {df['jenis_kelamin'].unique()}")
print(f"jenis_kelamin value lengths: {df['jenis_kelamin'].str.len().unique()}")

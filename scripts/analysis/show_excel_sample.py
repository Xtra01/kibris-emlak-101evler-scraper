import pandas as pd
from pathlib import Path

# Read Excel
base_path = Path(__file__).parent.parent.parent
excel_path = base_path / 'data_samples' / 'sample_girne_satilik_villa.xlsx'
df = pd.read_excel(excel_path)

print(f'\n{"="*80}')
print(f'📊 EXCEL SAMPLE: {len(df)} KAYIT, {len(df.columns)} KOLON')
print(f'{"="*80}\n')

print('📋 KOLONLAR:')
for i, col in enumerate(df.columns, 1):
    print(f'  {i:2d}. {col}')

print(f'\n{"="*80}')
print('--- İLK 5 KAYIT (TEMEL BİLGİLER) ---')
print(f'{"="*80}\n')

# Show key columns
key_cols = ['property_id', 'title', 'price', 'currency', 'area_m2', 'location', 'room_count', 'property_type', 'listing_date', 'update_date']
available = [c for c in key_cols if c in df.columns]

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 60)

print(df[available].head(5).to_string(index=True))

print(f'\n{"="*80}')
print('--- DETAYLI GÖRÜNÜM (İLK 2 KAYIT) ---')
print(f'{"="*80}\n')

for idx in range(min(2, len(df))):
    print(f'\n🏠 KAYIT #{idx+1}:')
    print('-' * 80)
    for col in df.columns:
        value = df.iloc[idx][col]
        if pd.notna(value):
            # Truncate long values
            str_val = str(value)
            if len(str_val) > 100:
                str_val = str_val[:100] + '...'
            print(f'  {col:25s}: {str_val}')

print(f'\n{"="*80}')
print(f'✅ Excel dosyası: {excel_path}')
print(f'{"="*80}\n')

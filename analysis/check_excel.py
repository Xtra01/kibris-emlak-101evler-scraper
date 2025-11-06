import pandas as pd

df = pd.read_excel('reports/lefkosa_rentals_under_30k.xlsx')
print(f'Excel records: {len(df)}')
print(f'\nColumns: {list(df.columns)}')
print(f'\nPrice range (TRY): {df["price_try"].min():.2f} - {df["price_try"].max():.2f}')
print(f'\nRoom distribution:')
print(df['room_count'].value_counts())
print(f'\nDistrict distribution:')
print(df['district'].value_counts())
print(f'\nSample records (first 5):')
print(df[['property_id', 'title', 'district', 'room_count', 'price', 'currency', 'price_try']].head())

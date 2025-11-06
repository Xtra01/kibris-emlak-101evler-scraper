import pandas as pd

df = pd.read_excel('reports/lefkosa_rentals_30k-35k.xlsx')
print(f'Excel records (30-35k): {len(df)}')
print(f'\nPrice range (TRY): {df["price_try"].min():.2f} - {df["price_try"].max():.2f}')
print(f'\nRoom distribution:')
print(df['room_count'].value_counts())
print(f'\nDistrict distribution:')
print(df['district'].value_counts())
print(f'\nPrice statistics:')
print(f'Average: ₺{df["price_try"].mean():.2f}')
print(f'Median: ₺{df["price_try"].median():.2f}')
print(f'\nSample records:')
print(df[['property_id', 'title', 'district', 'room_count', 'price', 'currency', 'price_try']].head(5))

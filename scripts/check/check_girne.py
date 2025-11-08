import pandas as pd

df = pd.read_csv('property_details.csv')

print(f'Toplam ilan: {len(df)}')
print(f'\nGirne ilanları:')
girne = df[df['city']=='Girne']
print(f'  Toplam: {len(girne)}')
print(f'  Kiralık: {len(girne[girne["listing_type"]=="Rent"])}')
print(f'  Satılık: {len(girne[girne["listing_type"]=="Sale"])}')

print(f'\nGirne Kiralık Mahalleler:')
girne_rent = girne[girne['listing_type']=='Rent']
if len(girne_rent) > 0:
    print(girne_rent['district'].value_counts())
else:
    print('  Hiç kiralık yok!')

print(f'\nÖrnek Property ID\'ler:')
print(girne_rent[['property_id', 'district']].head(10))

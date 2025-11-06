import pandas as pd

df = pd.read_csv('property_details.csv')

print(f'Toplam: {len(df)}')
print(f'Kiralık: {len(df[df["listing_type"]=="Kiralık"])}')
print(f'Satılık: {len(df[df["listing_type"]=="Satılık"])}')
print('\nSatılık Kategoriler:')
print(df[df['listing_type']=='Satılık']['property_type'].value_counts())
print('\nSatılık Şehirler:')
print(df[df['listing_type']=='Satılık']['city'].value_counts())

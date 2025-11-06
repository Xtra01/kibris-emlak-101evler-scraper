import pandas as pd

df = pd.read_csv('property_details.csv')
print(f'Total records: {len(df)}')

# Check Lefkosa rentals
lefkosa_rent = df[(df['city'].str.contains('Lefko', case=False, na=False)) & (df['listing_type'] == 'Rent')]
print(f'\nLefkosa Rent records: {len(lefkosa_rent)}')

if len(lefkosa_rent) > 0:
    print(f'Price range: {lefkosa_rent["price"].min()} - {lefkosa_rent["price"].max()}')
    print(f'\nCurrency distribution:')
    print(lefkosa_rent['currency'].value_counts())
    
    # Check price_try column
    if 'price_try' in df.columns:
        print(f'\nTRY price range: {lefkosa_rent["price_try"].min():.2f} - {lefkosa_rent["price_try"].max():.2f}')
        under_30k = lefkosa_rent[lefkosa_rent['price_try'] <= 30000]
        print(f'Records under 30,000 TRY: {len(under_30k)}')
    else:
        print('\nNo price_try column found in CSV')
else:
    print('No Lefkosa rental records found!')

print(f'\nCity distribution:')
print(df['city'].value_counts().head(10))
print(f'\nListing type distribution:')
print(df['listing_type'].value_counts())

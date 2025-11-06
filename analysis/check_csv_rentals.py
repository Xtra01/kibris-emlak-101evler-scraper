import pandas as pd

df = pd.read_csv('property_details.csv')

print(f"Total records in CSV: {len(df)}")
print(f"\nListing type distribution:")
print(df['listing_type'].value_counts())
print(f"\nCurrency distribution:")
print(df['currency'].value_counts())
print(f"\nPrice statistics:")
print(df['price'].describe())

# Filter for rentals
rentals = df[df['listing_type'] == 'Rent']
print(f"\n{'='*60}")
print(f"Total rental listings: {len(rentals)}")

if len(rentals) > 0:
    print(f"\nRental price range:")
    print(f"Min: {rentals['price'].min()}")
    print(f"Max: {rentals['price'].max()}")
    print(f"Mean: {rentals['price'].mean():.2f}")
    
    # Filter ≤550 GBP
    under_550 = rentals[rentals['price'] <= 550]
    print(f"\nRentals ≤550 GBP: {len(under_550)}")
    
    if len(under_550) > 0:
        print(f"\nPrice distribution:")
        print(under_550['price'].value_counts().sort_index())
        print(f"\nCity distribution:")
        print(under_550['city'].value_counts())

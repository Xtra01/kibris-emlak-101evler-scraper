#!/usr/bin/env python3
"""
451524 VE 484941 Kontrol Script
"""

import pandas as pd

df = pd.read_csv('property_details.csv')

print("="*70)
print("HEDEF ILANLAR KONTROLU")
print("="*70)
print()

# 451524
row1 = df[df['property_id'] == 451524.0]
if not row1.empty:
    print("BULUNDU 451524!")
    print(f"  Baslik: {row1.iloc[0]['title']}")
    print(f"  Sehir: {row1.iloc[0]['city']}")
    print(f"  Mahalle: {row1.iloc[0]['district']}")
    print(f"  Tip: {row1.iloc[0]['listing_type']}")
    print(f"  Fiyat: {row1.iloc[0]['price']} {row1.iloc[0]['currency']}")
else:
    print("YOK 451524")

print()

# 484941
row2 = df[df['property_id'] == 484941.0]
if not row2.empty:
    print("BULUNDU 484941!")
    print(f"  Baslik: {row2.iloc[0]['title']}")
    print(f"  Sehir: {row2.iloc[0]['city']}")
    print(f"  Mahalle: {row2.iloc[0]['district']}")
    print(f"  Tip: {row2.iloc[0]['listing_type']}")
    print(f"  Fiyat: {row2.iloc[0]['price']} {row2.iloc[0]['currency']}")
else:
    print("YOK 484941")

print()
print("="*70)
print("GIRNE GENEL")
print("="*70)

girne = df[df['city'] == 'Girne']
girne_kiralik = girne[girne['listing_type'] == 'Kiralik']

print(f"Toplam ilan: {len(df)}")
print(f"Girne Toplam: {len(girne)}")
print(f"Girne Kiralik: {len(girne_kiralik)}")

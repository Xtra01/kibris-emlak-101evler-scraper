#!/usr/bin/env python3
"""CSV Analiz ve İstatistikler"""

import pandas as pd

# Archive'deki CSV'yi analiz et
print("\n" + "="*70)
print("📊 CSV ANALİZ VE İSTATİSTİKLER")
print("="*70)

df = pd.read_csv('reports/archive/property_details.csv')
print(f"\n✅ CSV Yüklendi: {len(df):,} kayıt")
print(f"📁 Dosya: reports/archive/property_details.csv")

print("\n🏙️  ŞEHİR DAĞILIMI:")
print("-" * 50)
city_counts = df['city'].value_counts().head(10)
for city, count in city_counts.items():
    percent = (count / len(df)) * 100
    print(f"   {str(city)[:20]:20} : {count:4,} ilan (%{percent:.1f})")

print("\n🏠 EMLAK TİPİ DAĞILIMI:")
print("-" * 50)
type_counts = df['property_type'].value_counts()
for ptype, count in type_counts.items():
    percent = (count / len(df)) * 100
    print(f"   {str(ptype)[:20]:20} : {count:4,} ilan (%{percent:.1f})")

print("\n💰 SATILAL/KİRALIK DAĞILIMI:")
print("-" * 50)
listing_counts = df['listing_type'].value_counts()
for ltype, count in listing_counts.items():
    percent = (count / len(df)) * 100
    print(f"   {str(ltype)[:20]:20} : {count:4,} ilan (%{percent:.1f})")

print("\n" + "="*70)
print("✅ Veri analizi tamamlandı!")
print("="*70)
print()

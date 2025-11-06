import pandas as pd
import numpy as np
from datetime import datetime

# Load data
df = pd.read_excel('reports/all_rentals_under_550gbp.xlsx')

print(f"📊 TOPLAM İLAN SAYISI: {len(df)}")
print(f"\n{'='*80}\n")

# Compute price_try if not exists
if 'price_try' not in df.columns:
    # Simple conversion using approximate rate
    df['price_try'] = df.apply(lambda r: r['price'] * 54.69 if r['currency'] == 'GBP' else r['price'] * 37.86 if r['currency'] == 'USD' else r['price'], axis=1)

# Basic statistics
print("💰 FİYAT ANALİZİ")
print(f"Min: {df['price'].min()} {df['currency'].mode()[0]}")
print(f"Max: {df['price'].max()} {df['currency'].mode()[0]}")
print(f"Ortalama: {df['price'].mean():.2f} {df['currency'].mode()[0]}")
print(f"Medyan: {df['price'].median():.2f} {df['currency'].mode()[0]}")
print(f"\nTRY cinsinden:")
print(f"Min: ₺{df['price_try'].min():,.2f}")
print(f"Max: ₺{df['price_try'].max():,.2f}")
print(f"Ortalama: ₺{df['price_try'].mean():,.2f}")
print(f"Medyan: ₺{df['price_try'].median():,.2f}")

print(f"\n{'='*80}\n")

# City distribution
print("🏙️ ŞEHİR DAĞILIMI")
city_dist = df['city'].value_counts()
for city, count in city_dist.items():
    pct = (count / len(df)) * 100
    avg_price = df[df['city'] == city]['price_try'].mean()
    print(f"{city}: {count} ilan (%{pct:.1f}) - Ort. kira: ₺{avg_price:,.2f}")

print(f"\n{'='*80}\n")

# Room type distribution
print("🏠 ODA TİPİ DAĞILIMI")
room_dist = df['room_count'].value_counts()
for room, count in room_dist.items():
    pct = (count / len(df)) * 100
    avg_price = df[df['room_count'] == room]['price_try'].mean()
    print(f"{room}: {count} ilan (%{pct:.1f}) - Ort. kira: ₺{avg_price:,.2f}")

print(f"\n{'='*80}\n")

# District analysis (top 10)
print("📍 EN POPÜLER BÖLGELER (İlk 10)")
district_dist = df['district'].value_counts().head(10)
for district, count in district_dist.items():
    avg_price = df[df['district'] == district]['price_try'].mean()
    print(f"{district}: {count} ilan - Ort. kira: ₺{avg_price:,.2f}")

print(f"\n{'='*80}\n")

# Area analysis
if 'area_m2' in df.columns:
    has_area = df['area_m2'].notna().sum()
    print(f"📐 ALAN BİLGİSİ")
    print(f"Alan bilgisi olan: {has_area} ilan ({(has_area/len(df)*100):.1f}%)")
    if has_area > 0:
        print(f"Min alan: {df['area_m2'].min():.0f} m²")
        print(f"Max alan: {df['area_m2'].max():.0f} m²")
        print(f"Ortalama alan: {df['area_m2'].mean():.0f} m²")
        
        # Price per m2
        df['price_per_m2'] = df['price_try'] / df['area_m2']
        valid_price_m2 = df['price_per_m2'].dropna()
        if len(valid_price_m2) > 0:
            print(f"\nMetrekare fiyatı:")
            print(f"Min: ₺{valid_price_m2.min():.2f}/m²")
            print(f"Max: ₺{valid_price_m2.max():.2f}/m²")
            print(f"Ortalama: ₺{valid_price_m2.mean():.2f}/m²")

print(f"\n{'='*80}\n")

# Payment terms analysis
if 'payment_interval' in df.columns:
    print("💳 ÖDEME ŞARTLARI")
    payment_dist = df['payment_interval'].value_counts()
    for payment, count in payment_dist.items():
        pct = (count / len(df)) * 100
        print(f"{payment}: {count} ilan (%{pct:.1f})")

print(f"\n{'='*80}\n")

# Contact info availability
print("📞 İLETİŞİM BİLGİSİ DURUM")
has_phone = df['phone_numbers'].notna().sum() if 'phone_numbers' in df.columns else 0
has_whatsapp = df['whatsapp_numbers'].notna().sum() if 'whatsapp_numbers' in df.columns else 0
print(f"Telefon numarası olan: {has_phone} ilan ({(has_phone/len(df)*100):.1f}%)")
print(f"WhatsApp numarası olan: {has_whatsapp} ilan ({(has_whatsapp/len(df)*100):.1f}%)")

print(f"\n{'='*80}\n")

# Price ranges
print("💵 FİYAT ARALIKLARI (GBP)")
price_ranges = [
    (0, 350, "Çok Ekonomik"),
    (350, 450, "Ekonomik"),
    (450, 500, "Orta"),
    (500, 550, "Üst Orta")
]

for min_p, max_p, label in price_ranges:
    count = len(df[(df['price'] >= min_p) & (df['price'] < max_p)])
    pct = (count / len(df)) * 100
    print(f"{label} (£{min_p}-{max_p}): {count} ilan (%{pct:.1f})")

print(f"\n{'='*80}\n")

# SCORING SYSTEM
print("🎯 PUANLAMA SİSTEMİ HESAPLANIYOR...")
print("Kriterler: Fiyat (30%), Alan (20%), Konum (20%), İletişim (15%), Güncellik (15%)\n")

# Initialize score
df['score'] = 0.0
df['score_details'] = ''

# 1. Price Score (30 points) - Lower is better
if 'price_try' in df.columns:
    max_price = df['price_try'].max()
    min_price = df['price_try'].min()
    df['price_score'] = ((max_price - df['price_try']) / (max_price - min_price)) * 30
    df['score'] += df['price_score']

# 2. Area Score (20 points) - Bigger is better
if 'area_m2' in df.columns:
    max_area = df['area_m2'].max()
    min_area = df['area_m2'].min()
    df['area_score'] = df.apply(
        lambda r: ((r['area_m2'] - min_area) / (max_area - min_area)) * 20 if pd.notna(r['area_m2']) else 10,
        axis=1
    )
    df['score'] += df['area_score']
else:
    df['area_score'] = 10  # Default if no area info

# 3. Location Score (20 points)
# Prefer: Lefkoşa > Girne > Mağusa > İskele > Güzelyurt
location_scores = {
    'Lefkoşa': 20,
    'Girne': 18,
    'Mağusa': 16,
    'Gazimağusa': 16,
    'İskele': 14,
    'Güzelyurt': 12
}
df['location_score'] = df['city'].map(lambda x: location_scores.get(x, 10) if pd.notna(x) else 10)
df['score'] += df['location_score']

# 4. Contact Score (15 points)
df['contact_score'] = 0
if 'phone_numbers' in df.columns:
    df['contact_score'] += df['phone_numbers'].notna().astype(int) * 7.5
if 'whatsapp_numbers' in df.columns:
    df['contact_score'] += df['whatsapp_numbers'].notna().astype(int) * 7.5
df['score'] += df['contact_score']

# 5. Freshness Score (15 points) - Recent updates are better
if 'update_date' in df.columns:
    df['update_date_parsed'] = pd.to_datetime(df['update_date'], format='%d/%m/%Y', errors='coerce')
    latest_date = df['update_date_parsed'].max()
    oldest_date = df['update_date_parsed'].min()
    
    df['freshness_score'] = df.apply(
        lambda r: ((r['update_date_parsed'] - oldest_date).days / (latest_date - oldest_date).days) * 15 
        if pd.notna(r['update_date_parsed']) else 7.5,
        axis=1
    )
    df['score'] += df['freshness_score']
else:
    df['freshness_score'] = 7.5  # Default

# Round scores
df['score'] = df['score'].round(1)

# Sort by score
df_sorted = df.sort_values('score', ascending=False)

print(f"✅ Puanlama tamamlandı!\n")
print(f"{'='*80}\n")

# Top 20 listings
print("🏆 EN İYİ 20 İLAN (Puan Sırasına Göre)\n")
display_cols = ['property_id', 'title', 'city', 'district', 'room_count', 'price', 'currency', 
                'price_try', 'area_m2', 'score']
top20 = df_sorted[display_cols].head(20)

for idx, row in top20.iterrows():
    print(f"\n{'─'*80}")
    print(f"🏅 PUAN: {row['score']}/100")
    print(f"ID: {row['property_id']}")
    print(f"📍 {row['city']} - {row['district']}")
    print(f"🏠 {row['room_count']}")
    print(f"💰 £{row['price']} ({row['currency']}) = ₺{row['price_try']:,.2f}/ay")
    if pd.notna(row['area_m2']):
        print(f"📐 {row['area_m2']:.0f} m²")
    print(f"📝 {row['title'][:80]}...")

print(f"\n{'='*80}\n")

# Score distribution
print("📊 PUAN DAĞILIMI")
score_ranges = [
    (80, 100, "Mükemmel"),
    (70, 80, "Çok İyi"),
    (60, 70, "İyi"),
    (50, 60, "Orta"),
    (0, 50, "Düşük")
]

for min_s, max_s, label in score_ranges:
    count = len(df_sorted[(df_sorted['score'] >= min_s) & (df_sorted['score'] < max_s)])
    pct = (count / len(df_sorted)) * 100
    print(f"{label} ({min_s}-{max_s}): {count} ilan (%{pct:.1f})")

# Save scored data
output_file = 'reports/all_rentals_under_550gbp_SCORED.xlsx'
df_sorted.to_excel(output_file, index=False)
print(f"\n✅ Puanlanmış data kaydedildi: {output_file}")

# Export top 20 separately
top20_full = df_sorted.head(20)
top20_file = 'reports/TOP20_rentals_under_550gbp.xlsx'
top20_full.to_excel(top20_file, index=False)
print(f"✅ En iyi 20 ilan ayrı dosyaya kaydedildi: {top20_file}")

print(f"\n{'='*80}")
print("🎉 ANALİZ TAMAMLANDI!")
print(f"{'='*80}\n")

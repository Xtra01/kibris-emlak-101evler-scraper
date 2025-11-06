import pandas as pd
import numpy as np
from datetime import datetime

# Load data from CSV
df = pd.read_csv('property_details.csv')

# Filter for rentals ≤550 GBP
rentals = df[(df['listing_type'] == 'Rent') & (df['price'] <= 550)]

print(f"📊 550 GBP VE ALTI KİRALIK EVLER - DETAYLI ANALİZ VE PUANLAMA")
print(f"{'='*80}\n")
print(f"📌 TOPLAM İLAN SAYISI: {len(rentals)}")
print(f"\n{'='*80}\n")

# Compute TRY prices with current exchange rate
GBP_RATE = 54.693  # Current TCMB rate
rentals = rentals.copy()
rentals['price_try'] = rentals['price'] * GBP_RATE

# Basic statistics
print("💰 FİYAT ANALİZİ")
print(f"\nGBP Fiyatları:")
print(f"  Min: £{rentals['price'].min():.2f}")
print(f"  Max: £{rentals['price'].max():.2f}")
print(f"  Ortalama: £{rentals['price'].mean():.2f}")
print(f"  Medyan: £{rentals['price'].median():.2f}")
print(f"\nTRY Fiyatları (Kur: {GBP_RATE}):")
print(f"  Min: ₺{rentals['price_try'].min():,.2f}")
print(f"  Max: ₺{rentals['price_try'].max():,.2f}")
print(f"  Ortalama: ₺{rentals['price_try'].mean():,.2f}")
print(f"  Medyan: ₺{rentals['price_try'].median():,.2f}")

print(f"\n{'='*80}\n")

# City distribution
print("🏙️ ŞEHİR DAĞILIMI")
city_dist = rentals['city'].value_counts()
for city, count in city_dist.items():
    pct = (count / len(rentals)) * 100
    avg_price = rentals[rentals['city'] == city]['price_try'].mean()
    print(f"  {city}: {count} ilan (%{pct:.1f}) - Ort. kira: ₺{avg_price:,.2f}")

print(f"\n{'='*80}\n")

# Room type distribution
print("🏠 ODA TİPİ DAĞILIMI")
room_dist = rentals['room_count'].value_counts()
for room, count in room_dist.items():
    pct = (count / len(rentals)) * 100
    avg_price = rentals[rentals['room_count'] == room]['price_try'].mean()
    print(f"  {room}: {count} ilan (%{pct:.1f}) - Ort. kira: ₺{avg_price:,.2f}")

print(f"\n{'='*80}\n")

# District analysis
print("📍 BÖLGE DAĞILIMI")
district_dist = rentals['district'].value_counts()
for district, count in district_dist.items():
    avg_price = rentals[rentals['district'] == district]['price_try'].mean()
    print(f"  {district}: {count} ilan - Ort. kira: ₺{avg_price:,.2f}")

print(f"\n{'='*80}\n")

# Area analysis
has_area = rentals['area_m2'].notna().sum()
print(f"📐 ALAN BİLGİSİ")
print(f"  Alan bilgisi olan: {has_area} ilan (%{(has_area/len(rentals)*100):.1f})")
if has_area > 0:
    area_data = rentals[rentals['area_m2'].notna()]
    print(f"  Min alan: {area_data['area_m2'].min():.0f} m²")
    print(f"  Max alan: {area_data['area_m2'].max():.0f} m²")
    print(f"  Ortalama alan: {area_data['area_m2'].mean():.0f} m²")
    
    # Price per m2
    area_data = area_data.copy()
    area_data['price_per_m2'] = area_data['price_try'] / area_data['area_m2']
    print(f"\n  Metrekare Fiyatı:")
    print(f"    Min: ₺{area_data['price_per_m2'].min():.2f}/m²")
    print(f"    Max: ₺{area_data['price_per_m2'].max():.2f}/m²")
    print(f"    Ortalama: ₺{area_data['price_per_m2'].mean():.2f}/m²")

print(f"\n{'='*80}\n")

# Payment terms analysis
print("💳 ÖDEME ŞARTLARI")
payment_dist = rentals['payment_interval'].value_counts()
for payment, count in payment_dist.items():
    pct = (count / len(rentals)) * 100
    print(f"  {payment}: {count} ilan (%{pct:.1f})")

print(f"\n{'='*80}\n")

# Rental period
print("📅 KİRALAMA SÜRESİ")
period_dist = rentals['min_rental_period'].value_counts()
for period, count in period_dist.items():
    pct = (count / len(rentals)) * 100
    print(f"  {period}: {count} ilan (%{pct:.1f})")

print(f"\n{'='*80}\n")

# Contact info availability
has_phone = rentals['phone_numbers'].notna().sum()
has_whatsapp = rentals['whatsapp_numbers'].notna().sum()
print("📞 İLETİŞİM BİLGİSİ DURUM")
print(f"  Telefon numarası olan: {has_phone} ilan (%{(has_phone/len(rentals)*100):.1f})")
print(f"  WhatsApp numarası olan: {has_whatsapp} ilan (%{(has_whatsapp/len(rentals)*100):.1f})")

print(f"\n{'='*80}\n")

# Price ranges
print("💵 FİYAT ARALIKLARI")
price_ranges = [
    (0, 400, "Çok Ekonomik", "🟢"),
    (400, 475, "Ekonomik", "🟡"),
    (475, 525, "Orta", "🟠"),
    (525, 550, "Üst Sınır", "🔴")
]

for min_p, max_p, label, emoji in price_ranges:
    count = len(rentals[(rentals['price'] >= min_p) & (rentals['price'] < max_p)])
    pct = (count / len(rentals)) * 100
    print(f"  {emoji} {label} (£{min_p}-{max_p}): {count} ilan (%{pct:.1f})")

print(f"\n{'='*80}\n")

# SCORING SYSTEM
print("🎯 AKILLI PUANLAMA SİSTEMİ")
print("=" * 80)
print("""
Puanlama Kriterleri (Toplam 100 Puan):

1️⃣ Fiyat Puanı (30 puan)
   - Düşük fiyat = Yüksek puan
   - £320-400: 25-30 puan
   - £400-500: 15-25 puan
   - £500-550: 0-15 puan

2️⃣ Alan Puanı (20 puan)
   - Geniş alan = Yüksek puan
   - Alan bilgisi yoksa: 10 puan (ortalama)
   - 80+ m²: 15-20 puan
   - 60-80 m²: 10-15 puan
   - <60 m²: 5-10 puan

3️⃣ Lokasyon Puanı (20 puan)
   - Merkezi bölgeler: +5 puan
   - Ulaşım kolaylığı (durak/market yakını): +5 puan
   - Okul yakınlığı: +5 puan
   - Şehir merkezi uzaklığı: +5 puan

4️⃣ İletişim Puanı (15 puan)
   - Telefon var: +7.5 puan
   - WhatsApp var: +7.5 puan

5️⃣ Güncellik Puanı (15 puan)
   - Son 7 gün: 13-15 puan
   - Son 30 gün: 10-13 puan
   - Son 90 gün: 5-10 puan
   - 90+ gün: 0-5 puan

🏆 BONUS PUANLAR:
   + Full eşyalı: +3 puan
   + Asansör var: +2 puan
   + Site içinde: +2 puan
   + Yeni/sıfır: +3 puan
""")
print("=" * 80 + "\n")

# Initialize score
rentals = rentals.copy()
rentals['score'] = 0.0
rentals['score_breakdown'] = ''

# 1. Price Score (30 points) - Lower is better
max_price = rentals['price'].max()
min_price = rentals['price'].min()
if max_price > min_price:
    rentals['price_score'] = ((max_price - rentals['price']) / (max_price - min_price)) * 30
else:
    rentals['price_score'] = 15
rentals['score'] += rentals['price_score']

# 2. Area Score (20 points) - Bigger is better
def calculate_area_score(row):
    if pd.notna(row['area_m2']):
        area = row['area_m2']
        if area >= 80:
            return 20
        elif area >= 60:
            return 15
        elif area >= 40:
            return 10
        else:
            return 5
    return 10  # Default for missing area

rentals['area_score'] = rentals.apply(calculate_area_score, axis=1)
rentals['score'] += rentals['area_score']

# 3. Location Score (20 points)
def calculate_location_score(row):
    score = 10  # Base score
    title_desc = str(row['title']).lower() + ' ' + str(row['description']).lower()
    district = str(row['district']).lower()
    
    # Central locations
    if any(word in district for word in ['kaymaklı', 'merkez', 'center']):
        score += 5
    
    # Transport proximity
    if any(word in title_desc for word in ['durak', 'terminal', 'metro', 'otobüs']):
        score += 5
    
    # School proximity
    if any(word in title_desc for word in ['okul', 'school', 'üniversite']):
        score += 3
    
    # Market proximity
    if any(word in title_desc for word in ['market', 'çarşı', 'alışveriş']):
        score += 2
    
    return min(score, 20)  # Cap at 20

rentals['location_score'] = rentals.apply(calculate_location_score, axis=1)
rentals['score'] += rentals['location_score']

# 4. Contact Score (15 points)
rentals['contact_score'] = 0
rentals['contact_score'] += rentals['phone_numbers'].notna().astype(int) * 7.5
rentals['contact_score'] += rentals['whatsapp_numbers'].notna().astype(int) * 7.5
rentals['score'] += rentals['contact_score']

# 5. Freshness Score (15 points)
def calculate_freshness_score(row):
    if pd.isna(row['update_date']):
        return 7.5
    
    try:
        update_date = pd.to_datetime(row['update_date'], format='%d/%m/%Y')
        today = pd.Timestamp.now()
        days_ago = (today - update_date).days
        
        if days_ago <= 7:
            return 15
        elif days_ago <= 30:
            return 12
        elif days_ago <= 90:
            return 8
        else:
            return 3
    except:
        return 7.5

rentals['freshness_score'] = rentals.apply(calculate_freshness_score, axis=1)
rentals['score'] += rentals['freshness_score']

# BONUS POINTS
def calculate_bonus(row):
    bonus = 0
    title_desc = str(row['title']).lower() + ' ' + str(row['description']).lower()
    
    # Full furnished
    if any(word in title_desc for word in ['full eşya', 'full eşyalı', 'fully furnished']):
        bonus += 3
    
    # Elevator
    if any(word in title_desc for word in ['asansör', 'elevator', 'lift']):
        bonus += 2
    
    # In complex/site
    if any(word in title_desc for word in ['site', 'kompleks', 'complex']):
        bonus += 2
    
    # New/Brand new
    if any(word in title_desc for word in ['sıfır', 'yeni', 'new', 'brand new']):
        bonus += 3
    
    return min(bonus, 10)  # Cap bonus at 10

rentals['bonus_score'] = rentals.apply(calculate_bonus, axis=1)
rentals['score'] += rentals['bonus_score']

# Round scores
rentals['score'] = rentals['score'].round(1)

# Sort by score
rentals_sorted = rentals.sort_values('score', ascending=False).reset_index(drop=True)

print("✅ Puanlama tamamlandı!\n")
print(f"{'='*80}\n")

# Score distribution
print("📊 PUAN DAĞILIMI")
score_ranges = [
    (80, 100, "⭐⭐⭐⭐⭐ Mükemmel"),
    (70, 80, "⭐⭐⭐⭐ Çok İyi"),
    (60, 70, "⭐⭐⭐ İyi"),
    (50, 60, "⭐⭐ Orta"),
    (0, 50, "⭐ Düşük")
]

for min_s, max_s, label in score_ranges:
    count = len(rentals_sorted[(rentals_sorted['score'] >= min_s) & (rentals_sorted['score'] < max_s)])
    pct = (count / len(rentals_sorted)) * 100
    print(f"  {label}: {count} ilan (%{pct:.1f})")

print(f"\n{'='*80}\n")

# Top 10 listings
print("🏆 EN İYİ 10 İLAN (Detaylı Puanlama)")
print("=" * 80 + "\n")

for idx in range(min(10, len(rentals_sorted))):
    row = rentals_sorted.iloc[idx]
    print(f"\n{'━'*80}")
    print(f"🥇 SIRA: #{idx+1}  |  🎯 TOPLAM PUAN: {row['score']:.1f}/100")
    print(f"{'━'*80}")
    print(f"🆔 İlan No: {row['property_id']}")
    print(f"📝 Başlık: {row['title'][:70]}...")
    print(f"📍 Konum: {row['city']} - {row['district']}")
    print(f"🏠 Oda Sayısı: {row['room_count']}")
    print(f"💰 Kira: £{row['price']:.0f} ({row['currency']}) = ₺{row['price_try']:,.2f}/ay")
    
    if pd.notna(row['area_m2']):
        price_per_m2 = row['price_try'] / row['area_m2']
        print(f"📐 Alan: {row['area_m2']:.0f} m² (₺{price_per_m2:.2f}/m²)")
    else:
        print(f"📐 Alan: Bilgi yok")
    
    if pd.notna(row['payment_interval']):
        print(f"💳 Ödeme: {row['payment_interval']}")
    
    if pd.notna(row['min_rental_period']):
        print(f"📅 Süre: {row['min_rental_period']}")
    
    # Score breakdown
    print(f"\n📊 PUAN DETAYI:")
    print(f"   💵 Fiyat: {row['price_score']:.1f}/30")
    print(f"   📐 Alan: {row['area_score']:.1f}/20")
    print(f"   📍 Lokasyon: {row['location_score']:.1f}/20")
    print(f"   📞 İletişim: {row['contact_score']:.1f}/15")
    print(f"   🕐 Güncellik: {row['freshness_score']:.1f}/15")
    if row['bonus_score'] > 0:
        print(f"   🎁 Bonus: +{row['bonus_score']:.1f}")
    
    if pd.notna(row['phone_numbers']):
        print(f"📞 Tel: {row['phone_numbers']}")
    if pd.notna(row['whatsapp_numbers']):
        print(f"💬 WhatsApp: {row['whatsapp_numbers']}")
    
    if pd.notna(row['url']):
        print(f"🔗 Link: {row['url']}")

print(f"\n{'='*80}\n")

# Save scored data
output_file = 'reports/all_rentals_under_550gbp_SCORED.xlsx'
rentals_sorted.to_excel(output_file, index=False)
print(f"✅ Puanlanmış tam data kaydedildi: {output_file}")

# Export top 10 separately
top10_file = 'reports/TOP10_rentals_under_550gbp.xlsx'
rentals_sorted.head(10).to_excel(top10_file, index=False)
print(f"✅ En iyi 10 ilan ayrı dosyaya kaydedildi: {top10_file}")

# Create summary report
print(f"\n{'='*80}")
print("📄 ÖZET RAPOR HAZIR!")
print(f"{'='*80}\n")

print("📦 OLUŞTURULAN DOSYALAR:")
print(f"  1. {output_file}")
print(f"     → Tüm ilanlar puanlarıyla ({len(rentals_sorted)} kayıt)")
print(f"  2. {top10_file}")
print(f"     → En iyi 10 ilan detaylı bilgilerle")

print(f"\n💡 ÖNERİLER:")
print(f"  • En yüksek puan: {rentals_sorted['score'].max():.1f}/100")
print(f"  • Ortalama puan: {rentals_sorted['score'].mean():.1f}/100")
print(f"  • 70+ puan alan ilan sayısı: {len(rentals_sorted[rentals_sorted['score'] >= 70])}")

# Best value recommendations
print(f"\n🎯 EN İYİ DEĞER ÖNERİLERİ:")
best_value = rentals_sorted.head(3)
for idx, row in best_value.iterrows():
    print(f"\n  {idx+1}. {row['district']} - {row['room_count']}")
    print(f"     £{row['price']:.0f}/ay (₺{row['price_try']:,.2f})")
    print(f"     Puan: {row['score']:.1f}/100")
    if pd.notna(row['area_m2']):
        print(f"     {row['area_m2']:.0f} m²")

print(f"\n{'='*80}")
print("🎉 ANALİZ TAMAMLANDI!")
print(f"{'='*80}\n")

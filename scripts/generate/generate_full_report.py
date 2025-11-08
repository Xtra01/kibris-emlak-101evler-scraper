#!/usr/bin/env python3
"""
KKTC KİRALIK EMLAK - KAPSAMLI DÜZENLI RAPOR OLUŞTURUCU
======================================================

Bu script, property_details.csv'den tüm kiralık ilanları alıp:
- Detaylı sütunlar halinde düzenli Excel raporu
- Raw data formatında ama düzenli
- Tüm kategorileri içeren
- Filtrelenebilir ve sıralanabilir

ÇIKTI:
    reports/FULL_RENTAL_DATA_KKTC_TIMESTAMP.xlsx
    reports/FULL_RENTAL_DATA_KKTC_TIMESTAMP_summary.md
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path

print("""
╔════════════════════════════════════════════════════════════╗
║   KKTC KİRALIK EMLAK - KAPSAMLI RAPOR OLUŞTURUCU         ║
╚════════════════════════════════════════════════════════════╝
""")

# Rapor klasörü
reports_dir = Path('reports')
reports_dir.mkdir(exist_ok=True)

# Timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# CSV oku
csv_path = 'property_details.csv'
if not os.path.exists(csv_path):
    print(f"❌ CSV dosyası bulunamadı: {csv_path}")
    print("   Önce scraping yapmalısınız: python full_rental_scan.py")
    exit(1)

print(f"📊 CSV okunuyor: {csv_path}")
df = pd.read_csv(csv_path)

print(f"   Toplam kayıt: {len(df)}")

# Sadece kiralıklar
rentals = df[df['listing_type'] == 'Rent'].copy()
print(f"   Kiralık kayıt: {len(rentals)}")

if len(rentals) == 0:
    print("❌ Kiralık ilan bulunamadı!")
    exit(1)

print(f"\n📋 Sütunlar ({len(rentals.columns)} adet):")
for col in rentals.columns:
    print(f"   • {col}")

# TRY fiyat hesapla (yoksa)
if 'price_try' not in rentals.columns or rentals['price_try'].isna().all():
    print("\n💱 TRY fiyatları hesaplanıyor...")
    
    # TCMB kuru al (varsayılan 54.7)
    try:
        import requests
        response = requests.get('https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.GBP.S.YTL&type=json')
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                gbp_rate = float(data['items'][-1]['TP_DK_GBP_S_YTL'])
                print(f"   TCMB GBP kuru: {gbp_rate:.4f}")
            else:
                gbp_rate = 54.7
                print(f"   Varsayılan GBP kuru: {gbp_rate}")
        else:
            gbp_rate = 54.7
            print(f"   Varsayılan GBP kuru: {gbp_rate}")
    except:
        gbp_rate = 54.7
        print(f"   Varsayılan GBP kuru: {gbp_rate}")
    
    # Fiyat hesapla
    def calculate_try(row):
        if pd.isna(row['price']):
            return None
        if row['currency'] == 'GBP' or row['currency'] == '£':
            return row['price'] * gbp_rate
        return row['price']
    
    rentals['price_try'] = rentals.apply(calculate_try, axis=1)
    print(f"   ✅ {rentals['price_try'].notna().sum()} ilan için TRY fiyat hesaplandı")

# Sıralama için sütunları düzenle
column_order = [
    # Temel bilgiler
    'property_id',
    'title',
    'city',
    'district',
    
    # Kategori
    'listing_type',
    'property_type',
    'property_subtype',
    
    # Fiyat
    'price',
    'currency',
    'price_try',
    
    # Alan bilgileri
    'room_count',
    'area_m2',
    'area_text',
    
    # Özellikler
    'features',
    'furnished',
    'elevator',
    
    # İletişim
    'phone_numbers',
    'whatsapp_numbers',
    'agent_name',
    
    # Tarih
    'listing_date',
    'listing_age_days',
    
    # Link
    'url',
    
    # Açıklama
    'description',
]

# Mevcut sütunları sırayla ekle
ordered_columns = []
for col in column_order:
    if col in rentals.columns:
        ordered_columns.append(col)

# Kalan sütunları ekle
for col in rentals.columns:
    if col not in ordered_columns:
        ordered_columns.append(col)

rentals = rentals[ordered_columns]

# Excel'e kaydet
print(f"\n📊 Excel raporu oluşturuluyor...")

excel_path = reports_dir / f'FULL_RENTAL_DATA_KKTC_{timestamp}.xlsx'

with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    
    # Tüm veriler
    rentals.to_excel(writer, sheet_name='TÜM KİRALIKLAR', index=False)
    
    # Kategorilere göre ayrı sheet'ler
    if 'property_subtype' in rentals.columns:
        for category in rentals['property_subtype'].unique():
            if pd.notna(category):
                category_data = rentals[rentals['property_subtype'] == category]
                sheet_name = str(category)[:31]  # Excel limit
                category_data.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Şehirlere göre ayrı sheet'ler
    for city in rentals['city'].unique():
        if pd.notna(city):
            city_data = rentals[rentals['city'] == city]
            sheet_name = f"📍 {str(city)}"[:31]
            city_data.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Fiyat aralıklarına göre
    if 'price_try' in rentals.columns:
        # 0-30k
        price_0_30k = rentals[rentals['price_try'] <= 30000]
        if len(price_0_30k) > 0:
            price_0_30k.to_excel(writer, sheet_name='💰 0-30K TRY', index=False)
        
        # 30-50k
        price_30_50k = rentals[(rentals['price_try'] > 30000) & (rentals['price_try'] <= 50000)]
        if len(price_30_50k) > 0:
            price_30_50k.to_excel(writer, sheet_name='💰 30-50K TRY', index=False)
        
        # 50k+
        price_50k_plus = rentals[rentals['price_try'] > 50000]
        if len(price_50k_plus) > 0:
            price_50k_plus.to_excel(writer, sheet_name='💰 50K+ TRY', index=False)
    
    # İstatistikler sheet'i
    stats_data = []
    
    # Genel istatistikler
    stats_data.append(['📊 GENEL İSTATİSTİKLER', ''])
    stats_data.append(['Toplam İlan', len(rentals)])
    stats_data.append(['', ''])
    
    # Şehir dağılımı
    stats_data.append(['🏙️ ŞEHİR DAĞILIMI', ''])
    for city, count in rentals['city'].value_counts().items():
        stats_data.append([city, count])
    stats_data.append(['', ''])
    
    # Kategori dağılımı
    if 'property_subtype' in rentals.columns:
        stats_data.append(['🏠 KATEGORİ DAĞILIMI', ''])
        for cat, count in rentals['property_subtype'].value_counts().items():
            stats_data.append([cat, count])
        stats_data.append(['', ''])
    
    # Fiyat istatistikleri
    if 'price_try' in rentals.columns:
        stats_data.append(['💰 FİYAT İSTATİSTİKLERİ (TRY)', ''])
        stats_data.append(['Minimum', f"{rentals['price_try'].min():.0f}"])
        stats_data.append(['Maksimum', f"{rentals['price_try'].max():.0f}"])
        stats_data.append(['Ortalama', f"{rentals['price_try'].mean():.0f}"])
        stats_data.append(['Medyan', f"{rentals['price_try'].median():.0f}"])
        stats_data.append(['', ''])
    
    # Alan istatistikleri
    if 'area_m2' in rentals.columns:
        stats_data.append(['📐 ALAN İSTATİSTİKLERİ (m²)', ''])
        area_data = rentals[rentals['area_m2'].notna()]
        if len(area_data) > 0:
            stats_data.append(['Minimum', f"{area_data['area_m2'].min():.0f}"])
            stats_data.append(['Maksimum', f"{area_data['area_m2'].max():.0f}"])
            stats_data.append(['Ortalama', f"{area_data['area_m2'].mean():.0f}"])
    
    stats_df = pd.DataFrame(stats_data, columns=['İstatistik', 'Değer'])
    stats_df.to_excel(writer, sheet_name='📊 İSTATİSTİKLER', index=False)

print(f"✅ Excel raporu oluşturuldu: {excel_path}")
print(f"   Sheet sayısı: {len(rentals['city'].unique()) + len(rentals['property_subtype'].unique()) + 5}")

# Markdown özet raporu
print(f"\n📝 Markdown özeti oluşturuluyor...")

md_path = reports_dir / f'FULL_RENTAL_DATA_KKTC_{timestamp}_summary.md'

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"""# KKTC KİRALIK EMLAK - KAPSAMLI RAPOR

**Oluşturulma Tarihi:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Excel Rapor:** `{excel_path.name}`

---

## 📊 GENEL İSTATİSTİKLER

- **Toplam İlan:** {len(rentals):,}
- **Şehir Sayısı:** {rentals['city'].nunique()}
- **Kategori Sayısı:** {rentals['property_subtype'].nunique() if 'property_subtype' in rentals.columns else 'N/A'}

---

## 🏙️ ŞEHİR DAĞILIMI

| Şehir | İlan Sayısı | Yüzde |
|-------|-------------|-------|
""")
    
    for city, count in rentals['city'].value_counts().items():
        percentage = (count / len(rentals)) * 100
        f.write(f"| {city} | {count:,} | {percentage:.1f}% |\n")
    
    f.write(f"""
---

## 🏠 KATEGORİ DAĞILIMI

""")
    
    if 'property_subtype' in rentals.columns:
        f.write("| Kategori | İlan Sayısı | Yüzde |\n")
        f.write("|----------|-------------|-------|\n")
        for cat, count in rentals['property_subtype'].value_counts().items():
            percentage = (count / len(rentals)) * 100
            f.write(f"| {cat} | {count:,} | {percentage:.1f}% |\n")
    
    f.write(f"""
---

## 💰 FİYAT ANALİZİ (TRY)

""")
    
    if 'price_try' in rentals.columns:
        price_data = rentals[rentals['price_try'].notna()]
        f.write(f"""
- **Minimum:** ₺{price_data['price_try'].min():,.0f}
- **Maksimum:** ₺{price_data['price_try'].max():,.0f}
- **Ortalama:** ₺{price_data['price_try'].mean():,.0f}
- **Medyan:** ₺{price_data['price_try'].median():,.0f}

### Fiyat Dağılımı

| Aralık | İlan Sayısı | Yüzde |
|--------|-------------|-------|
| 0-30,000 TRY | {len(rentals[rentals['price_try'] <= 30000]):,} | {(len(rentals[rentals['price_try'] <= 30000]) / len(rentals)) * 100:.1f}% |
| 30,001-50,000 TRY | {len(rentals[(rentals['price_try'] > 30000) & (rentals['price_try'] <= 50000)]):,} | {(len(rentals[(rentals['price_try'] > 30000) & (rentals['price_try'] <= 50000)]) / len(rentals)) * 100:.1f}% |
| 50,000+ TRY | {len(rentals[rentals['price_try'] > 50000]):,} | {(len(rentals[rentals['price_try'] > 50000]) / len(rentals)) * 100:.1f}% |
""")
    
    f.write(f"""
---

## 📐 ALAN ANALİZİ

""")
    
    if 'area_m2' in rentals.columns:
        area_data = rentals[rentals['area_m2'].notna()]
        if len(area_data) > 0:
            f.write(f"""
- **Minimum:** {area_data['area_m2'].min():.0f} m²
- **Maksimum:** {area_data['area_m2'].max():.0f} m²
- **Ortalama:** {area_data['area_m2'].mean():.0f} m²
- **Medyan:** {area_data['area_m2'].median():.0f} m²
""")
    
    f.write(f"""
---

## 📞 İLETİŞİM BİLGİSİ DURUMU

- **Telefon numarası olan:** {rentals['phone_numbers'].notna().sum():,} ({(rentals['phone_numbers'].notna().sum() / len(rentals)) * 100:.1f}%)
- **WhatsApp olan:** {rentals['whatsapp_numbers'].notna().sum():,} ({(rentals['whatsapp_numbers'].notna().sum() / len(rentals)) * 100:.1f}%)

---

## 📁 EXCEL SHEET'LERİ

Excel dosyasında aşağıdaki sheet'ler bulunmaktadır:

1. **TÜM KİRALIKLAR** - Tüm kiralık ilanlar (ham data)
2. **Kategori Sheet'leri** - Her kategori için ayrı sheet
3. **Şehir Sheet'leri** - Her şehir için ayrı sheet
4. **Fiyat Aralığı Sheet'leri** - 0-30K, 30-50K, 50K+ TRY
5. **📊 İSTATİSTİKLER** - Özet istatistikler

---

## 🔍 KULLANIM

Excel dosyasını açtıktan sonra:

1. **Filtreleme:** Her sütun başlığına tıklayıp filtre uygulayabilirsiniz
2. **Sıralama:** Sütun başlığına tıklayıp sıralayabilirsiniz
3. **Arama:** Ctrl+F ile arama yapabilirsiniz
4. **Pivot Tablo:** Insert > Pivot Table ile özel analizler yapabilirsiniz

---

## 📊 SÜTUN AÇIKLAMALARI

- **property_id:** Benzersiz ilan ID
- **title:** İlan başlığı
- **city:** Şehir
- **district:** İlçe/bölge
- **listing_type:** İlan tipi (Rent/Sale)
- **property_type:** Emlak türü
- **property_subtype:** Alt kategori (Daire, Villa, vs.)
- **price:** Fiyat (orijinal para birimi)
- **currency:** Para birimi (GBP/TRY)
- **price_try:** TRY cinsinden fiyat
- **room_count:** Oda sayısı (örn: 2+1)
- **area_m2:** Alan (m²)
- **features:** Özellikler
- **phone_numbers:** Telefon numaraları
- **whatsapp_numbers:** WhatsApp numaraları
- **listing_date:** İlan tarihi
- **url:** İlan linki

---

**Rapor Tarihi:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Not:** Bu rapor otomatik olarak oluşturulmuştur.
""")

print(f"✅ Markdown özeti oluşturuldu: {md_path}")

print(f"""
╔════════════════════════════════════════════════════════════╗
║   RAPOR OLUŞTURMA TAMAMLANDI!                             ║
╚════════════════════════════════════════════════════════════╝

📊 ÇIKTILAR:
   • Excel: {excel_path}
   • Markdown: {md_path}

📈 İSTATİSTİKLER:
   • Toplam ilan: {len(rentals):,}
   • Şehir: {rentals['city'].nunique()}
   • Kategori: {rentals['property_subtype'].nunique() if 'property_subtype' in rentals.columns else 'N/A'}

🎯 SONRAKİ ADIMLAR:
   1. Excel dosyasını açın ve inceleyin
   2. Filtreleme ve sıralama yapın
   3. İhtiyacınıza göre pivot tablo oluşturun

✨ Raporunuz hazır!
""")

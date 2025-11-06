#!/usr/bin/env python3
"""
KKTC SATILIK EMLAK - Kapsamlı Rapor Oluşturucu

CSV'deki tüm satılık ilanları Excel ve Markdown formatında raporlar.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import sys

# Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Sabitler
CSV_FILE = "property_details.csv"
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# GBP kuru (varsayılan)
DEFAULT_GBP_RATE = 54.7

def print_header():
    """Başlık yazdır"""
    print("\n" + "="*60)
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   KKTC SATILIK EMLAK - KAPSAMLI RAPOR OLUŞTURUCU         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()


def load_data():
    """CSV'yi yükle"""
    logger.info(f"📊 CSV okunuyor: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    
    # Sadece satılıkları filtrele (Sale veya Satılık)
    sale_df = df[df['listing_type'].isin(['Sale', 'Satılık'])].copy()
    
    logger.info(f"   Toplam kayıt: {len(df)}")
    logger.info(f"   Satılık kayıt: {len(sale_df)}")
    
    # Sütunları göster
    logger.info(f"\n📋 Sütunlar ({len(sale_df.columns)} adet):")
    for col in sale_df.columns:
        logger.info(f"   • {col}")
    
    return sale_df


def calculate_try_prices(df):
    """TRY fiyatlarını hesapla"""
    logger.info(f"\n💱 TRY fiyatları hesaplanıyor...")
    logger.info(f"   Varsayılan GBP kuru: {DEFAULT_GBP_RATE}")
    
    def convert_to_try(row):
        """Satır bazında TRY'ye çevir"""
        try:
            price = row['price']
            currency = row['currency']
            
            if pd.isna(price) or pd.isna(currency):
                return None
            
            price = float(price)
            
            if currency == 'TL':
                return price
            elif currency == 'GBP' or currency == '£':
                return price * DEFAULT_GBP_RATE
            elif currency == 'USD' or currency == '$':
                return price * 35.0  # Yaklaşık USD kuru
            elif currency == 'EUR' or currency == '€':
                return price * 38.0  # Yaklaşık EUR kuru
            else:
                return None
        except:
            return None
    
    df['price_try'] = df.apply(convert_to_try, axis=1)
    
    # İstatistik
    converted = df['price_try'].notna().sum()
    logger.info(f"   ✅ {converted} ilan için TRY fiyat hesaplandı")
    
    return df


def create_excel_report(df, timestamp):
    """Excel raporu oluştur"""
    logger.info(f"\n📊 Excel raporu oluşturuluyor...")
    
    filename = REPORTS_DIR / f"FULL_SALE_DATA_KKTC_{timestamp}.xlsx"
    
    # Sütun sırası
    column_order = [
        'property_id', 'title', 'city', 'district',
        'listing_type', 'property_type', 'property_subtype',
        'price', 'currency', 'price_try',
        'room_count', 'area_m2',
        'title_deed_type',
        'phone_numbers', 'whatsapp_numbers', 'agency_name',
        'listing_date', 'update_date',
        'url', 'description'
    ]
    
    # Mevcut sütunları al
    available_cols = [col for col in column_order if col in df.columns]
    other_cols = [col for col in df.columns if col not in available_cols]
    final_cols = available_cols + other_cols
    
    df_sorted = df[final_cols].copy()
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: TÜM SATILIKLAR
        df_sorted.to_excel(writer, sheet_name='TÜM SATILIKLAR', index=False)
        
        # Sheet 2-5: Kategorilere göre
        for category in df['property_type'].unique():
            if pd.notna(category):
                cat_df = df_sorted[df_sorted['property_type'] == category]
                sheet_name = str(category)[:31]  # Excel limit
                cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Sheet 6-11: Şehirlere göre
        for city in df['city'].unique():
            if pd.notna(city):
                city_df = df_sorted[df_sorted['city'] == city]
                sheet_name = f"🏙️ {city}"[:31]
                city_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Sheet 12-14: Fiyat aralıklarına göre (TRY)
        price_ranges = [
            (0, 3_000_000, "0-3M TRY"),
            (3_000_000, 10_000_000, "3M-10M TRY"),
            (10_000_000, float('inf'), "10M+ TRY")
        ]
        
        for min_price, max_price, range_name in price_ranges:
            range_df = df_sorted[
                (df_sorted['price_try'] >= min_price) & 
                (df_sorted['price_try'] < max_price)
            ]
            if len(range_df) > 0:
                range_df.to_excel(writer, sheet_name=range_name, index=False)
        
        # Sheet 15: İSTATİSTİKLER
        stats_data = {
            'Metrik': [
                'Toplam İlan',
                'Ortalama Fiyat (TRY)',
                'Medyan Fiyat (TRY)',
                'Min Fiyat (TRY)',
                'Max Fiyat (TRY)',
                'Ortalama m²',
                'Şehir Sayısı',
                'Kategori Sayısı'
            ],
            'Değer': [
                len(df),
                f"{df['price_try'].mean():,.0f}" if df['price_try'].notna().any() else 'N/A',
                f"{df['price_try'].median():,.0f}" if df['price_try'].notna().any() else 'N/A',
                f"{df['price_try'].min():,.0f}" if df['price_try'].notna().any() else 'N/A',
                f"{df['price_try'].max():,.0f}" if df['price_try'].notna().any() else 'N/A',
                f"{df['area_m2'].mean():.0f}" if 'area_m2' in df.columns and df['area_m2'].notna().any() else 'N/A',
                df['city'].nunique(),
                df['property_type'].nunique()
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='İSTATİSTİKLER', index=False)
    
    # Sheet sayısını hesapla
    sheet_count = (
        1 +  # Tüm satılıklar
        df['property_type'].nunique() +  # Kategoriler
        df['city'].nunique() +  # Şehirler
        3 +  # Fiyat aralıkları
        1  # İstatistikler
    )
    
    logger.info(f"✅ Excel raporu oluşturuldu: {filename}")
    logger.info(f"   Sheet sayısı: {sheet_count}")
    
    return filename


def create_markdown_summary(df, excel_file, timestamp):
    """Markdown özeti oluştur"""
    logger.info(f"\n📝 Markdown özeti oluşturuluyor...")
    
    filename = REPORTS_DIR / f"FULL_SALE_DATA_KKTC_{timestamp}_summary.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# KKTC SATILIK EMLAK - Kapsamlı Rapor\n\n")
        f.write(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Genel İstatistikler
        f.write("## 📊 Genel İstatistikler\n\n")
        f.write(f"- **Toplam İlan:** {len(df)}\n")
        if df['price_try'].notna().any():
            f.write(f"- **Ortalama Fiyat:** {df['price_try'].mean():,.0f} TRY\n")
            f.write(f"- **Medyan Fiyat:** {df['price_try'].median():,.0f} TRY\n")
            f.write(f"- **Min Fiyat:** {df['price_try'].min():,.0f} TRY\n")
            f.write(f"- **Max Fiyat:** {df['price_try'].max():,.0f} TRY\n")
        f.write(f"- **Şehir Sayısı:** {df['city'].nunique()}\n")
        f.write(f"- **Kategori Sayısı:** {df['property_type'].nunique()}\n")
        f.write("\n")
        
        # Kategori Dağılımı
        f.write("## 🏠 Kategori Dağılımı\n\n")
        f.write("| Kategori | İlan Sayısı | Oran |\n")
        f.write("|----------|-------------|------|\n")
        for cat, count in df['property_type'].value_counts().items():
            percent = (count / len(df)) * 100
            f.write(f"| {cat} | {count} | {percent:.1f}% |\n")
        f.write("\n")
        
        # Şehir Dağılımı
        f.write("## 🏙️ Şehir Dağılımı\n\n")
        f.write("| Şehir | İlan Sayısı | Oran |\n")
        f.write("|-------|-------------|------|\n")
        for city, count in df['city'].value_counts().items():
            percent = (count / len(df)) * 100
            f.write(f"| {city} | {count} | {percent:.1f}% |\n")
        f.write("\n")
        
        # Fiyat Dağılımı
        if df['price_try'].notna().any():
            f.write("## 💰 Fiyat Aralıkları (TRY)\n\n")
            f.write("| Aralık | İlan Sayısı | Oran |\n")
            f.write("|--------|-------------|------|\n")
            
            ranges = [
                (0, 3_000_000, "0 - 3M"),
                (3_000_000, 10_000_000, "3M - 10M"),
                (10_000_000, float('inf'), "10M+")
            ]
            
            for min_p, max_p, label in ranges:
                count = len(df[(df['price_try'] >= min_p) & (df['price_try'] < max_p)])
                if count > 0:
                    percent = (count / len(df)) * 100
                    f.write(f"| {label} | {count} | {percent:.1f}% |\n")
            f.write("\n")
        
        # Dosyalar
        f.write("## 📁 Dosyalar\n\n")
        f.write(f"- **Excel Raporu:** `{excel_file.name}`\n")
        f.write(f"- **CSV:** `property_details.csv`\n")
        f.write("\n---\n\n")
        f.write("*Bu rapor otomatik olarak oluşturulmuştur.*\n")
    
    logger.info(f"✅ Markdown özeti oluşturuldu: {filename}")
    
    return filename


def main():
    """Ana fonksiyon"""
    print_header()
    
    # Veriyi yükle
    df = load_data()
    
    if len(df) == 0:
        logger.error("\n❌ Satılık ilan bulunamadı!")
        return
    
    # TRY fiyatları hesapla
    df = calculate_try_prices(df)
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Excel raporu oluştur
    excel_file = create_excel_report(df, timestamp)
    
    # Markdown özeti oluştur
    md_file = create_markdown_summary(df, excel_file, timestamp)
    
    # Final
    print("\n" + "="*60)
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   RAPOR OLUŞTURMA TAMAMLANDI!                             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    logger.info("📊 ÇIKTILAR:")
    logger.info(f"   • Excel: {excel_file}")
    logger.info(f"   • Markdown: {md_file}")
    logger.info("")
    
    logger.info("📈 İSTATİSTİKLER:")
    logger.info(f"   • Toplam ilan: {len(df)}")
    logger.info(f"   • Şehir: {df['city'].nunique()}")
    logger.info(f"   • Kategori: {df['property_type'].nunique()}")
    logger.info("")
    
    logger.info("🎯 SONRAKİ ADIMLAR:")
    logger.info("   1. Excel dosyasını açın ve inceleyin")
    logger.info("   2. Filtreleme ve sıralama yapın")
    logger.info("   3. İhtiyacınıza göre pivot tablo oluşturun")
    logger.info("")
    
    print("✨ Raporunuz hazır!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

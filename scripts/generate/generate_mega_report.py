#!/usr/bin/env python3
"""
KKTC EMLAK - Birleşik Mega Rapor Oluşturucu

Hem kiralık hem satılık tüm verileri tek bir kapsamlı Excel'de toplar.
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
    print("\n" + "="*70)
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   KKTC EMLAK - BİRLEŞİK MEGA RAPOR OLUŞTURUCU                   ║")
    print("║   📊 Hem Kiralık + Hem Satılık = Tam Kapsamlı Analiz           ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("="*70 + "\n")


def load_data():
    """CSV'yi yükle"""
    logger.info(f"📊 CSV okunuyor: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    
    # İstatistikler
    rental_count = len(df[df['listing_type'] == 'Kiralık'])
    sale_count = len(df[df['listing_type'] == 'Satılık'])
    
    logger.info(f"   📈 Toplam kayıt: {len(df)}")
    logger.info(f"   🏠 Kiralık: {rental_count}")
    logger.info(f"   💰 Satılık: {sale_count}")
    logger.info(f"   🏙️  Şehir: {df['city'].nunique()}")
    logger.info(f"   🏗️  Kategori: {df['property_type'].nunique()}")
    
    return df


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
                return price * 35.0
            elif currency == 'EUR' or currency == '€':
                return price * 38.0
            else:
                return None
        except:
            return None
    
    df['price_try'] = df.apply(convert_to_try, axis=1)
    
    converted = df['price_try'].notna().sum()
    logger.info(f"   ✅ {converted} ilan için TRY fiyat hesaplandı")
    
    return df


def create_mega_excel_report(df, timestamp):
    """Mega Excel raporu oluştur"""
    logger.info(f"\n📊 MEGA Excel raporu oluşturuluyor...")
    logger.info(f"   Bu rapor TÜM verileri içerecek!")
    
    filename = REPORTS_DIR / f"KKTC_MEGA_EMLAK_RAPORU_{timestamp}.xlsx"
    
    # Sütun sırası
    column_order = [
        'listing_type', 'property_id', 'title', 'city', 'district',
        'property_type', 'property_subtype',
        'price', 'currency', 'price_try',
        'room_count', 'area_m2',
        'title_deed_type', 'min_rental_period', 'payment_interval',
        'phone_numbers', 'whatsapp_numbers', 'agency_name',
        'listing_date', 'update_date',
        'url', 'description'
    ]
    
    available_cols = [col for col in column_order if col in df.columns]
    other_cols = [col for col in df.columns if col not in available_cols]
    final_cols = available_cols + other_cols
    
    df_sorted = df[final_cols].copy()
    
    # Kiralık ve satılık ayır (Rent/Kiralık ve Sale/Satılık)
    rental_df = df_sorted[df_sorted['listing_type'].isin(['Rent', 'Kiralık'])].copy()
    sale_df = df_sorted[df_sorted['listing_type'].isin(['Sale', 'Satılık'])].copy()
    
    logger.info(f"   📝 Sheet'ler oluşturuluyor...")
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # ========================================
        # ANA SHEET'LER
        # ========================================
        
        # Sheet 1: GENEL BAKIŞ
        overview_data = {
            'Kategori': ['Toplam İlan', 'Kiralık İlan', 'Satılık İlan', '', 
                        'Şehir Sayısı', 'Emlak Türü Sayısı', 'Acente Sayısı'],
            'Değer': [
                len(df),
                len(rental_df),
                len(sale_df),
                '',
                df['city'].nunique(),
                df['property_type'].nunique(),
                df['agency_name'].nunique() if 'agency_name' in df.columns else 'N/A'
            ]
        }
        overview_df = pd.DataFrame(overview_data)
        overview_df.to_excel(writer, sheet_name='📊 GENEL BAKIŞ', index=False)
        
        # Sheet 2: TÜM İLANLAR
        df_sorted.to_excel(writer, sheet_name='🏘️ TÜM İLANLAR', index=False)
        
        # ========================================
        # KİRALIK SHEET'LER
        # ========================================
        
        if len(rental_df) > 0:
            # Sheet 3: Tüm kiralıklar
            rental_df.to_excel(writer, sheet_name='🏠 KİRALIKLAR', index=False)
            
            # Kiralık - Kategorilere göre
            for category in rental_df['property_type'].unique():
                if pd.notna(category):
                    cat_df = rental_df[rental_df['property_type'] == category]
                    sheet_name = f"K-{category}"[:31]
                    cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Kiralık - Şehirlere göre
            for city in rental_df['city'].unique():
                if pd.notna(city):
                    city_df = rental_df[rental_df['city'] == city]
                    sheet_name = f"K-{city}"[:31]
                    city_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Kiralık - Fiyat aralıkları
            rental_ranges = [
                (0, 30_000, "K-0-30K TRY"),
                (30_000, 50_000, "K-30-50K TRY"),
                (50_000, float('inf'), "K-50K+ TRY")
            ]
            
            for min_p, max_p, range_name in rental_ranges:
                range_df = rental_df[
                    (rental_df['price_try'] >= min_p) & 
                    (rental_df['price_try'] < max_p)
                ]
                if len(range_df) > 0:
                    range_df.to_excel(writer, sheet_name=range_name, index=False)
        
        # ========================================
        # SATILIK SHEET'LER
        # ========================================
        
        if len(sale_df) > 0:
            # Sheet N: Tüm satılıklar
            sale_df.to_excel(writer, sheet_name='💰 SATILIKLAR', index=False)
            
            # Satılık - Kategorilere göre
            for category in sale_df['property_type'].unique():
                if pd.notna(category):
                    cat_df = sale_df[sale_df['property_type'] == category]
                    sheet_name = f"S-{category}"[:31]
                    cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Satılık - Şehirlere göre
            for city in sale_df['city'].unique():
                if pd.notna(city):
                    city_df = sale_df[sale_df['city'] == city]
                    sheet_name = f"S-{city}"[:31]
                    city_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Satılık - Fiyat aralıkları
            sale_ranges = [
                (0, 3_000_000, "S-0-3M TRY"),
                (3_000_000, 10_000_000, "S-3M-10M TRY"),
                (10_000_000, float('inf'), "S-10M+ TRY")
            ]
            
            for min_p, max_p, range_name in sale_ranges:
                range_df = sale_df[
                    (sale_df['price_try'] >= min_p) & 
                    (sale_df['price_try'] < max_p)
                ]
                if len(range_df) > 0:
                    range_df.to_excel(writer, sheet_name=range_name, index=False)
        
        # ========================================
        # KARŞILAŞTIRMA VE İSTATİSTİK SHEET'LER
        # ========================================
        
        # Sheet: Şehir Karşılaştırması
        city_stats = df.groupby(['city', 'listing_type']).size().unstack(fill_value=0)
        city_stats.to_excel(writer, sheet_name='🏙️ ŞEHİR KARŞILAŞTIRMA')
        
        # Sheet: Kategori Karşılaştırması
        cat_stats = df.groupby(['property_type', 'listing_type']).size().unstack(fill_value=0)
        cat_stats.to_excel(writer, sheet_name='🏗️ KATEGORİ KARŞILAŞTIRMA')
        
        # Sheet: Fiyat İstatistikleri
        if df['price_try'].notna().any():
            price_stats_data = {
                'Metrik': ['Ortalama', 'Medyan', 'Min', 'Max', 'Standart Sapma'],
                'Kiralık (TRY)': [
                    f"{rental_df['price_try'].mean():,.0f}" if len(rental_df) > 0 else 'N/A',
                    f"{rental_df['price_try'].median():,.0f}" if len(rental_df) > 0 else 'N/A',
                    f"{rental_df['price_try'].min():,.0f}" if len(rental_df) > 0 else 'N/A',
                    f"{rental_df['price_try'].max():,.0f}" if len(rental_df) > 0 else 'N/A',
                    f"{rental_df['price_try'].std():,.0f}" if len(rental_df) > 0 else 'N/A'
                ],
                'Satılık (TRY)': [
                    f"{sale_df['price_try'].mean():,.0f}" if len(sale_df) > 0 else 'N/A',
                    f"{sale_df['price_try'].median():,.0f}" if len(sale_df) > 0 else 'N/A',
                    f"{sale_df['price_try'].min():,.0f}" if len(sale_df) > 0 else 'N/A',
                    f"{sale_df['price_try'].max():,.0f}" if len(sale_df) > 0 else 'N/A',
                    f"{sale_df['price_try'].std():,.0f}" if len(sale_df) > 0 else 'N/A'
                ]
            }
            price_stats_df = pd.DataFrame(price_stats_data)
            price_stats_df.to_excel(writer, sheet_name='💵 FİYAT İSTATİSTİKLERİ', index=False)
    
    # Sheet sayısını hesapla (yaklaşık)
    sheet_count = (
        3 +  # Genel bakış, tüm ilanlar, tüm kiralıklar/satılıklar
        (rental_df['property_type'].nunique() if len(rental_df) > 0 else 0) +
        (rental_df['city'].nunique() if len(rental_df) > 0 else 0) +
        3 +  # Kiralık fiyat aralıkları
        (sale_df['property_type'].nunique() if len(sale_df) > 0 else 0) +
        (sale_df['city'].nunique() if len(sale_df) > 0 else 0) +
        3 +  # Satılık fiyat aralıkları
        3  # Karşılaştırma sheet'leri
    )
    
    logger.info(f"✅ MEGA Excel raporu oluşturuldu!")
    logger.info(f"   📁 Dosya: {filename}")
    logger.info(f"   📊 Sheet sayısı: ~{sheet_count}")
    
    return filename, sheet_count


def create_summary_markdown(df, excel_file, timestamp):
    """Özet Markdown oluştur"""
    logger.info(f"\n📝 Markdown özeti oluşturuluyor...")
    
    filename = REPORTS_DIR / f"KKTC_MEGA_EMLAK_RAPORU_{timestamp}_summary.md"
    
    rental_df = df[df['listing_type'].isin(['Rent', 'Kiralık'])]
    sale_df = df[df['listing_type'].isin(['Sale', 'Satılık'])]
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# KKTC EMLAK - BİRLEŞİK MEGA RAPOR\n\n")
        f.write(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Genel İstatistikler
        f.write("## 📊 Genel İstatistikler\n\n")
        f.write(f"- **Toplam İlan:** {len(df):,}\n")
        f.write(f"- **Kiralık İlan:** {len(rental_df):,}\n")
        f.write(f"- **Satılık İlan:** {len(sale_df):,}\n")
        f.write(f"- **Şehir Sayısı:** {df['city'].nunique()}\n")
        f.write(f"- **Kategori Sayısı:** {df['property_type'].nunique()}\n\n")
        
        # Kiralık İstatistikler
        if len(rental_df) > 0:
            f.write("## 🏠 Kiralık İstatistikler\n\n")
            f.write(f"- **Toplam:** {len(rental_df):,}\n")
            if rental_df['price_try'].notna().any():
                f.write(f"- **Ortalama Fiyat:** {rental_df['price_try'].mean():,.0f} TRY\n")
                f.write(f"- **Medyan Fiyat:** {rental_df['price_try'].median():,.0f} TRY\n")
            
            f.write("\n### Kategori Dağılımı\n\n")
            f.write("| Kategori | İlan Sayısı |\n")
            f.write("|----------|-------------|\n")
            for cat, count in rental_df['property_type'].value_counts().head(10).items():
                f.write(f"| {cat} | {count} |\n")
            f.write("\n")
        
        # Satılık İstatistikler
        if len(sale_df) > 0:
            f.write("## 💰 Satılık İstatistikler\n\n")
            f.write(f"- **Toplam:** {len(sale_df):,}\n")
            if sale_df['price_try'].notna().any():
                f.write(f"- **Ortalama Fiyat:** {sale_df['price_try'].mean():,.0f} TRY\n")
                f.write(f"- **Medyan Fiyat:** {sale_df['price_try'].median():,.0f} TRY\n")
            
            f.write("\n### Kategori Dağılımı\n\n")
            f.write("| Kategori | İlan Sayısı |\n")
            f.write("|----------|-------------|\n")
            for cat, count in sale_df['property_type'].value_counts().head(10).items():
                f.write(f"| {cat} | {count} |\n")
            f.write("\n")
        
        # Şehir Karşılaştırması
        f.write("## 🏙️ Şehir Karşılaştırması\n\n")
        f.write("| Şehir | Kiralık | Satılık | Toplam |\n")
        f.write("|-------|---------|---------|--------|\n")
        for city in df['city'].unique():
            if pd.notna(city):
                city_rental = len(rental_df[rental_df['city'] == city])
                city_sale = len(sale_df[sale_df['city'] == city])
                city_total = city_rental + city_sale
                f.write(f"| {city} | {city_rental} | {city_sale} | {city_total} |\n")
        f.write("\n")
        
        f.write("---\n\n")
        f.write(f"📁 **Excel Raporu:** `{excel_file.name}`\n\n")
        f.write("*Bu rapor otomatik olarak oluşturulmuştur.*\n")
    
    logger.info(f"✅ Markdown özeti oluşturuldu: {filename}")
    
    return filename


def main():
    """Ana fonksiyon"""
    print_header()
    
    # Veriyi yükle
    df = load_data()
    
    if len(df) == 0:
        logger.error("\n❌ Hiç ilan bulunamadı!")
        return
    
    # TRY fiyatları hesapla
    df = calculate_try_prices(df)
    
    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Mega Excel raporu oluştur
    excel_file, sheet_count = create_mega_excel_report(df, timestamp)
    
    # Markdown özeti oluştur
    md_file = create_summary_markdown(df, excel_file, timestamp)
    
    # Final
    print("\n" + "="*70)
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   🎉 MEGA RAPOR BAŞARIYLA OLUŞTURULDU!                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    logger.info("📊 ÇIKTILAR:")
    logger.info(f"   • 📁 Excel: {excel_file}")
    logger.info(f"   • 📝 Markdown: {md_file}")
    logger.info("")
    
    logger.info("📈 İSTATİSTİKLER:")
    logger.info(f"   • Toplam ilan: {len(df):,}")
    logger.info(f"   • Kiralık: {len(df[df['listing_type'].isin(['Rent', 'Kiralık'])]):,}")
    logger.info(f"   • Satılık: {len(df[df['listing_type'].isin(['Sale', 'Satılık'])]):,}")
    logger.info(f"   • Sheet sayısı: ~{sheet_count}")
    logger.info("")
    
    logger.info("🎯 ÖNEMLİ:")
    logger.info("   Bu Excel dosyası TÜM verileri içerir:")
    logger.info("   ✅ Hem kiralık hem satılık ilanlar")
    logger.info("   ✅ Şehir ve kategori bazında ayrıntılı sheet'ler")
    logger.info("   ✅ Fiyat aralıklarına göre filtrelenmiş veriler")
    logger.info("   ✅ Karşılaştırmalı istatistikler")
    logger.info("")
    
    print("="*70)
    print("✨ Kapsamlı raporunuz kullanıma hazır!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

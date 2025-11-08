#!/usr/bin/env python3
"""
Otomatik Parse + Excel Generator
=================================
Her config tamamlandığında HTML'leri parse edip CSV ve Excel oluşturur.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import logging
import asyncio
from bs4 import BeautifulSoup

# Add project root to path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.emlak_scraper.core.parser import (
    extract_details,
    fetch_exchange_rates,
    calculate_tl_price
)

logger = logging.getLogger(__name__)

def parse_config_directory(city: str, category: str, exchange_rates: dict = None) -> pd.DataFrame:
    """
    Belirli bir config'in HTML dosyalarını parse eder
    
    Args:
        city: Şehir (girne, iskele, lefkosa...)
        category: Kategori (satilik-daire, kiralik-villa...)
        exchange_rates: Döviz kurları (None ise fetch edilir)
    
    Returns:
        Pandas DataFrame
    """
    if exchange_rates is None:
        exchange_rates = fetch_exchange_rates()
    
    # HTML directory
    html_dir = BASE_DIR / "data" / "raw" / "listings" / city / category
    if not html_dir.exists():
        logger.warning(f"Directory not found: {html_dir}")
        return pd.DataFrame()
    
    # Parse all HTML files
    data_list = []
    html_files = list(html_dir.glob("*.html"))
    
    logger.info(f"Parsing {len(html_files)} HTML files from {city}/{category}")
    
    # Create async event loop for parsing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for html_file in html_files:
        try:
            # Parse HTML using existing parser (async)
            property_data = loop.run_until_complete(
                extract_details(str(html_file))
            )
            
            if property_data:
                # Add metadata
                if 'city' not in property_data or not property_data['city']:
                    property_data['city'] = city.capitalize()
                property_data['category'] = category
                
                # Calculate TL price if needed
                if property_data.get('price') and property_data.get('currency'):
                    property_data['price_tl'] = calculate_tl_price(
                        property_data['price'],
                        property_data['currency'],
                        exchange_rates
                    )
                
                data_list.append(property_data)
        
        except Exception as e:
            logger.error(f"Error parsing {html_file.name}: {e}")
            continue
    
    loop.close()
    
    logger.info(f"Successfully parsed {len(data_list)}/{len(html_files)} files")
    
    return pd.DataFrame(data_list)


def append_to_csv(df: pd.DataFrame, csv_path: Path):
    """
    DataFrame'i mevcut CSV'ye ekler veya yeni oluşturur
    
    Args:
        df: Pandas DataFrame
        csv_path: CSV dosya yolu
    """
    if df.empty:
        logger.warning("Empty DataFrame, skipping CSV append")
        return
    
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    if csv_path.exists():
        # Mevcut CSV'ye append
        existing_df = pd.read_csv(csv_path)
        
        # Remove duplicates by property_id
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['property_id'], keep='last')
        
        combined_df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"Appended {len(df)} rows to {csv_path} (Total: {len(combined_df)})")
    else:
        # Yeni CSV oluştur
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"Created new CSV with {len(df)} rows: {csv_path}")


def generate_excel_report(csv_path: Path, excel_path: Path = None):
    """
    CSV'den Excel rapor oluşturur
    
    Args:
        csv_path: Kaynak CSV dosyası
        excel_path: Hedef Excel dosyası (None ise otomatik oluşturulur)
    """
    if not csv_path.exists():
        logger.warning(f"CSV not found: {csv_path}")
        return
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    if df.empty:
        logger.warning("Empty CSV, skipping Excel generation")
        return
    
    # Excel path
    if excel_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = BASE_DIR / "data" / "reports" / f"KKTC_Emlak_Raporu_{timestamp}.xlsx"
    
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Generating Excel report: {excel_path}")
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sheet 1: Tüm İlanlar
        df_sorted = df.sort_values(['city', 'listing_type', 'property_id'])
        df_sorted.to_excel(writer, sheet_name='Tüm İlanlar', index=False)
        
        # Sheet 2: Şehir bazlı sheets (sadece 1000+ ilan varsa)
        for city in df['city'].unique():
            city_df = df[df['city'] == city]
            if len(city_df) >= 100:  # En az 100 ilan varsa sheet oluştur
                city_df_sorted = city_df.sort_values(['listing_type', 'district', 'property_id'])
                sheet_name = city[:30]  # Excel sheet name limit: 31 chars
                city_df_sorted.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Sheet 3: Özet
        summary_data = {
            'Şehir': [],
            'Kiralık': [],
            'Satılık': [],
            'Toplam': []
        }
        
        for city in sorted(df['city'].unique()):
            city_data = df[df['city'] == city]
            kiralik = len(city_data[city_data['listing_type'] == 'Kiralık'])
            satilik = len(city_data[city_data['listing_type'] == 'Satılık'])
            
            summary_data['Şehir'].append(city)
            summary_data['Kiralık'].append(kiralik)
            summary_data['Satılık'].append(satilik)
            summary_data['Toplam'].append(kiralik + satilik)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Özet', index=False)
    
    # File size
    file_size_mb = excel_path.stat().st_size / (1024 * 1024)
    logger.info(f"✅ Excel report created: {excel_path.name} ({file_size_mb:.2f} MB, {len(df)} ilanlar)")
    
    return excel_path


def parse_and_update(city: str, category: str, auto_excel: bool = True):
    """
    Config tamamlandığında otomatik çalışır:
    1. HTML'leri parse et
    2. CSV'ye ekle
    3. Excel güncelle (opsiyonel)
    
    Args:
        city: Şehir
        category: Kategori
        auto_excel: Excel otomatik güncellensin mi? (Her 1000 ilan'da)
    """
    logger.info(f"🔄 Auto-parse başladı: {city}/{category}")
    
    # Paths
    csv_path = BASE_DIR / "data" / "processed" / "property_details.csv"
    
    # 1. Parse HTML files
    df = parse_config_directory(city, category)
    
    if df.empty:
        logger.warning(f"No data parsed from {city}/{category}")
        return
    
    # 2. Append to CSV
    append_to_csv(df, csv_path)
    
    # 3. Update Excel (her 1000 ilan'da bir)
    if auto_excel and csv_path.exists():
        existing_df = pd.read_csv(csv_path)
        total_count = len(existing_df)
        
        # Her 1000'de bir VEYA ilk config'te Excel oluştur
        if total_count % 1000 < len(df) or total_count < 1000:
            logger.info(f"📊 Toplam {total_count} ilan - Excel güncellemesi başladı")
            generate_excel_report(csv_path)
    
    logger.info(f"✅ Auto-parse tamamlandı: {len(df)} ilan eklendi")


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    # Example: Parse Girne/satilik-daire
    parse_and_update('girne', 'satilik-daire', auto_excel=True)

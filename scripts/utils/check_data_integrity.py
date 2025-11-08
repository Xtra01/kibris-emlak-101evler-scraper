#!/usr/bin/env python3
"""
Veri Bütünlüğü ve Eksiklik Kontrol Sistemi v2.0.0
Yeni yapıya uygun: emlak_scraper paketi kullanır
"""

import os
import pandas as pd
from pathlib import Path
from collections import Counter

# Yeni yapıya göre path'ler
HTML_DIR = Path("data/raw/listings")
CSV_FILE = Path("data/processed/property_details.csv")

def check_data_integrity():
    """Veri bütünlüğünü kontrol et"""
    
    print("\n" + "="*70)
    print("🔍 VERİ BÜTÜNLÜĞÜ VE EKSİKLİK KONTROL SİSTEMİ v2.0.0")
    print("="*70)
    print()
    
    # 1. HTML Dosyaları Kontrolü
    print("📊 1. MEVCUT VERİ DURUMU")
    print("="*70)
    
    html_files = list(HTML_DIR.glob("*.html"))
    html_count = len(html_files)
    print(f"   📁 HTML İlanlar       : {html_count:,} dosya")
    
    # HTML ID'leri çıkar
    html_ids = set()
    for html_file in html_files:
        # Dosya adından ID çıkar (örn: 123456.html -> 123456)
        try:
            file_id = html_file.stem
            if file_id.isdigit():
                html_ids.add(file_id)
        except:
            pass
    
    print(f"   🔢 Benzersiz ID       : {len(html_ids):,} ilan")
    
    # 2. CSV Kontrolü
    csv_exists = CSV_FILE.exists()
    
    if csv_exists:
        try:
            df = pd.read_csv(CSV_FILE)
            csv_count = len(df)
            csv_size = CSV_FILE.stat().st_size / (1024 * 1024)  # MB
            
            print(f"   📄 CSV Kayıtları      : {csv_count:,} kayıt ({csv_size:.2f} MB)")
            
            # CSV'deki ID'ler
            csv_ids = set(df['ID'].astype(str)) if 'ID' in df.columns else set()
            
            # Fark analizi
            difference = html_count - csv_count
            if difference == 0:
                print(f"   ✅ Eşleşme            : Tüm HTML'ler CSV'de")
            elif difference > 0:
                print(f"   ⚠️  Eksik Parse        : {difference:,} HTML parse edilmemiş")
            else:
                print(f"   ⚠️  Fazla Kayıt        : CSV'de {abs(difference):,} fazla kayıt")
            
            # Eksik ID'leri bul
            missing_in_csv = html_ids - csv_ids
            if missing_in_csv:
                print(f"   ⚠️  CSV'de Eksik       : {len(missing_in_csv):,} ID")
                if len(missing_in_csv) <= 10:
                    print(f"      Eksik ID'ler: {', '.join(sorted(missing_in_csv))}")
            
            missing_in_html = csv_ids - html_ids
            if missing_in_html:
                print(f"   ⚠️  HTML'de Eksik      : {len(missing_in_html):,} ID")
                if len(missing_in_html) <= 10:
                    print(f"      Eksik ID'ler: {', '.join(sorted(missing_in_html))}")
            
        except Exception as e:
            print(f"   ❌ CSV Okuma Hatası   : {e}")
            df = None
            csv_count = 0
    else:
        print(f"   ❌ CSV Yok            : property_details.csv bulunamadı")
        df = None
        csv_count = 0
    
    # 3. CSV İçerik Analizi
    if df is not None and len(df) > 0:
        print()
        print("📊 2. CSV İÇERİK ANALİZİ")
        print("="*70)
        
        # Şehir dağılımı
        if 'Sehir' in df.columns:
            print("   🏙️  Şehir Dağılımı:")
            city_counts = df['Sehir'].value_counts().head(10)
            for city, count in city_counts.items():
                percent = (count / csv_count) * 100
                city_display = str(city)[:15].ljust(15)
                print(f"      {city_display} : {count:>4,} ilan (%{percent:.1f})")
        
        print()
        
        # Tip dağılımı
        if 'Tip' in df.columns:
            print("   🏠 Emlak Tipi:")
            type_counts = df['Tip'].value_counts()
            for prop_type, count in type_counts.items():
                percent = (count / csv_count) * 100
                type_display = str(prop_type)[:15].ljust(15)
                print(f"      {type_display} : {count:>4,} ilan (%{percent:.1f})")
        
        print()
        
        # Satılık/Kiralık
        if 'Durum' in df.columns:
            print("   💰 Satılık/Kiralık:")
            status_counts = df['Durum'].value_counts()
            for status, count in status_counts.items():
                percent = (count / csv_count) * 100
                status_display = str(status)[:15].ljust(15)
                print(f"      {status_display} : {count:>4,} ilan (%{percent:.1f})")
        
        print()
        
        # Fiyat istatistikleri
        if 'Fiyat_TRY' in df.columns:
            prices = pd.to_numeric(df['Fiyat_TRY'], errors='coerce').dropna()
            if len(prices) > 0:
                print("   💵 Fiyat İstatistikleri (TRY):")
                print(f"      Ortalama         : ₺{prices.mean():>,.0f}")
                print(f"      Medyan           : ₺{prices.median():>,.0f}")
                print(f"      Minimum          : ₺{prices.min():>,.0f}")
                print(f"      Maksimum         : ₺{prices.max():>,.0f}")
    
    # 4. Sonuç ve Öneriler
    print()
    print("="*70)
    print("🎯 SONUÇ VE ÖNERİLER")
    print("="*70)
    
    if csv_exists and df is not None and html_count == csv_count:
        print("   ✅ Veri bütünlüğü TAMAM - Tüm ilanlar raporlanmış")
        print("   ✅ Excel raporu oluşturulabilir")
        return True, "OK"
    elif not csv_exists:
        print("   ❌ CSV dosyası YOK - Parser çalıştırılmalı")
        print("   📝 Komut: python -m emlak_scraper.core.parser")
        return False, "NO_CSV"
    elif html_count > csv_count:
        diff = html_count - csv_count
        print(f"   ⚠️  {diff:,} ilan parse edilmemiş")
        print("   📝 Komut: python -m emlak_scraper.core.parser")
        return False, "INCOMPLETE"
    else:
        print("   ⚠️  Veri tutarsızlığı var - İncelenmeli")
        return False, "INCONSISTENT"

if __name__ == "__main__":
    success, status = check_data_integrity()
    print()
    exit(0 if success else 1)

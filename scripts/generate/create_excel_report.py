#!/usr/bin/env python3
"""
Excel Raporu Oluşturma - Standalone Script
Yeni yapıya uygun: data/processed/ → data/reports/
"""

import os
import pandas as pd
from datetime import datetime

# Yeni yapıya göre path'ler
CSV_FILE = 'data/processed/property_details.csv'
REPORTS_DIR = 'data/reports'
OUTPUT_XLSX = os.path.join(REPORTS_DIR, f'market_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')

def create_excel_report():
    """Excel raporu oluştur"""
    
    print("\n" + "="*70)
    print("📊 EXCEL RAPORU OLUŞTURMA SİSTEMİ v2.0.0")
    print("="*70)
    print()
    
    # CSV'yi yükle
    print(f"📁 CSV Yükleniyor: {CSV_FILE}")
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"✅ {len(df):,} kayıt yüklendi")
    except Exception as e:
        print(f"❌ CSV yükleme hatası: {e}")
        return False
    
    # Reports dizinini oluştur
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Excel writer oluştur
    print(f"\n📝 Excel dosyası oluşturuluyor: {OUTPUT_XLSX}")
    
    try:
        with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
            # 1. Tüm Veriler (Ana Sayfa)
            df.to_excel(writer, sheet_name='Tüm İlanlar', index=False)
            print("   ✅ Sayfa 1: Tüm İlanlar")
            
            # 2. Şehir Özeti
            if 'city' in df.columns:
                city_summary = df.groupby('city').agg({
                    'property_id': 'count',
                    'price': ['mean', 'median', 'min', 'max']
                }).round(0)
                city_summary.columns = ['İlan Sayısı', 'Ort. Fiyat', 'Medyan Fiyat', 'Min Fiyat', 'Maks Fiyat']
                city_summary = city_summary.sort_values('İlan Sayısı', ascending=False)
                city_summary.to_excel(writer, sheet_name='Şehir Özeti')
                print("   ✅ Sayfa 2: Şehir Özeti")
            
            # 3. Emlak Tipi Özeti
            if 'property_type' in df.columns:
                type_summary = df.groupby('property_type').agg({
                    'property_id': 'count',
                    'price': ['mean', 'median']
                }).round(0)
                type_summary.columns = ['İlan Sayısı', 'Ort. Fiyat', 'Medyan Fiyat']
                type_summary = type_summary.sort_values('İlan Sayısı', ascending=False)
                type_summary.to_excel(writer, sheet_name='Emlak Tipi Özeti')
                print("   ✅ Sayfa 3: Emlak Tipi Özeti")
            
            # 4. Satılık/Kiralık Özeti
            if 'listing_type' in df.columns:
                listing_summary = df.groupby('listing_type').agg({
                    'property_id': 'count',
                    'price': ['mean', 'median', 'min', 'max']
                }).round(0)
                listing_summary.columns = ['İlan Sayısı', 'Ort. Fiyat', 'Medyan Fiyat', 'Min Fiyat', 'Maks Fiyat']
                listing_summary.to_excel(writer, sheet_name='Satılık-Kiralık Özeti')
                print("   ✅ Sayfa 4: Satılık-Kiralık Özeti")
            
            # 5. Girne Detay (En çok ilan olan şehir)
            if 'city' in df.columns:
                girne_df = df[df['city'].str.contains('Girne', case=False, na=False)]
                if len(girne_df) > 0:
                    girne_df.to_excel(writer, sheet_name='Girne İlanları', index=False)
                    print(f"   ✅ Sayfa 5: Girne İlanları ({len(girne_df):,} ilan)")
            
            # 6. Lefkoşa Detay
            if 'city' in df.columns:
                lefkosa_df = df[df['city'].str.contains('Lefkoşa|Lefkosa', case=False, na=False)]
                if len(lefkosa_df) > 0:
                    lefkosa_df.to_excel(writer, sheet_name='Lefkoşa İlanları', index=False)
                    print(f"   ✅ Sayfa 6: Lefkoşa İlanları ({len(lefkosa_df):,} ilan)")
            
            # 7. İstatistikler Sayfası
            stats_data = {
                'Metrik': [
                    'Toplam İlan Sayısı',
                    'Benzersiz Şehir',
                    'Benzersiz Emlak Tipi',
                    'Satılık İlan',
                    'Kiralık İlan',
                    'Ortalama Fiyat',
                    'Medyan Fiyat',
                    'En Düşük Fiyat',
                    'En Yüksek Fiyat',
                ],
                'Değer': [
                    len(df),
                    df['city'].nunique() if 'city' in df.columns else 'N/A',
                    df['property_type'].nunique() if 'property_type' in df.columns else 'N/A',
                    len(df[df['listing_type'] == 'Sale']) if 'listing_type' in df.columns else 'N/A',
                    len(df[df['listing_type'] == 'Rent']) if 'listing_type' in df.columns else 'N/A',
                    f"{df['price'].mean():.0f}" if 'price' in df.columns else 'N/A',
                    f"{df['price'].median():.0f}" if 'price' in df.columns else 'N/A',
                    f"{df['price'].min():.0f}" if 'price' in df.columns else 'N/A',
                    f"{df['price'].max():.0f}" if 'price' in df.columns else 'N/A',
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Genel İstatistikler', index=False)
            print("   ✅ Sayfa 7: Genel İstatistikler")
        
        # Başarı mesajı
        file_size = os.path.getsize(OUTPUT_XLSX) / (1024 * 1024)
        print()
        print("="*70)
        print(f"✅ EXCEL RAPORU OLUŞTURULDU!")
        print("="*70)
        print(f"   📁 Dosya: {OUTPUT_XLSX}")
        print(f"   📊 Boyut: {file_size:.2f} MB")
        print(f"   📄 Sayfa: 7 adet")
        print(f"   📈 Kayıt: {len(df):,} ilan")
        print("="*70)
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Excel oluşturma hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_excel_report()
    exit(0 if success else 1)

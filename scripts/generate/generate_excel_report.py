#!/usr/bin/env python3
"""
Excel Rapor Oluşturucu - KKTC 101evler.com Tam Veritabanı
"""

import pandas as pd
from datetime import datetime
import os

def create_excel_report():
    """property_details.csv'den Excel rapor oluştur"""
    
    print("="*70)
    print("📊 EXCEL RAPOR OLUŞTURULUYOR")
    print("="*70)
    print()
    
    # CSV oku
    print("📂 property_details.csv okunuyor...")
    df = pd.read_csv('property_details.csv')
    
    # Temel istatistikler
    print(f"✅ {len(df)} ilan yüklendi\n")
    
    # Şehir bazlı özet
    print("📍 Şehir Bazlı Dağılım:")
    print("-" * 40)
    city_summary = df.groupby(['city', 'listing_type']).size().unstack(fill_value=0)
    print(city_summary)
    print()
    
    # Girne detayları
    girne = df[df['city'] == 'Girne']
    if len(girne) > 0:
        print("🏖️  GİRNE DETAYLARI:")
        print("-" * 40)
        print(f"Toplam: {len(girne)}")
        girne_summary = girne.groupby('listing_type').size()
        for listing_type, count in girne_summary.items():
            print(f"  {listing_type}: {count}")
        
        girne_kiralik = girne[girne['listing_type'] == 'Kiralık']
        if len(girne_kiralik) > 0:
            print(f"\n  Kiralık Mahalleler:")
            districts = girne_kiralik['district'].value_counts().head(10)
            for district, count in districts.items():
                print(f"    {district}: {count}")
        print()
    
    # Excel dosyası oluştur
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"KKTC_Emlak_Raporu_{timestamp}.xlsx"
    
    print(f"💾 Excel dosyası oluşturuluyor: {excel_file}")
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Ana sayfa - Tüm ilanlar
        df_sorted = df.sort_values(['city', 'listing_type', 'property_id'])
        df_sorted.to_excel(writer, sheet_name='Tüm İlanlar', index=False)
        
        # Girne sayfası
        if len(girne) > 0:
            girne_sorted = girne.sort_values(['listing_type', 'district', 'property_id'])
            girne_sorted.to_excel(writer, sheet_name='Girne', index=False)
        
        # Özet sayfası
        summary_data = {
            'Şehir': [],
            'Kiralık': [],
            'Satılık': [],
            'Toplam': []
        }
        
        for city in df['city'].unique():
            city_data = df[df['city'] == city]
            kiralik = len(city_data[city_data['listing_type'] == 'Kiralık'])
            satilik = len(city_data[city_data['listing_type'] == 'Satılık'])
            
            summary_data['Şehir'].append(city)
            summary_data['Kiralık'].append(kiralik)
            summary_data['Satılık'].append(satilik)
            summary_data['Toplam'].append(kiralik + satilik)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Özet', index=False)
    
    print(f"✅ Excel rapor oluşturuldu: {excel_file}")
    print()
    print("="*70)
    print("🎉 RAPOR HAZIR!")
    print("="*70)
    
    # Dosya boyutu
    file_size = os.path.getsize(excel_file) / (1024 * 1024)
    print(f"📁 Dosya boyutu: {file_size:.2f} MB")
    print(f"📊 Toplam ilan: {len(df)}")
    print(f"📋 Sayfa sayısı: {len(df['city'].unique()) + 2}")  # Şehirler + Tüm İlanlar + Özet
    print()
    
    return excel_file


if __name__ == "__main__":
    try:
        excel_file = create_excel_report()
        print(f"\n✅ Başarılı! Dosya: {excel_file}")
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
KKTC Tam Kapsamlı SATILIK Emlak Tarama Aracı

Tüm satılık kategorileri ve şehirleri kapsar:
- 4 Kategori: daire, villa, ev, arsa
- 6 Şehir: Lefkosa, Girne, Magusa, Gazimagusa, Iskele, Guzelyurt
- Toplam: 24 konfigürasyon
"""

import subprocess
import time
import shutil
from pathlib import Path
import json
from datetime import datetime
import logging
import sys

# Şehirler
CITIES = [
    'lefkosa',
    'girne', 
    'magusa',
    'gazimagusa',
    'iskele',
    'guzelyurt'
]

# Satılık emlak türleri
SALE_TYPES = [
    'satilik-daire',
    'satilik-villa',
    'satilik-ev',
    'satilik-arsa'
]

# Türkçe isimler
CITY_NAMES = {
    'lefkosa': 'Lefkosa',
    'girne': 'Girne',
    'magusa': 'Magusa',
    'gazimagusa': 'Gazimagusa',
    'iskele': 'Iskele',
    'guzelyurt': 'Guzelyurt'
}

SALE_TYPE_NAMES = {
    'satilik-daire': 'Daire',
    'satilik-villa': 'Villa',
    'satilik-ev': 'Ev',
    'satilik-arsa': 'Arsa'
}

# Toplam konfigürasyon sayısı
TOTAL_CONFIGS = len(CITIES) * len(SALE_TYPES)

# Log dosyası
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"full_sale_scan_{timestamp}.log"
JSON_FILE = LOG_DIR / f"full_sale_scan_{timestamp}.json"

# Logger ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def backup_config():
    """Config dosyasını yedekle"""
    config_path = Path("src/scraper/config.py")
    backup_path = Path("src/scraper/config.py.backup_sale")
    
    if config_path.exists():
        shutil.copy2(config_path, backup_path)
        logger.info(f"✅ Config yedeklendi: {backup_path}")
        return True
    else:
        logger.error(f"❌ Config dosyası bulunamadı: {config_path}")
        return False


def restore_config():
    """Config dosyasını geri yükle"""
    config_path = Path("src/scraper/config.py")
    backup_path = Path("src/scraper/config.py.backup_sale")
    
    if backup_path.exists():
        shutil.copy2(backup_path, config_path)
        backup_path.unlink()
        logger.info("✅ Config restore edildi")
        return True
    else:
        logger.warning("⚠️  Backup dosyası bulunamadı")
        return False


def update_config(city, property_type):
    """Config dosyasını güncelle"""
    config_path = Path("src/scraper/config.py")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # CITY güncelle
        import re
        content = re.sub(
            r'CITY = "[^"]*"(\s+# Auto-updated.*)?',
            f'CITY = "{city}"  # Auto-updated by full_sale_scan.py',
            content
        )
        
        # PROPERTY_TYPE güncelle
        content = re.sub(
            r'PROPERTY_TYPE = "[^"]*"(\s+# Auto-updated.*)?',
            f'PROPERTY_TYPE = "{property_type}"  # Auto-updated by full_sale_scan.py',
            content
        )
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Config güncellenemedi: {e}")
        return False


def run_scraper():
    """Scraper'ı çalıştır"""
    try:
        result = subprocess.run(
            ['python', '-m', 'scraper.main'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300  # 5 dakika timeout
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    except subprocess.TimeoutExpired:
        logger.error("❌ Scraper timeout (5 dakika)")
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Timeout'
        }
    
    except Exception as e:
        logger.error(f"❌ Scraper çalıştırılamadı: {e}")
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def run_extraction():
    """Extraction işlemini çalıştır"""
    try:
        result = subprocess.run(
            ['python', 'extract_listing_details.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120  # 2 dakika timeout
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    except Exception as e:
        logger.error(f"❌ Extraction hatası: {e}")
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e)
        }


def main():
    """Ana fonksiyon"""
    
    print("\n" + "="*60)
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   KKTC TAM KAPSAMLI SATILIK EMLAK TARAMASI                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\n📊 KAPSAM:")
    print(f"   • 4 Kategori: daire, villa, ev, arsa")
    print(f"   • 6 Şehir: Lefkosa, Girne, Magusa, Gazimagusa, Iskele, Guzelyurt")
    print(f"   • Toplam: {TOTAL_CONFIGS} konfigürasyon")
    print("\n⏱️  TAHMİNİ SÜRE: ~12-24 dakika")
    print("\n🎯 HEDEF: KKTC'deki TÜM satılık emlak verilerini toplamak")
    print("\n⚠️  Bu işlem yaklaşık 15-20 dakika sürecek.")
    
    # Kullanıcı onayı
    response = input("   Devam etmek istiyor musunuz? (E/H): ")
    if response.upper() not in ['E', 'Y', 'EVET', 'YES']:
        print("\n❌ İşlem iptal edildi.")
        return
    
    print("\n✅ Tarama başlatılıyor...\n")
    
    # Başlangıç bilgileri
    start_time = time.time()
    logger.info(f"📅 Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📝 Log: {LOG_FILE}")
    logger.info(f"📊 JSON: {JSON_FILE}")
    logger.info("")
    
    # Config'i yedekle
    if not backup_config():
        print("\n❌ Config yedeklenemedi. İşlem iptal edildi.")
        return
    
    # İstatistikler
    results = []
    success_count = 0
    failed_count = 0
    
    # Her şehir ve emlak türü için
    current = 0
    for sale_type in SALE_TYPES:
        for city in CITIES:
            current += 1
            
            city_name = CITY_NAMES[city]
            type_name = SALE_TYPE_NAMES[sale_type]
            
            logger.info("\n" + "="*60)
            logger.info(f"[{current}/{TOTAL_CONFIGS}] 🏃 {city_name} - {type_name}")
            logger.info(f"📍 {city_name} | 🏠 {sale_type}")
            logger.info("="*60 + "\n")
            
            # Config güncelle
            if not update_config(city, sale_type):
                logger.error(f"❌ Config güncellenemedi: {city} - {sale_type}")
                failed_count += 1
                results.append({
                    'city': city,
                    'sale_type': sale_type,
                    'success': False,
                    'error': 'Config update failed',
                    'duration': 0
                })
                continue
            
            # Scraper'ı çalıştır
            iter_start = time.time()
            result = run_scraper()
            duration = time.time() - iter_start
            
            if result['success']:
                logger.info(f"✅ BAŞARILI: {city_name} - {type_name} ({duration:.1f}s)")
                success_count += 1
                results.append({
                    'city': city,
                    'city_name': city_name,
                    'sale_type': sale_type,
                    'type_name': type_name,
                    'success': True,
                    'duration': duration,
                    'returncode': result['returncode']
                })
            else:
                logger.error(f"❌ HATA: {city_name} - {type_name} (code: {result['returncode']})")
                if result['stderr']:
                    logger.error(f"Stderr: {result['stderr'][:500]}")
                failed_count += 1
                results.append({
                    'city': city,
                    'city_name': city_name,
                    'sale_type': sale_type,
                    'type_name': type_name,
                    'success': False,
                    'duration': duration,
                    'returncode': result['returncode'],
                    'error': result['stderr'][:500]
                })
            
            # İlerleme raporu
            elapsed = time.time() - start_time
            avg_time = elapsed / current
            remaining = avg_time * (TOTAL_CONFIGS - current)
            
            logger.info(f"\n📊 İlerleme: {current}/{TOTAL_CONFIGS}")
            logger.info(f"✅ Başarılı: {success_count} | ❌ Hatalı: {failed_count}")
            logger.info(f"⏱️  Geçen: {elapsed/60:.1f}m | Kalan: ~{remaining/60:.1f}m")
            
            # Son config değilse bekle
            if current < TOTAL_CONFIGS:
                logger.info(f"⏸️  3 saniye bekleniyor...")
                time.sleep(3)
    
    # Config'i geri yükle
    restore_config()
    
    # Özet
    total_time = time.time() - start_time
    logger.info("\n" + "="*60)
    logger.info("📊 GENEL ÖZET")
    logger.info("="*60)
    logger.info(f"✅ Başarılı: {success_count}/{TOTAL_CONFIGS}")
    logger.info(f"❌ Hatalı: {failed_count}/{TOTAL_CONFIGS}")
    logger.info(f"⏱️  Toplam süre: {total_time/60:.1f} dakika")
    logger.info(f"⚡ Ortalama: {total_time/TOTAL_CONFIGS:.1f} saniye/config")
    logger.info("")
    
    # Hatalı olanları listele
    if failed_count > 0:
        logger.warning("⚠️  HATALI KONFIGÜRASYONLAR:")
        for r in results:
            if not r['success']:
                logger.warning(f"  - {r['city_name']} - {r['type_name']}: {r.get('error', 'Unknown error')[:100]}")
    
    # JSON'a kaydet
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_configs': TOTAL_CONFIGS,
        'success_count': success_count,
        'failed_count': failed_count,
        'duration_seconds': total_time,
        'duration_minutes': total_time / 60,
        'results': results
    }
    
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 JSON kaydedildi: {JSON_FILE}")
    
    # Extraction çalıştır
    logger.info("\n" + "="*60)
    logger.info("🔄 EXTRACTION BAŞLATILIYOR")
    logger.info("="*60)
    
    extraction_result = run_extraction()
    if extraction_result['success']:
        logger.info("✅ Extraction başarılı!")
        logger.info(f"📊 {extraction_result['stdout'][-500:]}")
    else:
        logger.error("❌ Extraction başarısız!")
        logger.error(f"Stderr: {extraction_result['stderr'][:500]}")
    
    # Final
    logger.info("\n" + "="*60)
    logger.info("🎉 İŞLEM TAMAMLANDI!")
    logger.info("="*60)
    logger.info(f"📁 HTML: listings/")
    logger.info(f"📄 CSV: property_details.csv")
    logger.info(f"📝 Log: {LOG_FILE}")
    logger.info(f"📊 JSON: {JSON_FILE}")
    logger.info("")
    
    # CSV özeti
    try:
        import pandas as pd
        df = pd.read_csv('property_details.csv')
        sale_df = df[df['listing_type'] == 'Satılık']
        
        logger.info("📊 CSV ÖZET:")
        logger.info(f"  Toplam kayıt: {len(df)}")
        logger.info(f"  Satılık kayıt: {len(sale_df)}")
        logger.info("")
        
        if len(sale_df) > 0:
            logger.info("  Kategori dağılımı (satılıklar):")
            for cat, count in sale_df['property_type'].value_counts().items():
                logger.info(f"    {cat}: {count}")
            logger.info("")
            
            logger.info("  Şehir dağılımı (satılıklar):")
            for city, count in sale_df['city'].value_counts().items():
                logger.info(f"    {city}: {count}")
    
    except Exception as e:
        logger.warning(f"⚠️  CSV özeti oluşturulamadı: {e}")
    
    print("\n" + "="*60)
    print("✅ SATILIK EMLAK TARAMASI TAMAMLANDI!")
    print("="*60)


if __name__ == "__main__":
    main()

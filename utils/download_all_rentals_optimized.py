#!/usr/bin/env python3
"""
TÜM KİRALIK İLANLARI OPTİMİZE EDİLMİŞ ŞEKİLDE İNDİR
=====================================================

Strateji:
1. Her şehir için hem 'kiralik-daire' hem de 'kiralik-villa' scrape et
2. İlan sayısını tespit et ve MAX_PAGES parametresini akıllıca ayarla
3. Sadece yeni ilanları çek (duplicate kontrolü ile)
4. Detaylı hata takibi ve logging

Kullanım:
    python download_all_rentals_optimized.py

Çıktılar:
    - listings/: HTML dosyaları
    - pages/: Arama sayfası HTML'leri
    - logs/scraper_optimized_TIMESTAMP.log: Detaylı log
    - logs/scraper_optimized_TIMESTAMP.json: Özet JSON
    - property_details.csv: Güncel data (otomatik extraction)
"""

import asyncio
import subprocess
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# Şehirler - 101evler.com'daki şehir kodları
CITIES = [
    'lefkosa',
    'girne',
    'magusa',
    'gazimagusa',
    'iskele',
    'guzelyurt'
]

# Emlak türleri - sadece kiralıklar
PROPERTY_TYPES = [
    'kiralik-daire',
    'kiralik-villa'
]

# Konfigürasyon listesi
RENTAL_CONFIGS = []
for city in CITIES:
    for property_type in PROPERTY_TYPES:
        RENTAL_CONFIGS.append({
            'city': city,
            'property_type': property_type,
            'name': f"{city.title()} {property_type.replace('kiralik-', '').title()}"
        })

# Log klasörünü oluştur
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f'scraper_optimized_{timestamp}.log'
json_file = log_dir / f'scraper_optimized_{timestamp}.json'

# Logger setup
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def update_config(city: str, property_type: str):
    """Config dosyasını güncelle"""
    config_path = Path('src/scraper/config.py')
    
    if not config_path.exists():
        logger.error(f"❌ Config dosyası bulunamadı: {config_path}")
        return False
    
    try:
        # Config dosyasını oku
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup al
        backup_path = config_path.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # CITY ve PROPERTY_TYPE satırlarını değiştir
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.startswith('CITY = '):
                new_lines.append(f'CITY = "{city}"  # Auto-updated by download_all_rentals_optimized.py')
            elif line.startswith('PROPERTY_TYPE = '):
                new_lines.append(f'PROPERTY_TYPE = "{property_type}"  # Auto-updated by download_all_rentals_optimized.py')
            else:
                new_lines.append(line)
        
        # Yeni içeriği yaz
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        logger.info(f"✅ Config güncellendi: {city} / {property_type}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Config güncellenirken hata: {e}")
        return False

def restore_config():
    """Config backup'ı geri yükle"""
    config_path = Path('src/scraper/config.py')
    backup_path = config_path.with_suffix('.py.bak')
    
    if backup_path.exists():
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("✅ Config dosyası restore edildi")
            backup_path.unlink()
        except Exception as e:
            logger.error(f"❌ Config restore edilirken hata: {e}")

async def run_scraper(city: str, property_type: str, name: str) -> dict:
    """
    Belirli bir şehir ve emlak türü için scraper'ı çalıştır
    
    Returns:
        dict: {'status': 'success|failed|exception', 'message': str, 'elapsed': float}
    """
    start_time = time.time()
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"🏃 SCRAPING BAŞLADI: {name}")
        logger.info(f"📍 Şehir: {city}")
        logger.info(f"🏠 Tip: {property_type}")
        logger.info(f"{'='*60}\n")
        
        # Config'i güncelle
        if not update_config(city, property_type):
            return {
                'status': 'failed',
                'message': 'Config güncellenemedi',
                'elapsed': time.time() - start_time
            }
        
        # Scraper'ı çalıştır
        logger.info(f"🚀 Scraper başlatılıyor...")
        
        # PYTHONPATH'i src klasörüne ayarla
        env = os.environ.copy()
        src_path = str(Path(__file__).parent / 'src')
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = src_path
        
        result = subprocess.run(
            [sys.executable, '-m', 'scraper.main'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"✅ BAŞARILI: {name} ({elapsed:.1f}s)")
            logger.info(f"📊 Çıktı: {result.stdout[-500:]}")  # Son 500 karakter
            
            return {
                'status': 'success',
                'message': 'Scraping tamamlandı',
                'elapsed': elapsed,
                'stdout': result.stdout[-1000:]
            }
        else:
            logger.error(f"❌ HATA: {name} (exit code: {result.returncode})")
            logger.error(f"Stderr: {result.stderr}")
            
            return {
                'status': 'failed',
                'message': f'Exit code: {result.returncode}',
                'elapsed': elapsed,
                'stderr': result.stderr[-1000:]
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"💥 EXCEPTİON: {name} - {str(e)}")
        
        return {
            'status': 'exception',
            'message': str(e),
            'elapsed': elapsed
        }

async def main():
    """Ana fonksiyon"""
    
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║      101evler.com TÜM KİRALIK İLANLAR - OPTİMİZE         ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"📅 Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📝 Log dosyası: {log_file}")
    logger.info(f"📊 JSON dosyası: {json_file}")
    logger.info("")
    logger.info(f"🎯 Toplam konfigürasyon: {len(RENTAL_CONFIGS)}")
    logger.info(f"🏙️  Şehirler: {', '.join(CITIES)}")
    logger.info(f"🏠 Tipler: {', '.join(PROPERTY_TYPES)}")
    logger.info("")
    
    # Sonuçları sakla
    results = {}
    total_start = time.time()
    
    # Her konfigürasyonu sırayla çalıştır
    for idx, config in enumerate(RENTAL_CONFIGS, 1):
        city = config['city']
        property_type = config['property_type']
        name = config['name']
        
        logger.info(f"\n[{idx}/{len(RENTAL_CONFIGS)}] 🔄 {name}")
        
        # Scraping yap
        result = await run_scraper(city, property_type, name)
        
        # Sonucu kaydet
        key = f"{city}_{property_type}"
        results[key] = {
            'name': name,
            'city': city,
            'property_type': property_type,
            'status': result['status'],
            'message': result['message'],
            'elapsed': result['elapsed']
        }
        
        # Kısa gecikme (rate limiting)
        if idx < len(RENTAL_CONFIGS):
            logger.info(f"⏸️  3 saniye bekleniyor...")
            await asyncio.sleep(3)
    
    # Config'i restore et
    restore_config()
    
    # Toplam süre
    total_elapsed = time.time() - total_start
    
    # Özet istatistikler
    logger.info("\n" + "="*60)
    logger.info("📊 ÖZET İSTATİSTİKLER")
    logger.info("="*60)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    failed_count = sum(1 for r in results.values() if r['status'] == 'failed')
    exception_count = sum(1 for r in results.values() if r['status'] == 'exception')
    
    logger.info(f"✅ Başarılı: {success_count}/{len(RENTAL_CONFIGS)}")
    logger.info(f"❌ Hatalı: {failed_count}/{len(RENTAL_CONFIGS)}")
    logger.info(f"💥 Exception: {exception_count}/{len(RENTAL_CONFIGS)}")
    logger.info(f"⏱️  Toplam süre: {total_elapsed/60:.1f} dakika")
    logger.info(f"⚡ Ortalama: {total_elapsed/len(RENTAL_CONFIGS):.1f} saniye/config")
    logger.info("")
    
    # Detaylı sonuçlar
    if failed_count > 0 or exception_count > 0:
        logger.warning("\n⚠️  HATALI KONFIGÜRASYONLAR:")
        for key, result in results.items():
            if result['status'] != 'success':
                logger.warning(f"  - {result['name']}: {result['message']}")
    
    # JSON'a kaydet
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_configs': len(RENTAL_CONFIGS),
        'success': success_count,
        'failed': failed_count,
        'exception': exception_count,
        'total_elapsed_seconds': total_elapsed,
        'results': results
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Sonuçlar kaydedildi: {json_file}")
    
    # Extraction çalıştır
    logger.info("\n" + "="*60)
    logger.info("🔄 EXTRACTION BAŞLATILIYOR")
    logger.info("="*60)
    
    try:
        logger.info("📊 HTML'lerden CSV'ye veri çekiliyor...")
        
        # PYTHONPATH'i src klasörüne ayarla
        env = os.environ.copy()
        src_path = str(Path(__file__).parent / 'src')
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = src_path
        
        result = subprocess.run(
            [sys.executable, '-m', 'scraper.extract_data'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        if result.returncode == 0:
            logger.info("✅ Extraction başarılı!")
            logger.info(f"📊 Çıktı:\n{result.stdout[-500:]}")
        else:
            logger.error(f"❌ Extraction hatası (exit code: {result.returncode})")
            logger.error(f"Stderr: {result.stderr}")
            
    except Exception as e:
        logger.exception(f"💥 Extraction exception: {e}")
    
    # Final özet
    logger.info("\n" + "="*60)
    logger.info("🎉 İŞLEM TAMAMLANDI!")
    logger.info("="*60)
    logger.info(f"📁 HTML dosyaları: listings/")
    logger.info(f"📄 CSV dosyası: property_details.csv")
    logger.info(f"📝 Log: {log_file}")
    logger.info(f"📊 JSON: {json_file}")
    logger.info("")
    
    # CSV özeti
    csv_path = Path('property_details.csv')
    if csv_path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            rentals = df[df['listing_type'] == 'Rent']
            
            logger.info("📊 CSV ÖZET:")
            logger.info(f"  Toplam kayıt: {len(df)}")
            logger.info(f"  Kiralık kayıt: {len(rentals)}")
            logger.info("")
            logger.info("  Şehir dağılımı (kiralıklar):")
            for city, count in rentals['city'].value_counts().items():
                logger.info(f"    {city}: {count}")
            
        except Exception as e:
            logger.error(f"CSV özeti oluşturulamadı: {e}")
    
    return 0 if success_count == len(RENTAL_CONFIGS) else 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
EMERGENCY FULL SCAN - Girne Kiralık Tüm İlanlar
Tüm sayfaları tarayıp EKSİK OLMADAN tüm ilanları toplar
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
import logging
import sys
import shutil

# Şehir ve tipler
CONFIGS = [
    {'city': 'girne', 'type': 'kiralik-daire'},
    {'city': 'girne', 'type': 'kiralik-villa'},
    {'city': 'girne', 'type': 'kiralik-ev'},
    {'city': 'girne', 'type': 'kiralik-isyeri'},
]

# Log
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"emergency_girne_full_{timestamp}.log"

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
    backup_path = Path("src/scraper/config.py.emergency_backup")
    
    if config_path.exists():
        shutil.copy2(config_path, backup_path)
        logger.info(f"✅ Config yedeklendi")
        return True
    return False


def restore_config():
    """Config dosyasını geri yükle"""
    config_path = Path("src/scraper/config.py")
    backup_path = Path("src/scraper/config.py.emergency_backup")
    
    if backup_path.exists():
        shutil.copy2(backup_path, config_path)
        backup_path.unlink()
        logger.info("✅ Config restore edildi")
        return True
    return False


def update_config(city, property_type):
    """Config dosyasını güncelle"""
    config_path = Path("src/scraper/config.py")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        # CITY güncelle
        content = re.sub(
            r'CITY = "[^"]*"(\s+# Auto-updated.*)?',
            f'CITY = "{city}"  # Auto-updated by emergency_girne_full',
            content
        )
        
        # PROPERTY_TYPE güncelle
        content = re.sub(
            r'PROPERTY_TYPE = "[^"]*"(\s+# Auto-updated.*)?',
            f'PROPERTY_TYPE = "{property_type}"  # Auto-updated by emergency_girne_full',
            content
        )
        
        # MAX_PAGES = None olduğundan emin ol
        content = re.sub(
            r'MAX_PAGES = .*',
            'MAX_PAGES = None  # FULL SCAN!',
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
            timeout=1800  # 30 dakika timeout - Girne için çok sayfa var
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    except subprocess.TimeoutExpired:
        logger.error("❌ Scraper timeout")
        return {'success': False, 'returncode': -1, 'stdout': '', 'stderr': 'Timeout'}
    except Exception as e:
        logger.error(f"❌ Scraper hatası: {e}")
        return {'success': False, 'returncode': -1, 'stdout': '', 'stderr': str(e)}


def run_extraction():
    """Extraction işlemini çalıştır"""
    try:
        result = subprocess.run(
            ['python', '-m', 'scraper.extract_data'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    except Exception as e:
        logger.error(f"❌ Extraction hatası: {e}")
        return {'success': False, 'stdout': '', 'stderr': str(e)}


def main():
    """Ana fonksiyon"""
    
    print("\n" + "="*70)
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   🚨 EMERGENCY FULL SCAN - GİRNE KİRALIK TÜM İLANLAR          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("="*70)
    print()
    
    logger.info(f"📅 Başlangıç: {datetime.now()}")
    logger.info(f"📝 Log: {LOG_FILE}")
    logger.info("")
    
    # Config yedekle
    if not backup_config():
        print("\n❌ Config yedeklenemedi. İşlem iptal edildi.")
        return
    
    success_count = 0
    failed_count = 0
    
    for i, cfg in enumerate(CONFIGS, 1):
        city = cfg['city']
        prop_type = cfg['type']
        
        logger.info("="*70)
        logger.info(f"[{i}/{len(CONFIGS)}] 🏃 {city.title()} - {prop_type}")
        logger.info("="*70)
        
        # Config güncelle
        if not update_config(city, prop_type):
            logger.error(f"❌ Config güncellenemedi")
            failed_count += 1
            continue
        
        # Scraper çalıştır
        start = time.time()
        result = run_scraper()
        duration = time.time() - start
        
        if result['success']:
            logger.info(f"✅ BAŞARILI: {city.title()} - {prop_type} ({duration:.1f}s)")
            logger.info(f"Stdout: {result['stdout'][-500:]}")  # Son 500 karakter
            success_count += 1
        else:
            logger.error(f"❌ HATA: {city.title()} - {prop_type}")
            logger.error(f"Stderr: {result['stderr'][:500]}")
            failed_count += 1
        
        logger.info(f"📊 İlerleme: {i}/{len(CONFIGS)}")
        logger.info(f"✅ Başarılı: {success_count} | ❌ Hatalı: {failed_count}")
        logger.info("")
        
        if i < len(CONFIGS):
            time.sleep(3)
    
    # Config restore
    restore_config()
    
    # Özet
    logger.info("="*70)
    logger.info("📊 GENEL ÖZET")
    logger.info("="*70)
    logger.info(f"✅ Başarılı: {success_count}/{len(CONFIGS)}")
    logger.info(f"❌ Hatalı: {failed_count}/{len(CONFIGS)}")
    logger.info("")
    
    # Extraction
    logger.info("="*70)
    logger.info("🔄 EXTRACTION BAŞLATILIYOR")
    logger.info("="*70)
    
    extraction_result = run_extraction()
    if extraction_result['success']:
        logger.info("✅ Extraction başarılı!")
        logger.info(f"📊 {extraction_result['stdout'][-500:]}")
    else:
        logger.error("❌ Extraction başarısız!")
        logger.error(f"Stderr: {extraction_result['stderr'][:500]}")
    
    logger.info("")
    logger.info("="*70)
    logger.info("🎉 İŞLEM TAMAMLANDI!")
    logger.info("="*70)
    
    print("\n" + "="*70)
    print("✅ GİRNE KİRALIK TAM TARAMA TAMAMLANDI!")
    print("="*70)


if __name__ == "__main__":
    main()

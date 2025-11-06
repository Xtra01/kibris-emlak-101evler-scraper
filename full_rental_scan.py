#!/usr/bin/env python3
"""
TAM KAPSAMLI KKTC KİRALIK EMLAK TARAMASI
=========================================

KAPSAM:
- 4 Kategori: daire, villa, ev, işyeri
- 6 Şehir: Lefkoşa, Girne, Mağusa, Gazimağusa, İskele, Güzelyurt
- Toplam: 24 konfigürasyon

ÖZELLİKLER:
- Otomatik config güncelleme
- Detaylı logging
- Progress tracking
- JSON sonuç export
- Otomatik extraction
- Hata yönetimi

KULLANIM:
    python full_rental_scan.py
    
ÇIKTILAR:
    - listings/: HTML dosyaları
    - property_details.csv: Ana data
    - logs/full_scan_TIMESTAMP.log: Detaylı log
    - logs/full_scan_TIMESTAMP.json: Özet JSON
    - reports/full_rental_report_TIMESTAMP.xlsx: Detaylı rapor
"""

import asyncio
import subprocess
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# KONFİGÜRASYON
# ============================================================================

# Şehirler
CITIES = [
    'lefkosa',      # En fazla ilan
    'girne',        # Turizm bölgesi
    'magusa',       # Doğu
    'gazimagusa',   # Üniversite bölgesi
    'iskele',       # Sahil
    'guzelyurt'     # Batı
]

# Kiralık kategoriler - TAM KAPSAM
RENTAL_TYPES = [
    'kiralik-daire',    # ⭐⭐⭐⭐⭐ Çok yaygın
    'kiralik-villa',    # ⭐⭐⭐⭐ Yaygın
    'kiralik-ev',       # ⭐⭐⭐ Orta
    'kiralik-isyeri'    # ⭐⭐⭐ Orta (dükkan, ofis)
]

# Toplam konfigürasyon
TOTAL_CONFIGS = len(CITIES) * len(RENTAL_TYPES)

print(f"""
╔════════════════════════════════════════════════════════════╗
║   KKTC TAM KAPSAMLI KİRALIK EMLAK TARAMASI                ║
╚════════════════════════════════════════════════════════════╝

📊 KAPSAM:
   • {len(RENTAL_TYPES)} Kategori: {', '.join([t.replace('kiralik-', '') for t in RENTAL_TYPES])}
   • {len(CITIES)} Şehir: {', '.join([c.title() for c in CITIES])}
   • Toplam: {TOTAL_CONFIGS} konfigürasyon

⏱️  TAHMİNİ SÜRE: ~{TOTAL_CONFIGS * 0.5:.0f}-{TOTAL_CONFIGS * 1:.0f} dakika

🎯 HEDEF: KKTC'deki TÜM kiralık emlak verilerini toplamak
""")

# Onay al
print("⚠️  Bu işlem yaklaşık 15-20 dakika sürecek.")
print("   Devam etmek istiyor musunuz? (E/H): ", end='', flush=True)

# Auto-proceed for automation
proceed = input().strip().upper() if sys.stdin.isatty() else 'E'

if proceed not in ['E', 'Y', 'YES', 'EVET']:
    print("❌ İşlem iptal edildi.")
    sys.exit(0)

print("\n✅ Tarama başlatılıyor...\n")

# ============================================================================
# SETUP
# ============================================================================

# Log klasörü
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f'full_scan_{timestamp}.log'
json_file = log_dir / f'full_scan_{timestamp}.json'

# Logger
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

# ============================================================================
# FONKSİYONLAR
# ============================================================================

def update_config(city: str, property_type: str) -> bool:
    """Config dosyasını güncelle"""
    config_path = Path('src/scraper/config.py')
    
    if not config_path.exists():
        logger.error(f"❌ Config dosyası bulunamadı: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup
        backup_path = config_path.with_suffix('.py.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Güncelle
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.startswith('CITY = '):
                new_lines.append(f'CITY = "{city}"  # Auto-updated by full_rental_scan.py')
            elif line.startswith('PROPERTY_TYPE = '):
                new_lines.append(f'PROPERTY_TYPE = "{property_type}"  # Auto-updated by full_rental_scan.py')
            else:
                new_lines.append(line)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Config güncellenirken hata: {e}")
        return False

def restore_config():
    """Config'i geri yükle"""
    config_path = Path('src/scraper/config.py')
    backup_path = config_path.with_suffix('.py.bak')
    
    if backup_path.exists():
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("✅ Config restore edildi")
            backup_path.unlink()
        except Exception as e:
            logger.error(f"❌ Config restore hatası: {e}")

async def run_scraper(city: str, property_type: str, name: str, index: int, total: int) -> dict:
    """Scraper çalıştır"""
    start_time = time.time()
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"[{index}/{total}] 🏃 {name}")
        logger.info(f"📍 {city.title()} | 🏠 {property_type}")
        logger.info(f"{'='*60}\n")
        
        # Config güncelle
        if not update_config(city, property_type):
            return {
                'status': 'failed',
                'message': 'Config update failed',
                'elapsed': time.time() - start_time
            }
        
        # Scraper çalıştır
        env = os.environ.copy()
        src_path = str(Path(__file__).parent / 'src')
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
            return {
                'status': 'success',
                'message': 'Completed',
                'elapsed': elapsed
            }
        else:
            logger.error(f"❌ HATA: {name} (code: {result.returncode})")
            logger.error(f"Stderr: {result.stderr[-500:]}")
            return {
                'status': 'failed',
                'message': f'Exit code: {result.returncode}',
                'elapsed': elapsed,
                'error': result.stderr[-500:]
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"💥 EXCEPTION: {name}")
        return {
            'status': 'exception',
            'message': str(e),
            'elapsed': elapsed
        }

async def main():
    """Ana fonksiyon"""
    
    logger.info(f"📅 Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📝 Log: {log_file}")
    logger.info(f"📊 JSON: {json_file}")
    logger.info("")
    
    # Sonuçlar
    results = {}
    total_start = time.time()
    
    # Her kombinasyonu tara
    config_index = 0
    for property_type in RENTAL_TYPES:
        for city in CITIES:
            config_index += 1
            name = f"{city.title()} - {property_type.replace('kiralik-', '').title()}"
            
            # Scrape
            result = await run_scraper(city, property_type, name, config_index, TOTAL_CONFIGS)
            
            # Kaydet
            key = f"{city}_{property_type}"
            results[key] = {
                'name': name,
                'city': city,
                'property_type': property_type,
                **result
            }
            
            # Progress
            success_count = sum(1 for r in results.values() if r['status'] == 'success')
            failed_count = sum(1 for r in results.values() if r['status'] != 'success')
            
            elapsed = time.time() - total_start
            remaining = (TOTAL_CONFIGS - config_index) * (elapsed / config_index) if config_index > 0 else 0
            
            logger.info(f"\n📊 İlerleme: {config_index}/{TOTAL_CONFIGS}")
            logger.info(f"✅ Başarılı: {success_count} | ❌ Hatalı: {failed_count}")
            logger.info(f"⏱️  Geçen: {elapsed/60:.1f}m | Kalan: ~{remaining/60:.1f}m")
            
            # Rate limiting
            if config_index < TOTAL_CONFIGS:
                logger.info("⏸️  3 saniye bekleniyor...\n")
                await asyncio.sleep(3)
    
    # Config restore
    restore_config()
    
    # Toplam istatistikler
    total_elapsed = time.time() - total_start
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    failed_count = len(results) - success_count
    
    logger.info("\n" + "="*60)
    logger.info("📊 GENEL ÖZET")
    logger.info("="*60)
    logger.info(f"✅ Başarılı: {success_count}/{TOTAL_CONFIGS}")
    logger.info(f"❌ Hatalı: {failed_count}/{TOTAL_CONFIGS}")
    logger.info(f"⏱️  Toplam süre: {total_elapsed/60:.1f} dakika")
    logger.info(f"⚡ Ortalama: {total_elapsed/TOTAL_CONFIGS:.1f} saniye/config")
    logger.info("")
    
    # Hatalılar
    if failed_count > 0:
        logger.warning("⚠️  HATALI KONFIGÜRASYONLAR:")
        for key, result in results.items():
            if result['status'] != 'success':
                logger.warning(f"  - {result['name']}: {result['message']}")
    
    # JSON export
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_configs': TOTAL_CONFIGS,
        'success': success_count,
        'failed': failed_count,
        'total_elapsed_seconds': total_elapsed,
        'cities': CITIES,
        'property_types': RENTAL_TYPES,
        'results': results
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 JSON kaydedildi: {json_file}")
    
    # Extraction
    logger.info("\n" + "="*60)
    logger.info("🔄 EXTRACTION BAŞLATILIYOR")
    logger.info("="*60)
    
    try:
        env = os.environ.copy()
        src_path = str(Path(__file__).parent / 'src')
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
            logger.info(f"📊 {result.stdout[-300:]}")
        else:
            logger.error(f"❌ Extraction hatası (code: {result.returncode})")
            logger.error(result.stderr)
            
    except Exception as e:
        logger.exception(f"💥 Extraction exception: {e}")
    
    # CSV özeti
    logger.info("\n" + "="*60)
    logger.info("🎉 İŞLEM TAMAMLANDI!")
    logger.info("="*60)
    logger.info(f"📁 HTML: listings/")
    logger.info(f"📄 CSV: property_details.csv")
    logger.info(f"📝 Log: {log_file}")
    logger.info(f"📊 JSON: {json_file}")
    logger.info("")
    
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
            logger.info("  Kategori dağılımı (kiralıklar):")
            if 'property_subtype' in rentals.columns:
                for cat, count in rentals['property_subtype'].value_counts().head(10).items():
                    logger.info(f"    {cat}: {count}")
            logger.info("")
            logger.info("  Şehir dağılımı (kiralıklar):")
            for city, count in rentals['city'].value_counts().items():
                logger.info(f"    {city}: {count}")
            
        except Exception as e:
            logger.error(f"CSV özeti oluşturulamadı: {e}")
    
    return 0 if success_count == TOTAL_CONFIGS else 1

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

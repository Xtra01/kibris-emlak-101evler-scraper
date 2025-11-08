#!/usr/bin/env python3
"""
COMPREHENSIVE 101evler.com SCRAPER
====================================

HEDEF: TUM KKTC emlak ilanlarini cekmek
- 25,185 Satilik Ilan
- 7,365 Kiralik Ilan  
- TOPLAM: 32,550+ Ilan

OZELLIKLER:
- 7 Sehir × 11 Kategori = 77 konfigurasyon
- Resume capability (crash recovery)
- Progress tracking with ETA
- Rate limiting & block detection
- Comprehensive reporting
- Docker-ready

KULLANIM:
    # Tam tarama (tum 77 config)
    python scripts/scan/comprehensive_full_scan.py
    
    # Sadece satiliklar
    python scripts/scan/comprehensive_full_scan.py --type sale
    
    # Sadece kiraliklar  
    python scripts/scan/comprehensive_full_scan.py --type rent
    
    # Resume from crash
    python scripts/scan/comprehensive_full_scan.py --resume
    
    # Docker ile
    docker-compose run scraper python scripts/scan/comprehensive_full_scan.py
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import logging

# Notification imports
try:
    from emlak_scraper import notifications
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    logging.warning("Notification module not available - running without notifications")

# Auto-parse imports
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from scripts.utils.auto_parse import parse_and_update
    AUTO_PARSE_AVAILABLE = True
except ImportError:
    AUTO_PARSE_AVAILABLE = False
    logging.warning("Auto-parse module not available - running without auto-parse")

# ============================================================================
# Windows UTF-8 Encoding Fix (MUST be before any imports that use Rich)
# ============================================================================
import io
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# ============================================================================
# KONFIGURASYON
# ============================================================================

# Sehirler (ilan sayilarina gore siralanmis)
CITIES = [
    'girne',        # 13,063 satilik / 3,592 kiralik (EN FAZLA)
    'iskele',       # 4,626 satilik / 1,238 kiralik
    'lefkosa',      # 3,513 satilik / 1,523 kiralik
    'gazimagusa',   # ? satilik / 978 kiralik
    'guzelyurt',    # 76 satilik / 14 kiralik
    'lefke'         # 334 satilik / 20 kiralik
]

# Satilik kategoriler - TÜM OLASI KATEGORİLER (yoksa skip)
SALE_CATEGORIES = [
    'satilik-daire',     # Apartments - CONFIRMED EXISTS
    'satilik-villa',     # Villas - CONFIRMED EXISTS
    'satilik-ev',        # Houses - WILL TRY (may 404)
    'satilik-arsa',      # Land - WILL TRY (may 404)
    'satilik-arazi',     # Land alt - WILL TRY (may 404)
    'satilik-isyeri',    # Commercial - CONFIRMED EXISTS
    'satilik-proje',     # Projects - WILL TRY (may 404)
]

# Kiralik kategoriler - TÜM OLASI KATEGORİLER (yoksa skip)
RENT_CATEGORIES = [
    'kiralik-daire',     # Apartments - CONFIRMED EXISTS
    'kiralik-villa',     # Villas - CONFIRMED EXISTS
    'kiralik-ev',        # Houses - WILL TRY (may 404)
    'kiralik-isyeri',    # Commercial - CONFIRMED EXISTS
    'kiralik-gunluk',    # Daily rental - WILL TRY (may 404)
]

# Turkce isimler
CITY_NAMES = {
    'girne': 'Girne',
    'iskele': 'Iskele', 
    'lefkosa': 'Lefkosa',
    'gazimagusa': 'Gazimagusa',
    'guzelyurt': 'Guzelyurt',
    'lefke': 'Lefke'
}

CATEGORY_NAMES = {
    'satilik-daire': 'Satilik Daire',
    'satilik-villa': 'Satilik Villa',
    'satilik-ev': 'Satilik Ev',
    'satilik-arsa': 'Satilik Arsa',
    'satilik-arazi': 'Satilik Arazi',
    'satilik-isyeri': 'Satilik Isyeri',
    'satilik-proje': 'Satilik Proje',
    'kiralik-daire': 'Kiralik Daire',
    'kiralik-villa': 'Kiralik Villa',
    'kiralik-ev': 'Kiralik Ev',
    'kiralik-isyeri': 'Kiralik Isyeri',
    'kiralik-gunluk': 'Kiralik Gunluk'
}

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "data" / "cache" / "scraper_state.json"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "data" / "reports"

# Tum kombinasyonlar
ALL_CONFIGS = []
for city in CITIES:
    for category in SALE_CATEGORIES + RENT_CATEGORIES:
        ALL_CONFIGS.append({
            'city': city,
            'category': category,
            'name': f"{CITY_NAMES[city]} - {CATEGORY_NAMES[category]}"
        })

TOTAL_CONFIGS = len(ALL_CONFIGS)

# Skip banner for Windows encoding issues - will be in logs
if __name__ == '__main__':
    pass  # Banner moved to after argument parsing

# ============================================================================
# SETUP
# ============================================================================

# Log klasoru
LOG_DIR.mkdir(exist_ok=True, parents=True)

# Timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = LOG_DIR / f'comprehensive_scan_{timestamp}.log'
json_file = LOG_DIR / f'comprehensive_scan_{timestamp}.json'

# Logger
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
# STATE MANAGEMENT
# ============================================================================

def load_state():
    """Resume ozelligi icin state'i yukle"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            logger.info(f"[OK] State yuklendi: {len(state.get('completed', []))} tamamlanmis")
            return state
        except Exception as e:
            logger.error(f"State yukleme hatasi: {e}")
    
    return {
        'completed': [],
        'failed': [],
        'current': None,
        'started_at': datetime.now().isoformat(),
        'last_updated': None
    }

def save_state(state):
    """State'i kaydet"""
    try:
        STATE_FILE.parent.mkdir(exist_ok=True, parents=True)
        state['last_updated'] = datetime.now().isoformat()
        
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"State kaydedildi: {len(state.get('completed', []))} completed")
    except Exception as e:
        logger.error(f"State kaydetme hatasi: {e}")

# ============================================================================
# CONFIG MANAGEMENT
# ============================================================================

def update_config(city: str, property_type: str) -> bool:
    """Config dosyasini guncelle"""
    config_path = BASE_DIR / 'src' / 'emlak_scraper' / 'core' / 'config.py'
    
    if not config_path.exists():
        logger.error(f"[ERROR] Config dosyasi bulunamadi: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup
        backup_path = config_path.with_suffix('.py.comprehensive_backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Guncelle
        import re
        content = re.sub(
            r'CITY = "[^"]*"(\s+# Auto-updated.*)?',
            f'CITY = "{city}"  # Auto-updated by comprehensive_full_scan.py',
            content
        )
        content = re.sub(
            r'PROPERTY_TYPE = "[^"]*"(\s+# Auto-updated.*)?',
            f'PROPERTY_TYPE = "{property_type}"  # Auto-updated by comprehensive_full_scan.py',
            content
        )
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Config guncellenirken hata: {e}")
        return False

def restore_config():
    """Config'i geri yukle"""
    config_path = BASE_DIR / 'src' / 'emlak_scraper' / 'core' / 'config.py'
    backup_path = config_path.with_suffix('.py.comprehensive_backup')
    
    if backup_path.exists():
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("[OK] Config restore edildi")
            backup_path.unlink()
        except Exception as e:
            logger.error(f"[ERROR] Config restore hatasi: {e}")

# ============================================================================
# SCRAPER EXECUTION
# ============================================================================

async def run_scraper(city: str, category: str, name: str, index: int, total: int) -> dict:
    """Scraper calistir"""
    start_time = time.time()
    
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"[{index}/{total}] [START] {name}")
        logger.info(f"[LOCATION] {city.title()} | [TYPE] {category}")
        logger.info(f"{'='*70}\n")
        
        # 🔧 FIX: NO CONFIG FILE MODIFICATION NEEDED
        # City/category passed as parameters to scraper.main()
        
        # ============================================================================
        # DIRECT ASYNC CALL - With city/category parameters
        # ============================================================================
        # NO module reload needed - pass city/category as parameters
        try:
            from emlak_scraper.core import scraper
            
            logger.info(f"[RUN] Starting scraper for {name}...")
            logger.info(f"[CONFIG] City={city}, Category={category}")
            
            # Clear sys.argv to prevent argparse conflicts
            original_argv = sys.argv.copy()
            sys.argv = [sys.argv[0]]  # Only keep script name
            
            try:
                # 🔧 FIX: Pass city/category as parameters (NO RELOAD!)
                await scraper.main(city=city, category=category)
            finally:
                # Restore original argv
                sys.argv = original_argv
            
            # Count collected files
            from pathlib import Path
            output_dir = Path('data/raw/listings') / city / category
            files_collected = len(list(output_dir.glob('*.html'))) if output_dir.exists() else 0
            
            elapsed = time.time() - start_time
            logger.info(f"[OK] BASARILI: {name} ({elapsed:.1f}s, {files_collected} files)")
            
            return {
                'status': 'success',
                'message': 'Completed',
                'elapsed': elapsed,
                'files_collected': files_collected
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[ERROR] HATA: {name} ({str(e)})")
            logger.error(f"Exception type: {type(e).__name__}")
            
            return {
                'status': 'failed',
                'message': str(e),
                'elapsed': elapsed
            }
        # ============================================================================
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        logger.warning(f"[INTERRUPT] Kullanici tarafindan iptal edildi: {name}")
        return {
            'status': 'interrupted',
            'message': 'Interrupted by user',
            'elapsed': elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.exception(f"[CRASH] EXCEPTION: {name}")
        return {
            'status': 'exception',
            'message': str(e),
            'elapsed': elapsed
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main(args):
    """Ana fonksiyon"""
    
    logger.info("="*70)
    logger.info("  COMPREHENSIVE 101evler.com SCRAPER v2.1.0")
    logger.info("="*70)
    logger.info(f"Baslangic: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Tarama Tipi: {args.type.upper()}")
    logger.info(f"Resume Mode: {'EVET' if args.resume else 'HAYIR'}")
    logger.info("")
    logger.info("HEDEF:")
    logger.info(f"  - Satilik: ~25,185 ilan")
    logger.info(f"  - Kiralik: ~7,365 ilan")
    logger.info(f"  - TOPLAM: ~32,550+ ilan")
    logger.info("")
    logger.info("KAPSAM:")
    logger.info(f"  - {len(CITIES)} Sehir: {', '.join([CITY_NAMES[c] for c in CITIES])}")
    logger.info(f"  - {len(SALE_CATEGORIES)} Satilik Kategori")
    logger.info(f"  - {len(RENT_CATEGORIES)} Kiralik Kategori")
    logger.info(f"  - Toplam: {TOTAL_CONFIGS} konfigurasyon")
    logger.info("")
    logger.info("TAHMINI SURE:")
    logger.info(f"  - Ortalama: ~{TOTAL_CONFIGS * 0.5:.0f}-{TOTAL_CONFIGS * 1:.0f} dakika")
    logger.info(f"  - Maksimum: ~{TOTAL_CONFIGS * 2:.0f} dakika")
    logger.info("")
    logger.info("DOSYALAR:")
    logger.info(f"  - Log: {log_file.name}")
    logger.info(f"  - JSON: {json_file.name}")
    logger.info("="*70)
    logger.info("")
    
    # State yukle
    state = load_state() if args.resume else {
        'completed': [],
        'failed': [],
        'current': None,
        'started_at': datetime.now().isoformat(),
        'last_updated': None
    }
    
    # Filter configs
    configs_to_run = ALL_CONFIGS.copy()
    
    if args.type == 'sale':
        configs_to_run = [c for c in configs_to_run if c['category'].startswith('satilik-')]
        logger.info(f"[FILTER] Filtreleme: Sadece SATILIK kategoriler ({len(configs_to_run)} config)")
    elif args.type == 'rent':
        configs_to_run = [c for c in configs_to_run if c['category'].startswith('kiralik-')]
        logger.info(f"[FILTER] Filtreleme: Sadece KIRALIK kategoriler ({len(configs_to_run)} config)")
    
    # Resume logic
    if args.resume:
        completed_keys = set([f"{c['city']}_{c['category']}" for c in state.get('completed', [])])
        configs_to_run = [c for c in configs_to_run if f"{c['city']}_{c['category']}" not in completed_keys]
        logger.info(f"[RUNNING] RESUME MODE: {len(configs_to_run)} konfigurasyon kaldi")
    
    if not configs_to_run:
        logger.info("[OK] Tum konfigurasyonlar tamamlanmis!")
        return
    
    # Send scan started notification
    if NOTIFICATIONS_AVAILABLE and not args.resume:
        try:
            notifications.notify_scan_started(len(configs_to_run))
        except Exception as e:
            logger.warning(f"Notification failed: {e}")
    
    # Sonuclar
    results = {}
    total_start = time.time()
    
    # Her kombinasyonu tara
    for idx, config in enumerate(configs_to_run, 1):
        city = config['city']
        category = config['category']
        name = config['name']
        
        # State guncelle
        state['current'] = config
        save_state(state)
        
        # Scrape
        result = await run_scraper(city, category, name, idx, len(configs_to_run))
        
        # Kaydet
        key = f"{city}_{category}"
        results[key] = {
            'name': name,
            'city': city,
            'category': category,
            **result
        }
        
        # State guncelle
        if result['status'] == 'success':
            state['completed'].append(config)
            
            # 🔄 AUTO-PARSE: Config tamamlandı, hemen parse et
            if AUTO_PARSE_AVAILABLE:
                try:
                    logger.info(f"[PARSE] Auto-parsing {name}...")
                    parse_and_update(city, category, auto_excel=True)
                    logger.info(f"[PARSE] ✅ Auto-parse completed for {name}")
                except Exception as e:
                    logger.error(f"[PARSE] ❌ Auto-parse failed for {name}: {e}")
            
            # Notify success
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notifications.notify_config_completed(
                        config_name=name,
                        file_count=result.get('files_collected', 0),
                        completed=len(state['completed']),
                        total=len(configs_to_run),
                        duration=time.time() - total_start
                    )
                except Exception as e:
                    logger.debug(f"Notification failed: {e}")
        elif result.get('message') and '404' in result.get('message', ''):
            # Category doesn't exist - mark as skipped, not failed
            state['completed'].append({**config, 'skipped': True, 'reason': 'Category not found (404)'})
            logger.info(f"[SKIP] Category doesn't exist: {name}")
        else:
            state['failed'].append({**config, 'error': result.get('message')})
            # Notify failure
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notifications.notify_config_failed(
                        config_name=name,
                        error=result.get('message', 'Unknown error'),
                        completed=len(state['completed']),
                        total=len(configs_to_run)
                    )
                except Exception as e:
                    logger.debug(f"Notification failed: {e}")
        
        state['current'] = None
        save_state(state)
        
        # Progress
        total_completed = len(state['completed'])
        total_failed = len(state['failed'])
        
        elapsed = time.time() - total_start
        remaining = (len(configs_to_run) - idx) * (elapsed / idx) if idx > 0 else 0
        
        logger.info(f"\n[STATS] Ilerleme: {idx}/{len(configs_to_run)}")
        logger.info(f"[OK] Basarili: {total_completed} | [ERROR] Hatali: {total_failed}")
        logger.info(f"[TIME]  Gecen: {elapsed/60:.1f}m | Kalan: ~{remaining/60:.1f}m")
        
        # Rate limiting
        if idx < len(configs_to_run):
            logger.info("[WAIT]  3 saniye bekleniyor...\n")
            await asyncio.sleep(3)
    
    # Config restore
    restore_config()
    
    # Toplam istatistikler
    total_elapsed = time.time() - total_start
    success_count = len([r for r in results.values() if r['status'] == 'success'])
    failed_count = len(results) - success_count
    
    logger.info("\n" + "="*70)
    logger.info("[STATS] GENEL OZET")
    logger.info("="*70)
    logger.info(f"[OK] Basarili: {success_count}/{len(configs_to_run)}")
    logger.info(f"[ERROR] Hatali: {failed_count}/{len(configs_to_run)}")
    logger.info(f"[TIME]  Toplam sure: {total_elapsed/60:.1f} dakika")
    logger.info(f"[SPEED] Ortalama: {total_elapsed/len(configs_to_run):.1f} saniye/config")
    logger.info("")
    
    # JSON export
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_configs': len(configs_to_run),
        'success': success_count,
        'failed': failed_count,
        'total_elapsed_seconds': total_elapsed,
        'cities': CITIES,
        'sale_categories': SALE_CATEGORIES,
        'rent_categories': RENT_CATEGORIES,
        'results': results,
        'state': state
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"[SAVE] JSON kaydedildi: {json_file}")
    
    # Calculate total files collected
    total_files = sum([r.get('files_collected', 0) for r in results.values() if r.get('status') == 'success'])
    data_path = Path('data/raw/listings')
    data_size_mb = sum(f.stat().st_size for f in data_path.glob('*.html')) / 1024 / 1024 if data_path.exists() else 0
    
    # Send scan finished notification
    if NOTIFICATIONS_AVAILABLE:
        try:
            notifications.notify_scan_finished({
                'total_configs': len(configs_to_run),
                'completed': success_count,
                'failed': failed_count,
                'total_files': total_files,
                'data_size_mb': data_size_mb,
                'duration_minutes': total_elapsed / 60
            })
        except Exception as e:
            logger.warning(f"Notification failed: {e}")
    
    # Parser calistir
    logger.info("\n" + "="*70)
    logger.info("[RUNNING] PARSER BASLATILIYOR")
    logger.info("="*70)
    
    try:
        # Direct import instead of subprocess
        from emlak_scraper.core import parser
        
        # Run parser
        parser_result = parser.parse_all_listings()
        
        logger.info("[OK] Parser basarili!")
            
    except Exception as e:
        logger.exception(f"[CRASH] Parser exception: {e}")
    
    # Final
    logger.info("\n" + "="*70)
    logger.info("[DONE] ISLEM TAMAMLANDI!")
    logger.info("="*70)
    logger.info(f"[FOLDER] HTML: data/raw/listings/")
    logger.info(f"[FILE] CSV: data/processed/property_details.csv")
    logger.info(f"[LOG] Log: {log_file}")
    logger.info(f"[STATS] JSON: {json_file}")
    logger.info("")
    
    return 0 if success_count == len(configs_to_run) else 1

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Comprehensive 101evler.com scraper - Tum KKTC ilanlari'
    )
    parser.add_argument(
        '--type',
        choices=['all', 'sale', 'rent'],
        default='all',
        help='Tarama tipi: all (hepsi), sale (sadece satilik), rent (sadece kiralik)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Crash sonrasi devam et (resume mode)'
    )
    
    args = parser.parse_args()
    
    try:
        exit_code = asyncio.run(main(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n[ERROR] Kullanici tarafindan iptal edildi")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"[CRASH] Fatal error: {e}")
        sys.exit(1)

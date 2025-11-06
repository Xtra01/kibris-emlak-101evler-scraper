#!/usr/bin/env python3
"""
TÜMÜ KİRALIK İLAN İNDİRİCİ - 101evler.com
Tüm şehirlerdeki tüm kiralık daire ve villaları indirir.
Hata kontrolü, logging ve progress tracking ile.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
import json

# Configure logging
LOG_FILE = f"logs/scraper_all_rentals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Scraper configurations
RENTAL_CONFIGS = [
    # Daireler (her şehir)
    {"city": "lefkosa", "property_type": "kiralik-daire", "name": "Lefkoşa Kiralık Daire"},
    {"city": "girne", "property_type": "kiralik-daire", "name": "Girne Kiralık Daire"},
    {"city": "magusa", "property_type": "kiralik-daire", "name": "Mağusa Kiralık Daire"},
    {"city": "gazimagusa", "property_type": "kiralik-daire", "name": "Gazimağusa Kiralık Daire"},
    {"city": "iskele", "property_type": "kiralik-daire", "name": "İskele Kiralık Daire"},
    {"city": "guzelyurt", "property_type": "kiralik-daire", "name": "Güzelyurt Kiralık Daire"},
    
    # Villalar (her şehir)
    {"city": "lefkosa", "property_type": "kiralik-villa", "name": "Lefkoşa Kiralık Villa"},
    {"city": "girne", "property_type": "kiralik-villa", "name": "Girne Kiralık Villa"},
    {"city": "magusa", "property_type": "kiralik-villa", "name": "Mağusa Kiralık Villa"},
    {"city": "gazimagusa", "property_type": "kiralik-villa", "name": "Gazimağusa Kiralık Villa"},
    {"city": "iskele", "property_type": "kiralik-villa", "name": "İskele Kiralık Villa"},
    {"city": "guzelyurt", "property_type": "kiralik-villa", "name": "Güzelyurt Kiralık Villa"},
]

async def run_scraper(city, property_type, name):
    """Run scraper for a specific configuration"""
    logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"🚀 Başlatılıyor: {name}")
    logger.info(f"   Şehir: {city}, Tip: {property_type}")
    logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        # Update config file temporarily
        config_path = Path("src/scraper/config.py")
        config_content = config_path.read_text(encoding='utf-8')
        
        # Backup original config
        backup_content = config_content
        
        # Replace CITY and PROPERTY_TYPE
        import re
        config_content = re.sub(
            r'CITY = "[^"]*"',
            f'CITY = "{city}"',
            config_content
        )
        config_content = re.sub(
            r'PROPERTY_TYPE = "[^"]*"',
            f'PROPERTY_TYPE = "{property_type}"',
            config_content
        )
        
        # Write updated config
        config_path.write_text(config_content, encoding='utf-8')
        
        # Run scraper
        logger.info(f"📥 Scraper çalıştırılıyor...")
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "scraper.main",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path.cwd()
        )
        
        stdout, stderr = await process.communicate()
        
        # Restore original config
        config_path.write_text(backup_content, encoding='utf-8')
        
        if process.returncode == 0:
            logger.info(f"✅ {name} - BAŞARILI")
            output = stdout.decode('utf-8', errors='ignore')
            
            # Extract stats from output
            if "toplam ilan" in output.lower():
                for line in output.split('\n'):
                    if "toplam ilan" in line.lower() or "listing" in line.lower():
                        logger.info(f"   📊 {line.strip()}")
            
            return {
                "config": name,
                "status": "success",
                "returncode": 0,
                "output_lines": len(output.split('\n'))
            }
        else:
            logger.error(f"❌ {name} - HATA!")
            logger.error(f"   Return code: {process.returncode}")
            if stderr:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"   Error: {error_msg[:500]}")
            
            return {
                "config": name,
                "status": "failed",
                "returncode": process.returncode,
                "error": stderr.decode('utf-8', errors='ignore')[:500] if stderr else "Unknown error"
            }
    
    except Exception as e:
        logger.exception(f"💥 BEKLENMEYEN HATA - {name}: {str(e)}")
        return {
            "config": name,
            "status": "exception",
            "error": str(e)
        }

async def main():
    """Main execution function"""
    start_time = datetime.now()
    
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║   101evler.com TÜM KİRALIK İLANLAR İNDİRİCİ              ║")
    logger.info("║   Tüm şehirler + Daire + Villa                            ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"⏰ Başlangıç: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📋 Toplam Konfigurasyon: {len(RENTAL_CONFIGS)}")
    logger.info("")
    
    results = []
    
    for idx, config in enumerate(RENTAL_CONFIGS, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"[{idx}/{len(RENTAL_CONFIGS)}] {config['name']}")
        logger.info(f"{'='*60}\n")
        
        result = await run_scraper(
            config['city'],
            config['property_type'],
            config['name']
        )
        
        results.append(result)
        
        # Small delay between configs
        if idx < len(RENTAL_CONFIGS):
            logger.info("\n⏳ 3 saniye bekleniyor...\n")
            await asyncio.sleep(3)
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║                    ÖZET RAPOR                              ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    logger.info(f"✅ Başarılı: {len(successful)}/{len(RENTAL_CONFIGS)}")
    logger.info(f"❌ Başarısız: {len(failed)}/{len(RENTAL_CONFIGS)}")
    logger.info(f"⏱️  Toplam Süre: {duration}")
    logger.info("")
    
    if failed:
        logger.warning("⚠️  BAŞARISIZ OLAN YAPILANDIRMALAR:")
        for r in failed:
            logger.warning(f"   • {r['config']}: {r.get('error', 'Unknown')[:100]}")
        logger.info("")
    
    # Save results to JSON
    results_file = f"logs/scraper_results_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_configs': len(RENTAL_CONFIGS),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Sonuçlar kaydedildi: {results_file}")
    logger.info(f"📝 Log dosyası: {LOG_FILE}")
    logger.info("")
    logger.info("🎉 TÜM İŞLEMLER TAMAMLANDI!")
    logger.info("")
    
    # Now run extraction
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║           VERİ ÇIKARIMI BAŞLATILIYOR                       ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    try:
        logger.info("📤 extract_data.py çalıştırılıyor...")
        extract_process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "scraper.extract_data",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path.cwd()
        )
        
        extract_stdout, extract_stderr = await extract_process.communicate()
        
        if extract_process.returncode == 0:
            logger.info("✅ Veri çıkarımı BAŞARILI!")
            extract_output = extract_stdout.decode('utf-8', errors='ignore')
            
            # Log important lines
            for line in extract_output.split('\n'):
                if any(keyword in line.lower() for keyword in ['successfully', 'processed', 'failed', 'extraction summary']):
                    logger.info(f"   {line.strip()}")
        else:
            logger.error("❌ Veri çıkarımı BAŞARISIZ!")
            if extract_stderr:
                logger.error(extract_stderr.decode('utf-8', errors='ignore')[:500])
    
    except Exception as e:
        logger.exception(f"💥 Veri çıkarımı hatası: {str(e)}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("BÜTÜN İŞLEMLER BİTTİ!")
    logger.info("=" * 60)
    
    return len(failed) == 0  # Return True if all successful

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  İşlem kullanıcı tarafından iptal edildi!")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"💥 FATAL ERROR: {str(e)}")
        sys.exit(1)

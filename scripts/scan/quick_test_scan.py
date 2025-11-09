#!/usr/bin/env python3
"""
Quick Test Scan - Test single small config to verify full flow
- File structure
- Auto-parse
- CSV generation
- Excel report

Should complete in 2-3 minutes
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.emlak_scraper.core import scraper
from scripts.parse.auto_parse import parse_and_update

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_single_config():
    """Test with small config: Lefkoşa - Kiralik Gunluk"""
    
    city = "lefkosa"
    category = "kiralik-gunluk"
    
    logger.info("="*70)
    logger.info(f"🧪 QUICK TEST: {city.upper()} - {category.upper()}")
    logger.info("="*70)
    
    # 1. RUN SCRAPER
    logger.info("📥 [1/3] Running scraper...")
    try:
        await scraper.main(city=city, category=category)
        logger.info("✅ Scraper completed")
    except Exception as e:
        logger.error(f"❌ Scraper failed: {e}")
        return False
    
    # 2. AUTO-PARSE
    logger.info("🔄 [2/3] Running auto-parse...")
    try:
        parse_and_update(city, category)
        logger.info("✅ Auto-parse completed")
    except Exception as e:
        logger.error(f"❌ Auto-parse failed: {e}")
        return False
    
    # 3. VERIFY FILES
    logger.info("🔍 [3/3] Verifying results...")
    
    # Check HTML files
    html_dir = Path(f"data/raw/listings/{city}/{category}")
    html_files = list(html_dir.glob("*.html")) if html_dir.exists() else []
    logger.info(f"   📁 HTML files: {len(html_files)}")
    
    # Check CSV
    csv_file = Path(f"data/processed/{city}/{category}/property_details.csv")
    csv_exists = csv_file.exists()
    logger.info(f"   📊 CSV exists: {csv_exists}")
    if csv_exists:
        import pandas as pd
        df = pd.read_csv(csv_file)
        logger.info(f"   📊 CSV rows: {len(df)}")
    
    # Check Excel
    excel_file = Path(f"data/processed/{city}/{category}/property_report.xlsx")
    excel_exists = excel_file.exists()
    logger.info(f"   📈 Excel exists: {excel_exists}")
    
    logger.info("="*70)
    if len(html_files) > 0 and csv_exists:
        logger.info("✅ TEST PASSED - Full flow working!")
        return True
    else:
        logger.error("❌ TEST FAILED - Missing files")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_single_config())
    sys.exit(0 if success else 1)

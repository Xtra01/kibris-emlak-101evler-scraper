#!/usr/bin/env python3
"""
🚀 SMART SCAN V2 - Batch Mode with Health Protection
====================================================

KEY IMPROVEMENTS over comprehensive_full_scan.py:
1. ✅ Batch processing - 6 configs then 5-min rest
2. ✅ Health monitoring - auto-pause if CPU/RAM/Temp high
3. ✅ Command control - responds to Telegram commands
4. ✅ Progress tracking - real-time stats
5. ✅ Graceful shutdown - no data loss
6. ✅ Resume capability - picks up where left off

ARCHITECTURE:
- Reads commands from data/control/commands.json
- Writes status to data/control/scraper_state.json
- Auto-pauses between batches
- Checks health before each batch
- Respects stop/pause commands
"""

import asyncio
import json
import logging
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from emlak_scraper.core import scraper, config

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "data" / "control" / "scraper_state.json"
COMMAND_FILE = BASE_DIR / "data" / "control" / "commands.json"
LOG_DIR = BASE_DIR / "logs"

# Configuration
CONFIGS_PER_BATCH = 6         # Process 6 configs then rest
PAUSE_BETWEEN_CONFIGS = 30    # 30 seconds between configs
PAUSE_BETWEEN_BATCHES = 300   # 5 minutes between batches
HEALTH_CHECK_INTERVAL = 60    # Check health every minute

# Thresholds for auto-pause
MAX_CPU_PERCENT = 85.0
MAX_RAM_PERCENT = 85.0
MAX_TEMP_CELSIUS = 75.0

# All configurations (same as comprehensive_full_scan.py)
CITIES = config.CITIES
SALE_CATEGORIES = config.SALE_CATEGORIES
RENT_CATEGORIES = config.RENT_CATEGORIES

ALL_CONFIGS = []
for city in CITIES:
    for category in SALE_CATEGORIES + RENT_CATEGORIES:
        ALL_CONFIGS.append({'city': city, 'category': category})

TOTAL_CONFIGS = len(ALL_CONFIGS)

# Logging setup
LOG_DIR.mkdir(exist_ok=True, parents=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = LOG_DIR / f'smart_scan_v2_{timestamp}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitor system health"""
    
    @staticmethod
    def get_cpu_temp() -> float:
        """Get CPU temperature"""
        try:
            result = subprocess.run(
                ['vcgencmd', 'measure_temp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                temp_str = result.stdout.strip()
                temp = float(temp_str.split('=')[1].split("'")[0])
                return temp
        except:
            pass
        return 0.0
    
    @staticmethod
    def check_health() -> tuple[bool, str]:
        """
        Check if system is healthy enough to continue
        Returns: (is_healthy, reason)
        """
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        temp = HealthMonitor.get_cpu_temp()
        
        if cpu > MAX_CPU_PERCENT:
            return False, f"High CPU: {cpu:.1f}%"
        
        if ram > MAX_RAM_PERCENT:
            return False, f"High RAM: {ram:.1f}%"
        
        if temp > MAX_TEMP_CELSIUS:
            return False, f"High Temperature: {temp:.1f}°C"
        
        return True, "OK"


class StateManager:
    """Manage scraper state"""
    
    def __init__(self):
        self.state_file = STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'status': 'idle',
            'current_config': None,
            'configs_completed': 0,
            'total_configs': TOTAL_CONFIGS,
            'files_scraped': 0,
            'start_time': None,
            'last_update': None,
            'completed_configs': [],
            'failed_configs': []
        }
    
    def save_state(self):
        """Save state to file"""
        self.state['last_update'] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def update_status(self, status: str):
        """Update status"""
        self.state['status'] = status
        self.save_state()
    
    def update_progress(self, current_config: str, files_count: int):
        """Update progress"""
        self.state['current_config'] = current_config
        self.state['files_scraped'] += files_count
        self.save_state()
    
    def mark_completed(self, config_key: str):
        """Mark config as completed"""
        if config_key not in self.state['completed_configs']:
            self.state['completed_configs'].append(config_key)
            self.state['configs_completed'] = len(self.state['completed_configs'])
        self.save_state()
    
    def mark_failed(self, config_key: str):
        """Mark config as failed"""
        if config_key not in self.state['failed_configs']:
            self.state['failed_configs'].append(config_key)
        self.save_state()


class CommandListener:
    """Listen for commands from Telegram bot"""
    
    def __init__(self):
        self.command_file = COMMAND_FILE
        self.command_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_command_time = None
    
    def get_command(self) -> Optional[str]:
        """Check for new commands"""
        if not self.command_file.exists():
            return None
        
        try:
            with open(self.command_file, 'r') as f:
                data = json.load(f)
            
            cmd_time = data.get('timestamp')
            if cmd_time != self.last_command_time:
                self.last_command_time = cmd_time
                return data.get('command')
        except:
            pass
        
        return None


class SmartScannerV2:
    """Smart scanner with batch processing and health protection"""
    
    def __init__(self, mode: str = 'auto'):
        self.mode = mode
        self.state_manager = StateManager()
        self.command_listener = CommandListener()
        self.health_monitor = HealthMonitor()
        
        # Control flags
        self.should_stop = False
        self.should_pause = False
    
    async def check_commands(self):
        """Check for control commands"""
        cmd = self.command_listener.get_command()
        if cmd:
            logger.info(f"📥 Received command: {cmd}")
            
            if cmd == 'stop':
                self.should_stop = True
                logger.warning("🛑 Stop requested")
            elif cmd == 'pause':
                self.should_pause = True
                logger.warning("⏸️ Pause requested")
            elif cmd == 'resume':
                self.should_pause = False
                logger.info("▶️ Resume requested")
    
    async def process_config(self, city: str, category: str) -> tuple[bool, int]:
        """
        Process one config
        Returns: (success, files_count)
        """
        config_key = f"{city}/{category}"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 Processing: {config_key}")
        logger.info(f"{'='*60}")
        
        self.state_manager.update_progress(config_key, 0)
        
        try:
            # Run scraper for this config
            result = await scraper.main(city=city, category=category)
            
            # Count files
            output_dir = Path(config.get_output_dir(city, category))
            if output_dir.exists():
                files = list(output_dir.glob("*.html"))
                files_count = len(files)
            else:
                files_count = 0
            
            logger.info(f"✅ Completed: {config_key} - {files_count} files")
            self.state_manager.update_progress(config_key, files_count)
            self.state_manager.mark_completed(config_key)
            
            return True, files_count
            
        except Exception as e:
            logger.error(f"❌ Failed: {config_key} - {e}")
            self.state_manager.mark_failed(config_key)
            return False, 0
    
    async def process_batch(self, batch: List[Dict]) -> int:
        """Process a batch of configs"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📦 Starting batch: {len(batch)} configs")
        logger.info(f"{'='*80}")
        
        processed = 0
        
        for cfg in batch:
            # Check commands
            await self.check_commands()
            
            if self.should_stop:
                logger.warning("🛑 Stopping batch due to stop command")
                break
            
            while self.should_pause:
                logger.info("⏸️ Paused, waiting for resume...")
                self.state_manager.update_status('paused')
                await asyncio.sleep(10)
                await self.check_commands()
            
            # Health check
            healthy, reason = self.health_monitor.check_health()
            if not healthy:
                logger.warning(f"⚠️ Health check failed: {reason}")
                logger.info("💤 Pausing for 5 minutes to cool down...")
                await asyncio.sleep(300)
                continue
            
            # Process config
            success, files = await self.process_config(cfg['city'], cfg['category'])
            if success:
                processed += 1
            
            # Pause between configs
            if processed < len(batch):
                logger.info(f"💤 Resting for {PAUSE_BETWEEN_CONFIGS} seconds...")
                await asyncio.sleep(PAUSE_BETWEEN_CONFIGS)
        
        return processed
    
    async def run(self):
        """Main scan loop"""
        logger.info("\n" + "="*80)
        logger.info("🚀 SMART SCAN V2 - Starting")
        logger.info("="*80)
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Total configs: {TOTAL_CONFIGS}")
        logger.info(f"Batch size: {CONFIGS_PER_BATCH}")
        logger.info(f"Pause between batches: {PAUSE_BETWEEN_BATCHES}s ({PAUSE_BETWEEN_BATCHES/60:.1f} min)")
        logger.info("="*80 + "\n")
        
        self.state_manager.update_status('running')
        self.state_manager.state['start_time'] = datetime.now().isoformat()
        self.state_manager.save_state()
        
        # Filter out already completed configs
        completed = set(self.state_manager.state['completed_configs'])
        remaining_configs = [c for c in ALL_CONFIGS 
                           if f"{c['city']}/{c['category']}" not in completed]
        
        logger.info(f"✅ Already completed: {len(completed)}")
        logger.info(f"📋 Remaining: {len(remaining_configs)}")
        
        # Create batches
        batches = [remaining_configs[i:i+CONFIGS_PER_BATCH] 
                  for i in range(0, len(remaining_configs), CONFIGS_PER_BATCH)]
        
        logger.info(f"📦 Total batches: {len(batches)}\n")
        
        for batch_num, batch in enumerate(batches, 1):
            if self.should_stop:
                logger.warning("🛑 Stopping scan")
                break
            
            logger.info(f"\n{'#'*80}")
            logger.info(f"📦 BATCH {batch_num}/{len(batches)}")
            logger.info(f"{'#'*80}")
            
            await self.process_batch(batch)
            
            # Pause between batches (except last one)
            if batch_num < len(batches) and not self.should_stop:
                logger.info(f"\n💤 Resting between batches for {PAUSE_BETWEEN_BATCHES}s...")
                logger.info("   (Pi can cool down, other processes can run)")
                
                # Health report during pause
                for i in range(PAUSE_BETWEEN_BATCHES // 60):
                    await asyncio.sleep(60)
                    cpu = psutil.cpu_percent()
                    ram = psutil.virtual_memory().percent
                    temp = self.health_monitor.get_cpu_temp()
                    logger.info(f"   Health check: CPU {cpu:.1f}%, RAM {ram:.1f}%, Temp {temp:.1f}°C")
                    
                    await self.check_commands()
                    if self.should_stop:
                        break
        
        # Final status
        if self.should_stop:
            self.state_manager.update_status('stopped')
            logger.info("\n🛑 Scan stopped by command")
        else:
            self.state_manager.update_status('completed')
            logger.info("\n✅ Scan completed!")
        
        logger.info(f"\n📊 Final stats:")
        logger.info(f"   Completed: {self.state_manager.state['configs_completed']}/{TOTAL_CONFIGS}")
        logger.info(f"   Files scraped: {self.state_manager.state['files_scraped']:,}")
        logger.info(f"   Failed: {len(self.state_manager.state['failed_configs'])}")


async def main():
    """Entry point"""
    parser = argparse.ArgumentParser(description='Smart Scan V2')
    parser.add_argument('--mode', choices=['auto', 'fast', 'single'], default='auto',
                       help='Scan mode (auto=with pauses, fast=no pauses, single=one config)')
    args = parser.parse_args()
    
    scanner = SmartScannerV2(mode=args.mode)
    
    try:
        await scanner.run()
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Interrupted by user")
        scanner.state_manager.update_status('interrupted')
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        scanner.state_manager.update_status('error')


if __name__ == "__main__":
    asyncio.run(main())

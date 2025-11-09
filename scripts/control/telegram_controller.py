#!/usr/bin/env python3
"""
🎮 TELEGRAM CONTROL SYSTEM
==========================
Full control of scraper via Telegram bot

FEATURES:
- /scan start - Start scanning
- /scan stop - Stop scanning  
- /scan status - Check progress
- /scan pause - Pause current scan
- /scan resume - Resume paused scan
- /health - Check Pi health (CPU, RAM, temp, disk)
- /logs - Get recent logs
- /configs - List all configurations

ARCHITECTURE:
- Runs as separate daemon
- Communicates with scraper via state files
- Always responsive (low resource usage)
- Scraper runs ONLY when commanded
"""

import asyncio
import json
import logging
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import sys

# Telegram bot library (needs to be installed)
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    print("❌ python-telegram-bot not installed!")
    print("Install: pip install python-telegram-bot")
    sys.exit(1)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "data" / "control" / "scraper_state.json"
CONTROL_FILE = BASE_DIR / "data" / "control" / "commands.json"
LOG_FILE = BASE_DIR / "logs" / "telegram_bot.log"

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # TODO: Set your bot token
AUTHORIZED_USERS = [123456789]  # TODO: Add your Telegram user ID

# Setup logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PiHealthMonitor:
    """Monitor Raspberry Pi health metrics"""
    
    @staticmethod
    def get_cpu_temp() -> float:
        """Get CPU temperature (Raspberry Pi specific)"""
        try:
            result = subprocess.run(
                ['vcgencmd', 'measure_temp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                temp_str = result.stdout.strip()
                # Format: temp=45.0'C
                temp = float(temp_str.split('=')[1].split("'")[0])
                return temp
        except Exception as e:
            logger.warning(f"Failed to get CPU temp: {e}")
        return 0.0
    
    @staticmethod
    def get_health_stats() -> Dict:
        """Get all health metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'ram_percent': psutil.virtual_memory().percent,
            'ram_total_gb': psutil.virtual_memory().total / (1024**3),
            'ram_used_gb': psutil.virtual_memory().used / (1024**3),
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_free_gb': psutil.disk_usage('/').free / (1024**3),
            'cpu_temp': PiHealthMonitor.get_cpu_temp(),
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def format_health_message(stats: Dict) -> str:
        """Format health stats as pretty message"""
        # Emojis based on thresholds
        cpu_emoji = "🔴" if stats['cpu_percent'] > 80 else "🟡" if stats['cpu_percent'] > 50 else "🟢"
        ram_emoji = "🔴" if stats['ram_percent'] > 80 else "🟡" if stats['ram_percent'] > 50 else "🟢"
        temp_emoji = "🔴" if stats['cpu_temp'] > 75 else "🟡" if stats['cpu_temp'] > 60 else "🟢"
        disk_emoji = "🔴" if stats['disk_percent'] > 90 else "🟡" if stats['disk_percent'] > 70 else "🟢"
        
        msg = f"""
🏥 **Raspberry Pi 5 Health Report**

{cpu_emoji} **CPU Usage**: {stats['cpu_percent']:.1f}% ({stats['cpu_count']} cores)
{ram_emoji} **RAM**: {stats['ram_used_gb']:.1f} / {stats['ram_total_gb']:.1f} GB ({stats['ram_percent']:.1f}%)
{temp_emoji} **Temperature**: {stats['cpu_temp']:.1f}°C
{disk_emoji} **Disk**: {stats['disk_percent']:.1f}% used ({stats['disk_free_gb']:.1f} GB free)

⏰ **Checked**: {stats['timestamp'].split('T')[1][:8]}
"""
        return msg


class ScraperController:
    """Control scraper operations"""
    
    def __init__(self):
        self.state_file = STATE_FILE
        self.control_file = CONTROL_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.control_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_state(self) -> Dict:
        """Read current scraper state"""
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
            'total_configs': 72,
            'files_scraped': 0,
            'start_time': None,
            'last_update': None
        }
    
    def send_command(self, command: str, params: Optional[Dict] = None):
        """Send command to scraper"""
        cmd_data = {
            'command': command,
            'params': params or {},
            'timestamp': datetime.now().isoformat()
        }
        with open(self.control_file, 'w') as f:
            json.dump(cmd_data, f, indent=2)
        logger.info(f"Sent command: {command}")
    
    def start_scan(self, mode: str = 'auto'):
        """Start a scan"""
        self.send_command('start', {'mode': mode})
        # Also trigger the actual script in container
        subprocess.Popen([
            'docker', 'exec', '-d', 'emlak-scraper-101evler',
            'python', 'scripts/scan/smart_scan_v2.py',
            '--mode', mode
        ])
    
    def stop_scan(self):
        """Stop current scan"""
        self.send_command('stop')
    
    def pause_scan(self):
        """Pause current scan"""
        self.send_command('pause')
    
    def resume_scan(self):
        """Resume paused scan"""
        self.send_command('resume')
    
    def format_status_message(self, state: Dict) -> str:
        """Format status as pretty message"""
        status_emoji = {
            'idle': '💤',
            'running': '🏃',
            'paused': '⏸️',
            'completed': '✅',
            'error': '❌'
        }
        
        emoji = status_emoji.get(state['status'], '❓')
        
        if state['status'] == 'idle':
            return f"{emoji} **Status**: Idle\n\n✨ Ready to start scanning!"
        
        progress = (state['configs_completed'] / state['total_configs'] * 100) if state['total_configs'] > 0 else 0
        
        msg = f"""
{emoji} **Status**: {state['status'].title()}

📊 **Progress**: {state['configs_completed']}/{state['total_configs']} configs ({progress:.1f}%)
📁 **Files Scraped**: {state['files_scraped']:,}
🎯 **Current**: {state['current_config'] or 'N/A'}

⏱️ **Started**: {state['start_time'] or 'N/A'}
🕐 **Last Update**: {state['last_update'] or 'N/A'}
"""
        return msg


# Initialize controllers
health_monitor = PiHealthMonitor()
scraper_controller = ScraperController()


# ==============================================================================
# TELEGRAM BOT COMMANDS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🎮 **Emlak Scraper Control Bot**\n\n"
        "Available commands:\n"
        "/scan start - Start scanning\n"
        "/scan stop - Stop scanning\n"
        "/scan status - Check progress\n"
        "/scan pause - Pause scan\n"
        "/scan resume - Resume scan\n"
        "/health - Pi health check\n"
        "/logs - Recent logs\n"
        "/help - Show this message"
    )


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command"""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    logger.info(f"Health check requested by {update.effective_user.username}")
    
    stats = health_monitor.get_health_stats()
    message = health_monitor.format_health_message(stats)
    
    await update.message.reply_text(message, parse_mode='Markdown')


async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /scan commands"""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/scan start - Start scanning\n"
            "/scan stop - Stop scanning\n"
            "/scan status - Check progress\n"
            "/scan pause - Pause scan\n"
            "/scan resume - Resume scan"
        )
        return
    
    action = context.args[0].lower()
    
    if action == 'start':
        mode = context.args[1] if len(context.args) > 1 else 'auto'
        logger.info(f"Scan start requested by {update.effective_user.username}, mode: {mode}")
        scraper_controller.start_scan(mode)
        await update.message.reply_text(
            f"🚀 **Starting scan** (mode: {mode})\n\n"
            "Use /scan status to check progress"
        )
    
    elif action == 'stop':
        logger.info(f"Scan stop requested by {update.effective_user.username}")
        scraper_controller.stop_scan()
        await update.message.reply_text("🛑 **Stopping scan**...\n\nWait for current config to finish")
    
    elif action == 'pause':
        logger.info(f"Scan pause requested by {update.effective_user.username}")
        scraper_controller.pause_scan()
        await update.message.reply_text("⏸️ **Pausing scan**...\n\nWait for current config to finish")
    
    elif action == 'resume':
        logger.info(f"Scan resume requested by {update.effective_user.username}")
        scraper_controller.resume_scan()
        await update.message.reply_text("▶️ **Resuming scan**...")
    
    elif action == 'status':
        state = scraper_controller.get_state()
        message = scraper_controller.format_status_message(state)
        await update.message.reply_text(message, parse_mode='Markdown')
    
    else:
        await update.message.reply_text(f"❌ Unknown action: {action}")


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command"""
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    
    logger.info(f"Logs requested by {update.effective_user.username}")
    
    # Get last 20 lines of scraper log
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', '20', 'emlak-scraper-101evler'],
            capture_output=True,
            text=True,
            timeout=10
        )
        logs = result.stdout or result.stderr or "No logs available"
        # Truncate if too long
        if len(logs) > 3000:
            logs = logs[-3000:]
        await update.message.reply_text(f"```\n{logs}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to get logs: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start_command(update, context)


# ==============================================================================
# MAIN BOT RUNNER
# ==============================================================================

def main():
    """Start the Telegram bot"""
    logger.info("="*60)
    logger.info("🤖 Starting Telegram Control Bot")
    logger.info("="*60)
    
    # Check bot token
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Please set TELEGRAM_BOT_TOKEN in the script!")
        logger.error("Get token from @BotFather on Telegram")
        sys.exit(1)
    
    if not AUTHORIZED_USERS or AUTHORIZED_USERS == [123456789]:
        logger.warning("⚠️ AUTHORIZED_USERS not set! Anyone can control the bot!")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("logs", logs_command))
    
    # Start bot
    logger.info("✅ Bot is running! Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)

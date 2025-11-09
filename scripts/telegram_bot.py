#!/usr/bin/env python3
"""
Telegram Bot for Emlak Scraper Control
Manages scraper remotely via Telegram commands
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ALLOWED_USER_IDS = [int(x) for x in os.getenv("TELEGRAM_USER_IDS", "").split(",") if x]

# Paths
BASE_DIR = Path("/app")
STATE_FILE = BASE_DIR / "data" / "control" / "scraper_state.json"
COMMAND_FILE = BASE_DIR / "data" / "control" / "commands.json"
THERMAL_STATE = BASE_DIR / "data" / "control" / "thermal_state.json"

def check_auth(user_id: int) -> bool:
    """Check if user is authorized"""
    if not ALLOWED_USER_IDS:
        return True  # If no restrictions, allow all
    return user_id in ALLOWED_USER_IDS

def get_cpu_temp():
    """Get current CPU temperature"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            timeout=5
        )
        temp_str = result.stdout.strip().split("=")[1].replace("'C", "")
        return float(temp_str)
    except:
        return 0.0

def get_cpu_freq():
    """Get CPU frequency in MHz"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_clock", "arm"],
            capture_output=True,
            text=True,
            timeout=5
        )
        freq_hz = int(result.stdout.strip().split("=")[1])
        return freq_hz / 1_000_000
    except:
        return 0

def get_memory_usage():
    """Get memory usage"""
    try:
        result = subprocess.run(
            ["free", "-h"],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split("\n")
        mem_line = lines[1].split()
        return f"{mem_line[2]}/{mem_line[1]}"
    except:
        return "N/A"

def get_scraper_state():
    """Read scraper state"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def get_thermal_state():
    """Read thermal manager state"""
    try:
        if THERMAL_STATE.exists():
            with open(THERMAL_STATE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def send_command(action: str):
    """Send command to scraper"""
    try:
        command = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "source": "telegram_bot"
        }
        COMMAND_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMAND_FILE, "w") as f:
            json.dump(command, f, indent=2)
        return True
    except Exception as e:
        print(f"Error sending command: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show welcome message"""
    user_id = update.effective_user.id
    if not check_auth(user_id):
        await update.message.reply_text("❌ Unauthorized access!")
        return
    
    welcome = """
🤖 **Emlak Scraper Bot**

Available commands:
/status - Current scraper status
/temp - Temperature and system info
/health - System health check
/start_scrape - Start scraping
/pause - Pause scraping
/resume - Resume scraping
/stop - Stop scraping
/stats - Scraping statistics

Use /help for detailed command info.
"""
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get scraper status"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    state = get_scraper_state()
    
    status_text = f"""
📊 **Scraper Status**

Status: {state.get('status', 'unknown').upper()}
Current Config: {state.get('current_config', 'N/A')}
Progress: {state.get('current_index', 0)}/{state.get('total_configs', 72)}
Success: {state.get('success_count', 0)}
Errors: {state.get('error_count', 0)}

Last Update: {state.get('last_update', 'N/A')}
"""
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get temperature and system info"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    cpu_temp = get_cpu_temp()
    cpu_freq = get_cpu_freq()
    mem = get_memory_usage()
    thermal = get_thermal_state()
    
    temp_emoji = "🟢" if cpu_temp < 60 else "🟡" if cpu_temp < 70 else "🔴"
    
    temp_text = f"""
🌡️ **System Temperature**

{temp_emoji} CPU Temp: **{cpu_temp:.1f}°C**
⚡ CPU Freq: {cpu_freq:.0f} MHz
💾 Memory: {mem}

Thermal Status: {thermal.get('status', 'N/A')}
"""
    await update.message.reply_text(temp_text, parse_mode="Markdown")

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comprehensive health check"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    cpu_temp = get_cpu_temp()
    cpu_freq = get_cpu_freq()
    mem = get_memory_usage()
    state = get_scraper_state()
    thermal = get_thermal_state()
    
    # Determine health status
    health_status = "✅ HEALTHY"
    if cpu_temp > 70:
        health_status = "⚠️ WARNING - High Temperature"
    elif cpu_temp > 75:
        health_status = "🚨 CRITICAL - Overheating"
    
    health_text = f"""
🏥 **System Health Check**

Overall: {health_status}

**Hardware:**
🌡️ Temperature: {cpu_temp:.1f}°C
⚡ CPU: {cpu_freq:.0f} MHz
💾 Memory: {mem}

**Scraper:**
Status: {state.get('status', 'unknown').upper()}
Progress: {state.get('current_index', 0)}/{state.get('total_configs', 72)}

**Thermal Manager:**
Status: {thermal.get('status', 'UNKNOWN')}
Last Check: {thermal.get('timestamp', 'N/A')[:19] if thermal.get('timestamp') else 'N/A'}
"""
    await update.message.reply_text(health_text, parse_mode="Markdown")

async def start_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start scraping"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if send_command("start"):
        await update.message.reply_text("▶️ Scraping started!")
    else:
        await update.message.reply_text("❌ Failed to start scraping")

async def pause_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pause scraping"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if send_command("pause"):
        await update.message.reply_text("⏸️ Scraping paused!")
    else:
        await update.message.reply_text("❌ Failed to pause")

async def resume_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resume scraping"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if send_command("resume"):
        await update.message.reply_text("▶️ Scraping resumed!")
    else:
        await update.message.reply_text("❌ Failed to resume")

async def stop_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop scraping"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    if send_command("stop"):
        await update.message.reply_text("🛑 Scraping stopped!")
    else:
        await update.message.reply_text("❌ Failed to stop")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get scraping statistics"""
    if not check_auth(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized")
        return
    
    # Count scraped files
    try:
        result = subprocess.run(
            ["find", "/app/data/raw/listings", "-name", "*.html"],
            capture_output=True,
            text=True,
            timeout=10
        )
        file_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
    except:
        file_count = 0
    
    state = get_scraper_state()
    
    stats_text = f"""
📈 **Scraping Statistics**

Total Files: **{file_count:,}**
Configs Processed: {state.get('current_index', 0)}/72
Success Rate: {state.get('success_count', 0)} ✅
Errors: {state.get('error_count', 0)} ❌

Uptime: {state.get('elapsed_time', 'N/A')}
"""
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """
📚 **Command Reference**

**Status & Monitoring:**
/status - Current scraper status
/temp - Temperature and CPU info
/health - Full system health check
/stats - Scraping statistics

**Control:**
/start_scrape - Start the scraper
/pause - Pause current operation
/resume - Resume paused operation
/stop - Stop scraping completely

**Info:**
/help - Show this help message
/start - Welcome message

⚠️ All commands require authorization.
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    """Start the bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Error: TELEGRAM_BOT_TOKEN not set!")
        print("Set environment variable: export TELEGRAM_BOT_TOKEN='your_token'")
        return
    
    print("🤖 Starting Telegram Bot...")
    print(f"Authorized users: {ALLOWED_USER_IDS if ALLOWED_USER_IDS else 'All users'}")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("temp", temp))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("start_scrape", start_scrape))
    app.add_handler(CommandHandler("pause", pause_scrape))
    app.add_handler(CommandHandler("resume", resume_scrape))
    app.add_handler(CommandHandler("stop", stop_scrape))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    print("✅ Bot started successfully!")
    print("Press Ctrl+C to stop")
    
    # Run the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

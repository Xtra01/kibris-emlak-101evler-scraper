# 🚀 Quick Start Guide - Telegram Bot Setup

## ✅ What's Done

Your Raspberry Pi 5 thermal management and Telegram bot infrastructure is **ready**!

- ✅ Thermal manager script created
- ✅ Telegram bot code deployed
- ✅ Docker container built
- ✅ Old analyzer process killed (freed resources)
- ✅ Temperature: 63.7°C (monitoring)
- ✅ Scan running: 2030 files scraped, 54/302 batches

## 🤖 To Activate Telegram Bot (5 minutes)

### Step 1: Create Your Bot

1. Open Telegram
2. Search for `@BotFather`
3. Send: `/newbot`
4. Name it: `Emlak Scraper Control` (or any name)
5. Username: `your_name_emlak_bot` (must end with 'bot')
6. **Copy the token** you receive (looks like `1234567890:ABCdef...`)

### Step 2: Get Your User ID

1. Search for `@userinfobot` on Telegram
2. Send any message
3. **Copy your ID** (like `123456789`)

### Step 3: Configure on Pi

```bash
# SSH to Pi
ssh ekrem@192.168.1.143

# Edit .env file
cd /home/ekrem/projects/emlak-scraper
nano .env
```

Replace the placeholder token with your real token:
```bash
TELEGRAM_BOT_TOKEN=YOUR_REAL_TOKEN_HERE
TELEGRAM_USER_IDS=YOUR_USER_ID_HERE
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 4: Start the Bot

```bash
docker compose up -d telegram-bot
docker logs emlak-telegram-bot -f
```

You should see: `✅ Bot started successfully!`

### Step 5: Test It!

Open Telegram and send `/start` to your bot.

Try these commands:
- `/temp` - Check Pi temperature
- `/status` - Scraper status
- `/health` - Full system health
- `/stats` - Scraping statistics

## 🌡️ Current Status

**Raspberry Pi 5 Temperature:** 63.7°C

This is **acceptable** but could be better. Recommendations:

### Immediate Actions (Software - Already Done ✅)
- ✅ Killed unnecessary processes
- ✅ Docker CPU limit: 1.5 cores (37.5%)
- ✅ Docker RAM limit: 3GB (37.5%)
- ✅ Thermal manager ready to auto-pause at 65°C

### Recommended Hardware Upgrade
🛒 **Buy Official Pi 5 Active Cooler** (~$5)
- Will drop temp to ~50-55°C
- Amazon/official stores
- Easy installation (clips on)

### Alternative Cooling Solutions
- Any 5V fan with heatsink
- Ensure case has ventilation
- Keep in cool room (AC if possible)

## 📊 Scraping Progress

**Current Stats:**
- Files scraped: **2,030** HTML files
- Progress: **54/302 batches** (18%)
- ETA: **70 minutes** remaining
- Config: girne/satilik-villa

**Monitor Progress:**
```bash
# Via Telegram (once bot active)
/stats

# Via SSH
ssh ekrem@192.168.1.143
docker exec emlak-scraper-101evler tail -20 /app/logs/comprehensive_scan.log

# Via Web
https://emlak.devtestenv.org
```

## 📚 Full Documentation

- **Telegram Bot Setup:** `docs/TELEGRAM_BOT.md`
- **Thermal Optimization:** `docs/THERMAL_OPTIMIZATION.md`

## 🆘 Troubleshooting

**Bot not responding?**
```bash
docker logs emlak-telegram-bot
# Check for "InvalidToken" error
# Make sure token is correct in .env
```

**Temperature still high?**
```bash
# Check current temp
vcgencmd measure_temp

# Check if scan is paused
docker exec emlak-scraper-101evler ps aux | grep python

# Thermal manager will auto-pause at 65°C
```

**Need to stop scraping temporarily?**
```bash
docker exec emlak-scraper-101evler pkill -STOP python  # Pause
docker exec emlak-scraper-101evler pkill -CONT python  # Resume
```

## 🎯 Next Steps

1. ⏳ Let current scan complete (~70 min)
2. 🤖 Setup Telegram bot (5 min - follow steps above)
3. 🛒 Order active cooler for Pi5
4. 📊 Monitor via Telegram bot remotely

---

**Commit:** `37769b3` - All thermal and bot files pushed to GitHub ✅

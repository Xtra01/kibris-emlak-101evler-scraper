# 🚀 QUICK SETUP AFTER PI RESTART

## Step 1: Physical Restart
1. Unplug Pi power
2. Wait 10 seconds
3. Plug back in
4. Wait 2-3 minutes for boot

## Step 2: Check Pi Health

```bash
ssh ekrem@192.168.1.143

# Check system status
uptime
free -h
vcgencmd measure_temp
df -h

# Check what was running
docker ps -a
docker logs emlak-scraper-101evler --tail 50 | grep -E "ERROR|CRITICAL|404"
```

## Step 3: Update Code

```bash
cd ~/projects/emlak-scraper

# Pull latest changes
git pull

# Stop old container
docker compose down

# Rebuild with new config
docker compose build

# Start with NEW idle mode (no auto-scan!)
docker compose up -d
```

## Step 4: Verify Container is Idle

```bash
# Check container status
docker ps

# Should show: "tail -f /dev/null" (idle, not scanning!)
docker logs emlak-scraper-101evler

# Check resource usage (should be LOW)
docker stats --no-stream
# Expected: CPU < 5%, RAM < 500MB
```

## Step 5: Optional - Start Telegram Bot

```bash
# Install python-telegram-bot if not installed
pip3 install python-telegram-bot

# Get your Telegram bot token from @BotFather
# Edit the script and add:
# - TELEGRAM_BOT_TOKEN = "your_token_here"
# - AUTHORIZED_USERS = [your_telegram_user_id]

# Start bot (in background)
cd ~/projects/emlak-scraper
nohup python3 scripts/control/telegram_controller.py > logs/telegram_bot.log 2>&1 &

# Check bot is running
ps aux | grep telegram_controller
tail -f logs/telegram_bot.log
```

## Step 6: Manual Scan (Optional)

If you want to run a scan manually (without Telegram):

```bash
# Enter container
docker exec -it emlak-scraper-101evler bash

# Inside container:
cd /app

# Option A: Analyze existing data (INSTANT)
python scripts/analysis/analyze_existing_data.py

# Option B: Run site analyzer (5-10 min, gets totals)
python scripts/analysis/deep_site_analyzer.py

# Option C: Start smart scan (LONG, scans all configs)
python scripts/scan/smart_scan_v2.py --mode auto

# Exit container
exit
```

## Step 7: Monitor Health

```bash
# Watch resources in real-time
watch -n 5 'vcgencmd measure_temp && free -h && docker stats --no-stream'

# Check logs
docker logs -f emlak-scraper-101evler

# Stop if needed
docker compose down
```

## 🎮 Using Telegram Bot (Recommended)

Once Telegram bot is running, you can control everything from your phone:

```
/health              - Check Pi CPU, RAM, temperature
/scan status         - Check scan progress
/scan start          - Start scanning
/scan pause          - Pause current scan
/scan stop           - Stop scan
/logs                - See recent logs
```

## ⚠️ Troubleshooting

### Container won't start
```bash
docker logs emlak-scraper-101evler
# Check for errors, fix accordingly
```

### Git pull fails
```bash
cd ~/projects/emlak-scraper
git stash          # Save local changes
git pull           # Pull updates
git stash pop      # Restore local changes (if needed)
```

### High resource usage
```bash
# Stop container immediately
docker compose down

# Check what's using resources
top
htop  # if installed

# Reboot Pi if needed
sudo reboot
```

## 📊 Expected Resource Usage

### Idle State (Default Now!)
- CPU: < 5%
- RAM: < 500MB
- Temp: < 50°C

### During Scan
- CPU: 30-60% (limited by docker)
- RAM: 1-3GB (limited by docker)
- Temp: 50-70°C
- **Note**: Will pause if exceeds limits!

## ✅ Success Checklist

- [ ] Pi boots and SSH works
- [ ] Container starts in IDLE mode (not auto-scanning)
- [ ] Resource usage is LOW
- [ ] Temperature is normal (< 50°C)
- [ ] Telegram bot responds (if using)
- [ ] Manual scan works when requested
- [ ] Scan auto-pauses if resources high

---

**Next**: Use Telegram bot or manual commands to control scans!

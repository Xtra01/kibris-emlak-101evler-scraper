# Raspberry Pi 5 Thermal Optimization Guide

## 🌡️ Problem

Raspberry Pi 5 can overheat during intensive scraping operations, especially when:
- Running Playwright with Chromium (multiple processes)
- CPU at 2.4 GHz full speed
- Multiple concurrent scraping operations
- Poor ventilation

**Target Temperature**: Keep below 65°C for stable operation

## 🔧 Solutions Implemented

### 1. **Thermal Manager Script**

Automatic temperature monitoring and scraper control:

```bash
# Location: scripts/thermal_manager.py
python scripts/thermal_manager.py
```

**Features:**
- Monitors temperature every 30 seconds
- Auto-pauses scraper at 65°C
- Auto-resumes at 60°C
- Emergency stop at 75°C
- Logs all thermal events

### 2. **Docker Resource Limits**

CPU and memory limits to prevent overload:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.5'      # Max 1.5 cores (37.5% of 4 cores)
      memory: 3G       # Max 3GB (37.5% of 8GB)
```

### 3. **Scraper Batch Delays**

Reduced CPU load by adding pauses:
- 30 seconds between configs
- 5 minutes between batches
- 1 second between individual requests

### 4. **Kill Unnecessary Processes**

Remove old/stuck processes consuming resources:

```bash
# Find Python processes
docker exec emlak-scraper-101evler ps aux | grep python

# Kill specific PID
docker exec emlak-scraper-101evler kill <PID>
```

## 📊 Monitoring Temperature

### Via Telegram Bot:
```
/temp     # Quick temperature check
/health   # Full system health
```

### Via SSH:
```bash
# Temperature
vcgencmd measure_temp

# CPU frequency
vcgencmd measure_clock arm

# CPU throttling status
vcgencmd get_throttled
```

### Thermal State File:
```bash
cat /home/ekrem/projects/emlak-scraper/data/control/thermal_state.json
```

## 🛠️ Hardware Optimization

### Essential (Highly Recommended):

1. **Active Cooling**
   - Official Pi 5 Active Cooler (recommended)
   - 3rd party fan + heatsink combo
   - Target: Keep below 60°C under load

2. **Case Ventilation**
   - Open case or case with large vents
   - Ensure airflow around Pi
   - Don't stack Pi with other devices

3. **Thermal Paste**
   - Apply quality thermal paste to CPU
   - Re-apply every 6-12 months

### Optional Improvements:

4. **Undervolting** (Advanced)
   ```bash
   # Edit config.txt
   sudo nano /boot/firmware/config.txt
   
   # Add (test stability!):
   over_voltage=-2
   ```

5. **CPU Governor** (Software limit)
   ```bash
   # Install
   sudo apt-get install cpufrequtils
   
   # Set to powersave
   sudo cpufreq-set -g powersave
   
   # Or ondemand (scales based on load)
   sudo cpufreq-set -g ondemand
   ```

6. **Environment**
   - Keep room cool (< 25°C)
   - Avoid direct sunlight
   - Consider air conditioning

## 📈 Thermal Thresholds

| Temperature | Status | Action |
|-------------|--------|--------|
| < 60°C | 🟢 Normal | Full operation |
| 60-65°C | 🟡 Warm | Monitor closely |
| 65-75°C | 🟠 Hot | Auto-pause scraper |
| > 75°C | 🔴 Critical | Emergency stop |
| > 80°C | 🚨 Danger | Risk of thermal throttling/damage |

## 🔍 Checking Throttling

```bash
# Check if Pi has throttled
vcgencmd get_throttled

# Output meanings:
# 0x0 = No throttling (good!)
# 0x50000 = Throttled in the past
# 0x50005 = Currently throttled + was throttled
```

**Throttling flags:**
- Bit 0: Under-voltage detected
- Bit 1: ARM frequency capped
- Bit 2: Currently throttled
- Bit 3: Soft temperature limit active

## 🚀 Quick Temperature Fix

If Pi is too hot **right now**:

```bash
# 1. Pause scraper
ssh ekrem@192.168.1.143
docker exec emlak-scraper-101evler kill -STOP $(pgrep python)

# 2. Wait for cool down
watch vcgencmd measure_temp  # Ctrl+C to exit

# 3. Resume when < 60°C
docker exec emlak-scraper-101evler kill -CONT $(pgrep python)
```

## 📋 Recommended Setup

For **optimal** temperature management:

1. ✅ Install official Pi 5 Active Cooler (~$5)
2. ✅ Enable thermal manager script (runs in background)
3. ✅ Use Telegram bot to monitor remotely
4. ✅ Keep Docker resource limits (already configured)
5. ✅ Ensure good ventilation

This should keep temperature below 60°C even under heavy load.

## 🔄 Automatic Thermal Management

The thermal manager runs automatically with these settings:

```python
MAX_TEMP = 65.0       # Pause scraping
RESUME_TEMP = 60.0    # Resume scraping
CRITICAL_TEMP = 75.0  # Emergency stop
TEMP_CHECK_INTERVAL = 30  # Check every 30s
```

To adjust these values, edit `scripts/thermal_manager.py`

## 📞 Support

If temperature issues persist:
- Check `/temp` on Telegram bot
- Review logs: `docker logs emlak-scraper-101evler`
- Check thermal state: `cat data/control/thermal_state.json`
- Consider hardware upgrades (active cooler)

# 🏥 RASPBERRY PI HEALTH & PROTECTION SYSTEM

## 🚨 CURRENT CRISIS: Pi Crashed (Nov 9, 2025)

**Status**: Pi unreachable at 192.168.1.143
**Cause**: Likely resource exhaustion from scraper loop
**Action**: Physical restart required

---

## 🎯 ROOT CAUSE ANALYSIS

### Problem 1: Continuous Scraper Loop
**Issue**: `comprehensive_full_scan.py` runs 24/7 in loop mode
- No pause mechanism
- Consumes CPU/RAM continuously
- No idle time between scans

### Problem 2: No Resource Limits
**Issue**: Docker container has unlimited access
- Can consume all Pi RAM (8GB)
- Can max out CPU (4 cores)
- No automatic throttling

### Problem 3: No Health Monitoring
**Issue**: No alerts when problems occur
- No CPU/RAM monitoring
- No temperature alerts
- No automatic shutdown on overload

---

## ✅ PERMANENT SOLUTIONS

### Solution 1: ON-DEMAND MODE (PRIORITY 1)

**Strategy**: Scraper sleeps until explicitly requested

#### Implementation:
```python
# New architecture: control_daemon.py
# - Listens for Telegram commands
# - Scraper runs ONLY when commanded
# - Auto-stops after completion
# - Sends progress updates via Telegram
```

**Benefits**:
- Zero resource usage when idle
- Full control via Telegram
- No accidental overload
- Other projects unaffected

#### Commands:
```
/scan start           - Start full scan
/scan status          - Check progress
/scan pause           - Pause current scan
/scan resume          - Resume paused scan
/scan stop            - Stop and cleanup
/health               - Check Pi health (CPU, RAM, temp)
```

---

### Solution 2: Resource Limits (Docker)

**Add to docker-compose.yml**:
```yaml
services:
  emlak-scraper-101evler:
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Max 2 cores (50% of Pi5)
          memory: 4G       # Max 4GB RAM (50% of Pi5)
        reservations:
          cpus: '0.5'      # Minimum 0.5 core
          memory: 512M     # Minimum 512MB
```

**Benefits**:
- Other containers get guaranteed resources
- Prevents Pi freeze/crash
- Automatic throttling
- System stays responsive

---

### Solution 3: Health Monitoring

**Add monitoring script**: `monitor_health.py`

```python
# Runs every 5 minutes via cron
# Checks:
# 1. CPU usage > 90% for 5 min → Alert + pause scraper
# 2. RAM usage > 90% → Alert + pause scraper  
# 3. Temperature > 75°C → Alert + pause scraper
# 4. Disk usage > 90% → Alert
# 5. Network unreachable > 2 min → Alert

# Actions:
# - Send Telegram alert
# - Auto-pause heavy processes
# - Log to /var/log/pi_health.log
# - Email notification (optional)
```

---

### Solution 4: Graceful Scan Architecture

**Current Problem**: Loop runs forever
**Solution**: Batch mode with pause

```python
# New scan architecture:

class SmartScan:
    def __init__(self):
        self.pause_between_configs = 30  # 30 sec pause
        self.pause_between_batches = 300  # 5 min pause
        self.configs_per_batch = 6       # 6 configs then rest
        
    async def run(self):
        for batch in self.batches:
            # Run 6 configs
            await self.process_batch(batch)
            
            # PAUSE - let Pi breathe
            logger.info(f"💤 Resting for 5 minutes...")
            await asyncio.sleep(300)
            
            # Health check before continuing
            if not self.check_health():
                logger.warning("⚠️ Health check failed, pausing scan")
                await self.telegram.send("Scan paused: High CPU/RAM")
                return
```

**Benefits**:
- Pi gets rest periods
- Heat dissipation time
- Other processes can run
- Prevents resource exhaustion

---

### Solution 5: Telegram Control Integration

**Priority**: HIGH - This is your main interface

```python
# telegram_controller.py

class ScanController:
    """Control scraper via Telegram"""
    
    async def start_scan(self, mode='auto'):
        """
        Modes:
        - auto: Smart scan with pauses
        - fast: No pauses (use carefully!)
        - single: One config only
        """
        await self.send_message("🚀 Starting scan...")
        
        # Start in background with status updates
        self.scan_task = asyncio.create_task(
            self.run_scan(mode)
        )
        
        # Send updates every 10 minutes
        while not self.scan_task.done():
            status = await self.get_status()
            await self.send_message(f"📊 Progress: {status}")
            await asyncio.sleep(600)
    
    async def pause_scan(self):
        """Gracefully pause current scan"""
        self.pause_flag.set()
        await self.send_message("⏸️ Scan paused, waiting for current config to finish...")
    
    async def health_check(self):
        """Send Pi health stats"""
        stats = {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'temp': get_cpu_temp(),
            'disk': psutil.disk_usage('/').percent
        }
        
        msg = f"""
🏥 Pi Health Report:
├─ CPU: {stats['cpu']:.1f}%
├─ RAM: {stats['ram']:.1f}%
├─ Temp: {stats['temp']:.1f}°C
└─ Disk: {stats['disk']:.1f}%
        """
        await self.send_message(msg)
```

---

## 🚀 IMPLEMENTATION PRIORITY

### Phase 1: IMMEDIATE (After Pi restart)
1. ✅ Add Docker resource limits
2. ✅ Stop auto-restart of comprehensive scan
3. ✅ Create health check script
4. ✅ Add temperature monitoring

### Phase 2: SHORT-TERM (This week)
1. ✅ Implement Telegram control system
2. ✅ Refactor scan to batch mode with pauses
3. ✅ Add manual start/stop commands
4. ✅ Create status dashboard

### Phase 3: LONG-TERM (Optional)
1. ⏳ Web dashboard for monitoring
2. ⏳ Email alerts
3. ⏳ Automatic backup system
4. ⏳ Multi-Pi load balancing

---

## 📝 MANUAL RESTART CHECKLIST

When you physically restart the Pi:

```bash
# 1. Check system health
uptime
free -h
df -h
vcgencmd measure_temp

# 2. Check what was running
docker ps -a
docker logs emlak-scraper-101evler --tail 100

# 3. Check for crash logs
dmesg | tail -50
journalctl -xe | tail -50

# 4. Stop auto-start scanners
docker compose down

# 5. Start only Telegram bot
docker compose up -d telegram-bot

# 6. Verify health
docker stats --no-stream
```

---

## 🎯 SUCCESS METRICS

**Before**: 
- Pi crashes during scans
- SSH becomes unresponsive
- No control over running processes
- Other projects affected

**After**:
- Pi runs 24/7 stable
- SSH always responsive
- Full control via Telegram
- Other projects unaffected
- Predictable resource usage

---

## 📞 EMERGENCY CONTACTS

If Pi becomes unresponsive:
1. Physical restart (power cycle)
2. Check router for Pi IP
3. Check physical connections
4. Check power supply (5V 3A minimum for Pi5)
5. Check SD card health

---

## 🔗 RELATED FILES

- `docker-compose.yml` - Resource limits
- `scripts/control/telegram_controller.py` - Telegram commands
- `scripts/monitoring/health_monitor.py` - Health checks
- `scripts/scan/smart_scan_v2.py` - Batch mode scanner
- `logs/pi_health.log` - Health log history

---

**Last Updated**: November 9, 2025
**Status**: 🚨 Pi crashed - awaiting restart
**Next Action**: Physical restart + implement protections

#!/usr/bin/env python3
"""
Thermal Manager for Raspberry Pi 5
Monitors temperature and throttles scraper to prevent overheating
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Configuration
TEMP_CHECK_INTERVAL = 30  # seconds
MAX_TEMP = 65.0  # Celsius - pause scraping above this
RESUME_TEMP = 60.0  # Celsius - resume scraping below this
CRITICAL_TEMP = 75.0  # Emergency stop

STATE_FILE = Path("/app/data/control/thermal_state.json")
COMMAND_FILE = Path("/app/data/control/commands.json")

def get_cpu_temp():
    """Get CPU temperature from Pi"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Output: temp=63.7'C
        temp_str = result.stdout.strip().split("=")[1].replace("'C", "")
        return float(temp_str)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return 0.0

def get_cpu_freq():
    """Get current CPU frequency"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_clock", "arm"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Output: frequency(0)=2400030464
        freq_hz = int(result.stdout.strip().split("=")[1])
        return freq_hz / 1_000_000  # Convert to MHz
    except:
        return 0

def set_cpu_governor(governor="powersave"):
    """Set CPU frequency governor"""
    try:
        subprocess.run(
            ["sudo", "cpufreq-set", "-g", governor],
            capture_output=True,
            timeout=5
        )
        return True
    except:
        return False

def pause_scraper():
    """Send pause command to scraper"""
    try:
        commands = {"action": "pause", "timestamp": datetime.now().isoformat()}
        COMMAND_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COMMAND_FILE, "w") as f:
            json.dump(commands, f)
        print(f"🛑 PAUSED scraper due to high temperature")
        return True
    except Exception as e:
        print(f"Error pausing scraper: {e}")
        return False

def resume_scraper():
    """Send resume command to scraper"""
    try:
        commands = {"action": "resume", "timestamp": datetime.now().isoformat()}
        with open(COMMAND_FILE, "w") as f:
            json.dump(commands, f)
        print(f"▶️  RESUMED scraper - temperature normalized")
        return True
    except Exception as e:
        print(f"Error resuming scraper: {e}")
        return False

def emergency_stop():
    """Emergency stop all scraping"""
    try:
        commands = {"action": "stop", "timestamp": datetime.now().isoformat()}
        with open(COMMAND_FILE, "w") as f:
            json.dump(commands, f)
        print(f"🚨 EMERGENCY STOP - Critical temperature!")
        return True
    except:
        return False

def update_state(temp, freq, status):
    """Update thermal state file"""
    try:
        state = {
            "temperature": temp,
            "cpu_freq_mhz": freq,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error updating state: {e}")

def main():
    """Main monitoring loop"""
    print("🌡️  Thermal Manager Started")
    print(f"Max temp: {MAX_TEMP}°C | Resume: {RESUME_TEMP}°C | Critical: {CRITICAL_TEMP}°C")
    print(f"Check interval: {TEMP_CHECK_INTERVAL}s\n")
    
    is_paused = False
    
    while True:
        try:
            temp = get_cpu_temp()
            freq = get_cpu_freq()
            
            # Determine status and action
            if temp >= CRITICAL_TEMP:
                status = "CRITICAL"
                emergency_stop()
                print(f"🚨 {temp:.1f}°C - CRITICAL! Emergency stop triggered")
                
            elif temp >= MAX_TEMP and not is_paused:
                status = "HOT"
                pause_scraper()
                is_paused = True
                print(f"🔥 {temp:.1f}°C ({freq:.0f}MHz) - Too hot, paused")
                
            elif temp <= RESUME_TEMP and is_paused:
                status = "NORMAL"
                resume_scraper()
                is_paused = False
                print(f"✅ {temp:.1f}°C ({freq:.0f}MHz) - Cooled down, resumed")
                
            elif is_paused:
                status = "COOLING"
                print(f"❄️  {temp:.1f}°C ({freq:.0f}MHz) - Cooling... (target: {RESUME_TEMP}°C)")
                
            else:
                status = "NORMAL"
                print(f"✓  {temp:.1f}°C ({freq:.0f}MHz) - Normal operation")
            
            update_state(temp, freq, status)
            time.sleep(TEMP_CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Thermal manager stopped")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(TEMP_CHECK_INTERVAL)

if __name__ == "__main__":
    main()

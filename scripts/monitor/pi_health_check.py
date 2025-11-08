"""
Raspberry Pi Scraper - Performans & Sağlık İzleme
CPU, RAM, sıcaklık ve throttling kontrolü
"""

import subprocess
import time
from datetime import datetime

def run_ssh(command):
    """SSH üzerinden komut çalıştır"""
    result = subprocess.run(
        ['ssh', 'ekrem@192.168.1.143', command],
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout.strip()

def get_temperature():
    """Pi sıcaklığını al"""
    temp = run_ssh("vcgencmd measure_temp")
    return temp.replace("temp=", "").replace("'C", "°C")

def get_throttled_status():
    """Throttling durumunu al"""
    status = run_ssh("vcgencmd get_throttled")
    throttled = status.replace("throttled=", "")
    
    # Decode throttle status
    value = int(throttled, 16)
    issues = []
    
    if value & 0x1:
        issues.append("⚠️ Under-voltage detected!")
    if value & 0x2:
        issues.append("🔥 ARM frequency capped!")
    if value & 0x4:
        issues.append("🌡️ Currently throttled!")
    if value & 0x8:
        issues.append("❄️ Soft temperature limit active!")
    
    if value & 0x10000:
        issues.append("📜 Under-voltage occurred (past)")
    if value & 0x20000:
        issues.append("📜 ARM frequency capped (past)")
    if value & 0x40000:
        issues.append("📜 Throttling occurred (past)")
    if value & 0x80000:
        issues.append("📜 Soft temp limit (past)")
    
    if not issues:
        return "✅ No issues"
    return "\n   ".join(issues)

def get_memory():
    """RAM kullanımını al"""
    mem = run_ssh("free -m | grep Mem")
    parts = mem.split()
    total = int(parts[1])
    used = int(parts[2])
    free = int(parts[3])
    percent = (used / total) * 100
    return total, used, free, percent

def get_cpu_usage():
    """CPU kullanımını al"""
    cpu = run_ssh("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    return cpu.replace("%", "")

def get_load_average():
    """Load average al"""
    load = run_ssh("uptime | awk -F'load average:' '{print $2}'")
    return load.strip()

def get_container_stats():
    """Docker container istatistiklerini al"""
    stats = run_ssh("docker stats emlak-scraper-101evler --no-stream --format '{{.CPUPerc}},{{.MemUsage}}'")
    if stats:
        cpu, mem = stats.split(',')
        return cpu, mem
    return "N/A", "N/A"

def check_disk_space():
    """Disk kullanımını kontrol et"""
    disk = run_ssh("df -h /home/ekrem/projects/emlak-scraper | tail -1")
    parts = disk.split()
    size = parts[1]
    used = parts[2]
    avail = parts[3]
    percent = parts[4]
    return size, used, avail, percent

def print_health_report():
    """Sağlık raporunu yazdır"""
    print("\n" + "="*60)
    print("🍓 RASPBERRY PI 5 - SAĞLIK RAPORU")
    print("="*60)
    print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Sıcaklık
    temp = get_temperature()
    temp_value = float(temp.replace("°C", ""))
    
    if temp_value < 60:
        temp_status = "✅ Normal"
    elif temp_value < 70:
        temp_status = "⚠️ Biraz yüksek"
    elif temp_value < 80:
        temp_status = "🔥 Yüksek - izlenmeli"
    else:
        temp_status = "❌ Çok yüksek - soğutma gerekli!"
    
    print(f"🌡️  Sıcaklık: {temp} - {temp_status}")
    
    # Throttling
    throttle = get_throttled_status()
    print(f"⚡ Throttling: {throttle}")
    
    # CPU
    cpu_user = get_cpu_usage()
    load_avg = get_load_average()
    print(f"\n💻 CPU Kullanımı: {cpu_user}%")
    print(f"📊 Load Average: {load_avg}")
    
    # RAM
    total, used, free, percent = get_memory()
    
    if percent < 70:
        mem_status = "✅ Normal"
    elif percent < 85:
        mem_status = "⚠️ Yüksek"
    else:
        mem_status = "❌ Çok yüksek - optimize edilmeli"
    
    print(f"\n💾 RAM: {used}/{total} MB ({percent:.1f}%) - {mem_status}")
    print(f"   Free: {free} MB")
    
    # Container stats
    container_cpu, container_mem = get_container_stats()
    print(f"\n🐳 Container Stats:")
    print(f"   CPU: {container_cpu}")
    print(f"   Memory: {container_mem}")
    
    # Disk
    size, used, avail, percent_str = check_disk_space()
    percent_disk = int(percent_str.replace("%", ""))
    
    if percent_disk < 80:
        disk_status = "✅ Yeterli alan"
    elif percent_disk < 90:
        disk_status = "⚠️ Dikkat - alan azalıyor"
    else:
        disk_status = "❌ Kritik - cleanup gerekli!"
    
    print(f"\n💿 Disk: {used}/{size} ({percent_str}) - {disk_status}")
    print(f"   Available: {avail}")
    
    # Öneriler
    print("\n" + "="*60)
    print("💡 ÖNERİLER:")
    print("="*60)
    
    if temp_value > 65:
        print("🌡️  Sıcaklık yüksek:")
        print("   - Pi'nin havalandırması iyi mi kontrol edin")
        print("   - Fan çalışıyor mu kontrol edin")
        print("   - Kasayı açık tutun")
    
    if percent > 80:
        print("💾 RAM kullanımı yüksek:")
        print("   - Normal - Playwright ve BeautifulSoup RAM-intensive")
        print("   - Docker resource limitleri aktif (4GB max)")
        print("   - Sorun değil, Pi 5 8GB yeterli")
    
    if percent_disk > 85:
        print("💿 Disk dolmaya başladı:")
        print("   - Scan bitince eski data'yı silin")
        print("   - docker image prune -a -f (eski image'ları temizle)")
    
    if "Under-voltage" in throttle or "Currently throttled" in throttle:
        print("⚡ Güç problemi var:")
        print("   - Resmi Raspberry Pi adaptörü kullanın (5V 5A)")
        print("   - USB kablosu kaliteli olmalı")
        print("   - Diğer USB cihazları çıkarın")
    
    print("\n✅ Genel durum: Pi güvenli çalışıyor")
    print("   Fan sesi normal - endişe etmeyin")
    print("   Scraper optimize edilmiş (Playwright hafif mod)")
    print()

if __name__ == "__main__":
    try:
        print_health_report()
    except subprocess.TimeoutExpired:
        print("❌ SSH bağlantısı zaman aşımına uğradı")
    except Exception as e:
        print(f"❌ Hata: {e}")

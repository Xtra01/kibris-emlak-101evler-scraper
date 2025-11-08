"""
FINAL SETUP - Raspberry Pi Notification System
===============================================
Scan bitince bu scripti çalıştırın:
1. Container restart eder
2. Notification sistemi aktif olur
3. Sonraki scan'lerde bildirimler çalışacak
"""

import subprocess
import time

PI_HOST = "ekrem@192.168.1.143"

def run_ssh(command):
    """SSH komutu çalıştır"""
    result = subprocess.run(
        ['ssh', PI_HOST, command],
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.returncode

print("\n" + "="*60)
print("🍓 RASPBERRY PI - NOTIFICATION SYSTEM FINAL SETUP")
print("="*60)
print()

# 1. Dosya sayısını kontrol et
print("📊 1. Dosya sayısı kontrol ediliyor...")
count, _ = run_ssh("find /home/ekrem/projects/emlak-scraper/data/raw/listings -name '*.html' 2>/dev/null | wc -l")
print(f"   ✅ {count} HTML dosya toplandı")
print()

# 2. Container durumunu kontrol et
print("🐳 2. Container durumu kontrol ediliyor...")
status, _ = run_ssh("docker ps --filter name=emlak-scraper-101evler --format '{{.Status}}'")
print(f"   ℹ️  Durum: {status}")
print()

# 3. Git pull
print("📥 3. Son kod değişiklikleri çekiliyor...")
output, code = run_ssh("cd /home/ekrem/projects/emlak-scraper && git pull")
if code == 0:
    print("   ✅ Git pull başarılı")
else:
    print(f"   ⚠️  Git pull: {output}")
print()

# 4. Docker compose güncelle
print("🔄 4. Docker compose güncelleniyor...")
run_ssh("cd /home/ekrem/projects/emlak-scraper && docker cp docker-compose.yml emlak-scraper-101evler:/app/docker-compose.yml")
print("   ✅ docker-compose.yml güncellendi")
print()

# 5. Notifications.py kopyala
print("🔔 5. Notification modülü güncelleniyor...")
run_ssh("docker cp /home/ekrem/projects/emlak-scraper/src/emlak_scraper/notifications.py emlak-scraper-101evler:/app/src/emlak_scraper/notifications.py")
print("   ✅ notifications.py güncellendi")
print()

# 6. .env dosyasını kopyala
print("⚙️  6. .env dosyası kontrol ediliyor...")
env_check, _ = run_ssh("test -f /home/ekrem/projects/emlak-scraper/.env && echo 'exists' || echo 'missing'")
if 'exists' in env_check:
    run_ssh("docker cp /home/ekrem/projects/emlak-scraper/.env emlak-scraper-101evler:/app/.env")
    print("   ✅ .env dosyası güncellendi")
else:
    print("   ⚠️  .env dosyası Pi'de bulunamadı!")
    print("   👉 Lokal .env'i kopyalayın:")
    print("      scp .env ekrem@192.168.1.143:/home/ekrem/projects/emlak-scraper/")
print()

# 7. Container restart
print("🔄 7. Container restart ediliyor...")
print("   ⚠️  Mevcut scan duracak!")
response = input("   Devam etmek istiyor musunuz? (y/N): ")

if response.lower() == 'y':
    print("   🛑 Container durduruluyor...")
    run_ssh("docker stop emlak-scraper-101evler")
    time.sleep(2)
    
    print("   🚀 Container başlatılıyor...")
    run_ssh("cd /home/ekrem/projects/emlak-scraper && docker-compose up -d")
    time.sleep(3)
    
    # Durum kontrol
    status, _ = run_ssh("docker ps --filter name=emlak-scraper-101evler --format '{{.Status}}'")
    print(f"   ✅ Yeni durum: {status}")
    print()
    
    # Test mesajı gönder
    print("📱 8. Telegram test mesajı gönderiliyor...")
    test_output, test_code = run_ssh(
        "docker exec emlak-scraper-101evler python3 -c \""
        "from emlak_scraper.notifications import get_notifier; "
        "n = get_notifier(); "
        "n.send_telegram('🍓 *Notification Sistemi Aktif!*\\\\n\\\\n"
        "✅ Raspberry Pi restart tamamlandı\\\\n"
        "🔔 Bildirimler çalışıyor\\\\n\\\\n"
        "_Sonraki scan\\'lerde otomatik bildirim alacaksınız_')\""
    )
    
    if test_code == 0:
        print("   ✅ Test mesajı gönderildi!")
        print("   👉 Telegram'dan kontrol edin")
    else:
        print(f"   ⚠️  Test mesajı başarısız: {test_output}")
    print()
    
    print("="*60)
    print("🎉 KURULUM TAMAMLANDI!")
    print("="*60)
    print()
    print("📌 Sonraki Adımlar:")
    print("   1. Yeni bir scan başlatın:")
    print("      ssh ekrem@192.168.1.143")
    print("      cd ~/projects/emlak-scraper")
    print("      docker-compose up -d")
    print()
    print("   2. Telegram'dan bildirimleri takip edin:")
    print("      - Scan başlangıcı")
    print("      - Her 5 config'de ilerleme")
    print("      - Hata bildirimleri")
    print("      - Scan tamamlanma raporu")
    print()
    print("   3. Monitoring:")
    print("      .\\scripts\\monitor\\check_pi_status.ps1 -Continuous")
    print()
else:
    print("   ❌ İptal edildi")
    print()
    print("💡 Not: Mevcut scan bitince tekrar çalıştırın:")
    print("   python scripts/test/setup_pi_notifications.py")
    print()

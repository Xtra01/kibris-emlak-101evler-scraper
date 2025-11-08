# 🔔 Notification System - Kullanım Kılavuzu

## 📋 Genel Bakış

KKTC Emlak Scraper'a **Telegram** ve **Email** üzerinden gerçek zamanlı bildirimler eklendi.

**Bildirim Tipleri:**
- ✅ Scan başladığında (tek sefer)
- 📊 Her 5 config tamamlandığında (ilerleme güncellemesi)
- ❌ Hata oluştuğunda
- 🎉 Tüm scan tamamlandığında (detaylı rapor)

## 🚀 Hızlı Başlangıç

### 1. Telegram Bot Kurulumu (5 dakika)

#### Adım 1.1: Bot Oluştur
1. Telegram'da [@BotFather](https://t.me/BotFather) ile konuşma aç
2. `/newbot` komutunu gönder
3. Bot için isim ver: "KKTC Emlak Monitor"
4. Bot için username ver: `kktc_emlak_bot` (unique olmalı)
5. **Bot Token**'ı kaydet (örnek: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Adım 1.2: Chat ID Bul
1. Telegram'da [@userinfobot](https://t.me/userinfobot) ile konuşma aç
2. `/start` komutunu gönder
3. **Chat ID**'ni kaydet (örnek: `123456789`)

### 2. Gmail SMTP Kurulumu (3 dakika)

#### Adım 2.1: App Password Oluştur
1. Gmail hesabında 2FA (2-Step Verification) aktif olmalı
2. [Google App Passwords](https://myaccount.google.com/apppasswords) sayfasına git
3. "Select app" → "Mail"
4. "Select device" → "Other (Custom name)" → "KKTC Scraper"
5. **App Password**'ü kaydet (örnek: `abcd efgh ijkl mnop`)

⚠️ **ÖNEMLİ:** Normal Gmail şifrenizi KULLANMAYIN! App Password kullanın.

### 3. Konfigürasyon Dosyası (2 dakika)

`.env` dosyası oluşturun (root dizinde):

```bash
# Windows PowerShell
Copy-Item .env.example .env
notepad .env

# Linux/Mac
cp .env.example .env
nano .env
```

`.env` içeriği:
```ini
# ============================================
# TELEGRAM CONFIGURATION
# ============================================
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# ============================================
# EMAIL CONFIGURATION
# ============================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sizin-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
NOTIFY_EMAIL=hedef-email@example.com

# ============================================
# NOTIFICATION SETTINGS
# ============================================
ENABLE_TELEGRAM=true
ENABLE_EMAIL=true
NOTIFY_ON_START=true
NOTIFY_ON_COMPLETE=true
NOTIFY_ON_ERROR=true
NOTIFY_EVERY_N_CONFIGS=5
```

### 4. Test Et (1 dakika)

```python
# Test scripti
from emlak_scraper import notifications

notifier = notifications.get_notifier()

# Test Telegram
notifier.send_telegram("✅ Test mesajı - Telegram çalışıyor!")

# Test Email
notifier.send_email(
    subject="✅ Test Email",
    body="Email bildirimleri aktif!",
    html=False
)
```

## 📱 Örnek Bildirimler

### Scan Başladı (Telegram)
```
🚀 Scan Started

📊 Total configs: 72
🕐 Time: 2024-01-20 22:30:15
🍓 Host: Raspberry Pi 5

Monitoring in progress...
```

### İlerleme Güncellemesi (Her 5 Config)
```
✅ Progress Update

📍 Latest: Girne-Satilik-Villa
📄 Files: 1,245
📊 Progress: 20/72 configs
⏱️ Duration: 12.5 min
🕐 23:42:30
```

### Hata Bildirimi
```
❌ Config Failed

📍 Config: Lefke-Kiralik-Ev
⚠️ Error: 404 Not Found
📊 Progress: 35/72
🕐 00:15:45

Continuing with next config...
```

### Scan Tamamlandı (Email - HTML)
```html
🎉 Scan Completed Successfully!

📊 Statistics
Total Configs:     72
Completed:         68 ✅
Failed:            4 ❌
Total Files:       18,543
Data Size:         2,347.8 MB
Duration:          45.2 minutes
Completion Time:   2024-01-20 23:15:30

🎬 Next Steps
1. Download data from Raspberry Pi
2. Run HTML parser to generate CSV
3. Verify data quality
4. Export to Excel
```

## ⚙️ Gelişmiş Ayarlar

### Bildirimleri Kapat/Aç

```ini
# Sadece Telegram kullan
ENABLE_TELEGRAM=true
ENABLE_EMAIL=false

# Sadece Email kullan
ENABLE_TELEGRAM=false
ENABLE_EMAIL=true

# Hata bildirimleri kapat
NOTIFY_ON_ERROR=false

# Her 10 config'de bildir (daha az spam)
NOTIFY_EVERY_N_CONFIGS=10
```

### Farklı SMTP Servisleri

#### SendGrid (100 email/day ücretsiz)
```ini
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
```

#### Mailgun (5000 email/month ücretsiz)
```ini
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-smtp-password
```

#### Outlook/Hotmail
```ini
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=sizin-email@outlook.com
SMTP_PASSWORD=your-password
```

## 🛠️ Sorun Giderme

### ❌ Telegram Token Hatası
**Hata:** `Telegram API error: 401 - Unauthorized`

**Çözüm:**
- Bot token'ı doğru kopyaladığınızdan emin olun
- Token'da boşluk/satır sonu karakteri olmasın
- [@BotFather](https://t.me/BotFather) ile yeni token oluşturun

### ❌ Telegram Chat ID Hatası
**Hata:** `Telegram API error: 400 - Bad Request: chat not found`

**Çözüm:**
- Chat ID'yi [@userinfobot](https://t.me/userinfobot) ile kontrol edin
- Önce botunuzla `/start` komutu gönderin
- Group chat kullanıyorsanız chat ID eksi (-) işaretiyle başlar

### ❌ Gmail SMTP Hatası
**Hata:** `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`

**Çözüm:**
- Normal Gmail şifrenizi KULLANMAYIN
- App Password oluşturun (2FA gerekli)
- App Password'ü boşluksuz girin: `abcdefghijklmnop`

### ❌ Email Gönderme Hatası
**Hata:** `SMTPSenderRefused` veya `Connection refused`

**Çözüm:**
- SMTP_HOST ve SMTP_PORT doğru mu kontrol edin
- Firewall port 587'yi engelliyor mu?
- Gmail "Less secure app access" ayarını kontrol edin

### ⚠️ Bildirimler Gelmiyor
**Kontrol Listesi:**
1. `.env` dosyası root dizinde mi?
2. `ENABLE_TELEGRAM` ve `ENABLE_EMAIL` `true` olarak ayarlı mı?
3. Terminal loglarında "Notification failed" mesajı var mı?
4. `python-dotenv` ve `requests` kurulu mu?

**Debug Mode:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from emlak_scraper import notifications
notifier = notifications.get_notifier()
notifier.send_telegram("Test")
```

## 📊 Rate Limiting

### Telegram
- **Limit:** 30 mesaj/saniye (API limit)
- **Korunma:** 1 saniye bekleme süresi (kod içinde)
- **Önerilen:** `NOTIFY_EVERY_N_CONFIGS=5` (spam önleme)

### Gmail
- **Limit:** 500 email/gün
- **Korunma:** Batch bildirimleri (her 5 config)
- **Önerilen:** Sadece başlangıç ve bitiş bildirimleri için email kullanın

## 🔒 Güvenlik

### ✅ Yapılması Gerekenler
- `.env` dosyasını **asla** GitHub'a eklemeyin
- `.gitignore` içinde `.env` olduğundan emin olun
- App Password kullanın (Gmail için)
- Token'ları kimseyle paylaşmayın

### ❌ Yapılmaması Gerekenler
- Normal Gmail şifrenizi KULLANMAYIN
- Token'ları kod içine yazMAYIN
- Public repository'de `.env` yayınlaMAYIN

## 📦 Raspberry Pi'ye Deploy

### Adım 1: .env Dosyasını Kopyala
```powershell
# Windows'tan Pi'ye kopyala
scp .env ekrem@192.168.1.143:/home/ekrem/projects/emlak-scraper/
```

### Adım 2: Python-dotenv Kur
```bash
# Pi'de
ssh ekrem@192.168.1.143
cd ~/projects/emlak-scraper
pip install python-dotenv
```

### Adım 3: Test Et
```bash
# Pi'de test
python3 -c "
from emlak_scraper import notifications
notifier = notifications.get_notifier()
notifier.send_telegram('✅ Pi notification test!')
"
```

### Adım 4: Docker ile Çalıştır
```bash
# Docker container'a .env ekle
docker cp .env emlak-scraper-101evler:/app/.env

# Container'ı restart et
docker restart emlak-scraper-101evler
```

## 📖 API Referansı

### NotificationManager

```python
from emlak_scraper.notifications import get_notifier

notifier = get_notifier()

# Scan başlangıcı
notifier.notify_scan_started(total_configs=72)

# Config tamamlandı
notifier.notify_config_completed(
    config_name="Girne-Satilik-Villa",
    file_count=1245,
    completed=20,
    total=72,
    duration=750.5  # seconds
)

# Config başarısız
notifier.notify_config_failed(
    config_name="Lefke-Kiralik-Ev",
    error="404 Not Found",
    completed=35,
    total=72
)

# Scan tamamlandı
notifier.notify_scan_finished({
    'total_configs': 72,
    'completed': 68,
    'failed': 4,
    'total_files': 18543,
    'data_size_mb': 2347.8,
    'duration_minutes': 45.2
})

# Disk uyarısı
notifier.notify_disk_warning(
    usage_percent=85,
    available_gb=5.2
)
```

### Direkt Kullanım (Kısayollar)

```python
from emlak_scraper import notifications

# Daha kısa syntax
notifications.notify_scan_started(72)
notifications.notify_config_completed("Girne-Satilik-Villa", 1245, 20, 72, 750.5)
notifications.notify_config_failed("Lefke-Kiralik-Ev", "404 Not Found", 35, 72)
notifications.notify_scan_finished({...})
notifications.notify_disk_warning(85, 5.2)
```

## 💰 Maliyet

| Servis | Ücretsiz Limit | Fiyat (Aşım) |
|--------|---------------|--------------|
| Telegram Bot API | Sınırsız | $0 |
| Gmail SMTP | 500 email/gün | $0 (limit dahilinde) |
| SendGrid | 100 email/gün | $19.95/ay (40K email) |
| Mailgun | 5000 email/ay | $35/ay (50K email) |

**Önerilen:** Telegram (ücretsiz + sınırsız)

## 📚 Ek Kaynaklar

- [Telegram Bot API Docs](https://core.telegram.org/bots/api)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Python-dotenv Docs](https://pypi.org/project/python-dotenv/)
- [SMTP Configuration Examples](https://github.com/topics/smtp-configuration)

## 🆘 Destek

**Sorun mu yaşıyorsunuz?**
1. Log dosyasını kontrol edin: `logs/comprehensive_scan_YYYYMMDD.log`
2. Debug mode ile test edin (yukarıdaki örnekler)
3. `.env` dosyasındaki değerleri doğrulayın
4. Firewall/antivirus port 587'yi engelliyor mu?

**Hala çözülmedi mi?**
- GitHub Issues açın
- Log dosyasını (token'ları silerek) paylaşın
- Hata mesajını tam olarak kopyalayın

# 🔔 NOTIFICATION SYSTEM RESEARCH REPORT

## Araştırma Tarihi: 8 Kasım 2025

---

## 📋 GEREKSİNİMLER

1. **Telegram Bildirimleri** - Real-time push notifications
2. **E-posta Bildirimleri** - Detaylı raporlar için
3. **Olay Tetikleyicileri:**
   - Config başladığında
   - Config tamamlandığında
   - Hata oluştuğunda
   - Scan tamamlandığında
   - Disk %80 dolduğunda

---

## 🔍 ARAŞTIRMA: TELEGRAM BOT API

### Resmi Dokümantasyon
- **URL:** https://core.telegram.org/bots/api
- **Güvenilirlik:** ⭐⭐⭐⭐⭐ (Official Telegram)

### Temel Özellikler
```
✅ sendMessage - Text mesajları
✅ sendPhoto - Görsel + caption
✅ sendDocument - File gönderme
✅ Markdown/HTML formatting
✅ Rate limit: 30 msg/sec
✅ Ücretsiz!
```

### Entegrasyon Adımları

#### 1. Bot Oluşturma
```
1. Telegram'da @BotFather'ı ara
2. /newbot komutunu gönder
3. Bot adı belirle: "KKTC Emlak Scraper Bot"
4. Username belirle: @kktc_emlak_scraper_bot
5. Token al: 7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5YOUhHq1c (örnek)
```

#### 2. Chat ID Alma
```
1. Bot'a /start mesajı gönder
2. URL'ye git: https://api.telegram.org/bot<TOKEN>/getUpdates
3. "chat":{"id":123456789} değerini not al
```

#### 3. Python Kütüphaneleri
```python
# Seçenek 1: python-telegram-bot (Önerilen)
pip install python-telegram-bot==20.7

# Seçenek 2: requests (Minimal)
pip install requests
```

---

## 📧 ARAŞTIRMA: E-POSTA GÖNDERİMİ

### Python smtplib (Built-in)
- **Dokümantasyon:** https://docs.python.org/3/library/smtplib.html
- **Güvenilirlik:** ⭐⭐⭐⭐⭐ (Python Standard Library)

### Gmail SMTP Ayarları
```
Server: smtp.gmail.com
Port: 587 (TLS) veya 465 (SSL)
Auth: App Password (2FA gerekli)
Rate Limit: 500 email/day (ücretsiz)
```

### Alternatif Servisler
1. **SendGrid** - 100 email/day (free tier)
2. **Mailgun** - 5000 email/month (free tier)
3. **AWS SES** - 62,000 email/month (free tier - 1 yıl)

---

## 🏗️ MİMARİ TASARIM

### Notification Flow

```
┌─────────────────────────────────────────────────────────┐
│           RASPBERRY PI 5 - SCRAPER                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  comprehensive_full_scan.py                        │  │
│  │                                                     │  │
│  │  Events:                                           │  │
│  │  • config_started(city, category)                 │  │
│  │  • config_completed(city, category, count)        │  │
│  │  • config_failed(city, category, error)           │  │
│  │  • scan_finished(total_files, duration)           │  │
│  └─────────────┬───────────────────────────────────────┘  │
│                │                                           │
│                ▼                                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │  notifications.py                                  │   │
│  │  (Notification Manager)                            │   │
│  │                                                     │   │
│  │  • Queue events                                    │   │
│  │  • Rate limiting                                   │   │
│  │  • Retry logic                                     │   │
│  │  • Format messages                                 │   │
│  └─────────┬──────────────┬───────────────────────────┘   │
│            │              │                                │
└────────────┼──────────────┼────────────────────────────────┘
             │              │
             ▼              ▼
    ┌────────────────┐  ┌────────────────┐
    │  TELEGRAM BOT  │  │  EMAIL SMTP    │
    │                │  │                │
    │  • Instant     │  │  • Detailed    │
    │  • Mobile push │  │  • Attachments │
    │  • Interactive │  │  • HTML format │
    └────────────────┘  └────────────────┘
```

---

## 📝 ÖRNEK MESAJLAR

### Telegram Mesajı (Markdown)
```markdown
🚀 *Scan Started*

📍 Config: Girne - Satılık Daire
🕐 Time: 2025-11-08 22:30:45
🎯 Target: ~900 listings

_Monitoring on Pi..._
```

### E-posta (HTML)
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; }
        .success { color: green; }
        .error { color: red; }
        .stats { background: #f0f0f0; padding: 10px; }
    </style>
</head>
<body>
    <h2>✅ Scan Completed</h2>
    <div class="stats">
        <p><strong>Duration:</strong> 45 minutes</p>
        <p><strong>Files:</strong> 18,234 HTML files</p>
        <p><strong>Size:</strong> 1.2 GB</p>
    </div>
    <p>Download: <a href="...">Click here</a></p>
</body>
</html>
```

---

## ⚙️ KONFIGÜRASYON

### .env Dosyası
```ini
# Telegram
TELEGRAM_BOT_TOKEN=7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5YOUhHq1c
TELEGRAM_CHAT_ID=123456789

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFY_EMAIL=recipient@example.com

# Notification settings
ENABLE_TELEGRAM=true
ENABLE_EMAIL=true
NOTIFY_ON_START=true
NOTIFY_ON_COMPLETE=true
NOTIFY_ON_ERROR=true
NOTIFY_EVERY_N_CONFIGS=5  # Her 5 config'de bir bildir
```

---

## 🛡️ GÜVENLİK ÖNERİLERİ

1. **Token'ları GİZLE:**
   - ✅ .env dosyası kullan
   - ✅ .gitignore'a ekle
   - ❌ Kod içine hard-code YAPMA

2. **Rate Limiting:**
   - Telegram: Max 30 msg/sec
   - Gmail: Max 500 email/day
   - Batch notifications (her config yerine her 5 config)

3. **Error Handling:**
   - Network timeout (5 saniye)
   - Retry 3 kez
   - Silent fail (scraper'ı durdurma)

---

## 📦 PAKET GEREKSİNİMLERİ

```txt
# requirements-notifications.txt
python-telegram-bot==20.7
requests==2.31.0
python-dotenv==1.0.0

# Email için built-in: smtplib, email
```

---

## 🎯 UYGULAMA PLANI

### Aşama 1: Temel Notification Manager (15 dk)
- [ ] `notifications.py` oluştur
- [ ] Telegram send_message fonksiyonu
- [ ] Email send_email fonksiyonu
- [ ] .env config yükle

### Aşama 2: Scraper Entegrasyonu (10 dk)
- [ ] comprehensive_full_scan.py'ye import ekle
- [ ] config_started event
- [ ] config_completed event
- [ ] config_failed event
- [ ] scan_finished event

### Aşama 3: Test (5 dk)
- [ ] Telegram bot test
- [ ] Email test
- [ ] Pi'de test run

### Aşama 4: Deployment (5 dk)
- [ ] .env.example güncelle
- [ ] README güncelle
- [ ] Git push

**TOPLAM SÜRE:** ~35 dakika

---

## 📚 KAYNAKLAR

1. **Telegram Bot API**
   - Official: https://core.telegram.org/bots/api
   - python-telegram-bot: https://python-telegram-bot.org/

2. **Python Email**
   - smtplib docs: https://docs.python.org/3/library/smtplib.html
   - Gmail SMTP: https://support.google.com/mail/answer/7126229

3. **Best Practices**
   - 12-Factor App: https://12factor.net/config
   - Python dotenv: https://github.com/theskumar/python-dotenv

---

## ✅ SONUÇ

**Önerilen Çözüm:**
1. ✅ Telegram Bot (Instant notifications)
2. ✅ Gmail SMTP (Detailed reports)
3. ✅ python-telegram-bot kütüphanesi
4. ✅ Built-in smtplib (email için)
5. ✅ .env configuration

**Avantajlar:**
- 🆓 Tamamen ücretsiz
- 🚀 Kolay kurulum
- 📱 Mobile push (Telegram)
- 📊 Detaylı raporlar (Email)
- 🔒 Güvenli (.env ile)

**Toplam Maliyet:** $0
**Kurulum Süresi:** ~35 dakika
**Bakım:** Minimal (self-hosted)

---

**Hazırlayan:** Claude Sonnet 4.5  
**Tarih:** 8 Kasım 2025

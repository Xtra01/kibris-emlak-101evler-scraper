# 🤖 Interactive Telegram Bot - Kullanım Kılavuzu

## 📋 Özellikler

### 1. İnteraktif Komutlar (24/7 Erişim)

Bot'a Telegram'dan komut göndererek Pi'nin durumunu kontrol edebilirsiniz:

| Komut | Açıklama | Örnek |
|-------|----------|-------|
| `/start` | Bot'u başlat | Hoş geldin mesajı |
| `/help` | Komut listesi | Tüm komutlar |
| `/status` | Scan durumu | Tamamlanan/Kalan configler |
| `/progress` | Detaylı ilerleme | Progress bar + yüzde |
| `/files` | Toplanan dosyalar | Dosya sayısı + boyut + konum |
| `/disk` | Disk kullanımı | Kullanılan/Serbest alan |
| `/health` | Sistem sağlığı | CPU, RAM, sıcaklık |

### 2. Otomatik Bildirimler

#### Her Config Tamamlandığında (72 config = 72 bildirim)
```
✅ Config Tamamlandı!

📍 Girne-Satilik-Villa
📄 Dosya: 1,245 HTML
💾 Konum: /app/data/raw/listings/

📊 İlerleme:
███████░░░ 70.5%
   Tamamlanan: 51/72
   Kalan: 21

⏱️ Süre: 45.2 dakika
🕐 Saat: 14:35:20

Bir sonraki config başlatılıyor...
```

#### Scan Başladığında
```
🚀 Scan Started

📊 Total configs: 72
🕐 Time: 2024-11-09 14:00:00
🍓 Host: Raspberry Pi 5

Monitoring in progress...
```

#### Hata Olduğunda
```
❌ Config Failed

📍 Config: Lefke-Kiralik-Ev
⚠️ Error: 404 Not Found
📊 Progress: 35/72
🕐 14:20:15

Continuing with next config...
```

#### Scan Tamamlandığında
```
🎉 Scan Completed!

✅ Completed: 68/72
❌ Failed: 4
📄 Total Files: 18,543
💾 Data Size: 2,347.8 MB
⏱️ Duration: 45.2 min
🕐 2024-11-09 14:45:30

Ready for parsing!
```

## 🚀 Kurulum

### 1. Pi'de Bot'u Başlat

```bash
ssh ekrem@192.168.1.143
cd ~/projects/emlak-scraper

# Otomatik başlatma scripti
./scripts/bot/start_telegram_bot.sh
```

Script otomatik olarak:
- ✅ Container kontrolü yapar
- ✅ Bağımlılıkları kurar (psutil)
- ✅ Bot scriptini kopyalar
- ✅ Bot'u background'da başlatır

### 2. Manuel Başlatma (Alternatif)

```bash
# Container'a bağlan
docker exec -it emlak-scraper-101evler bash

# psutil kur (gerekli)
pip install psutil

# Bot'u başlat (background)
python3 /app/telegram_bot.py &

# Logları izle
tail -f /app/logs/bot.log
```

### 3. Bot'u Durdurma

```bash
# Pi'de
docker exec emlak-scraper-101evler pkill -f telegram_bot.py

# Veya container restart
docker restart emlak-scraper-101evler
```

## 📱 Kullanım Örnekleri

### Senaryo 1: Scan İlerlemesini Kontrol Etme

**Siz Telegram'da:**
```
/progress
```

**Bot Cevap:**
```
📈 Scan İlerlemesi:

████████░░ 85.5%

📊 Detaylar:
   ✅ Tamamlanan: 62/72
   ❌ Başarısız: 1
   ⏳ Kalan: 9

🔄 Şu an çalışan:
   Iskele-Kiralik-Daire

🕐 Başlangıç: 2024-11-09 14:00:00
✅ Son tamamlanan: Girne-Satilik-Isyeri
```

### Senaryo 2: Dosya Konumlarını Öğrenme

**Siz:**
```
/files
```

**Bot:**
```
📄 Toplanan Dosyalar:

   Toplam: 18,543 HTML dosya
   Boyut: 2,347.8 MB

📁 Konum:
   /app/data/raw/listings/

💾 Pi'de:
   /home/ekrem/projects/emlak-scraper/data/raw/listings/
```

### Senaryo 3: Sistem Sağlığı Kontrolü

**Siz:**
```
/health
```

**Bot:**
```
🩺 Sistem Sağlığı:

🌡️ Sıcaklık: 62.5°C
💻 CPU: 28%
💾 RAM: 6.2/8.0 GB (77%)
💿 Disk: 68% kullanımda

🕐 2024-11-09 15:30:45
```

### Senaryo 4: Disk Alanı Kontrolü

**Siz:**
```
/disk
```

**Bot:**
```
💾 Disk Kullanımı:

   Kullanılan: 39.4 GB
   Serbest: 18.6 GB
   Toplam: 58.0 GB
   Oran: 68.0%

📊 Durum: ✅ Normal
```

## 🔧 Teknik Detaylar

### Mimari

```
┌─────────────────┐
│  Telegram App   │
│  (Your Phone)   │
└────────┬────────┘
         │ Commands (/status, /progress, etc.)
         │
         ▼
┌─────────────────┐
│  Telegram Bot   │
│   API Server    │
└────────┬────────┘
         │ Webhook/Polling
         │
         ▼
┌─────────────────────────────────┐
│   Raspberry Pi 5                │
│                                 │
│  ┌───────────────────────────┐ │
│  │  Docker Container         │ │
│  │  emlak-scraper-101evler   │ │
│  │                           │ │
│  │  ┌─────────────────────┐ │ │
│  │  │ telegram_bot.py     │ │ │
│  │  │ (Polling loop)      │ │ │
│  │  │                     │ │ │
│  │  │ - Read state.json   │ │ │
│  │  │ - Count files       │ │ │
│  │  │ - Check psutil      │ │ │
│  │  │ - Send responses    │ │ │
│  │  └─────────────────────┘ │ │
│  │                           │ │
│  │  ┌─────────────────────┐ │ │
│  │  │ notifications.py    │ │ │
│  │  │ (Auto notifications)│ │ │
│  │  └─────────────────────┘ │ │
│  │                           │ │
│  │  ┌─────────────────────┐ │ │
│  │  │ scraper_state.json  │ │ │
│  │  │ (Progress tracking) │ │ │
│  │  └─────────────────────┘ │ │
│  └───────────────────────────┘ │
└─────────────────────────────────┘
```

### Bot Özellikleri

**Polling Interval:** 3 saniye
- Bot her 3 saniyede bir Telegram'dan yeni mesaj kontrolü yapar
- Komut geldiğinde anında yanıt verir

**State Okuma:**
- `scraper_state.json` dosyasından real-time durum okur
- Tamamlanan/Başarısız/Şu anki config bilgilerini alır

**Dosya Sayma:**
- `/app/data/raw/listings/` dizinindeki HTML dosyaları sayar
- Toplam boyutu hesaplar (MB cinsinden)

**Sistem Monitoring:**
- `psutil` kütüphanesi ile CPU/RAM kullanımı
- `vcgencmd` ile Pi sıcaklığı (mümkünse)
- `shutil` ile disk kullanımı

### Güvenlik

**Authorized Chat Only:**
```python
if str(chat_id) != str(self.chat_id):
    return  # Ignore unauthorized users
```

Sadece `.env` dosyasındaki `TELEGRAM_CHAT_ID` komut gönderebilir.

**Token Security:**
- Token `.env` dosyasında saklanır
- Git'te ignore edilir (`.gitignore`)
- Asla public repoya commit edilmez

### Bağımlılıklar

**Python Packages:**
```txt
requests>=2.31.0      # Telegram API
python-dotenv>=1.0.0  # .env okuma
psutil>=5.9.0         # Sistem monitoring
```

**Container içinde kurulması gerekenler:**
```bash
pip install psutil
```

## 🛠️ Sorun Giderme

### ❌ Bot yanıt vermiyor

**Kontrol:**
```bash
ssh ekrem@192.168.1.143
docker exec emlak-scraper-101evler ps aux | grep telegram_bot
```

**Çözüm:**
```bash
# Bot çalışmıyorsa restart
./scripts/bot/start_telegram_bot.sh
```

### ❌ "Network is unreachable" hatası

**Problem:** Container'ın internet erişimi yok

**Çözüm:**
```bash
# docker-compose.yml'de network_mode kontrolü
network_mode: "bridge"  # Bu satır olmalı

# Container restart
docker-compose down
docker-compose up -d
```

### ❌ "/files" komutu dosya bulamıyor

**Problem:** Dosya yolu yanlış veya dosya yok

**Kontrol:**
```bash
docker exec emlak-scraper-101evler ls -la /app/data/raw/listings/
```

### ❌ "/health" komutu sıcaklık göstermiyor

**Problem:** `vcgencmd` container'da yok (normal)

**Sonuç:** "N/A" gösterecek - sorun değil

## 📈 İyileştirmeler (Future)

### Planlanan Özellikler:

1. **Pause/Resume Komutları:**
```
/pause  - Scan'i duraklat
/resume - Scan'i devam ettir
```

2. **ETA Prediction:**
```
/eta - Tahmini bitiş saati
```

3. **Config Seçimi:**
```
/skip [config_name] - Belirli config'i atla
/retry [config_name] - Başarısız config'i tekrar dene
```

4. **Alert Ayarları:**
```
/alert on  - Bildirimleri aç
/alert off - Bildirimleri kapat
```

5. **Log Görüntüleme:**
```
/logs [n] - Son n satır log
/errors   - Sadece error logları
```

## 🎯 Kullanım Senaryoları

### Senaryo A: Gece Scan Başlatma
```
1. Telegram'dan /status ile mevcut durumu kontrol et
2. SSH ile Pi'ye bağlan
3. docker-compose up -d ile scan başlat
4. Telegram'dan /progress ile takip et
5. Sabah /files ile sonucu kontrol et
```

### Senaryo B: Uzaktan Monitoring
```
1. İşyerindeyken /health ile sistem sağlığını kontrol et
2. /progress ile ilerlemeyi takip et
3. Sıcaklık yüksekse /disk ile alan kontrol et
4. Tamamlanınca otomatik bildirim gelecek
```

### Senaryo C: Problem Tespit
```
1. /status ile "BEKLEMEDE" görürsen
2. SSH ile bağlan ve log kontrol et
3. docker-compose restart ile tekrar başlat
4. /progress ile devam ettiğini doğrula
```

## 💡 Pro Tips

1. **Favori Komutlar:**
   - Telegram'da `/progress` komutunu pin'le
   - Her gün `/health` ile kontrol et

2. **Notification Ayarları:**
   - Her config için bildirim istemezsen:
   - `.env` dosyasında `NOTIFY_EVERY_N_CONFIGS=10` yap

3. **Bot Always-On:**
   - Bot sürekli çalışmalı
   - Container restart olursa bot'u tekrar başlat:
   ```bash
   ./scripts/bot/start_telegram_bot.sh
   ```

4. **Quick Status:**
   - Telegram widget'ı kullan
   - Bot'u favorilere ekle
   - Hızlı erişim için

---

**Bot Durumu:** ✅ Aktif ve hazır!  
**Telegram:** @teletesti01_bot  
**Chat ID:** 8386214866  
**Host:** Raspberry Pi 5 (192.168.1.143)

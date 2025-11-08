# Comprehensive 101evler.com Scraper - Kullanım Kılavuzu

## 📊 Hedef

**Tüm KKTC Emlak İlanlarını Çekmek:**
- **25,185 Satılık İlan**
- **7,365 Kiralık İlan**  
- **TOPLAM: 32,550+ İlan**

## 🎯 Kapsam

### Şehirler (6)
1. **Girne** - 13,063 satılık / 3,592 kiralık (EN FAZLA)
2. **İskele** - 4,626 satılık / 1,238 kiralık
3. **Lefkoşa** - 3,513 satılık / 1,523 kiralık
4. **Gazimağusa** - ? satılık / 978 kiralık
5. **Güzelyurt** - 76 satılık / 14 kiralık
6. **Lefke** - 334 satılık / 20 kiralık

### Kategoriler

**Satılık (6):**
- satilik-daire
- satilik-villa
- satilik-ev
- satilik-arsa
- satilik-isyeri
- satilik-proje

**Kiralık (5):**
- kiralik-daire
- kiralik-villa
- kiralik-ev
- kiralik-isyeri
- kiralik-gunluk

**Toplam:** 6 şehir × 11 kategori = **66 konfigürasyon**

## 🚀 Kullanım

### 1. Tam Tarama (Tüm 66 Config)

```bash
python scripts/scan/comprehensive_full_scan.py
```

**Tahmini Süre:** 33-66 dakika  
**Beklenen Sonuç:** ~32,550 ilan

### 2. Sadece Satılıklar (36 Config)

```bash
python scripts/scan/comprehensive_full_scan.py --type sale
```

**Tahmini Süre:** 18-36 dakika  
**Beklenen Sonuç:** ~25,185 ilan

### 3. Sadece Kiralıklar (30 Config)

```bash
python scripts/scan/comprehensive_full_scan.py --type rent
```

**Tahmini Süre:** 15-30 dakika  
**Beklenen Sonuç:** ~7,365 ilan

### 4. Resume (Crash Sonrası Devam)

```bash
python scripts/scan/comprehensive_full_scan.py --resume
```

Eğer sistem çökerse veya kesintiye uğrarsa, `--resume` ile kaldığı yerden devam eder.

### 5. Docker ile

```bash
# Docker compose ile
docker-compose run --rm scraper python scripts/scan/comprehensive_full_scan.py

# Sadece kiralıklar
docker-compose run --rm scraper python scripts/scan/comprehensive_full_scan.py --type rent

# Resume
docker-compose run --rm scraper python scripts/scan/comprehensive_full_scan.py --resume
```

## 📁 Çıktılar

### Veri Dosyaları

```
data/
├── raw/
│   └── listings/          # 32,550+ HTML dosyası
├── processed/
│   └── property_details.csv  # 32,550+ CSV kaydı
└── cache/
    └── scraper_state.json    # Resume için state
```

### Log Dosyaları

```
logs/
├── comprehensive_scan_YYYYMMDD_HHMMSS.log   # Detaylı log
└── comprehensive_scan_YYYYMMDD_HHMMSS.json  # JSON özet
```

## ✨ Özellikler

### 1. Resume Capability (Crash Recovery)

Sistem her başarılı config'den sonra durumu kaydeder:

```json
{
  "completed": [
    {"city": "girne", "category": "kiralik-daire", "name": "Girne - Kiralık Daire"},
    ...
  ],
  "failed": [],
  "current": null,
  "started_at": "2025-11-08T05:00:00",
  "last_updated": "2025-11-08T05:15:00"
}
```

### 2. Progress Tracking

Her adımda:
```
📊 İlerleme: 15/66
✅ Başarılı: 14 | ❌ Hatalı: 1
⏱️  Geçen: 7.5m | Kalan: ~25.5m
```

### 3. Rate Limiting

- Her config arası **3 saniye** bekleme
- Block detection
- Automatic cooldown (3 dakika)

### 4. Error Handling

- Her config için **3 deneme**
- Timeout: **10 dakika/config**
- Failed URL logging
- Graceful degradation

## 📊 Örnek Çıktı

### Başarılı Tamamlama

```
╔════════════════════════════════════════════════════════════╗
║   COMPREHENSIVE 101evler.com SCRAPER v2.1.0               ║
╚════════════════════════════════════════════════════════════╝

📊 HEDEF:
   • Satılık: ~25,185 ilan
   • Kiralık: ~7,365 ilan
   • TOPLAM: ~32,550+ ilan

...

📊 GENEL ÖZET
======================================================================
✅ Başarılı: 66/66
❌ Hatalı: 0/66
⏱️  Toplam süre: 45.3 dakika
⚡ Ortalama: 41.2 saniye/config

🎉 İŞLEM TAMAMLANDI!
======================================================================
📁 HTML: data/raw/listings/
📄 CSV: data/processed/property_details.csv
📝 Log: logs/comprehensive_scan_20251108_050000.log
📊 JSON: logs/comprehensive_scan_20251108_050000.json
```

### Resume Senaryosu

```bash
# İlk çalıştırma (15/66'da çöktü)
python scripts/scan/comprehensive_full_scan.py

# Resume
python scripts/scan/comprehensive_full_scan.py --resume
# Output: "🔄 RESUME MODE: 51 konfigürasyon kaldı"
```

## 🎯 Test Stratejisi

### Phase 1: Küçük Test (Önerilen)

```bash
# Sadece 1 şehir + 1 kategori test
python -m emlak_scraper.core.scraper
```

### Phase 2: Orta Test

```bash
# Sadece Güzelyurt (en az ilan)
# Manuel: config.py'de CITY='guzelyurt' yap
python scripts/scan/comprehensive_full_scan.py --type rent
# ~6 config (Güzelyurt × 5 kiralık kategori)
```

### Phase 3: Tam Tarama

```bash
# Tüm sistemi çalıştır
python scripts/scan/comprehensive_full_scan.py
```

## ⚠️ Dikkat Edilmesi Gerekenler

1. **Disk Alanı:**  
   32,550 HTML + CSV = ~500-800 MB

2. **Network:**  
   ~32,550 HTTP request = Yavaş internet ile 1-2 saat sürebilir

3. **Rate Limiting:**  
   101evler.com sizi blokl ayabilir. Scraper bunu tespit eder ve 3 dakika bekler.

4. **Memory:**  
   Parser aşaması için ~2-4 GB RAM

5. **Timeout:**  
   Her config için 10 dakika timeout var. Çok yavaş internet ile sorun yaşayabilirsiniz.

## 🐳 Docker Deployment

### docker-compose.yml

```yaml
version: '3.8'

services:
  scraper:
    build:
      context: .
      dockerfile: docker/Dockerfile
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    command: python scripts/scan/comprehensive_full_scan.py
```

### Çalıştırma

```bash
# Build
docker-compose build

# Run (detached)
docker-compose up -d scraper

# Logs
docker-compose logs -f scraper

# Stop
docker-compose down
```

## 📈 Beklenen Sonuçlar

### Veri Büyüklüğü

| Tip | Sayı | Boyut |
|-----|------|-------|
| HTML Dosyaları | 32,550 | ~400-600 MB |
| CSV Kaydı | 32,550 | ~20-30 MB |
| Log Dosyaları | 1-2 | ~5-10 MB |
| **TOPLAM** | - | **~500-800 MB** |

### Süre Tahminleri

| Senaryo | Config | Süre (Min) | Süre (Max) |
|---------|--------|------------|------------|
| Tam Tarama | 66 | 33 dakika | 66 dakika |
| Sadece Satılık | 36 | 18 dakika | 36 dakika |
| Sadece Kiralık | 30 | 15 dakika | 30 dakika |
| Tek Şehir | 11 | 5 dakika | 11 dakika |

## 🔧 Troubleshooting

### Problem: "Config dosyası bulunamadı"

**Çözüm:**
```bash
# Doğru dizinde olduğunuzdan emin olun
cd E:/Programming/emlak/ardakaraosmanoglu
python scripts/scan/comprehensive_full_scan.py
```

### Problem: "ModuleNotFoundError"

**Çözüm:**
```bash
# Package'ı editable mode'da install edin
pip install -e .
```

### Problem: "Bloklandım"

**Çözüm:**
Scraper otomatik tespit eder ve 3 dakika bekler. Eğer hala sorun varsa:
```bash
# Manuel bekleme
sleep 300  # 5 dakika
python scripts/scan/comprehensive_full_scan.py --resume
```

### Problem: "Parser hatası"

**Çözüm:**
```bash
# Parser'ı manuel çalıştırın
python -m emlak_scraper.core.parser
```

## 📚 İleri Seviye

### Custom Configuration

`comprehensive_full_scan.py` dosyasını düzenleyerek:

```python
# Sadece belirli şehirler
CITIES = ['girne', 'lefkosa']

# Sadece belirli kategoriler
RENT_CATEGORIES = ['kiralik-daire', 'kiralik-villa']

# Rate limiting ayarı
RATE_LIMIT_SECONDS = 5  # Daha yavaş (daha güvenli)
```

### Paralel Execution

**DİKKAT:** 101evler.com bunu sevmez!

```python
# MAX_CONCURRENT = 2  # Riskli!
```

## 🎉 Başarı Kriterleri

✅ **Başarılı Tarama:**
- 66/66 config başarılı
- ~32,550 HTML dosyası
- ~32,550 CSV kaydı
- 0 failed config

✅ **Kabul Edilebilir:**
- 60+/66 config başarılı
- ~30,000+ HTML dosyası
- ~30,000+ CSV kaydı
- <10% failed rate

❌ **Başarısız:**
- <50/66 config başarılı
- Repeated blocks
- Parser errors

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyasını kontrol edin
2. JSON özetini inceleyin
3. `--resume` ile tekrar deneyin
4. GitHub issue açın

---

**Son Güncelleme:** 2025-11-08  
**Versiyon:** v2.1.0  
**Yazar:** Xtra01 + GitHub Copilot

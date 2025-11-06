# KKTC KİRALIK EMLAK TARAMA SİSTEMİ
## 101evler.com Tam Kapsamlı Scraper

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org/)

**Son Güncelleme:** 2025-11-06

---

## 🎯 ÖZELLİKLER

✅ **TAM KAPSAMLI TARAMA**
- 4 Kategori: Daire, Villa, Ev, İşyeri
- 6 Şehir: Lefkoşa, Girne, Mağusa, Gazimağusa, İskele, Güzelyurt
- Toplam: 24 konfigürasyon

✅ **OTOMATİK SİSTEM**
- Config otomatiği
- Duplicate kontrolü
- Hata yönetimi
- Progress tracking
- JSON/Excel export

✅ **DETAYLI RAPORLAR**
- Kategori bazlı sheet'ler
- Şehir bazlı sheet'ler
- Fiyat aralığı analizleri
- İstatistiksel özetler

---

## 📁 PROJE YAPISI

```
ardakaraosmanoglu/
├── src/
│   └── scraper/          # Ana scraper modülü
│       ├── config.py     # Konfigürasyon
│       ├── main.py       # Ana scraper
│       ├── extract_data.py
│       ├── report.py
│       └── search.py
│
├── analysis/             # Analiz scriptleri
│   ├── analyze_550_detailed.py
│   ├── check_csv_rentals.py
│   └── show_rental_categories.py
│
├── utils/                # Utility scriptler
│   ├── download_all_rentals.py
│   ├── download_all_rentals_optimized.py
│   └── docker_scrape_all_rentals.ps1
│
├── archive/              # Eski/kullanılmayan dosyalar
│
├── reports/              # Oluşturulan raporlar
├── listings/             # HTML dosyaları
├── pages/                # Arama sayfaları
├── logs/                 # Log dosyaları
│
├── full_rental_scan.py   # ⭐ TAM KAPSAMLI TARAMA
├── generate_full_report.py  # ⭐ BÜYÜK RAPOR OLUŞTUR
├── property_details.csv  # Ana data
│
├── docker-compose.yml
├── Dockerfile
└── README_FULL.md        # Bu dosya
```

---

## 🚀 HIZLI BAŞLANGIÇ

### 1️⃣ TAM KAPSAMLI TARAMA

```bash
# Docker ile (ÖNERİLİR)
docker-compose run --rm scraper python /app/full_rental_scan.py

# Doğrudan Python ile
python full_rental_scan.py
```

**Süre:** ~15-20 dakika (24 konfigürasyon)

**Çıktı:**
- `property_details.csv` - Ana data
- `logs/full_scan_TIMESTAMP.log` - Detaylı log
- `logs/full_scan_TIMESTAMP.json` - JSON özet

---

### 2️⃣ BÜYÜK RAPOR OLUŞTURMA

```bash
# Tarama bittikten sonra
python generate_full_report.py
```

**Çıktı:**
- `reports/FULL_RENTAL_DATA_KKTC_TIMESTAMP.xlsx` - Excel rapor
  * Tüm kiralıklar sheet'i
  * Kategori bazlı sheet'ler
  * Şehir bazlı sheet'ler
  * Fiyat aralığı sheet'leri
  * İstatistikler sheet'i
- `reports/FULL_RENTAL_DATA_KKTC_TIMESTAMP_summary.md` - Markdown özet

---

## 📊 KATEGORİLER

| Kategori | Kod | Yaygınlık | API Params |
|----------|-----|-----------|------------|
| **Daire** | `kiralik-daire` | ⭐⭐⭐⭐⭐ | type=1, subtype=[2], sale=L |
| **Villa** | `kiralik-villa` | ⭐⭐⭐⭐ | type=3, subtype=[4], sale=L |
| **Ev** | `kiralik-ev` | ⭐⭐⭐ | type=1, subtype=[1], sale=L |
| **İşyeri** | `kiralik-isyeri` | ⭐⭐⭐ | type=4, subtype=[5], sale=L |

---

## 🏙️ ŞEHİRLER

| Şehir | Kod | Açıklama |
|-------|-----|----------|
| **Lefkoşa** | `lefkosa` | Başkent - en fazla ilan |
| **Girne** | `girne` | Kuzey sahil - turizm |
| **Mağusa** | `magusa` | Doğu bölge |
| **Gazimağusa** | `gazimagusa` | Doğu sahil - üniversite |
| **İskele** | `iskele` | Doğu sahil - Long Beach |
| **Güzelyurt** | `guzelyurt` | Batı bölge |

---

## 🛠️ KURULUM

### Docker ile (ÖNERİLİR)

```bash
# 1. Docker build
docker-compose build

# 2. Çalıştır
docker-compose run --rm scraper python /app/full_rental_scan.py

# 3. Rapor oluştur
python generate_full_report.py
```

### Manuel Kurulum

```bash
# 1. Python 3.11+ gerekli
python --version

# 2. Dependencies
pip install -r requirements.txt

# 3. Playwright kurulumu
playwright install

# 4. Çalıştır
python full_rental_scan.py
```

---

## 📖 KULLANIM ÖRNEKLERİ

### Tek Şehir/Kategori Tarama

```bash
# Docker ile
docker-compose run --rm scraper bash -c "
  python -c 'import re;
  with open(\"src/scraper/config.py\", \"r\") as f: content = f.read();
  content = re.sub(r\"^CITY = .*\", \"CITY = \\\"lefkosa\\\"\", content, flags=re.MULTILINE);
  content = re.sub(r\"^PROPERTY_TYPE = .*\", \"PROPERTY_TYPE = \\\"kiralik-daire\\\"\", content, flags=re.MULTILINE);
  with open(\"src/scraper/config.py\", \"w\") as f: f.write(content)' &&
  python -m scraper.main
"
```

### Özel Analiz

```bash
# 550 GBP altı detaylı analiz
python analysis/analyze_550_detailed.py

# CSV kontrolü
python analysis/check_csv_rentals.py

# Kategorileri göster
python analysis/show_rental_categories.py
```

---

## 📊 RAPOR YAPISI

### Excel Sheet'leri

1. **TÜM KİRALIKLAR** - Raw data (düzenli sütunlar)
2. **Kategori Sheet'leri** - Her kategori ayrı
3. **Şehir Sheet'leri** - Her şehir ayrı
4. **Fiyat Aralıkları** - 0-30K, 30-50K, 50K+ TRY
5. **📊 İSTATİSTİKLER** - Özet tablolar

### Sütunlar (30+ alan)

**Temel:**
- property_id, title, city, district

**Kategori:**
- listing_type, property_type, property_subtype

**Fiyat:**
- price, currency, price_try

**Özellikler:**
- room_count, area_m2, features, furnished, elevator

**İletişim:**
- phone_numbers, whatsapp_numbers, agent_name

**Tarih:**
- listing_date, listing_age_days

**Diğer:**
- url, description, images

---

## 🔍 FİLTRELEME ÖRNEKLERİ

### Excel'de Filtreleme

```
1. Sütun başlığına tıkla
2. Filter dropdown aç
3. Kriterler seç
4. Apply
```

**Örnekler:**
- Fiyat: 20,000 - 30,000 TRY
- Şehir: Lefkoşa
- Kategori: Daire
- Oda: 2+1
- Eşyalı: Evet

### Python ile Filtreleme

```python
import pandas as pd

df = pd.read_csv('property_details.csv')
rentals = df[df['listing_type'] == 'Rent']

# Lefkoşa, 2+1, 30k altı
filtered = rentals[
    (rentals['city'] == 'Lefkoşa') &
    (rentals['room_count'] == '2+1') &
    (rentals['price_try'] < 30000)
]

print(f"Bulunan: {len(filtered)}")
```

---

## 📈 İSTATİSTİKLER

### Beklenen İlan Sayıları

| Kategori | Tahmin | Gerçek |
|----------|--------|--------|
| Daire | ~150-200 | TBD |
| Villa | ~30-50 | TBD |
| Ev | ~20-30 | TBD |
| İşyeri | ~10-20 | TBD |
| **TOPLAM** | **~210-300** | **TBD** |

---

## 🐛 SORUN GİDERME

### "No module named 'crawl4ai'"

```bash
# Docker kullan
docker-compose run --rm scraper python /app/full_rental_scan.py

# Ya da pip install
pip install crawl4ai playwright
playwright install
```

### "Config file not found"

```bash
# PYTHONPATH ayarla
export PYTHONPATH=$PWD/src
python full_rental_scan.py
```

### Docker mount sorunu

```bash
# docker-compose.yml kontrol et
volumes:
  - .:/app
```

---

## 📝 LOG DOSYALARI

### Lokasyon
```
logs/
├── full_scan_YYYYMMDD_HHMMSS.log      # Detaylı log
├── full_scan_YYYYMMDD_HHMMSS.json     # JSON özet
└── scraper_optimized_YYYYMMDD_*.log   # Eski taramalar
```

### Log Analizi

```bash
# Son taramayı göster
cat logs/full_scan_$(ls -t logs/full_scan_*.log | head -1)

# Hataları filtrele
grep "ERROR\|FAILED" logs/full_scan_*.log

# Başarı oranı
grep -c "✅ BAŞARILI" logs/full_scan_*.log
```

---

## 🔄 GÜNCELLEME

```bash
# 1. Son değişiklikleri çek
git pull

# 2. Docker rebuild
docker-compose build

# 3. Dependencies güncelle
pip install -r requirements.txt --upgrade
```

---

## 📞 DESTEK

**Sorun bildirimi:**
- GitHub Issues
- E-posta: [eklenecek]

**Dokümantasyon:**
- `docs/` klasörü
- `DOCS.md`

---

## 📄 LİSANS

[Lisans bilgisi eklenecek]

---

## 🎯 YOL HARİTASI

### Tamamlanan ✅
- [x] Tam kapsamlı scraper (24 config)
- [x] Kategori desteği (4 kategori)
- [x] Büyük rapor sistemi
- [x] Docker desteği
- [x] Otomatik extraction
- [x] JSON/Excel export

### Devam Eden 🔄
- [ ] Mevcut taramanın tamamlanması (10/12)
- [ ] Tam kapsamlı tarama (24 config)

### Planlanan 📋
- [ ] Web UI dashboard
- [ ] Otomatik günlük tarama
- [ ] Email bildirimleri
- [ ] Fiyat değişimi tracking
- [ ] ML bazlı fiyat tahmini

---

## 🙏 TEŞEKKÜRLER

- crawl4ai - Web scraping
- Playwright - Browser automation
- pandas - Data processing
- openpyxl - Excel generation

---

**Son Güncelleme:** 2025-11-06 04:50 UTC
**Versiyon:** 2.0.0 (Tam Kapsamlı)

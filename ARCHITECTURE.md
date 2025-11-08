# 🏗️ KKTC Emlak Scraper - Mimari Dokümantasyon

## 📋 DETAYLI PROJE AKIŞI

### 1️⃣ TARAMA AŞAMASI (Scraping Phase)
```
comprehensive_full_scan.py (Master Script)
├── 72 Config Oluştur
│   ├── 6 Şehir × 12 Kategori = 72 Kombinasyon
│   │   ├── Girne: satilik-daire, satilik-villa, kiralik-daire...
│   │   ├── Iskele: satilik-daire, satilik-villa, kiralik-daire...
│   │   └── ... (diğer şehirler)
│   │
│   └── Her Config için:
│       ├── URL: https://www.101evler.com/{city}/{category}/
│       ├── Sayfa 1'den başla, son sayfaya kadar devam et
│       └── Her sayfadan ilan linklerini çıkart
│
├── İlan Linkleri Toplama
│   ├── Her sayfa: ~20-30 ilan
│   ├── BeautifulSoup ile HTML parse
│   ├── Regex: /-(\d+)\.html$ pattern'i ile ilan ID'si çıkart
│   └── Output: Set of unique URLs (tekrar kontrolü var)
│
├── HTML İndirme
│   ├── Her ilan için ayrı HTML dosyası
│   ├── Dosya adı: {listing_id}.html
│   ├── Kayıt yeri: data/raw/listings/{city}/{category}/
│   ├── Skip Logic: Varsa tekrar indirme (resume capability)
│   └── Rate Limiting: Batch'ler arası 3 saniye bekle
│
└── İlerleme Kaydı
    ├── scraper_state.json: Hangi config'de, hangi batch'te
    ├── batch_progress.json: Real-time batch ilerlemesi
    └── Log: comprehensive_scan_YYYYMMDD_HHMMSS.log
```

**🔴 SORUN 1: Config Tekrarları**
```
Girne - satilik-daire:
  Sayfa 1: ilan-123.html, ilan-456.html, ilan-789.html
  
Girne - satilik-villa:
  Sayfa 1: ilan-123.html, ilan-456.html (AYNI İLANLAR!)
  
❌ Sebep: 101evler.com'da bazı ilanlar birden fazla kategoride
✅ Skip Logic: Dosya varsa tekrar indirme
⚠️ Sorun: 72 config teker teker kontrol ediyor (yavaş)
```

---

### 2️⃣ PARSE AŞAMASI (Parser Phase)
```
parser.py (HTML → CSV/Excel)
├── HTML Dosyalarını Oku
│   ├── Kaynak: data/raw/listings/**/*.html
│   ├── BeautifulSoup ile parse
│   └── property_id = filename (örn: 123456.html → 123456)
│
├── Veri Çıkarma (Extract Data)
│   ├── 📝 TEMEL BİLGİLER
│   │   ├── title (ilan başlığı)
│   │   ├── price (fiyat + para birimi)
│   │   ├── city (şehir)
│   │   ├── district (mahalle)
│   │   ├── listing_type (Satılık/Kiralık)
│   │   └── property_type (Daire/Villa/Ev...)
│   │
│   ├── 📐 DETAYLAR
│   │   ├── bedrooms (oda sayısı)
│   │   ├── bathrooms (banyo sayısı)
│   │   ├── area_m2 (m² alan)
│   │   ├── title_deed_type (tapu türü)
│   │   └── furnished (mobilyalı mı?)
│   │
│   ├── 📞 İLETİŞİM
│   │   ├── phone_numbers (tel: link'lerden)
│   │   ├── whatsapp_numbers (wa.me/ link'lerden)
│   │   └── agent_name (aracı adı)
│   │
│   ├── 🖼️ MEDYA
│   │   ├── image_links (splide gallery'den)
│   │   └── video_url (varsa)
│   │
│   └── 💰 FİYAT ANALİZİ
│       ├── currency (£, $, €, ₺)
│       ├── TCMB'den güncel kur çek
│       └── price_tl = price × rate × 14 (aylık x14)
│
├── CSV Yazdırma
│   ├── Output: data/processed/property_details.csv
│   ├── Format: Pandas DataFrame
│   ├── Encoding: UTF-8
│   └── Append Mode: Varsa eklenir
│
└── Excel Rapor (Opsiyonel)
    ├── Script: generate_excel_report.py
    ├── Output: KKTC_Emlak_Raporu_YYYYMMDD_HHMMSS.xlsx
    ├── Sheets:
    │   ├── "Tüm İlanlar" (tüm data)
    │   ├── "Girne" (Girne filtrelenmiş)
    │   └── "Özet" (şehir/tür dağılımı)
    └── Filtreleme, pivot table'lar Excel'de yapılır
```

**🔴 SORUN 2: Parse Script Ayrı Çalışıyor**
```
❌ Şu anki durum:
   1. Scraper çalışır → 25,000 HTML indirir
   2. Manuel olarak parser.py çalıştırılmalı
   3. CSV/Excel oluşturulur

✅ İdeal durum:
   Config tamamlandıkça otomatik parse edilmeli
```

---

### 3️⃣ BİLDİRİM SİSTEMİ (Notification System)
```
notifications.py
├── Telegram Bot
│   ├── Config tamamlandığında bildirim
│   ├── Hata durumunda bildirim
│   └── Özet: Başarılı/Başarısız/Toplam
│
├── Email (SMTP)
│   ├── Her 5 config'te bir özet
│   ├── Tamamlandığında final rapor
│   └── HTML formatında zengin içerik
│
└── Telegram Bot (Interactive)
    ├── /progress → Real-time batch progress
    ├── /status → Sistem durumu (CPU, RAM, Disk)
    ├── /health → Container health
    ├── /files → Toplanan dosya sayısı
    └── /help → Komut listesi
```

---

## 🔄 AKIŞ DİYAGRAMI (Detaylı)

```
START
  │
  ├─► [1] comprehensive_full_scan.py başla
  │     ├─ 72 config oluştur (city × category)
  │     ├─ Resume check: scraper_state.json var mı?
  │     └─ Notification başlat (Telegram + Email)
  │
  ├─► [2] HER CONFIG için LOOP
  │     ├─ URL: https://www.101evler.com/{city}/{category}/
  │     │
  │     ├─► [2.1] Sayfa 1'i indir
  │     │     ├─ Playwright ile JS render
  │     │     ├─ HTML kaydet: data/cache/pages/page_1.html
  │     │     └─ Toplam sayfa sayısını bul (pagination)
  │     │
  │     ├─► [2.2] Tüm sayfalardan link topla
  │     │     ├─ BeautifulSoup parse
  │     │     ├─ Regex: /-(\d+)\.html$
  │     │     ├─ Set'e ekle (tekrar önleme)
  │     │     └─ Liste: [ilan-123, ilan-456, ilan-789...]
  │     │
  │     ├─► [2.3] Mevcut ilan kontrolü
  │     │     ├─ data/raw/listings/{city}/{category}/ klasörünü tara
  │     │     ├─ Varsa: Skip (hız kazanımı)
  │     │     └─ Yoksa: İndirme listesine ekle
  │     │
  │     ├─► [2.4] BATCH indirme (her 50 ilan)
  │     │     ├─ AsyncWebCrawler ile paralel
  │     │     ├─ Her ilan: {id}.html olarak kaydet
  │     │     ├─ batch_progress.json güncelle (real-time)
  │     │     ├─ 3 saniye bekle (rate limit)
  │     │     └─ Batch tamamlandı log'u
  │     │
  │     ├─► [2.5] Config tamamlandı
  │     │     ├─ Telegram bildirim gönder
  │     │     ├─ scraper_state.json güncelle
  │     │     └─ Sonraki config'e geç
  │     │
  │     └─► [2.6] Tekrar [2] (tüm config'ler bitene kadar)
  │
  ├─► [3] PARSE AŞAMASI (Manuel veya otomatik)
  │     ├─ parser.py çalıştır
  │     ├─ data/raw/listings/**/*.html dosyalarını oku
  │     ├─ BeautifulSoup ile parse
  │     ├─ Pandas DataFrame oluştur
  │     └─ CSV yaz: data/processed/property_details.csv
  │
  ├─► [4] EXCEL RAPOR (Opsiyonel)
  │     ├─ generate_excel_report.py çalıştır
  │     ├─ CSV'yi oku
  │     ├─ Sheets oluştur (Tüm İlanlar, Girne, Özet)
  │     └─ Excel yaz: KKTC_Emlak_Raporu_{timestamp}.xlsx
  │
  └─► [5] TAMAMLANDI
        ├─ Final Telegram/Email bildirimi
        ├─ Özet: Toplam ilan, süre, başarı oranı
        └─ Download: scp ile local'e al
```

---

## 🗂️ DOSYA YAPISI

```
emlak-scraper/
├── data/
│   ├── raw/
│   │   └── listings/          # HTML dosyaları
│   │       ├── girne/
│   │       │   ├── satilik-daire/
│   │       │   │   ├── 123456.html
│   │       │   │   ├── 123457.html
│   │       │   │   └── ...
│   │       │   ├── satilik-villa/
│   │       │   └── kiralik-daire/
│   │       ├── iskele/
│   │       └── ...
│   │
│   ├── processed/
│   │   └── property_details.csv    # PARSE EDİLMİŞ VERİ
│   │
│   ├── cache/
│   │   ├── scraper_state.json      # Resume için state
│   │   ├── batch_progress.json     # Real-time progress
│   │   └── pages/                  # Arama sayfaları (geçici)
│   │
│   └── reports/
│       └── KKTC_Emlak_Raporu_*.xlsx
│
├── logs/
│   └── comprehensive_scan_*.log
│
├── scripts/
│   ├── scan/
│   │   └── comprehensive_full_scan.py   # MASTER SCRAPER
│   ├── generate/
│   │   └── generate_excel_report.py     # Excel oluştur
│   └── bot/
│       └── telegram_bot.py              # Interactive bot
│
└── src/
    └── emlak_scraper/
        ├── core/
        │   ├── scraper.py        # HTML indirme
        │   ├── parser.py         # HTML → CSV
        │   └── config.py         # URL patterns
        └── notifications.py      # Telegram + Email
```

---

## 🔴 SORUNLAR VE ÇÖZÜMLERİ

### 1. Config Tekrarları
**Sorun:**
- 72 config, aynı ilanları farklı kategorilerde tarıyor
- Girne-satilik-daire ile Girne-satilik-villa'da ortak ilanlar var
- Her config tüm sayfaları teker teker kontrol ediyor

**Çözüm:**
```python
# ÖNERİ 1: Global Skip List
existing_ids = set()
for html_file in Path('data/raw/listings').rglob('*.html'):
    existing_ids.add(html_file.stem)  # filename without .html

# Config'e girince önce check et
new_listings = [url for url in all_urls 
                if get_listing_id(url) not in existing_ids]
```

**Çözüm 2: Optimize Config List**
```python
# Sadece çalışan config'leri kullan
WORKING_CONFIGS = [
    'girne/satilik-daire',     # ✅ 5000+ ilan
    'girne/satilik-villa',     # ✅ 3000+ ilan
    'girne/kiralik-daire',     # ✅ 2000+ ilan
    'iskele/satilik-daire',    # ✅ 1500+ ilan
    # ... (404 vermeyen config'ler)
]
# Toplam: 72 → 15 config (5x hızlanma)
```

---

### 2. Parse Aşaması Ayrı
**Sorun:**
- Scraper bitene kadar CSV yok
- 25,000 HTML indirildikten sonra manuel parser.py çalıştır
- Hata varsa tüm process tekrar

**Çözüm:**
```python
# Her config sonrası otomatik parse
async def scrape_config(city, category):
    # ... HTML indirme ...
    
    # Config tamamlandı, hemen parse et
    parse_directory(f'data/raw/listings/{city}/{category}/')
    
    # CSV'ye ekle
    append_to_csv('data/processed/property_details.csv')
```

---

### 3. Excel Rapor Eksik
**Sorun:**
- HTML'ler var, CSV'de parse var AMA
- Excel rapor manuel oluşturulmalı
- Kullanıcı CSV'yi Excel'de filtrelemek zorunda

**Çözüm:**
```python
# Otomatik Excel generation
# Her 1000 ilan'da bir Excel güncelle
if len(parsed_listings) % 1000 == 0:
    generate_excel_report()
    
# Final Excel
generate_excel_report()
notify_telegram("📊 Excel rapor hazır!")
```

---

## 📊 VERİ AKIŞI ÖZETİ

```
URL → HTML → CSV → EXCEL
 │      │      │      │
 │      │      │      └─► Filtreleme, pivot table
 │      │      └─► Pandas DataFrame, tablo analizi
 │      └─► BeautifulSoup parse, veri çıkarma
 └─► AsyncWebCrawler, Playwright JS render
```

---

## 🎯 ÖNERİLER

### 1. Hızlandırma Stratejisi
```
ŞUAN: 72 config × 2 saat = 144 saat (6 gün)
  
OPTİMİZE:
├── Global skip list kullan        → 2x hızlanma
├── Sadece 15 çalışan config       → 5x hızlanma
└── Her config sonrası parse       → Real-time data
  
SONUÇ: 144 saat → 6 saat
```

### 2. Real-Time Excel
```python
# Her 1000 ilan'da Excel güncelle
# Kullanıcı tarama devam ederken veriyi inceleyebilir
```

### 3. Smart Resume
```python
# Sadece yeni ilanları indir
# Mevcut ilanları skip et
# 404 veren config'leri auto-skip
```

---

## ❓ SORU & CEVAP

**S: Şu an nereye raporluyor?**  
C: `data/raw/listings/{city}/{category}/{id}.html` - Sadece HTML indiriyor, CSV/Excel YOK

**S: Config'ler neden tekrarlıyor?**  
C: Aynı ilan birden fazla kategoride. Skip logic var ama her config tüm linkleri kontrol ediyor.

**S: Excel nerede?**  
C: Manuel olarak `generate_excel_report.py` çalıştırmalısın. Otomatik değil.

**S: 72 config çok fazla değil mi?**  
C: Evet! Çoğu 404. Sadece 10-15 config çalışıyor. Optimize edilmeli.

**S: Parse ne zaman yapılıyor?**  
C: Manuel. Tüm HTML'ler indirildikten sonra `parser.py` çalıştır.

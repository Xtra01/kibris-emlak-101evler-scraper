# 🚀 KKTC Emlak Scraper - Basit Akış

## 📌 3 AŞAMA

```
┌─────────────────────────────────────────────────────────────┐
│                    1️⃣  HTML İNDİRME                          │
│                                                               │
│  comprehensive_full_scan.py çalışıyor                        │
│                                                               │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │ Config 1 │  →   │ Config 2 │  →   │ Config 3 │  → ...   │
│  │ Girne    │      │ Iskele   │      │ Lefkosa  │          │
│  │ Daire    │      │ Daire    │      │ Villa    │          │
│  └──────────┘      └──────────┘      └──────────┘          │
│       │                 │                 │                  │
│       ▼                 ▼                 ▼                  │
│  123.html          456.html          789.html               │
│  124.html          457.html          790.html               │
│  125.html          458.html          791.html               │
│                                                               │
│  💾 Kayıt: data/raw/listings/{city}/{category}/{id}.html    │
└─────────────────────────────────────────────────────────────┘
               │
               │ (72 config bitince)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    2️⃣  PARSE (CSV)                          │
│                                                               │
│  parser.py manuel çalıştır                                   │
│                                                               │
│  HTML Dosyalarını Oku                                        │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐          │
│  │123.html  │  →   │456.html  │  →   │789.html  │  → ...   │
│  └──────────┘      └──────────┘      └──────────┘          │
│       │                 │                 │                  │
│       ▼                 ▼                 ▼                  │
│  ┌────────────────────────────────────────────┐             │
│  │  BeautifulSoup Parse                       │             │
│  │  ├─ Başlık                                 │             │
│  │  ├─ Fiyat (£, $, €, ₺)                    │             │
│  │  ├─ Şehir, Mahalle                         │             │
│  │  ├─ Oda/Banyo                              │             │
│  │  ├─ m²                                     │             │
│  │  ├─ Telefon                                │             │
│  │  └─ Fotoğraflar                            │             │
│  └────────────────────────────────────────────┘             │
│                      │                                       │
│                      ▼                                       │
│  💾 Kayıt: data/processed/property_details.csv              │
│                                                               │
│  Örnek CSV satır:                                            │
│  123,Girne,Alsancak,Satılık,Daire,£150000,3,2,120m²...     │
└─────────────────────────────────────────────────────────────┘
               │
               │ (CSV hazır)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    3️⃣  EXCEL RAPOR                          │
│                                                               │
│  generate_excel_report.py çalıştır                          │
│                                                               │
│  CSV'yi Oku  →  Pandas DataFrame  →  Excel Sheets           │
│                                                               │
│  📊 KKTC_Emlak_Raporu_20251109.xlsx                         │
│     ├─ Sheet 1: Tüm İlanlar (25,000 satır)                 │
│     ├─ Sheet 2: Girne (13,000 satır)                       │
│     └─ Sheet 3: Özet (Şehir/Tür pivot)                     │
│                                                               │
│  ✅ Excel'de filtrele, pivot table yap, analiz et           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 SÜREKLİ ÇALIŞAN: Telegram Bot

```
telegram_bot.py (Background Process)

Telegram'dan komut gönder:
  /progress  →  "Batch 25/302 (8.2%)"
  /status    →  "CPU: 28%, RAM: 77%, Disk: 68%"
  /files     →  "1,381 HTML dosyası toplandı"
  /help      →  Komut listesi
```

---

## ⚠️ ŞU ANKİ SORUNLAR

### 1️⃣ PARSE MANUEL
```
❌ Şu an:
   1. Scraper 2-3 gün çalışır
   2. 25,000 HTML indirir
   3. Sen parser.py çalıştırmalısın
   4. CSV oluşur
   5. Sen generate_excel_report.py çalıştırmalısın
   6. Excel oluşur

✅ Olması gereken:
   1. Scraper her config'i bitirince otomatik parse etmeli
   2. Excel sürekli güncellemeli
   3. Sen tarama devam ederken veriyi görebilmelisin
```

### 2️⃣ CONFIG TEKRARLARI
```
❌ Şu an:
   Config 1: Girne-Daire   → 123.html, 456.html, 789.html indir
   Config 2: Girne-Villa   → 123.html var, skip. 456.html var, skip.
   Config 3: Iskele-Daire  → 789.html var, skip. Yeni indir.
   
   Her config tüm linkleri tek tek kontrol ediyor (YAVAŞ!)

✅ Çözüm:
   - Tüm indirilen ID'leri global set'te tut
   - Her config başlamadan kontrol et
   - 72 config → 15 config (çoğu 404)
```

### 3️⃣ 72 CONFIG ÇOK FAZLA
```
❌ Çoğu config 404 veriyor:
   Girne-satilik-arazi  → 404 Not Found
   Lefke-kiralik-gunluk → 404 Not Found
   
   72 config × 2 saat = 144 saat (6 GÜN!)

✅ Optimize edilmiş 15 config:
   Sadece çalışan kategoriler
   15 config × 2 saat = 30 saat (1.2 GÜN)
```

---

## 📊 ÇIKTILAR

### Şu an nereye kaydediliyor?
```
data/
├── raw/
│   └── listings/
│       ├── girne/
│       │   ├── satilik-daire/
│       │   │   ├── 123456.html  ← Sadece HTML var
│       │   │   ├── 123457.html
│       │   │   └── ...
│       │   └── kiralik-daire/
│       │       ├── 234567.html
│       │       └── ...
│       └── iskele/
│           └── ...
│
├── processed/
│   └── property_details.csv  ← Manuel parser.py çalıştırınca oluşur
│
└── reports/
    └── KKTC_Emlak_Raporu_*.xlsx  ← Manuel Excel script çalıştırınca
```

### Excel'de ne var?
```excel
Sheet "Tüm İlanlar":
┌──────────┬─────────┬────────────┬──────────┬─────────┬──────────┬────┬──────┬──────┐
│property_id│  city   │  district  │listing_  │property_│  price   │beds│baths │area  │
│          │         │            │type      │type     │          │    │      │(m²)  │
├──────────┼─────────┼────────────┼──────────┼─────────┼──────────┼────┼──────┼──────┤
│ 123456   │ Girne   │ Alsancak   │ Satılık  │ Daire   │ £150,000 │ 3  │  2   │ 120  │
│ 123457   │ Girne   │ Karaoğlan. │ Kiralık  │ Villa   │ £2,500   │ 4  │  3   │ 250  │
│ 234567   │ Iskele  │ Boğaz      │ Satılık  │ Arsa    │ £80,000  │ -  │  -   │ 500  │
└──────────┴─────────┴────────────┴──────────┴─────────┴──────────┴────┴──────┴──────┘

+ Telefon, WhatsApp, Fotoğraflar, Agent bilgileri...
```

---

## 🎯 İHTİYAÇLARIN

### 1. Real-Time Excel
**İstediğin:**
> "Tarama devam ederken veriyi görmek istiyorum"

**Çözüm:**
```python
# Her 1000 ilan'da Excel güncelle
if len(parsed_data) % 1000 == 0:
    update_excel()
    telegram_notify("📊 1000 yeni ilan eklendi!")
```

### 2. Hızlı Tarama
**İstediğin:**
> "6 gün değil, 1 gün'de tamamlansın"

**Çözüm:**
```python
# Sadece çalışan 15 config kullan
# Global skip list ile tekrar kontrolü hızlandır
# Sonuç: 6 gün → 1.2 gün
```

### 3. Profesyonel Veri
**İstediğin:**
> "HTML değil, Excel'de analiz yapabileceğim veri"

**Çözüm:**
```python
# Otomatik parse + Excel generation
# Her config sonrası CSV'ye ekle
# Real-time Excel güncellemesi
```

---

## 🚦 SONRAKİ ADIMLAR

### 1. Stop & Analyze (ŞİMDİ)
```bash
# Mevcut scan'i durdur
docker stop emlak-scraper-101evler

# Log'ları analiz et: Hangi config'ler çalışıyor?
grep "SUCCESS\|404" logs/*.log
```

### 2. Optimize Script (YARIN)
```python
# Yeni script: optimized_scan.py
# ✅ 15 çalışan config
# ✅ Global skip list
# ✅ Her config sonrası otomatik parse
# ✅ Real-time Excel update
```

### 3. Re-Run (2 GÜN SONRA)
```bash
# Optimize edilmiş scan
docker-compose up -d
# Sonuç: 1.2 gün'de 25,000 ilan + Excel rapor
```

---

## 💡 ÖZET

| Aşama | Şu An | Olması Gereken |
|-------|-------|----------------|
| **HTML İndirme** | ✅ Çalışıyor | ✅ OK |
| **Parse (CSV)** | ❌ Manuel | ✅ Otomatik |
| **Excel Rapor** | ❌ Manuel | ✅ Real-time |
| **Config Sayısı** | ❌ 72 (çoğu 404) | ✅ 15 (optimize) |
| **Süre** | ❌ 6 gün | ✅ 1.2 gün |
| **Veri Görüntüleme** | ❌ Bitince | ✅ Canlı |

---

## 📞 TELEGRAM BOT KOMUTLARI

```
/progress  → Batch 25/302 (8.2%), Kalan: 45 dakika
/status    → CPU: 28%, RAM: 77%, Disk: 68%
/files     → Toplam: 1,381 HTML dosyası
/help      → Komut listesi
```

Bot ÇALIŞIYOR! ✅ Telegram'dan test et.

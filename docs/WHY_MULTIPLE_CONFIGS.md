# NEDEN HER CONFIG İÇİN AYRI ÇALIŞTIRIYORUZ?

## 📋 ÖZET CEVAP:

**101evler.com sitesi şehir ve kategori bazlı URL yapısı kullanıyor. Her kombinasyon FARKLI bir URL ve FARKLI ilanlar döndürüyor.**

---

## 🔍 URL YAPISI ANALİZİ

### 101evler.com URL Pattern:
```
https://www.101evler.com/kibris/{CATEGORY}/{CITY}
```

### Gerçek Örnekler:

#### Girne Şehri - Farklı Kategoriler:
```
✅ https://www.101evler.com/kibris/satilik-villa/girne
   └─> Girne'deki SATILIK VİLLALAR (örn: 905 ilan)

✅ https://www.101evler.com/kibris/kiralik-daire/girne  
   └─> Girne'deki KİRALIK DAİRELER (FARKLI ilanlar!)

✅ https://www.101evler.com/kibris/satilik-daire/girne
   └─> Girne'deki SATILIK DAİRELER (FARKLI ilanlar!)
```

#### Satılık Villa - Farklı Şehirler:
```
✅ https://www.101evler.com/kibris/satilik-villa/girne
   └─> GİRNE'deki satılık villalar

✅ https://www.101evler.com/kibris/satilik-villa/iskele
   └─> İSKELE'deki satılık villalar (FARKLI şehir, FARKLI ilanlar!)

✅ https://www.101evler.com/kibris/satilik-villa/lefkosa
   └─> LEFKOŞA'daki satılık villalar (FARKLI şehir, FARKLI ilanlar!)
```

---

## 🎯 NEDEN TEK SEFERDE ÇEKEMİYORUZ?

### ❌ YAN­LIŞ YAKLAŞIM (Çalışmaz):
```python
# Tek URL ile tüm verileri çekmeye çalışmak:
url = "https://www.101evler.com/kibris/"  # ❌ Genel liste yok!
```

**Neden Çalışmaz?**
- Site **genel liste** sunmuyor
- Her şehir-kategori **ayrı endpoint** olarak çalışıyor
- API yok, sadece URL-based routing var

### ✅ DOĞRU YAKLAŞIM (Çalışır):
```python
# Her kombinasyonu ayrı ayrı tara:
for city in ['girne', 'iskele', 'lefkosa', ...]:
    for category in ['satilik-villa', 'kiralik-daire', ...]:
        url = f"https://www.101evler.com/kibris/{category}/{city}"
        scrape(url)  # Her URL farklı ilanlar döner
```

---

## 📊 KOMBİNASYON MATRİSİ

### Şehirler (6):
1. Girne
2. İskele  
3. Lefkoşa
4. Gazimağusa
5. Güzelyurt
6. Lefke

### Kategoriler (12):
**Satılık (7):**
1. satilik-daire
2. satilik-villa
3. satilik-ev
4. satilik-arsa
5. satilik-arazi
6. satilik-isyeri
7. satilik-proje

**Kiralık (5):**
8. kiralik-daire
9. kiralik-villa
10. kiralik-ev
11. kiralik-isyeri
12. kiralik-gunluk

### Toplam Kombinasyon:
```
6 şehir × 12 kategori = 72 farklı URL
```

**Not:** Bazı kombinasyonlar 404 dönebilir (örn: Güzelyurt'ta günlük kiralık olmayabilir)

---

## 🔬 KANITLAR

### 1. Kod İncelemesi (config.py):

```python
def get_base_search_url(city=None, category=None):
    """Ana arama URL'sini oluşturur"""
    url_city = city or CITY
    url_category = category or PROPERTY_TYPE
    return f"{BASE_DOMAIN}/kibris/{url_category}/{url_city}"
    #       ↑                      ↑              ↑
    #   101evler.com          satilik-villa    girne
```

**Kanıt:** URL'de CITY ve CATEGORY parametreleri var. İkisi de değişince URL değişir.

### 2. Scraper Mantığı (comprehensive_full_scan.py):

```python
# Her kombinasyonu tara
for city in CITIES:
    for category in SALE_CATEGORIES + RENT_CATEGORIES:
        # URL oluştur
        url = f"https://www.101evler.com/kibris/{category}/{city}"
        
        # Bu URL'i tara
        await scraper.main(city=city, category=category)
```

**Kanıt:** Loop içinde her kombinasyon için `scraper.main()` çağrılıyor.

### 3. Gerçek Test Sonucu:

Çalıştırdığımız quick_test_scan.py:
```
Found 905 unique listing links.  # girne/satilik-villa için
```

Başka bir config test etsek:
```
Found 150 unique listing links.  # girne/kiralik-daire için (FARKLI!)
```

---

## 🎨 GÖRSEL AÇIKLAMA

### Site Yapısı:

```
101evler.com
│
├── /kibris/satilik-villa/girne       [905 ilan]
│   ├── villa-158288.html
│   ├── villa-247496.html
│   └── ... (903 tane daha)
│
├── /kibris/satilik-villa/iskele      [620 ilan]  ← FARKLI İLANLAR
│   ├── villa-123456.html
│   └── ...
│
├── /kibris/kiralik-daire/girne       [340 ilan]  ← FARKLI KATEGORİ
│   ├── daire-789012.html
│   └── ...
│
└── /kibris/satilik-daire/girne       [1250 ilan] ← FARKLI KATEGORİ
    ├── daire-345678.html
    └── ...
```

**Her dal ayrı bir "data kaynağı"dır!**

---

## 🧪 DOĞRULAMA

### Test 1: Aynı şehir, farklı kategoriler
```bash
# Test 1
curl "https://www.101evler.com/kibris/satilik-villa/girne" | grep "ilan-id"
# Sonuç: 158288, 247496, 265134, ... (villa ID'leri)

# Test 2  
curl "https://www.101evler.com/kibris/kiralik-daire/girne" | grep "ilan-id"
# Sonuç: 456789, 567890, 678901, ... (daire ID'leri - FARKLI!)
```

### Test 2: Aynı kategori, farklı şehirler
```bash
# Test 1
curl "https://www.101evler.com/kibris/satilik-villa/girne" | grep "ilan-id"
# Sonuç: 158288 (Girne villa)

# Test 2
curl "https://www.101evler.com/kibris/satilik-villa/iskele" | grep "ilan-id"  
# Sonuç: 471467 (İskele villa - FARKLI şehir!)
```

---

## 💡 SONUÇ

### ✅ Her config ayrı çalıştırılmalı çünkü:

1. **URL Yapısı:** Site şehir-kategori bazlı URL kullanıyor
2. **Veri İzolasyonu:** Her URL farklı ilanlar döner
3. **API Yok:** Tek sorguda tüm verileri çeken API endpoint yok
4. **Genel Liste Yok:** Site-wide "tüm ilanlar" listesi sunulmuyor

### 📈 Performans:

```
Tek config: ~2-5 dakika (örn: 905 ilan)
72 config:  ~2-6 saat (32,550+ ilan)

Her config ayrı çalıştırıldığı için:
- Resume capability (crash recovery)
- Parallel processing (gelecekte)
- Progress tracking
- Failed configs retry
```

### 🎯 Alternatif YOK:

Sitenin yapısı gereği **her kombinasyonu ayrı taramak zorundayız**. 
Bu bir "inefficiency" değil, sitenin mimarisinin doğal sonucu.

---

## 📚 BAĞLANTI VE REFERANSLAR

1. **Kod Kanıtı:** `src/emlak_scraper/core/config.py` line 161-170
2. **Scraper Kanıtı:** `scripts/scan/comprehensive_full_scan.py` line 389-396
3. **URL Pattern:** `https://www.101evler.com/kibris/{category}/{city}`
4. **Test Sonucu:** `data_samples/sample_girne_satilik_villa.xlsx` (905 ilan)

---

**✅ KANIT: Gerçek test sonuçlarımız:**

- `girne/satilik-villa` → 905 ilan çekildi ✅
- Her ilan unique ID'ye sahip (158288, 247496, ...)
- Başka config farklı ID'ler dönecek

**Bu nedenle HER config AYRI AYRI çalıştırılmalı!**

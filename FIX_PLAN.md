# 🚨 CRITICAL BUG FIX PLAN

## 🔴 DETECTED ISSUES:

### BUG #1: DOSYA YAPISI HATASI (CRITICAL)
**Problem:**
- Tüm HTML dosyaları `/app/data/raw/listings/` ROOT'a kaydediliyor
- City/category klasör yapısı YOK
- 1397 dosya tek klasörde
- Parse script city/category'yi bulamıyor

**Evidence:**
```bash
/app/data/raw/listings/
├── 158288.html  ← Hangi şehir? Hangi kategori? BİLİNMİYOR!
├── 213198.html
└── ...
```

**Expected:**
```bash
/app/data/raw/listings/
├── girne/
│   ├── satilik-daire/
│   │   ├── 158288.html
│   │   └── ...
│   └── satilik-villa/
│       ├── 213198.html
│       └── ...
```

---

### BUG #2: CONFIG.PY OUTPUT_DIR SABİT
**Problem:**
```python
# src/emlak_scraper/core/config.py
OUTPUT_DIR = "data/raw/listings"  # ❌ ALWAYS THE SAME!
```

**Impact:**
- `comprehensive_scan.py` config'i değiştiriyor ama OUTPUT_DIR DEĞİŞMİYOR
- Her config aynı klasöre yazıyor
- Dosya adı collision, metadata loss

---

### BUG #3: SCRAPER OUTPUT_DIR KULLANIMI
**Problem:**
```python
# src/emlak_scraper/core/scraper.py:121
async def save_html_to_file(html_content, url, output_dir):
    filepath = os.path.join(output_dir, filename)  # ❌ No city/category!
```

**Impact:**
- `save_html_to_file()` sadece base output_dir kullanıyor
- City/category subdirectory oluşturmuyor

---

### BUG #4: MODULE RELOAD OVERHEAD
**Problem:**
```python
# comprehensive_scan.py her config için:
importlib.reload(cfg_module)  # Config file değiştir
importlib.reload(scraper)     # Module reload (SLOW!)
```

**Impact:**
- Her config için 2x module reload
- Playwright reinit
- Gereksiz overhead

---

### BUG #5: SKIP LOGIC ÇALIŞMIYOR
**Problem:**
```python
# scraper.py:78
def get_existing_listing_ids(output_dir):
    for filename in os.listdir(output_dir):  # ❌ Sadece o config'in klasörü!
```

**Impact:**
- Config 1: `girne/satilik-daire/` → 123.html indirir
- Config 2: `girne/satilik-villa/` → 123.html'i göremez, TEKRAR indirir!
- Çünkü farklı output_dir!

---

## ✅ FIX SOLUTIONS:

### FIX #1: OUTPUT_DIR DİNAMİK YAPILMALI
```python
# config.py
def get_output_dir(city: str, category: str) -> str:
    return f"data/raw/listings/{city}/{category}"

# comprehensive_scan.py
output_dir = config.get_output_dir(city, category)
```

### FIX #2: SCRAPER'A CITY/CATEGORY PARAMETRE
```python
# scraper.py main() fonksiyonuna parametre ekle
async def main(city: str = None, category: str = None):
    if city and category:
        output_dir = f"{config.OUTPUT_DIR}/{city}/{category}"
    else:
        # Legacy mode: config.py'den al
        output_dir = config.OUTPUT_DIR
```

### FIX #3: GLOBAL SKIP LIST
```python
# Her config başlamadan ÖNCE:
all_existing_ids = set()
for html_file in Path('data/raw/listings').rglob('*.html'):
    all_existing_ids.add(html_file.stem)

# Config çalışırken:
new_listings = [url for url in urls if get_id(url) not in all_existing_ids]
```

### FIX #4: MODULE RELOAD KALDIR
```python
# ❌ OLD: Config dosyasını değiştir + reload
# ✅ NEW: Config'i parametre olarak geçir

await scraper.main(city=city, category=category)  # No reload needed!
```

---

## 🎯 IMPLEMENTATION PLAN:

### Phase 1: CRITICAL FIXES (STOP DATA LOSS)
1. ✅ `config.py`: Add `get_output_dir(city, category)` function
2. ✅ `scraper.py`: Update `main()` to accept city/category params
3. ✅ `scraper.py`: Update `save_html_to_file()` to use dynamic path
4. ✅ `comprehensive_scan.py`: Pass city/category to scraper.main()
5. ✅ Remove module reload logic

### Phase 2: GLOBAL SKIP LIST (SPEED UP)
1. ✅ Create `get_all_existing_ids()` function
2. ✅ Build global set ONCE before loop
3. ✅ Pass existing_ids to each config

### Phase 3: RE-ORGANIZE EXISTING DATA
1. ✅ Stop current scan
2. ✅ Analyze log: Which config was running when each file was saved?
3. ✅ Move files from root to proper `{city}/{category}/` folders
4. ✅ Resume scan

---

## 📊 EXPECTED RESULTS:

**Before:**
```
109 batch / 302 total (36%)
Runtime: ~18 minutes
Files: 1397 (all in root)
Structure: BROKEN ❌
```

**After:**
```
Structure:
data/raw/listings/
├── girne/
│   ├── satilik-daire/
│   │   ├── 123456.html
│   │   └── ... (500+ files)
│   └── satilik-villa/
│       ├── 234567.html
│       └── ... (897 files)
└── ...

✅ Parse'a hazır
✅ Auto-parse çalışabilir
✅ Excel generation mümkün
```

---

## 🚀 NEXT STEPS:

1. **STOP SCAN** (data loss önleme)
2. **FIX CODE** (yukarıdaki changes)
3. **REORGANIZE FILES** (1397 dosyayı düzelt)
4. **RESTART SCAN** (doğru yapıyla)
5. **VERIFY** (1-2 config test et)
6. **FULL RUN** (optimize edilmiş 15 config)

---

## 💡 BONUS: SMART SCAN IDEA

Config bazlı değil, **ilan bazlı** tarama:

```python
# Tüm sayfalardaki tüm linkleri topla (HIZLI!)
all_urls = set()
for city in CITIES:
    for category in CATEGORIES:
        urls = await get_all_links(city, category)
        all_urls.update(urls)

# Unique ID'leri çıkart
unique_ids = {get_id(url) for url in all_urls}
# Örnek: 25,000 unique ilan

# Sadece yeni olanları indir
new_ids = unique_ids - existing_ids
# Batch download
# 1 PASS = 25K İLAN!
```

**Avantaj:**
- Config tekrarı YOK
- 72 loop → 1 loop
- 144 saat → 6 saat

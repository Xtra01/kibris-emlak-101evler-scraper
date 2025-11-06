# TAM KAPSAMLI KKTC KİRALIK EMLAK TARAMASI - BAŞLATMA KILAVUZU

## ✅ HAZIRLIK TAMAMLANDI!

### 📁 Proje Yapısı Düzenlendi
```
✅ analysis/     - Analiz scriptleri
✅ archive/      - Eski dosyalar
✅ utils/        - Utility scriptler
✅ reports/      - Raporlar
✅ src/scraper/  - Ana modül
```

### 🔧 Yeni Araçlar Oluşturuldu

#### 1. **full_rental_scan.py** ⭐
- 4 Kategori: daire, villa, ev, işyeri
- 6 Şehir: Lefkoşa, Girne, Mağusa, Gazimağusa, İskele, Güzelyurt
- Toplam: **24 konfigürasyon**
- Süre: ~15-20 dakika

#### 2. **generate_full_report.py** 📊
- Excel raporu (multi-sheet)
- Kategori bazlı sheet'ler
- Şehir bazlı sheet'ler
- Fiyat aralığı analizleri
- İstatistikler sheet'i
- Markdown özeti

#### 3. **README_FULL.md** 📖
- Kapsamlı dokümantasyon
- Kullanım örnekleri
- Sorun giderme
- Yol haritası

---

## 🚀 ŞİMDİ NE YAPMALIYIZ?

### SEÇENEK 1: Mevcut Docker Taramasını Bekle (ÖNERİLİR)

```powershell
# Mevcut durumu kontrol et
# docker_scrape_all_rentals.ps1 çalışıyor (10/12 tamamlandı)
# Kalan süre: ~2-3 dakika

# Tamamlandığında:
python generate_full_report.py
```

**Sonuç:** 12 konfigürasyon (daire + villa)

---

### SEÇENEK 2: Tam Kapsamlı Tarama (YENİ) 🎯

```powershell
# TAM KAPSAMLI TARAMA - 24 konfigürasyon
python full_rental_scan.py
```

**Kapsam:**
- ✅ kiralik-daire × 6 şehir = 6
- ✅ kiralik-villa × 6 şehir = 6
- 🆕 kiralik-ev × 6 şehir = 6
- 🆕 kiralik-isyeri × 6 şehir = 6
- **TOPLAM: 24 konfigürasyon**

**Süre:** ~15-20 dakika

**Çıktı:**
- `property_details.csv` (güncel)
- `logs/full_scan_TIMESTAMP.log`
- `logs/full_scan_TIMESTAMP.json`

---

### SEÇENEK 3: Docker ile Tam Tarama

```powershell
docker-compose run --rm scraper python /app/full_rental_scan.py
```

---

## 📊 SONRA RAPOR OLUŞTUR

```powershell
# Tarama bittikten sonra
python generate_full_report.py
```

**Çıktı:**
- `reports/FULL_RENTAL_DATA_KKTC_TIMESTAMP.xlsx`
  * 📄 TÜM KİRALIKLAR sheet
  * 🏠 Kategori sheet'leri (4 adet)
  * 🏙️ Şehir sheet'leri (6 adet)
  * 💰 Fiyat aralığı sheet'leri (3 adet)
  * 📊 İSTATİSTİKLER sheet
- `reports/FULL_RENTAL_DATA_KKTC_TIMESTAMP_summary.md`

---

## 🎯 ÖNERİM

**ADIM 1:** Mevcut Docker taramasının bitmesini bekle (2-3 dakika)
```powershell
# Terminal çıktısını kontrol et
# docker_scrape_all_rentals.ps1 durumunu izle
```

**ADIM 2:** Mevcut data ile rapor oluştur
```powershell
python generate_full_report.py
```

**ADIM 3:** Sonuçları incele
```powershell
# Excel dosyasını aç
# reports/ klasöründeki en son dosya
```

**ADIM 4:** Tam kapsamlı tarama karar ver
```powershell
# Eğer ek kategoriler (ev, işyeri) istiyorsan:
python full_rental_scan.py
```

---

## 📈 BEKLENTİLER

### Mevcut Tarama (12 config - daire+villa)
- Tahmini ilan: ~150-200
- Kategori: 2 (daire, villa)
- Süre: ÇOK YAKIN (10/12 tamamlandı)

### Tam Tarama (24 config - tümü)
- Tahmini ilan: ~250-350
- Kategori: 4 (daire, villa, ev, işyeri)
- Süre: ~15-20 dakika (baştan başlar)

---

## ⚡ HIZLI KOMUTLAR

```powershell
# Mevcut durumu kontrol
Get-Content "logs\scraper_optimized_*.log" | Select-Object -Last 20

# Rapor oluştur
python generate_full_report.py

# Tam tarama başlat
python full_rental_scan.py

# CSV kontrol
python -c "import pandas as pd; df = pd.read_csv('property_details.csv'); print(f'Toplam: {len(df)}, Kiralık: {len(df[df[\"listing_type\"]==\"Rent\"])}')"
```

---

## 🎉 TAMAMLANAN İŞLER

✅ Proje klasör yapısı düzenlendi
✅ Tam kapsamlı scraper hazırlandı (24 config)
✅ Büyük rapor sistemi oluşturuldu
✅ Docker güncellendi
✅ Kapsamlı README yazıldı
✅ Config'e yeni kategoriler eklendi

---

## 🔜 SIRA SİZDE!

Hangi seçeneği tercih ediyorsunuz?

1. **Mevcut taramayı bekle + rapor oluştur** (2-3 dakika)
2. **Tam kapsamlı tarama başlat** (15-20 dakika)
3. **İkisini de yap** (önce 1, sonra 2)

Komut verin, başlatalım! 🚀

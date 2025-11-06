"""
101evler.com KİRALIK KATEGORİLERİ - KAPSAMLI LİSTE
================================================

Site yapısı analizi ve PROPERTY_CONFIGS'den çıkarılan kategoriler.
"""

print("╔════════════════════════════════════════════════════════════╗")
print("║   101evler.com KİRALIK KATEGORİLER - SEÇİM LİSTESİ        ║")
print("╚════════════════════════════════════════════════════════════╝")
print()

# Mevcut PROPERTY_CONFIGS'den bilinen kategoriler
KNOWN_RENTAL_TYPES = {
    "kiralik-daire": {
        "type": 1,
        "subtype": [2],
        "sale": "L",
        "açıklama": "Kiralık Daire - Apartman daireleri",
        "yaygınlık": "⭐⭐⭐⭐⭐ (Çok yaygın)"
    },
    "kiralik-villa": {
        "type": 3,
        "subtype": [4],
        "sale": "L",
        "açıklama": "Kiralık Villa - Müstakil villalar",
        "yaygınlık": "⭐⭐⭐⭐ (Yaygın)"
    }
}

# Site yapısından TAHMİNİ kategoriler (101evler.com URL pattern'ine göre)
# Bunlar PROPERTY_CONFIGS'e eklenebilir
POTENTIAL_RENTAL_TYPES = {
    "kiralik-ev": {
        "type": 1,
        "subtype": [1],
        "sale": "L",
        "açıklama": "Kiralık Ev - Müstakil evler",
        "yaygınlık": "⭐⭐⭐ (Orta)",
        "durum": "⚠️  Test edilmeli"
    },
    "kiralik-isyeri": {
        "type": "?",
        "subtype": "?",
        "sale": "L",
        "açıklama": "Kiralık İşyeri - Dükkan, ofis, mağaza",
        "yaygınlık": "⭐⭐⭐ (Orta)",
        "durum": "⚠️  Test edilmeli"
    },
    "kiralik-arsa": {
        "type": "?",
        "subtype": "?",
        "sale": "L",
        "açıklama": "Kiralık Arsa - Ticari arsalar",
        "yaygınlık": "⭐ (Nadir)",
        "durum": "⚠️  Test edilmeli"
    },
    "kiralik-ofis": {
        "type": "?",
        "subtype": "?",
        "sale": "L",
        "açıklama": "Kiralık Ofis - Ofis alanları",
        "yaygınlık": "⭐⭐ (Az)",
        "durum": "⚠️  Test edilmeli"
    },
    "kiralik-depo": {
        "type": "?",
        "subtype": "?",
        "sale": "L",
        "açıklama": "Kiralık Depo - Depo ve antrepo",
        "yaygınlık": "⭐ (Nadir)",
        "durum": "⚠️  Test edilmeli"
    }
}

print("=" * 70)
print("✅ DOĞRULANMIŞ KATEGORİLER (Mevcut sistemde çalışıyor)")
print("=" * 70)

for idx, (key, info) in enumerate(KNOWN_RENTAL_TYPES.items(), 1):
    print(f"\n{idx}. {key.upper()}")
    print(f"   📝 {info['açıklama']}")
    print(f"   {info['yaygınlık']}")
    print(f"   🔧 API Params: type={info['type']}, subtype={info['subtype']}, sale={info['sale']}")

print("\n" + "=" * 70)
print("🔍 POTANSİYEL KATEGORİLER (Test edilmeli)")
print("=" * 70)

for idx, (key, info) in enumerate(POTENTIAL_RENTAL_TYPES.items(), 1):
    print(f"\n{idx}. {key.upper()} {info['durum']}")
    print(f"   📝 {info['açıklama']}")
    print(f"   {info['yaygınlık']}")

print("\n" + "=" * 70)
print("📊 ŞEHIRLER (Tüm kategoriler için geçerli)")
print("=" * 70)

cities = [
    ("lefkosa", "Lefkoşa", "Başkent - en fazla ilan"),
    ("girne", "Girne", "Kuzey sahil - turizm bölgesi"),
    ("magusa", "Mağusa", "Doğu bölge"),
    ("gazimagusa", "Gazimağusa", "Doğu sahil - üniversite bölgesi"),
    ("iskele", "İskele", "Doğu sahil - Long Beach bölgesi"),
    ("guzelyurt", "Güzelyurt", "Batı bölge")
]

for city_code, city_name, description in cities:
    print(f"  • {city_code:15s} - {city_name:15s} ({description})")

print("\n" + "=" * 70)
print("💡 ÖNERİ: ÖNCELİKLİ TARAMA STRATEJİSİ")
print("=" * 70)

print("""
1. DOĞRULANMIŞ KATEGORİLER (ŞUAN):
   ✅ kiralik-daire × 6 şehir = 6 konfigürasyon
   ✅ kiralik-villa × 6 şehir = 6 konfigürasyon
   Toplam: 12 konfigürasyon (ŞU AN ÇALIŞTIRILMASI DEVAM EDİYOR)

2. EK KATEGORİ TEST EDİLEBİLİR:
   🔍 kiralik-ev × 6 şehir = 6 konfigürasyon
   🔍 kiralik-isyeri × 6 şehir = 6 konfigürasyon
   
3. TOPLAM KAPSAMLI TARAMA:
   📊 4 kategori × 6 şehir = 24 konfigürasyon
   ⏱️  Tahmini süre: ~8-10 dakika (her biri ~20-30 saniye)
""")

print("=" * 70)
print("🚀 ÇALIŞTIRMA KOMUTU ÖRNEKLERİ")
print("=" * 70)

print("""
# Mevcut script'i devam ettir (kiralik-daire ve kiralik-villa):
docker-compose run --rm scraper python -m scraper.main

# Yeni kategori test et (örnek: kiralik-ev):
docker-compose run --rm scraper bash -c "
  python -c 'import re; 
  with open(\"src/scraper/config.py\", \"r\") as f: content = f.read();
  content = re.sub(r\"^PROPERTY_TYPE = .*\", \"PROPERTY_TYPE = \\\"kiralik-ev\\\"\", content, flags=re.MULTILINE);
  with open(\"src/scraper/config.py\", \"w\") as f: f.write(content)' &&
  python -m scraper.main
"

# Tüm kategorileri otomatik tara (script güncelle):
# download_all_rentals_optimized.py içindeki PROPERTY_TYPES listesine ekle:
# PROPERTY_TYPES = ['kiralik-daire', 'kiralik-villa', 'kiralik-ev', 'kiralik-isyeri']
""")

print("\n" + "=" * 70)
print("❓ SORU: Hangi kategorileri taramak istersiniz?")
print("=" * 70)

print("""
SEÇENEK 1: Mevcut taramayı bekle (kiralik-daire + kiralik-villa)
           ✅ Güvenli, test edilmiş
           ⏱️  ~3-4 dakika (devam ediyor)

SEÇENEK 2: Ek kategori ekle (kiralik-ev)
           🔍 Test gerekli
           ⏱️  +2-3 dakika

SEÇENEK 3: Tam tarama (daire + villa + ev + isyeri)
           📊 Maksimum kapsam
           ⏱️  ~8-10 dakika

SEÇENEK 4: Özel kategori (belirtin)
           🎯 Sizin belirlediğiniz
""")

print("=" * 70)

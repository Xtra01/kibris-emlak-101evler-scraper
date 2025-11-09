"""
NEDEN HER CONFİG İÇİN AYRI ÇALIŞTIRIYORUZ?
==========================================

101evler.com sitesinin URL yapısı ŞEHIR ve KATEGORİ bazlı çalışıyor.
Her kombinasyon FARKLI BİR URL üretir ve FARKLI veri döner.

URL YAPISI:
-----------
https://www.101evler.com/kibris/{CATEGORY}/{CITY}

ÖRNEKLERİ TEST EDELİM:
"""

import requests
from bs4 import BeautifulSoup
import time

# Test configurations
test_configs = [
    ("girne", "satilik-villa", "Girne Satılık Villa"),
    ("girne", "kiralik-daire", "Girne Kiralık Daire"),
    ("iskele", "satilik-villa", "İskele Satılık Villa"),
    ("lefkosa", "satilik-daire", "Lefkoşa Satılık Daire"),
    ("gazimagusa", "satilik-isyeri", "Gazimağusa Satılık İşyeri"),
]

print("\n" + "="*80)
print("🔍 101evler.com URL YAPISI ANALİZİ")
print("="*80)
print("\nHer şehir-kategori kombinasyonu FARKLI bir URL ve FARKLI veri döner!\n")

results = []

for city, category, name in test_configs:
    url = f"https://www.101evler.com/kibris/{category}/{city}"
    
    print(f"\n📍 TEST: {name}")
    print(f"   URL: {url}")
    
    try:
        # Request with user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Count listings
            listing_links = soup.find_all('a', href=lambda x: x and '/kibris/' in x and '-emlak/' in x)
            unique_listings = set([link['href'] for link in listing_links if 'href' in link.attrs])
            
            # Get page title
            title = soup.find('title')
            title_text = title.text.strip() if title else "N/A"
            
            print(f"   ✅ STATUS: 200 OK")
            print(f"   📊 İlan Sayısı (sayfa 1): ~{len(unique_listings)} ilan")
            print(f"   📄 Sayfa Başlığı: {title_text[:60]}...")
            
            results.append({
                'name': name,
                'url': url,
                'status': 200,
                'listings': len(unique_listings),
                'title': title_text
            })
            
        elif response.status_code == 404:
            print(f"   ⚠️  STATUS: 404 - Bu kategori bu şehirde YOK!")
            results.append({
                'name': name,
                'url': url,
                'status': 404,
                'listings': 0,
                'title': 'Not Found'
            })
        else:
            print(f"   ❌ STATUS: {response.status_code}")
            results.append({
                'name': name,
                'url': url,
                'status': response.status_code,
                'listings': 0,
                'title': 'Error'
            })
            
    except Exception as e:
        print(f"   ❌ HATA: {e}")
        results.append({
            'name': name,
            'url': url,
            'status': 'error',
            'listings': 0,
            'title': str(e)
        })
    
    time.sleep(1)  # Rate limiting

print("\n" + "="*80)
print("📊 ÖZET: NEDEN AYRI ÇALIŞTIRMAK GEREKİYOR?")
print("="*80)

print("\n1️⃣  HER URL FARKLI VERİ DÖNER:")
print("-" * 80)
for r in results:
    if r['status'] == 200:
        print(f"   ✅ {r['name']:30s} → {r['listings']:3d} ilan")
    elif r['status'] == 404:
        print(f"   ⚠️  {r['name']:30s} → Kategori yok (404)")

print("\n2️⃣  URL YAPISI:")
print("-" * 80)
print("   Pattern: https://www.101evler.com/kibris/{CATEGORY}/{CITY}")
print("\n   Örnekler:")
for r in results[:3]:
    print(f"   • {r['url']}")

print("\n3️⃣  AYNI ŞEHİRDE FARKLI KATEGORİLER = FARKLI İLANLAR:")
print("-" * 80)
girne_configs = [r for r in results if 'Girne' in r['name']]
for r in girne_configs:
    if r['status'] == 200:
        print(f"   • {r['name']:30s} → {r['listings']} ilan")

print("\n4️⃣  AYNI KATEGORİDE FARKLI ŞEHİRLER = FARKLI İLANLAR:")
print("-" * 80)
villa_configs = [r for r in results if 'Villa' in r['name']]
for r in villa_configs:
    if r['status'] == 200:
        print(f"   • {r['name']:30s} → {r['listings']} ilan")

print("\n" + "="*80)
print("🎯 SONUÇ:")
print("="*80)
print("""
Her şehir-kategori kombinasyonu FARKLI bir URL'ye karşılık gelir.
Her URL'de FARKLI ilanlar vardır.

Örnek:
  - girne/satilik-villa    → Girne'deki satılık villalar
  - girne/kiralik-daire    → Girne'deki kiralık daireler (FARKLI ilanlar!)
  - iskele/satilik-villa   → İskele'deki satılık villalar (FARKLI şehir!)

TÜM verileri çekmek için HER kombinasyonu AYRI AYRI taramak GEREKLİ!

Toplam Kombinasyon: 6 şehir × 12 kategori = 72 farklı URL
(Bazı kategoriler bazı şehirlerde olmayabilir - 404 döner)
""")

print("\n" + "="*80)
print("✅ ANALİZ TAMAMLANDI")
print("="*80)

#!/usr/bin/env python3
"""
451524 İlanının Hangi Sayfalarda Göründüğünü Test Et
"""

import requests
from bs4 import BeautifulSoup
import re

def check_listing_in_page(url, target_id="451524"):
    """Bir sayfada belirli ID'yi ara"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if target_id in href and 'daire' in href:
                return True, f"BULUNDU: {href}"
        
        return False, "Bulunamadı"
    except Exception as e:
        return False, f"HATA: {e}"

def main():
    print("="*70)
    print("🔍 451524 İLANI ARAMA TESTİ")
    print("="*70)
    print()
    
    test_urls = [
        # Genel Girne
        ("Girne Genel (sayfa 1)", "https://www.101evler.com/kibris/kiralik-emlak/girne?page=1&sort=id"),
        ("Girne Genel (sayfa 10)", "https://www.101evler.com/kibris/kiralik-emlak/girne?page=10&sort=id"),
        
        # Girne Daire
        ("Girne Daire (sayfa 1)", "https://www.101evler.com/kibris/kiralik-emlak/girne/daire?page=1&sort=id"),
        ("Girne Daire (sayfa 5)", "https://www.101evler.com/kibris/kiralik-emlak/girne/daire?page=5&sort=id"),
        ("Girne Daire (sayfa 10)", "https://www.101evler.com/kibris/kiralik-emlak/girne/daire?page=10&sort=id"),
        
        # Alsancak
        ("Alsancak Genel", "https://www.101evler.com/kibris/kiralik-emlak/girne-alsancak?page=1&sort=id"),
        ("Alsancak Daire", "https://www.101evler.com/kibris/kiralik-emlak/girne-alsancak/daire?page=1&sort=id"),
    ]
    
    for name, url in test_urls:
        print(f"📍 Test: {name}")
        print(f"   URL: {url}")
        found, message = check_listing_in_page(url)
        if found:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
        print()
    
    print("="*70)
    print("🎯 SONUÇ: Hangi URL'de bulunduğunu göreceksiniz")
    print("="*70)

if __name__ == "__main__":
    main()

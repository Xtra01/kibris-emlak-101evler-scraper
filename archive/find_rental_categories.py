#!/usr/bin/env python3
"""
101evler.com'daki TÜM KİRALIK KATEGORİLERİNİ BUL
==============================================

Bu script, 101evler.com sitesindeki tüm kiralık emlak kategorilerini bulur.
"""

import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import re

async def find_rental_categories():
    """101evler.com'dan tüm kiralık kategorileri bul"""
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   101evler.com KİRALIK KATEGORİLER                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    async with AsyncWebCrawler() as crawler:
        print("📡 101evler.com ana sayfası çekiliyor...")
        result = await crawler.arun(
            url='https://www.101evler.com',
            use_playwright=True
        )
        
        if not result or not result.html:
            print("❌ Sayfa çekilemedi!")
            return
        
        print("✅ Sayfa çekildi, parse ediliyor...")
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Tüm linkleri bul
        all_links = soup.find_all('a', href=True)
        
        # Kiralık kategorilerini filtrele
        rental_categories = {}
        
        for link in all_links:
            href = link['href']
            text = link.get_text(strip=True)
            
            # /kibris/kiralik-XXX formatındaki linkleri bul
            if '/kibris/kiralik-' in href:
                # Kategori ismini çıkar (kiralik-XXX)
                match = re.search(r'/kibris/(kiralik-[\w-]+)', href)
                if match:
                    category = match.group(1)
                    if category not in rental_categories:
                        rental_categories[category] = {
                            'url': href,
                            'text': text or 'N/A'
                        }
        
        # Kategorileri sırala ve göster
        print()
        print("🏠 BULUNAN KİRALIK KATEGORİLER:")
        print("="*60)
        
        sorted_categories = sorted(rental_categories.items())
        
        for idx, (category, info) in enumerate(sorted_categories, 1):
            print(f"{idx:2d}. {category:30s} | {info['text']}")
        
        print("="*60)
        print(f"Toplam {len(rental_categories)} kategori bulundu")
        print()
        
        # Şehirler için örnekler
        print("📍 ŞEHİRLER:")
        print("   - lefkosa, girne, magusa, gazimagusa, iskele, guzelyurt")
        print()
        
        # Kullanım örnekleri
        print("💡 KULLANIM ÖRNEĞİ:")
        print("   docker-compose run --rm scraper \\")
        print("     bash -c 'sed -i \"s/^PROPERTY_TYPE = .*/PROPERTY_TYPE = \\\"kiralik-daire\\\"/\" src/scraper/config.py && \\")
        print("              python -m scraper.main'")
        print()
        
        return rental_categories

if __name__ == '__main__':
    asyncio.run(find_rental_categories())

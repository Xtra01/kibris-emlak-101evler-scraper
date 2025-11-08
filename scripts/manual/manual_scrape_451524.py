#!/usr/bin/env python3
"""
451524 ilanını MANUEL olarak çek ve kaydet
"""

import asyncio
from crawl4ai import AsyncWebCrawler
import os

async def manual_scrape():
    """451524 ilanını manuel çek"""
    
    target_url = "https://www.101evler.com/kibris/kiralik-emlak/girne-alsancak-daire-451524.html"
    output_file = "listings/451524.html"
    
    print("="*70)
    print("🎯 MANUEL SCRAPE - 451524")
    print("="*70)
    print(f"\nHedef URL: {target_url}")
    print(f"Çıktı: {output_file}\n")
    
    async with AsyncWebCrawler() as crawler:
        print("🌐 Sayfa çekiliyor (Playwright ile)...")
        try:
            result = await crawler.arun(
                url=target_url,
                bypass_cache=True,
                js_code="""
                // Sayfanın tamamen yüklenmesini bekle
                await new Promise(r => setTimeout(r, 2000));
                """
            )
            
            if result and result.html:
                html = result.html
                print(f"✅ HTML alındı ({len(html)} karakter)")
                
                # Kaydet
                os.makedirs("listings", exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                print(f"💾 Dosya kaydedildi: {output_file}")
                
                # İçerik kontrolü
                if "451524" in html:
                    print("✅ İlan ID doğrulandı")
                if "Alsancak" in html:
                    print("✅ Konum doğrulandı")
                if "Kiralık" in html or "Kiralik" in html:
                    print("✅ Tip doğrulandı")
                    
                print(f"\n📊 HTML başlığı: {html[:200]}")
                
            else:
                print("❌ HTML alınamadı!")
                
        except Exception as e:
            print(f"❌ HATA: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ Manuel scrape tamamlandı!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(manual_scrape())

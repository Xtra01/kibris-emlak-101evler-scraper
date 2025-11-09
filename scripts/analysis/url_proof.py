#!/usr/bin/env python3
"""Prove URL structure for different configs"""
import sys
from pathlib import Path

sys.path.insert(0, '/app')
from src.emlak_scraper.core import config

print("="*80)
print("URL YAPISI KANITLARI - 101evler.com")
print("="*80)

test_cases = [
    ("girne", "satilik-villa", "Girne Satılık Villa"),
    ("girne", "kiralik-daire", "Girne Kiralık Daire"),
    ("iskele", "satilik-villa", "İskele Satılık Villa"),
    ("lefkosa", "satilik-daire", "Lefkoşa Satılık Daire"),
]

print("\nHER KOMBİNASYON FARKLI URL ÜRETİYOR:\n")
for city, category, name in test_cases:
    url = config.get_base_search_url(city, category)
    print(f"{name:30s} → {url}")

print("\n" + "="*80)
print("KANIT: Scraped dosyalar (girne/satilik-villa):")
print("="*80)

html_dir = Path("/app/data/raw/listings/girne/satilik-villa")
if html_dir.exists():
    files = sorted(html_dir.glob("*.html"))[:5]
    print("\nİlk 5 dosya:")
    for f in files:
        print(f"  • {f.name} (Property ID: {f.stem})")
    
    total = len(list(html_dir.glob("*.html")))
    print(f"\nToplam: {total} dosya scraped edildi")
else:
    print("  Dizin henüz yok")

print("\n" + "="*80)
print("SONUÇ:")
print("="*80)
print("""
Bu ID'ler sadece girne/satilik-villa için!
Başka config (örn: iskele/satilik-villa) farklı ID'ler dönecek!

Her config = Farklı URL = Farklı ilanlar
Bu yüzden HER config AYRI AYRI çalıştırılmalı!
""")
print("="*80)

#!/usr/bin/env python3
"""
🚀 QUICK SITE TEST - 3 configs only
Test the analyzer with just 3 configs to verify it works
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from emlak_scraper.core.config import get_base_search_url
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
import re


# Just 3 test configs
TEST_CONFIGS = [
    ("girne", "satilik-villa"),
    ("iskele", "satilik-daire"),
    ("lefkosa", "kiralik-daire"),
]


def extract_total_from_html(html: str) -> dict:
    """Extract listing count from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    result = {"total": 0, "method": "none"}
    
    # Try patterns
    patterns = [
        (r'(\d+)\s*ilan', "ilan_count"),
        (r'Toplam[:\s]*(\d+)', "toplam"),
        (r'(\d+)\s*results?', "results"),
    ]
    
    for pattern, method in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["total"] = int(match.group(1))
            result["method"] = method
            break
    
    return result


async def test_config(crawler, city, category):
    """Test one config"""
    url = get_base_search_url(city, category)
    print(f"\n🔍 Testing: {city}/{category}")
    print(f"   URL: {url}")
    
    try:
        response = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until="networkidle",
                page_timeout=30000,
            )
        )
        
        if not response.success:
            print(f"   ❌ Failed")
            return None
        
        if response.status_code == 404:
            print(f"   ⚠️  404")
            return {"city": city, "category": category, "status": "404"}
        
        info = extract_total_from_html(response.html)
        print(f"   ✅ Found: {info['total']} listings (method: {info['method']})")
        
        return {
            "city": city,
            "category": category,
            "status": "success",
            "total": info["total"],
            "method": info["method"]
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


async def main():
    """Run quick test"""
    print("\n" + "="*60)
    print("🚀 QUICK SITE TEST - 3 Configs")
    print("="*60)
    
    results = []
    
    browser_config = BrowserConfig(headless=True, verbose=False)
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for city, category in TEST_CONFIGS:
            result = await test_config(crawler, city, category)
            if result:
                results.append(result)
            await asyncio.sleep(2)
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    for r in results:
        if r["status"] == "success":
            print(f"✅ {r['city']}/{r['category']}: {r['total']} listings")
        else:
            print(f"⚠️  {r['city']}/{r['category']}: {r['status']}")
    
    print(f"\n✅ Test complete! {len([r for r in results if r['status'] == 'success'])}/3 successful")


if __name__ == "__main__":
    asyncio.run(main())

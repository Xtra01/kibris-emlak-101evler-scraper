#!/usr/bin/env python3
"""
🔬 DEEP SITE ANALYZER
====================
Ultra-intelligent site structure discovery for 101evler.com

STRATEGY:
1. Fetch first page of EACH config (72 total)
2. Extract: Total listing count, pagination info, 404 status
3. Generate comprehensive statistics JSON
4. Calculate expected total and create progress baseline

This enables:
- Accurate progress tracking during full scan
- Smart config filtering (skip 404s)
- ETA calculation based on real data
- Professional progress reporting
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from emlak_scraper.core.config import get_base_search_url, CITIES, PROPERTY_TYPES
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup


class DeepSiteAnalyzer:
    """Ultra-intelligent site structure analyzer"""
    
    def __init__(self):
        self.results = {
            "scan_date": datetime.now().isoformat(),
            "total_configs": 0,
            "working_configs": 0,
            "failed_configs": 0,
            "configs": {},
            "statistics": {
                "total_expected_listings": 0,
                "total_expected_pages": 0,
                "estimated_scan_time_minutes": 0
            }
        }
    
    def extract_pagination_info(self, html: str) -> Dict:
        """
        🔍 ULTRA INTELLIGENCE: Extract all possible pagination indicators
        
        Strategy:
        1. Look for "Toplam X ilan" or "X results"
        2. Find pagination: "Sayfa 1/Y" or page buttons
        3. Extract per-page count (usually 20)
        4. Calculate total pages
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        info = {
            "total_listings": 0,
            "total_pages": 1,
            "per_page": 20,  # Default assumption
            "indicators_found": []
        }
        
        # Method 1: Search for total count text
        # Turkish: "1234 ilan", "Toplam 1234", "1234 sonuç"
        # English: "1234 results", "Total: 1234"
        text = soup.get_text()
        
        patterns = [
            r'(\d+)\s*ilan',
            r'Toplam[:\s]*(\d+)',
            r'(\d+)\s*sonuç',
            r'(\d+)\s*results?',
            r'Total[:\s]*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                if count > 0:
                    info["total_listings"] = count
                    info["indicators_found"].append(f"text_pattern: {pattern}")
                    break
        
        # Method 2: Pagination component
        # Look for: <span>Sayfa 1/15</span> or similar
        pagination_patterns = [
            r'Sayfa\s*1\s*/\s*(\d+)',
            r'Page\s*1\s*of\s*(\d+)',
            r'1\s*/\s*(\d+)\s*sayfa',
        ]
        
        for pattern in pagination_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                pages = int(match.group(1))
                info["total_pages"] = pages
                info["indicators_found"].append(f"pagination: {pattern}")
                # If we have pages but no total, estimate
                if info["total_listings"] == 0:
                    info["total_listings"] = pages * info["per_page"]
                break
        
        # Method 3: Count actual listings on first page
        # Common selectors for property cards
        listing_selectors = [
            '.property-card',
            '.listing-item',
            '.ilan-item',
            '[data-property-id]',
            '.real-estate-card',
        ]
        
        max_found = 0
        for selector in listing_selectors:
            found = len(soup.select(selector))
            if found > max_found:
                max_found = found
        
        if max_found > 0:
            info["per_page"] = max_found
            info["indicators_found"].append(f"listing_count_on_page: {max_found}")
            # Recalculate if needed
            if info["total_listings"] > 0 and info["total_pages"] == 1:
                info["total_pages"] = (info["total_listings"] + max_found - 1) // max_found
        
        # Method 4: Check for "No results" indicators
        no_results_texts = [
            'ilan bulunamadı',
            'sonuç bulunamadı',
            'no results',
            'no listings',
            'hiç ilan yok',
        ]
        
        for no_result_text in no_results_texts:
            if no_result_text in text.lower():
                info["total_listings"] = 0
                info["total_pages"] = 0
                info["indicators_found"].append("no_results_message")
                break
        
        return info
    
    async def analyze_config(
        self,
        crawler: AsyncWebCrawler,
        city: str,
        category: str
    ) -> Dict:
        """Analyze a single city-category configuration"""
        
        url = get_base_search_url(city, category)
        config_key = f"{city}/{category}"
        
        print(f"\n🔍 Analyzing: {config_key}")
        print(f"   URL: {url}")
        
        result = {
            "city": city,
            "category": category,
            "url": url,
            "status": "unknown",
            "total_listings": 0,
            "total_pages": 0,
            "per_page": 20,
            "indicators_found": [],
            "error": None
        }
        
        try:
            # Fetch first page
            response = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    wait_until="networkidle",
                    page_timeout=30000,
                    wait_for_images=False
                )
            )
            
            if not response.success:
                result["status"] = "failed"
                result["error"] = "Fetch failed"
                print(f"   ❌ Failed to fetch")
                return result
            
            # Check for 404
            if response.status_code == 404:
                result["status"] = "404"
                print(f"   ⚠️  404 NOT FOUND")
                return result
            
            # Extract pagination info
            info = self.extract_pagination_info(response.html)
            
            result.update(info)
            
            # Determine status
            if result["total_listings"] == 0 and len(result["indicators_found"]) == 0:
                result["status"] = "no_data"
                print(f"   ⚠️  No data (possibly empty category)")
            elif result["total_listings"] > 0:
                result["status"] = "success"
                print(f"   ✅ {result['total_listings']} listings, {result['total_pages']} pages")
                print(f"   📊 Indicators: {', '.join(result['indicators_found'])}")
            else:
                result["status"] = "uncertain"
                print(f"   ⚠️  Uncertain status")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        return result
    
    async def analyze_all_configs(self):
        """🚀 MAIN ANALYSIS: Scan all 72 configurations"""
        
        print("\n" + "="*80)
        print("🔬 DEEP SITE ANALYZER - ULTRA INTELLIGENCE MODE")
        print("="*80)
        print(f"\n📋 Total configs to analyze: {len(CITIES) * len(PROPERTY_TYPES)}")
        print(f"   Cities: {len(CITIES)} - {', '.join(CITIES)}")
        print(f"   Categories: {len(PROPERTY_TYPES)}")
        print("\n⏱️  Estimated time: ~5-10 minutes (72 configs × 5-8 seconds each)")
        print("\n" + "="*80 + "\n")
        
        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            
            for city in CITIES:
                print(f"\n{'='*60}")
                print(f"📍 CITY: {city.upper()}")
                print(f"{'='*60}")
                
                for category in PROPERTY_TYPES:
                    config_key = f"{city}/{category}"
                    
                    result = await self.analyze_config(crawler, city, category)
                    self.results["configs"][config_key] = result
                    self.results["total_configs"] += 1
                    
                    if result["status"] == "success":
                        self.results["working_configs"] += 1
                        self.results["statistics"]["total_expected_listings"] += result["total_listings"]
                        self.results["statistics"]["total_expected_pages"] += result["total_pages"]
                    elif result["status"] in ["404", "failed", "error"]:
                        self.results["failed_configs"] += 1
                    
                    # Small delay between requests
                    await asyncio.sleep(1)
        
        # Calculate estimated scan time
        # Assumption: ~3 seconds per page (conservative)
        total_pages = self.results["statistics"]["total_expected_pages"]
        self.results["statistics"]["estimated_scan_time_minutes"] = (total_pages * 3) / 60
        
        print("\n" + "="*80)
        print("📊 ANALYSIS COMPLETE - FINAL STATISTICS")
        print("="*80)
        print(f"\n✅ Working configs: {self.results['working_configs']}/{self.results['total_configs']}")
        print(f"❌ Failed configs: {self.results['failed_configs']}/{self.results['total_configs']}")
        print(f"\n📈 Expected totals:")
        print(f"   Total listings: {self.results['statistics']['total_expected_listings']:,}")
        print(f"   Total pages: {self.results['statistics']['total_expected_pages']:,}")
        print(f"   Estimated scan time: {self.results['statistics']['estimated_scan_time_minutes']:.1f} minutes")
        print("\n" + "="*80 + "\n")
    
    def save_results(self, output_path: str = "data/site_analysis.json"):
        """Save analysis results to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file.absolute()}")
        
        # Also create a human-readable summary
        summary_path = output_file.with_suffix('.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("DEEP SITE ANALYSIS SUMMARY\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Scan Date: {self.results['scan_date']}\n\n")
            
            f.write("OVERVIEW:\n")
            f.write(f"  Total Configs: {self.results['total_configs']}\n")
            f.write(f"  Working: {self.results['working_configs']}\n")
            f.write(f"  Failed: {self.results['failed_configs']}\n\n")
            
            f.write("EXPECTED TOTALS:\n")
            f.write(f"  Listings: {self.results['statistics']['total_expected_listings']:,}\n")
            f.write(f"  Pages: {self.results['statistics']['total_expected_pages']:,}\n")
            f.write(f"  Est. Time: {self.results['statistics']['estimated_scan_time_minutes']:.1f} min\n\n")
            
            f.write("="*80 + "\n")
            f.write("DETAILED BREAKDOWN BY CONFIG:\n")
            f.write("="*80 + "\n\n")
            
            for config_key, data in sorted(self.results['configs'].items()):
                status_emoji = {
                    "success": "✅",
                    "404": "❌",
                    "failed": "⚠️",
                    "no_data": "⚠️",
                    "error": "❌",
                    "uncertain": "❓"
                }.get(data["status"], "❓")
                
                f.write(f"{status_emoji} {config_key}\n")
                f.write(f"   Status: {data['status']}\n")
                if data["status"] == "success":
                    f.write(f"   Listings: {data['total_listings']:,}\n")
                    f.write(f"   Pages: {data['total_pages']}\n")
                    f.write(f"   Indicators: {', '.join(data['indicators_found'])}\n")
                elif data.get("error"):
                    f.write(f"   Error: {data['error']}\n")
                f.write("\n")
        
        print(f"📄 Summary saved to: {summary_path.absolute()}")


async def main():
    """Run deep site analysis"""
    analyzer = DeepSiteAnalyzer()
    
    try:
        await analyzer.analyze_all_configs()
        analyzer.save_results()
        
        print("\n✨ Analysis complete! Next steps:")
        print("   1. Review data/site_analysis.json for full details")
        print("   2. Use this data to create smart scan with progress tracking")
        print("   3. Skip failed configs automatically")
        print("   4. Show real-time progress: X/Y listings (Z%)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        print("💾 Saving partial results...")
        analyzer.save_results("data/site_analysis_partial.json")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

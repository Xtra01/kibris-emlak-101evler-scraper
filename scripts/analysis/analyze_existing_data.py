#!/usr/bin/env python3
"""
📊 EXISTING DATA ANALYZER
========================
Analyze ALREADY SCRAPED data to get actual statistics
Instead of fetching new pages, analyze what we already have!

STRATEGY:
1. Scan data/raw/listings/{city}/{category}/ folders
2. Count HTML files in each config
3. This gives us ACTUAL scraped data statistics
4. Much faster than web scraping (instant!)
5. Can estimate remaining work based on known totals
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def analyze_existing_data(base_path: str = "data/raw/listings"):
    """Analyze already scraped data"""
    
    base = Path(base_path)
    
    results = {
        "analysis_date": datetime.now().isoformat(),
        "base_path": str(base.absolute()),
        "configs": {},
        "statistics": {
            "total_configs_found": 0,
            "total_files_scraped": 0,
            "configs_with_data": 0,
            "configs_empty": 0
        }
    }
    
    print("\n" + "="*80)
    print("📊 EXISTING DATA ANALYZER - Instant Statistics")
    print("="*80)
    print(f"\nScanning: {base.absolute()}")
    print()
    
    if not base.exists():
        print(f"❌ Directory not found: {base.absolute()}")
        return results
    
    # Scan all city folders
    for city_dir in sorted(base.iterdir()):
        if not city_dir.is_dir():
            continue
        
        city = city_dir.name
        print(f"\n{'='*60}")
        print(f"📍 CITY: {city.upper()}")
        print(f"{'='*60}")
        
        # Scan all category folders
        for category_dir in sorted(city_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            
            category = category_dir.name
            
            # Count HTML files
            html_files = list(category_dir.glob("*.html"))
            count = len(html_files)
            
            config_key = f"{city}/{category}"
            results["configs"][config_key] = {
                "city": city,
                "category": category,
                "files_scraped": count,
                "path": str(category_dir.absolute())
            }
            
            results["statistics"]["total_configs_found"] += 1
            results["statistics"]["total_files_scraped"] += count
            
            if count > 0:
                results["statistics"]["configs_with_data"] += 1
                status = "✅"
            else:
                results["statistics"]["configs_empty"] += 1
                status = "⚠️"
            
            print(f"{status} {config_key:40} {count:>5} files")
    
    print("\n" + "="*80)
    print("📊 FINAL STATISTICS")
    print("="*80)
    print(f"\nConfigs found: {results['statistics']['total_configs_found']}")
    print(f"Configs with data: {results['statistics']['configs_with_data']}")
    print(f"Empty configs: {results['statistics']['configs_empty']}")
    print(f"\n✅ Total files scraped: {results['statistics']['total_files_scraped']:,}")
    print("\n" + "="*80)
    
    return results


def save_results(results: dict, output_path: str = "data/existing_data_analysis.json"):
    """Save analysis results"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file.absolute()}")
    
    # Create summary
    summary_path = output_file.with_suffix('.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("EXISTING DATA ANALYSIS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Analysis Date: {results['analysis_date']}\n")
        f.write(f"Base Path: {results['base_path']}\n\n")
        
        f.write("STATISTICS:\n")
        f.write(f"  Total Configs: {results['statistics']['total_configs_found']}\n")
        f.write(f"  With Data: {results['statistics']['configs_with_data']}\n")
        f.write(f"  Empty: {results['statistics']['configs_empty']}\n")
        f.write(f"  Total Files: {results['statistics']['total_files_scraped']:,}\n\n")
        
        f.write("="*80 + "\n")
        f.write("BREAKDOWN BY CONFIG:\n")
        f.write("="*80 + "\n\n")
        
        for config_key, data in sorted(results['configs'].items()):
            status = "✅" if data['files_scraped'] > 0 else "⚠️"
            f.write(f"{status} {config_key:40} {data['files_scraped']:>5} files\n")
    
    print(f"📄 Summary saved to: {summary_path.absolute()}")


def main():
    """Run analysis"""
    print("\n🔍 Starting EXISTING DATA analysis...")
    print("⚡ This is INSTANT - no web scraping needed!\n")
    
    results = analyze_existing_data()
    
    if results['statistics']['total_files_scraped'] > 0:
        save_results(results)
        
        print("\n✨ Analysis complete!")
        print("\n💡 Next steps:")
        print("   1. Compare with expected totals (if known)")
        print("   2. Identify configs that need (re)scraping")
        print("   3. Calculate remaining work")
    else:
        print("\n⚠️  No scraped data found!")
        print("    Run a scan first to collect data.")


if __name__ == "__main__":
    main()

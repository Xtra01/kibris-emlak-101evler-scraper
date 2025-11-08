#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
101evler.com sitesinde hangi kategorilerin gerçekten var olduğunu kontrol et
"""
import requests
from bs4 import BeautifulSoup
import time
import sys
import io

# Windows UTF-8 fix
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Test edilecek kombinasyonlar
CITIES = ['girne', 'iskele', 'lefkosa', 'gazimagusa', 'guzelyurt', 'lefke']

CATEGORIES = [
    'satilik-daire',
    'satilik-villa',
    'satilik-ev',
    'satilik-arsa',
    'satilik-arazi',
    'satilik-isyeri',
    'satilik-proje',
    'kiralik-daire',
    'kiralik-villa',
    'kiralik-ev',
    'kiralik-isyeri',
    'kiralik-gunluk'
]

def check_category(city, category):
    """Bir kategorinin var olup olmadığını kontrol et"""
    # Correct URL format: /kibris/{property_type}/{city}
    url = f"https://www.101evler.com/kibris/{category}/{city}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Sayfa var, ilan sayısını bul
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Toplam ilan sayısını bul
            result_text = soup.find('span', class_='count')
            if result_text:
                count = result_text.text.strip()
                return {'exists': True, 'count': count, 'status': 200}
            else:
                # Sayfa var ama ilan yok
                return {'exists': True, 'count': '0', 'status': 200}
        elif response.status_code == 404:
            return {'exists': False, 'count': '0', 'status': 404}
        else:
            return {'exists': False, 'count': '0', 'status': response.status_code}
            
    except Exception as e:
        return {'exists': False, 'count': '0', 'error': str(e)}

def main():
    """Ana fonksiyon"""
    print("=" * 80)
    print("101evler.com - CATEGORY VALIDATION")
    print("=" * 80)
    print(f"\nTesting {len(CITIES)} cities × {len(CATEGORIES)} categories = {len(CITIES) * len(CATEGORIES)} combinations\n")
    
    results = {}
    total = len(CITIES) * len(CATEGORIES)
    current = 0
    
    valid_configs = []
    invalid_configs = []
    
    for city in CITIES:
        results[city] = {}
        
        for category in CATEGORIES:
            current += 1
            print(f"[{current}/{total}] Testing: {city}/{category}... ", end='', flush=True)
            
            result = check_category(city, category)
            results[city][category] = result
            
            if result['exists']:
                status = f"✅ EXISTS ({result['count']} ilanlar)"
                valid_configs.append({
                    'city': city,
                    'category': category,
                    'count': result['count']
                })
            else:
                error_msg = result.get('error', f"Status: {result.get('status', 'unknown')}")
                status = f"❌ NOT FOUND ({error_msg})"
                invalid_configs.append({
                    'city': city,
                    'category': category,
                    'reason': error_msg
                })
            
            print(status)
            time.sleep(0.5)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Valid configs: {len(valid_configs)}/{total}")
    print(f"❌ Invalid configs: {len(invalid_configs)}/{total}")
    print(f"📊 Success rate: {len(valid_configs)/total*100:.1f}%")
    
    # Valid configs by city
    print("\n" + "-" * 80)
    print("VALID CONFIGURATIONS BY CITY:")
    print("-" * 80)
    
    for city in CITIES:
        city_valid = [c for c in valid_configs if c['city'] == city]
        if city_valid:
            print(f"\n{city.upper()}:")
            for config in city_valid:
                print(f"  - {config['category']}: {config['count']} ilanlar")
    
    # Invalid configs
    print("\n" + "-" * 80)
    print("INVALID CONFIGURATIONS:")
    print("-" * 80)
    
    for city in CITIES:
        city_invalid = [c for c in invalid_configs if c['city'] == city]
        if city_invalid:
            print(f"\n{city.upper()}:")
            for config in city_invalid:
                print(f"  - {config['category']}")
    
    # Optimization recommendation
    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATION:")
    print("=" * 80)
    print(f"\n🎯 RUN ONLY {len(valid_configs)} VALID CONFIGS")
    print(f"⏱️  SAVE ~{len(invalid_configs) * 15} SECONDS (skip invalid checks)")
    print(f"📉 REDUCE failure rate from {len(invalid_configs)/total*100:.1f}% to 0%")

if __name__ == '__main__':
    main()

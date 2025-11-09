#!/usr/bin/env python3
"""
Create sample Excel by running parser on first 10 HTML files
"""
import asyncio
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.emlak_scraper.core import parser

async def create_sample():
    """Create sample by parsing first 10 HTML files"""
    
    # Get first 10 HTML files from girne/satilik-villa
    html_dir = Path('data/raw/listings/girne/satilik-villa')
    if not html_dir.exists():
        print(f"❌ Directory not found: {html_dir}")
        return False
    
    html_files = sorted(html_dir.glob('*.html'))[:10]
    print(f'Found {len(html_files)} HTML files for sample')
    
    if len(html_files) == 0:
        print("❌ No HTML files found")
        return False
    
    # Fetch exchange rates
    print("Fetching exchange rates...")
    exchange_rates = parser.fetch_exchange_rates()
    
    # Parse files
    parsed_data = []
    for html_file in html_files:
        try:
            # extract_details expects just the filename, not full path
            # and reads from parser.HTML_FOLDER
            # So we need to temporarily change HTML_FOLDER
            original_folder = parser.HTML_FOLDER
            parser.HTML_FOLDER = str(html_dir)
            
            result = await parser.extract_details(html_file.name)
            
            parser.HTML_FOLDER = original_folder
            
            if result:
                # Convert to flat dict for DataFrame
                flat_result = {k: v for k, v in result.items() if not k.startswith('_')}
                parsed_data.append(flat_result)
                print(f'✓ Parsed: {html_file.name}')
            else:
                print(f'✗ No data: {html_file.name}')
        except Exception as e:
            print(f'✗ Failed {html_file.name}: {e}')
            import traceback
            traceback.print_exc()
    
    # Create sample files
    if parsed_data:
        df = pd.DataFrame(parsed_data)
        
        sample_dir = Path('data_samples')
        sample_dir.mkdir(exist_ok=True)
        
        # Save CSV
        csv_path = sample_dir / 'sample_girne_satilik_villa_10.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f'\n✅ Created CSV: {csv_path}')
        
        # Save Excel
        excel_path = sample_dir / 'sample_girne_satilik_villa_10.xlsx'
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f'✅ Created Excel: {excel_path}')
        
        print(f'\n📊 Total records: {len(parsed_data)}')
        print(f'📋 Columns ({len(df.columns)}): {", ".join(list(df.columns)[:10])}...')
        
        print(f'\n--- FIRST 3 ROWS PREVIEW ---')
        # Show key columns
        key_cols = ['title', 'price', 'currency', 'area_m2', 'location', 'property_type']
        available_cols = [col for col in key_cols if col in df.columns]
        if available_cols:
            print(df[available_cols].head(3).to_string())
        else:
            print(df.head(3).to_string())
        
        return True
    else:
        print('\n❌ No data parsed')
        return False

if __name__ == '__main__':
    success = asyncio.run(create_sample())
    sys.exit(0 if success else 1)

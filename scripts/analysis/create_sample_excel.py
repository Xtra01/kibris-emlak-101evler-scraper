#!/usr/bin/env python3
"""
Create sample Excel from first 10 scraped HTML files
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.emlak_scraper.core import parser
import pandas as pd

def create_sample():
    # Get first 10 HTML files
    html_dir = Path('data/raw/listings/girne/satilik-villa')
    html_files = sorted(html_dir.glob('*.html'))[:10]
    print(f'Found {len(html_files)} HTML files for sample')
    
    # Parse them
    parsed_data = []
    for html_file in html_files:
        try:
            data = parser.parse_html_file(str(html_file))
            if data:
                parsed_data.append(data)
                print(f'✓ Parsed: {html_file.name}')
        except Exception as e:
            print(f'✗ Failed {html_file.name}: {e}')
    
    # Create sample Excel
    if parsed_data:
        df = pd.DataFrame(parsed_data)
        sample_dir = Path('data_samples')
        sample_dir.mkdir(exist_ok=True)
        excel_path = sample_dir / 'sample_girne_satilik_villa_10.xlsx'
        
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f'\n✅ Created sample Excel with {len(parsed_data)} records')
        print(f'📁 Location: {excel_path}')
        print(f'\nColumns: {list(df.columns)}')
        print(f'\n--- FIRST 3 ROWS PREVIEW ---')
        print(df.head(3).to_string())
        return True
    else:
        print('❌ No data parsed')
        return False

if __name__ == '__main__':
    success = create_sample()
    sys.exit(0 if success else 1)

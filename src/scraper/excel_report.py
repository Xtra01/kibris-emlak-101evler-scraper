import os
import pandas as pd
from datetime import datetime
from scraper.report import fetch_exchange_rates, add_computed_columns, DONUM_M2

REPORTS_DIR = 'reports'
CSV_FILE = 'property_details.csv'
OUTPUT_XLSX = os.path.join(REPORTS_DIR, 'market_report.xlsx')

EVLEK_M2 = DONUM_M2 / 4.0
FT2_TO_M2 = 0.092903


def ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)


def quick_stats(series: pd.Series):
    s = pd.to_numeric(series, errors='coerce').dropna()
    if s.empty:
        return None
    return {
        'count': int(s.count()),
        'min': float(s.min()),
        'p25': float(s.quantile(0.25)),
        'median': float(s.median() ),
        'p75': float(s.quantile(0.75)),
        'max': float(s.max()),
        'mean': float(s.mean()),
    }


def is_guzelyurt(x):
    if pd.isna(x):
        return False
    t = str(x).lower().replace('ü', 'u').strip()
    return 'guzelyurt' in t


def is_lefkosa(x):
    if pd.isna(x):
        return False
    t = str(x).lower().replace('ö', 'o').replace('ş', 's').strip()
    return 'lefkosa' in t or 'lefko' in t


def is_land(row):
    pt = str(row.get('property_type', '')).lower()
    pst = str(row.get('property_subtype', '')).lower()
    return ('arsa' in pt) or ('arsa' in pst)


def is_rental(row):
    lt = str(row.get('listing_type', '')).lower()
    return 'rent' in lt or 'kiralik' in lt


def build_excel():
    ensure_reports_dir()
    df = pd.read_csv(CSV_FILE)
    rates = fetch_exchange_rates()
    df = add_computed_columns(df, rates)

    # Segments
    land = df[df.apply(lambda r: is_guzelyurt(r.get('city')) and is_land(r), axis=1)].copy()
    rent = df[df.apply(lambda r: is_lefkosa(r.get('city')) and is_rental(r), axis=1)].copy()

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    params_rows = [
        ['Generated At', now],
        ['Source CSV', CSV_FILE],
        ['Exchange Rates (TRY per 1 unit)', ''],
    ]
    for k in ['USD', 'EUR', 'GBP', 'TRY']:
        if k in rates:
            params_rows.append([f'  {k}', rates[k]])
    params_rows += [
        ['Area Conversions', ''],
        ['  DONUM_M2', DONUM_M2],
        ['  EVLEK_M2', EVLEK_M2],
        ['  FT2_TO_M2', FT2_TO_M2],
        ['Filters', ''],
        ["  Güzelyurt Land", "city contains 'guzelyurt' (lower, ü->u) AND (property_type or subtype contains 'arsa')"],
        ["  Lefkoşa Rentals", "city contains 'lefkosa' (lower, ö->o, ş->s) AND listing_type contains 'rent' or 'kiralik'"],
    ]

    dict_rows = [
        ['Column', 'Description'],
        ['price_try', 'Price converted to TRY using current ForexBuying rates'],
        ['price_per_m2_try', 'TRY price divided by area_m2'],
        ['price_per_donum_try', 'TRY price divided by (area_m2 / 1338)'],
        ['area_m2', 'Area in square meters (parsed from listing or description; dönüm/evlek/ft² converted)'],
        ['listing_type', 'Rent/Sale'],
        ['property_type', 'Top-level type (e.g., Konut/Arsa)'],
        ['property_subtype', 'Subtype (e.g., Daire, Konut İmarlı Arsa)'],
        ['room_count', 'Layout like 2+1, 3+1 where present'],
        ['district/city', 'Location parsed from listing'],
        ['price/currency', 'As listed'],
    ]

    # Compute stats blocks
    summary_blocks = []
    def stats_block(title, ser, unit='TRY'):
        st = quick_stats(ser)
        if not st:
            return pd.DataFrame([[title, 'No data']], columns=['Metric', 'Value'])
        rows = [
            [f'{title} - count', st['count']],
            [f'{title} - min', st['min']],
            [f'{title} - p25', st['p25']],
            [f'{title} - median', st['median']],
            [f'{title} - p75', st['p75']],
            [f'{title} - max', st['max']],
            [f'{title} - mean', st['mean']],
        ]
        return pd.DataFrame(rows, columns=['Metric', 'Value'])

    # Land overall
    if not land.empty:
        summary_blocks.append(stats_block('Land - Price TRY', land['price_try']))
        summary_blocks.append(stats_block('Land - Price per m2 (TRY/m²)', land['price_per_m2_try']))
        summary_blocks.append(stats_block('Land - Price per donum (TRY/donum)', land['price_per_donum_try']))

    # Rent overall
    if not rent.empty:
        summary_blocks.append(stats_block('Rent - Monthly price TRY', rent['price_try']))

    summary_df = pd.concat(summary_blocks, ignore_index=True) if summary_blocks else pd.DataFrame([['No data', '']], columns=['Metric','Value'])

    # District breakdowns
    land_by_district = None
    if not land.empty and 'district' in land.columns:
        land_by_district = land.groupby('district').agg(
            count=('price_per_m2_try', 'count'),
            m2_min=('price_per_m2_try', 'min'),
            m2_p25=('price_per_m2_try', lambda s: pd.to_numeric(s, errors='coerce').dropna().quantile(0.25) if pd.to_numeric(s, errors='coerce').dropna().size else None),
            m2_median=('price_per_m2_try', 'median'),
            m2_p75=('price_per_m2_try', lambda s: pd.to_numeric(s, errors='coerce').dropna().quantile(0.75) if pd.to_numeric(s, errors='coerce').dropna().size else None),
            m2_max=('price_per_m2_try', 'max'),
            donum_median=('price_per_donum_try', 'median')
        ).reset_index()

    rent_by_room = None
    if not rent.empty and 'room_count' in rent.columns:
        rent_by_room = rent.groupby('room_count').agg(
            count=('price_try', 'count'),
            price_min=('price_try', 'min'),
            price_p25=('price_try', lambda s: pd.to_numeric(s, errors='coerce').dropna().quantile(0.25) if pd.to_numeric(s, errors='coerce').dropna().size else None),
            price_median=('price_try', 'median'),
            price_p75=('price_try', lambda s: pd.to_numeric(s, errors='coerce').dropna().quantile(0.75) if pd.to_numeric(s, errors='coerce').dropna().size else None),
            price_max=('price_try', 'max'),
            price_mean=('price_try', 'mean')
        ).reset_index()

    # Choose columns for detail sheets
    land_cols = [c for c in ['property_id','title','district','price','currency','price_try','area_m2','price_per_m2_try','price_per_donum_try','url'] if c in land.columns or c in ['price_try','price_per_m2_try','price_per_donum_try']]
    rent_cols = [c for c in ['property_id','title','district','room_count','price','currency','price_try','url'] if c in rent.columns or c == 'price_try']

    # Write to Excel
    with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        if not land.empty:
            land.to_excel(writer, sheet_name='Raw_Land', index=False)
            land[land_cols].to_excel(writer, sheet_name='Guzelyurt_Land', index=False)
        if land_by_district is not None:
            land_by_district.to_excel(writer, sheet_name='Land_By_District', index=False)
        if not rent.empty:
            rent.to_excel(writer, sheet_name='Raw_Rent', index=False)
            rent[rent_cols].to_excel(writer, sheet_name='Lefkosa_Rentals', index=False)
        if rent_by_room is not None:
            rent_by_room.to_excel(writer, sheet_name='Rent_By_Room', index=False)
        # Parameters and Data Dictionary
        pd.DataFrame(params_rows, columns=['Parameter','Value']).to_excel(writer, sheet_name='Parameters', index=False)
        pd.DataFrame(dict_rows, columns=['Column','Description']).to_excel(writer, sheet_name='Data_Dictionary', index=False)

    return OUTPUT_XLSX


if __name__ == '__main__':
    path = build_excel()
    print(f"Excel report written: {path}")

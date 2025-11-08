import os
import json
from typing import List, Optional
import argparse

import pandas as pd
from scraper import search

REPORTS_DIR = 'reports'
OUTPUT_XLSX = os.path.join(REPORTS_DIR, 'guzelyurt_orchard_pricing.xlsx')


def _norm_text(s: str) -> str:
    if not isinstance(s, str):
        return ''
    s = s.lower()
    repl = str.maketrans({
        'ö':'o','Ö':'o','ü':'u','Ü':'u','ş':'s','Ş':'s','ı':'i','İ':'i','ğ':'g','Ğ':'g','ç':'c','Ç':'c'
    })
    return s.translate(repl)


def any_token_in(text_series: pd.Series, tokens: List[str]) -> pd.Series:
    tnorm = [_norm_text(t) for t in tokens]
    base = pd.Series(False, index=text_series.index)
    for t in tnorm:
        base = base | text_series.str.contains(t, na=False)
    return base


def stats(series: pd.Series):
    s = pd.to_numeric(series, errors='coerce').dropna()
    if s.empty:
        return None
    return {
        'count': int(s.count()),
        'min': float(s.min()),
        'p25': float(s.quantile(0.25)),
        'median': float(s.median()),
        'p75': float(s.quantile(0.75)),
        'max': float(s.max()),
        'mean': float(s.mean()),
    }


def run(
    city: str = 'guzelyurt',
    property_type: str = 'arsa',
    listing_type: str = 'Sale',
    min_donum: float = 1.0,
    core_city_token: Optional[str] = 'guzelyurt',
    core_district_tokens: Optional[List[str]] = None,
    orchard_terms: Optional[List[str]] = None,
    water_terms: Optional[List[str]] = None,
    dry_terms: Optional[List[str]] = None,
    export_xlsx: Optional[str] = None,
    export_json: Optional[str] = None,
):
    """Run orchard pricing analysis with configurable filters.

    Parameters
    - city: normalized city token for search. Default 'guzelyurt'.
    - property_type: e.g., 'arsa'.
    - listing_type: 'Sale' or 'Rent'.
    - min_donum: minimum area in dönüm for baseline filter.
    - core_city_token: token to match in district column for core subset.
    - core_district_tokens: list of tokens (any match) for core subset (e.g., ['merkez','piyalepasa']).
    - orchard_terms: keywords to detect orchard listings in text.
    - water_terms: keywords to detect water connection/availability.
    - dry_terms: keywords to detect dry trees/poor orchard condition.
    - export_xlsx: optional path to write Excel; defaults to reports/guzelyurt_orchard_pricing.xlsx.
    - export_json: optional path to write JSON summary in addition to stdout.
    """

    # Baseline: All lands in city >= min_donum
    base = search.advanced_search(
        city=city,
        property_type=property_type,
        listing_type=listing_type,
        min_donum=min_donum,
        limit=5000,
    )

    # Build normalized text
    # Build normalized text field from title + description
    text = (base['title'].fillna('') + ' ' + base['description'].fillna('')).map(_norm_text)

    # Default keyword sets (can be overridden via params)
    if orchard_terms is None:
        orchard_terms = [
            'portakal','narenciye','mandalina','limon','meyve',
            'bahce','bahcesi','bahcedir','agac','zeytin','ceviz','incir'
        ]
    if water_terms is None:
        water_terms = [
            'tatli su','tc su','turkiye su','turkiyeden su','anavatandan su',
            'sulama','sulama suyu','su hatti','su baglanti','su saati',
            'sebeke suyu','kuyu','artezyen','artezyen kuyu','damla','damlama',
            'hidrofor','su deposu','depo','tarimsal su','ciftci suyu','belediye su'
        ]
    if dry_terms is None:
        dry_terms = [
            'agaclar kuru','kurumus','kurumus agac','bakimsiz','verimsiz','sokum','yenileme gerekli','kurak'
        ]

    mask_orchard = any_token_in(text, orchard_terms)
    mask_water   = any_token_in(text, water_terms)
    mask_dry     = any_token_in(text, dry_terms)

    orchard_df = base[mask_orchard].copy()
    orchard_water_df = base[mask_orchard & mask_water].copy()
    orchard_dry_df = base[mask_orchard & mask_dry].copy()

    # District focus: Güzelyurt Merkez / Piyalepaşa
    dist_series = base.get('district', pd.Series('', index=base.index)).fillna('').map(_norm_text)
    # Core logic: require core_city_token and any of the core_district_tokens
    if core_district_tokens is None:
        core_district_tokens = ['merkez','piyalepasa']
    if core_city_token:
        city_ok = dist_series.str.contains(_norm_text(core_city_token))
    else:
        city_ok = pd.Series(True, index=base.index)
    any_core_token = pd.Series(False, index=base.index)
    for tok in core_district_tokens:
        if isinstance(tok, str) and tok.strip():
            any_core_token = any_core_token | dist_series.str.contains(_norm_text(tok.strip()))
    mask_core = city_ok & any_core_token
    orchard_core_df = orchard_df[mask_core.loc[orchard_df.index]].copy()
    orchard_water_core_df = orchard_water_df[mask_core.loc[orchard_water_df.index]].copy()
    orchard_dry_core_df = orchard_dry_df[mask_core.loc[orchard_dry_df.index]].copy()

    out = {
        'baseline_per_donum_try': stats(base['price_per_donum_try']),
        'orchard_per_donum_try': stats(orchard_df['price_per_donum_try']),
        'orchard_water_per_donum_try': stats(orchard_water_df['price_per_donum_try']),
        'orchard_dry_per_donum_try': stats(orchard_dry_df['price_per_donum_try']),
        'orchard_core_per_donum_try': stats(orchard_core_df['price_per_donum_try']) if len(orchard_core_df) else None,
        'orchard_water_core_per_donum_try': stats(orchard_water_core_df['price_per_donum_try']) if len(orchard_water_core_df) else None,
        'orchard_dry_core_per_donum_try': stats(orchard_dry_core_df['price_per_donum_try']) if len(orchard_dry_core_df) else None,
        'counts': {
            'baseline': int(len(base)),
            'orchard': int(len(orchard_df)),
            'orchard_water': int(len(orchard_water_df)),
            'orchard_dry': int(len(orchard_dry_df)),
            'orchard_core': int(len(orchard_core_df)),
            'orchard_water_core': int(len(orchard_water_core_df)),
            'orchard_dry_core': int(len(orchard_dry_core_df)),
        }
    }

    # Export details to Excel
    os.makedirs(REPORTS_DIR, exist_ok=True)
    xlsx_path = export_xlsx or OUTPUT_XLSX
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        base.to_excel(writer, sheet_name='Baseline_All_Land', index=False)
        orchard_df.to_excel(writer, sheet_name='Orchard_Mentions', index=False)
        orchard_water_df.to_excel(writer, sheet_name='Orchard_With_Water', index=False)
        orchard_dry_df.to_excel(writer, sheet_name='Orchard_Dry', index=False)
        orchard_core_df.to_excel(writer, sheet_name='Orchard_Core', index=False)
        orchard_water_core_df.to_excel(writer, sheet_name='Orchard_Water_Core', index=False)
        orchard_dry_core_df.to_excel(writer, sheet_name='Orchard_Dry_Core', index=False)
        pd.DataFrame([
            ['baseline', json.dumps(out['baseline_per_donum_try']) if out['baseline_per_donum_try'] else 'No data'],
            ['orchard', json.dumps(out['orchard_per_donum_try']) if out['orchard_per_donum_try'] else 'No data'],
            ['orchard_water', json.dumps(out['orchard_water_per_donum_try']) if out['orchard_water_per_donum_try'] else 'No data'],
            ['orchard_dry', json.dumps(out['orchard_dry_per_donum_try']) if out['orchard_dry_per_donum_try'] else 'No data'],
            ['orchard_core', json.dumps(out['orchard_core_per_donum_try']) if out.get('orchard_core_per_donum_try') else 'No data'],
            ['orchard_water_core', json.dumps(out['orchard_water_core_per_donum_try']) if out.get('orchard_water_core_per_donum_try') else 'No data'],
            ['orchard_dry_core', json.dumps(out['orchard_dry_core_per_donum_try']) if out.get('orchard_dry_core_per_donum_try') else 'No data'],
            ['counts', json.dumps(out['counts'])],
        ], columns=['metric','value']).to_excel(writer, sheet_name='Summary', index=False)

    # Optionally save JSON summary
    summary = {**out, 'excel': xlsx_path}
    if export_json:
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False)

    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    # CLI interface
    parser = argparse.ArgumentParser(description='Orchard pricing analysis for 101evler data')
    parser.add_argument('--city', type=str, default='guzelyurt', help='City token (normalized, e.g., guzelyurt)')
    parser.add_argument('--property-type', type=str, default='arsa', help='Property type (e.g., arsa)')
    parser.add_argument('--listing-type', type=str, default='Sale', help='Listing type (Sale or Rent)')
    parser.add_argument('--min-donum', type=float, default=1.0, help='Minimum area in dönüm for baseline filter')
    parser.add_argument('--core-city-token', type=str, default='guzelyurt', help='City token required for core mask (in district)')
    parser.add_argument('--core-district-tokens', type=str, default='merkez,piyalepasa', help='Comma-separated tokens for core districts (any match)')
    parser.add_argument('--orchard-terms', type=str, default='', help='Comma-separated override terms for orchard detection')
    parser.add_argument('--water-terms', type=str, default='', help='Comma-separated override terms for water detection')
    parser.add_argument('--dry-terms', type=str, default='', help='Comma-separated override terms for dry/poor condition detection')
    parser.add_argument('--export-xlsx', type=str, default='', help='Path to export Excel file')
    parser.add_argument('--export-json', type=str, default='', help='Path to export JSON summary file')

    args = parser.parse_args()

    def _split_terms(s: str) -> Optional[List[str]]:
        s = (s or '').strip()
        if not s:
            return None
        return [t.strip() for t in s.split(',') if t.strip()]

    run(
        city=args.city,
        property_type=args.property_type,
        listing_type=args.listing_type,
        min_donum=args.min_donum,
        core_city_token=args.core_city_token or None,
        core_district_tokens=_split_terms(args.core_district_tokens),
        orchard_terms=_split_terms(args.orchard_terms),
        water_terms=_split_terms(args.water_terms),
        dry_terms=_split_terms(args.dry_terms),
        export_xlsx=args.export_xlsx or None,
        export_json=args.export_json or None,
    )

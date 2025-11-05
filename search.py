import os
import re
import argparse
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
from report import fetch_exchange_rates, add_computed_columns, DONUM_M2

CSV_FILE = 'property_details.csv'


def _norm_text(s: Optional[str]) -> str:
    if not isinstance(s, str):
        return ''
    s = s.lower()
    # Turkish character normalization for simpler contains-search
    repl = str.maketrans({
        'ö': 'o', 'Ö': 'o',
        'ü': 'u', 'Ü': 'u',
        'ş': 's', 'Ş': 's',
        'ı': 'i', 'İ': 'i',
        'ğ': 'g', 'Ğ': 'g',
        'ç': 'c', 'Ç': 'c'
    })
    return s.translate(repl)


def _load_df() -> pd.DataFrame:
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"CSV not found: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    # add computed columns (price_try, price_per_m2_try, price_per_donum_try)
    rates = fetch_exchange_rates()
    df = add_computed_columns(df, rates)
    # normalize some types
    for c in ['price_try', 'area_m2', 'price_per_m2_try', 'price_per_donum_try']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def basic_search(query: str, limit: int = 50, fields: Optional[List[str]] = None) -> pd.DataFrame:
    """Free-text search across key fields, diacritics-tolerant.

    Default fields: title, description, district, city, property_type, property_subtype, agency_name
    """
    df = _load_df()
    if fields is None:
        fields = ['title', 'description', 'district', 'city', 'property_type', 'property_subtype', 'agency_name']
    qnorm = _norm_text(query)
    tokens = [t for t in re.split(r"\s+", qnorm) if t]
    # Build a combined text field
    combined = pd.Series('', index=df.index)
    for f in fields:
        if f in df.columns:
            combined = combined + ' ' + df[f].fillna('').map(_norm_text)
    # numeric property_id exact match if single-token digits
    mask = pd.Series(False, index=df.index)
    if len(tokens) == 1 and tokens[0].isdigit() and 'property_id' in df.columns:
        mask = mask | (df['property_id'].astype(str) == tokens[0])
    # All tokens must be present (AND)
    tok_mask = pd.Series(True, index=df.index)
    for t in tokens:
        tok_mask &= combined.str.contains(t, na=False)
    mask = mask | tok_mask
    out = df[mask].copy()
    # rank basic relevance: count of field matches
    out['_relevance'] = 0
    for t in tokens:
        out['_relevance'] += combined[out.index].str.contains(t, na=False).astype(int)
    out = out.sort_values(by=['_relevance', 'update_date'], ascending=[False, False], na_position='last')
    return out.drop(columns=['_relevance']).head(limit)


def advanced_search(
    *,
    city: Optional[str] = None,
    district: Optional[str] = None,
    listing_type: Optional[str] = None,  # 'Sale' or 'Rent'
    property_type: Optional[str] = None,
    property_subtype: Optional[str] = None,
    min_price_try: Optional[float] = None,
    max_price_try: Optional[float] = None,
    min_area_m2: Optional[float] = None,
    max_area_m2: Optional[float] = None,
    min_donum: Optional[float] = None,
    max_donum: Optional[float] = None,
    room_in: Optional[List[str]] = None,  # e.g., ['2+1','3+1']
    keywords_all: Optional[List[str]] = None,
    keywords_any: Optional[List[str]] = None,
    keywords_none: Optional[List[str]] = None,
    has_phone: Optional[bool] = None,
    has_images: Optional[bool] = None,
    date_from: Optional[str] = None,  # 'DD/MM/YYYY' listing_date/update_date
    date_to: Optional[str] = None,
    sort: Optional[str] = None,  # e.g., 'price_try:asc', 'price_per_donum_try:desc'
    limit: int = 200,
) -> pd.DataFrame:
    """Structured filtering on the extracted dataset.

    Notes:
    - Price filters are applied on price_try (TRY normalized).
    - min/max_donum are converted to m² using DONUM_M2.
    - keywords_* search title+description combined, diacritics-tolerant.
    - date_from/date_to compare against update_date if available, else listing_date.
    """
    df = _load_df()
    mask = pd.Series(True, index=df.index)

    def contains_norm(series: pd.Series, token: str) -> pd.Series:
        t = _norm_text(token)
        return series.fillna('').map(_norm_text).str.contains(t, na=False)

    # City/District
    if city:
        mask &= contains_norm(df.get('city', pd.Series(index=df.index)), city)
    if district:
        mask &= contains_norm(df.get('district', pd.Series(index=df.index)), district)

    # Listing type
    if listing_type:
        lt = _norm_text(listing_type)
        mask &= df.get('listing_type', pd.Series(index=df.index)).fillna('').map(_norm_text).str.contains(lt)

    # Property type/subtype
    if property_type:
        mask &= contains_norm(df.get('property_type', pd.Series(index=df.index)), property_type)
    if property_subtype:
        mask &= contains_norm(df.get('property_subtype', pd.Series(index=df.index)), property_subtype)

    # Area by m2 / dönüm
    if min_area_m2 is not None:
        mask &= df.get('area_m2', pd.Series(index=df.index)).fillna(0) >= float(min_area_m2)
    if max_area_m2 is not None:
        mask &= df.get('area_m2', pd.Series(index=df.index)).fillna(0) <= float(max_area_m2)
    if min_donum is not None:
        mask &= df.get('area_m2', pd.Series(index=df.index)).fillna(0) >= float(min_donum) * DONUM_M2
    if max_donum is not None:
        mask &= df.get('area_m2', pd.Series(index=df.index)).fillna(0) <= float(max_donum) * DONUM_M2

    # Price in TRY
    if min_price_try is not None:
        mask &= df.get('price_try', pd.Series(index=df.index)).fillna(0) >= float(min_price_try)
    if max_price_try is not None:
        mask &= df.get('price_try', pd.Series(index=df.index)).fillna(0) <= float(max_price_try)

    # Room selection
    if room_in:
        allowed = set(map(_norm_text, room_in))
        mask &= df.get('room_count', pd.Series(index=df.index)).fillna('').map(_norm_text).isin(allowed)

    # Keyword logic: ALL + ANY + NONE against title+description
    text = (df.get('title', pd.Series(index=df.index)).fillna('') + ' ' + df.get('description', pd.Series(index=df.index)).fillna('')).map(_norm_text)
    if keywords_all:
        for k in keywords_all:
            tk = _norm_text(k)
            mask &= text.str.contains(tk, na=False)
    if keywords_any:
        any_mask = pd.Series(False, index=df.index)
        for k in keywords_any:
            tk = _norm_text(k)
            any_mask |= text.str.contains(tk, na=False)
        mask &= any_mask
    if keywords_none:
        for k in keywords_none:
            tk = _norm_text(k)
            mask &= ~text.str.contains(tk, na=False)

    # Has phone / images
    if has_phone is True:
        mask &= df.get('phone_numbers', pd.Series(index=df.index)).fillna('') != ''
    if has_phone is False:
        mask &= df.get('phone_numbers', pd.Series(index=df.index)).fillna('') == ''
    if has_images is True:
        mask &= df.get('image_links', pd.Series(index=df.index)).fillna('') != ''
    if has_images is False:
        mask &= df.get('image_links', pd.Series(index=df.index)).fillna('') == ''

    # Date range (prefer update_date, fallback to listing_date)
    def parse_tr_date(s: Any) -> Optional[datetime]:
        try:
            return datetime.strptime(str(s), '%d/%m/%Y')
        except Exception:
            return None
    dates = df.get('update_date', pd.Series(index=df.index)).where(pd.notna(df.get('update_date')), df.get('listing_date'))
    dt_series = dates.apply(parse_tr_date)
    if date_from:
        df_from = parse_tr_date(date_from)
        if df_from:
            mask &= dt_series.apply(lambda d: (d is not None) and (d >= df_from))
    if date_to:
        df_to = parse_tr_date(date_to)
        if df_to:
            mask &= dt_series.apply(lambda d: (d is not None) and (d <= df_to))

    out = df[mask].copy()

    # Sorting
    if sort:
        try:
            col, _, direction = sort.partition(':')
            ascending = (direction.strip().lower() == 'asc') if direction else True
            if col in out.columns:
                out = out.sort_values(by=col, ascending=ascending, na_position='last')
        except Exception:
            pass

    return out.head(limit)


def save_to_excel(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Results', index=False)


def cli():
    parser = argparse.ArgumentParser(description='Search utilities over property_details.csv')
    sub = parser.add_subparsers(dest='mode')

    # Basic
    pb = sub.add_parser('basic', help='Basic free-text search')
    pb.add_argument('query', type=str)
    pb.add_argument('--limit', type=int, default=50)
    pb.add_argument('--out', type=str, default=None, help='Optional Excel path to export results')

    # Advanced
    pa = sub.add_parser('advanced', help='Advanced structured search')
    pa.add_argument('--city')
    pa.add_argument('--district')
    pa.add_argument('--listing-type', dest='listing_type')
    pa.add_argument('--property-type', dest='property_type')
    pa.add_argument('--property-subtype', dest='property_subtype')
    pa.add_argument('--min-price-try', type=float, dest='min_price_try')
    pa.add_argument('--max-price-try', type=float, dest='max_price_try')
    pa.add_argument('--min-area-m2', type=float, dest='min_area_m2')
    pa.add_argument('--max-area-m2', type=float, dest='max_area_m2')
    pa.add_argument('--min-donum', type=float, dest='min_donum')
    pa.add_argument('--max-donum', type=float, dest='max_donum')
    pa.add_argument('--room-in', nargs='*', dest='room_in')
    pa.add_argument('--keywords-all', nargs='*')
    pa.add_argument('--keywords-any', nargs='*')
    pa.add_argument('--keywords-none', nargs='*')
    pa.add_argument('--has-phone', choices=['yes','no'])
    pa.add_argument('--has-images', choices=['yes','no'])
    pa.add_argument('--date-from')
    pa.add_argument('--date-to')
    pa.add_argument('--sort', help='e.g., price_try:asc, price_per_donum_try:desc')
    pa.add_argument('--limit', type=int, default=200)
    pa.add_argument('--out', type=str, default=None, help='Optional Excel path to export results')

    args = parser.parse_args()
    if args.mode == 'basic':
        df = basic_search(args.query, limit=args.limit)
        if args.out:
            save_to_excel(df, args.out)
            print(f"Saved basic search results to: {args.out}")
        else:
            print(df.head(20).to_string(index=False))
    elif args.mode == 'advanced':
        df = advanced_search(
            city=args.city,
            district=args.district,
            listing_type=args.listing_type,
            property_type=args.property_type,
            property_subtype=args.property_subtype,
            min_price_try=args.min_price_try,
            max_price_try=args.max_price_try,
            min_area_m2=args.min_area_m2,
            max_area_m2=args.max_area_m2,
            min_donum=args.min_donum,
            max_donum=args.max_donum,
            room_in=args.room_in,
            keywords_all=args.keywords_all,
            keywords_any=args.keywords_any,
            keywords_none=args.keywords_none,
            has_phone=True if args.has_phone == 'yes' else False if args.has_phone == 'no' else None,
            has_images=True if args.has_images == 'yes' else False if args.has_images == 'no' else None,
            date_from=args.date_from,
            date_to=args.date_to,
            sort=args.sort,
            limit=args.limit,
        )
        if args.out:
            save_to_excel(df, args.out)
            print(f"Saved advanced search results to: {args.out}")
        else:
            print(df.head(20).to_string(index=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    cli()

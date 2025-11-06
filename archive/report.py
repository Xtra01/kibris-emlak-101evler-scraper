import os
import math
import pandas as pd
from datetime import datetime
import requests
import xml.etree.ElementTree as ET

REPORTS_DIR = 'reports'
CSV_FILE = 'property_details.csv'
DONUM_M2 = 1338.0

EXCHANGE_RATES_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"

def ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)


def fetch_exchange_rates():
    try:
        resp = requests.get(EXCHANGE_RATES_URL, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        rates = {}
        for currency in root.findall('./Currency'):
            code = currency.get('Kod')
            fb = currency.find('ForexBuying')
            if fb is not None and fb.text:
                rates[code] = float(fb.text.replace(',', '.'))
        # TRY baseline
        rates['TRY'] = 1.0
        return rates
    except Exception as e:
        # conservative fallback
        return {'USD': 37.8646, 'EUR': 41.8133, 'GBP': 48.7317, 'TRY': 1.0}


def to_try(price, currency, rates):
    if pd.isna(price) or pd.isna(currency):
        return None
    c = str(currency).upper()
    if c in ['£', 'GBP']:
        rate = rates.get('GBP', 1.0)
    elif c in ['$', 'USD']:
        rate = rates.get('USD', 1.0)
    elif c in ['€', 'EUR']:
        rate = rates.get('EUR', 1.0)
    elif c in ['₺', 'TRY', 'TL']:
        rate = 1.0
    else:
        rate = 1.0
    try:
        return float(price) * rate
    except:
        return None


def fmt_currency_try(x):
    if pd.isna(x):
        return '-'
    return f"₺{x:,.0f}".replace(',', '.')


def add_computed_columns(df, rates):
    # normalize types
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    if 'area_m2' in df.columns:
        df['area_m2'] = pd.to_numeric(df['area_m2'], errors='coerce')

    # price in TRY
    df['price_try'] = df.apply(lambda r: to_try(r.get('price'), r.get('currency'), rates), axis=1)

    # price per m2 / per donum (only where area > 0)
    df['price_per_m2_try'] = df.apply(lambda r: (r['price_try'] / r['area_m2']) if (pd.notna(r.get('price_try')) and pd.notna(r.get('area_m2')) and r['area_m2'] > 0) else None, axis=1)
    df['price_per_donum_try'] = df.apply(lambda r: (r['price_try'] / (r['area_m2'] / DONUM_M2)) if (pd.notna(r.get('price_try')) and pd.notna(r.get('area_m2')) and r['area_m2'] > 0) else None, axis=1)
    return df


def quick_stats(series):
    s = pd.to_numeric(series, errors='coerce').dropna()
    if s.empty:
        return {'count': 0}
    return {
        'count': int(s.count()),
        'min': float(s.min()),
        'p25': float(s.quantile(0.25)),
        'median': float(s.median()),
        'p75': float(s.quantile(0.75)),
        'max': float(s.max()),
        'mean': float(s.mean())
    }


def render_stats_md(title, stats, unit='₺'):
    if stats.get('count', 0) == 0:
        return f"### {title}\n\nVeri bulunamadı.\n\n"
    def fmt(v):
        return fmt_currency_try(v) if unit == '₺' else f"{v:.2f}"
    return (
        f"### {title}\n\n"
        f"- Kayıt sayısı: {stats['count']}\n"
        f"- Min: {fmt(stats['min'])}\n"
        f"- P25: {fmt(stats['p25'])}\n"
        f"- Medyan: {fmt(stats['median'])}\n"
        f"- P75: {fmt(stats['p75'])}\n"
        f"- Max: {fmt(stats['max'])}\n"
        f"- Ortalama: {fmt(stats['mean'])}\n\n"
    )


def save_markdown_report(filename, content):
    ensure_reports_dir()
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def general_report():
    df = pd.read_csv(CSV_FILE)
    rates = fetch_exchange_rates()
    df = add_computed_columns(df, rates)

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    parts = [f"# Genel Rapor\n\nTarih: {now}\n\nToplam kayıt: {len(df)}\n\n"]

    # by city
    if {'city', 'price_try'} <= set(df.columns):
        city_stats = {city: quick_stats(group['price_try']) for city, group in df.groupby('city')}
        parts.append("## Şehir Bazında Fiyat Özetleri (₺)\n\n")
        for city, st in city_stats.items():
            parts.append(render_stats_md(f"{city}", st, unit='₺'))

    # overall price per m2 where available
    parts.append(render_stats_md('Genel m² başına fiyat (₺/m²)', quick_stats(df['price_per_m2_try'])))

    return save_markdown_report('general_report.md', '\n'.join(parts))


def land_report_guzelyurt():
    df = pd.read_csv(CSV_FILE)
    rates = fetch_exchange_rates()
    df = add_computed_columns(df, rates)

    # Filter: city ~ Güzelyurt (case-insensitive) and property_type contains 'Arsa'
    def is_guzelyurt(x):
        if pd.isna(x):
            return False
        t = str(x).lower().replace('ü', 'u').strip()
        return 'guzelyurt' in t

    def is_land(row):
        pt = str(row.get('property_type', '')).lower()
        pst = str(row.get('property_subtype', '')).lower()
        return ('arsa' in pt) or ('arsa' in pst)

    land = df[df.apply(lambda r: is_guzelyurt(r.get('city')) and is_land(r), axis=1)].copy()

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    parts = [f"# Güzelyurt Arsa Raporu\n\nTarih: {now}\n\nKayıt: {len(land)}\n\n"]

    parts.append(render_stats_md('Toplam satış fiyatı (₺)', quick_stats(land['price_try'])))
    parts.append(render_stats_md('m² başına fiyat (₺/m²)', quick_stats(land['price_per_m2_try'])))
    parts.append(render_stats_md('Dönüm başına fiyat (₺/dönüm)', quick_stats(land['price_per_donum_try'])))

    # District breakdown (if available)
    if 'district' in land.columns and not land.empty:
        parts.append('## İlçe/Köy Bazında m² Fiyat Özeti\n')
        gb = {d: quick_stats(g['price_per_m2_try']) for d, g in land.groupby('district')}
        for d, st in gb.items():
            parts.append(render_stats_md(f"{d}", st))

    # Sample table
    show_cols = ['property_id', 'title', 'district', 'price', 'currency', 'price_try', 'area_m2', 'price_per_m2_try', 'price_per_donum_try', 'url']
    view = land[show_cols].copy() if all(c in land.columns for c in show_cols) else land.copy()
    view = view.head(50)  # keep it compact
    parts.append('## Örnek Kayıtlar (ilk 50)\n\n')
    try:
        parts.append(view.to_markdown(index=False))
    except Exception:
        parts.append(view.to_string(index=False))

    return save_markdown_report('land_report_guzelyurt.md', '\n'.join(parts))


def rent_guidance_section():
    bullets = [
        "Bütçe ve toplam maliyet: Depozito, komisyon, aidat, elektrik/su/ısınma.",
        "Konum ve ulaşım: İş/okul/servis hatları, park imkanı, gürültü seviyesi.",
        "Kontrat ve şartlar: Kira artış oranı, süre, tahliye şartları, alt kiralama yasağı.",
        "Evin durumu: Nem/ısı yalıtımı, beyaz eşyalar, kombi/klima, su basıncı, internet altyapısı.",
        "Apartman/site kuralları: Evcil hayvan, otopark, güvenlik, ortak alan kullanım kuralları.",
        "Sayaç devirleri ve borç kontrolü: Elektrik/su/telefon geçmiş borç.",
        "Hasar tespiti ve demirbaş listesi: Fotoğraflı tutanak, anahtar sayıları.",
    ]
    body = '## Kiralık Evlerde Dikkat Edilecekler\n\n' + '\n'.join([f"- {b}" for b in bullets]) + '\n\n'
    return body


def rent_report_lefkosa():
    df = pd.read_csv(CSV_FILE)
    rates = fetch_exchange_rates()
    df = add_computed_columns(df, rates)

    def is_lefkosa(x):
        if pd.isna(x):
            return False
        t = str(x).lower().replace('ö', 'o').replace('ş', 's').strip()
        return 'lefkosa' in t or 'lefko' in t

    def is_rental(row):
        lt = str(row.get('listing_type', '')).lower()
        return 'rent' in lt or 'kiralik' in lt

    rent = df[df.apply(lambda r: is_lefkosa(r.get('city')) and is_rental(r), axis=1)].copy()

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    parts = [f"# Lefkoşa Kiralık Konut Raporu\n\nTarih: {now}\n\nKayıt: {len(rent)}\n\n"]
    parts.append(rent_guidance_section())

    # price TRY per month (assuming listed price is monthly)
    parts.append(render_stats_md('Aylık kira (₺/ay)', quick_stats(rent['price_try'])))

    # room_count breakdown
    if 'room_count' in rent.columns:
        parts.append('## Oda Sayısına Göre Aylık Kira (₺)\n')
        gb = {rc: quick_stats(g['price_try']) for rc, g in rent.groupby('room_count')}
        for rc, st in gb.items():
            parts.append(render_stats_md(f"{rc}", st))

    # Sample rows
    show_cols = ['property_id', 'title', 'district', 'room_count', 'price', 'currency', 'price_try', 'url']
    view = rent[show_cols].copy() if all(c in rent.columns for c in show_cols) else rent.copy()
    view = view.head(50)
    parts.append('## Örnek Kayıtlar (ilk 50)\n\n')
    try:
        parts.append(view.to_markdown(index=False))
    except Exception:
        parts.append(view.to_string(index=False))

    return save_markdown_report('rent_report_lefkosa.md', '\n'.join(parts))


if __name__ == '__main__':
    ensure_reports_dir()
    p1 = general_report()
    print(f"General report written: {p1}")
    # The following functions are to be called after respective scrapes
    # p2 = land_report_guzelyurt()
    # p3 = rent_report_lefkosa()

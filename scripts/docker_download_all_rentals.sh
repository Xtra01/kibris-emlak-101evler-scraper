#!/bin/bash
# Docker içinden tüm kiralık ilanları indir ve raporla

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   101evler.com TÜM KİRALIK İLANLAR - DOCKER               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Create logs directory
mkdir -p /app/logs

# Run the comprehensive downloader
echo "🚀 Tüm kiralık ilanlar indiriliyor..."
python /app/download_all_rentals.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ TÜM İŞLEMLER BAŞARILI!"
    echo ""
    echo "📊 CSV'yi kontrol edelim..."
    python -c "
import pandas as pd
try:
    df = pd.read_csv('/app/property_details.csv')
    rentals = df[df['listing_type'] == 'Rent']
    print(f'Toplam kayıt: {len(df)}')
    print(f'Kiralık kayıt: {len(rentals)}')
    print(f'')
    print('Şehir dağılımı (kiralıklar):')
    print(rentals['city'].value_counts())
except Exception as e:
    print(f'CSV kontrol hatası: {e}')
"
else
    echo ""
    echo "❌ HATA! Exit code: $EXIT_CODE"
    echo "📝 Log dosyalarını kontrol edin: /app/logs/"
    exit $EXIT_CODE
fi

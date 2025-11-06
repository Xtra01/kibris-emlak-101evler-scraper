# Windows PowerShell script - Tüm kiralık ilanları indir
# Kullanım: .\run_download_all.ps1

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   101evler.com TÜM KİRALIK İLANLAR - DOWNLOADER           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path ".\download_all_rentals.py")) {
    Write-Host "❌ HATA: download_all_rentals.py bulunamadı!" -ForegroundColor Red
    Write-Host "Lütfen proje dizininden çalıştırın." -ForegroundColor Yellow
    exit 1
}

# Create logs directory
if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" | Out-Null
}

Write-Host "🚀 İndirme başlatılıyor..." -ForegroundColor Green
Write-Host "📝 Log: logs/scraper_all_rentals_*.log" -ForegroundColor Gray
Write-Host ""

# Run the downloader
python download_all_rentals.py

$EXIT_CODE = $LASTEXITCODE

Write-Host ""

if ($EXIT_CODE -eq 0) {
    Write-Host "✅ TÜM İŞLEMLER BAŞARILI!" -ForegroundColor Green
    Write-Host ""
    
    # Show summary
    Write-Host "📊 CSV Özeti:" -ForegroundColor Cyan
    python -c @"
import pandas as pd
import sys
try:
    df = pd.read_csv('property_details.csv')
    rentals = df[df['listing_type'] == 'Rent']
    print(f'Toplam kayıt: {len(df)}')
    print(f'Kiralık kayıt: {len(rentals)}')
    print('')
    print('Şehir dağılımı (kiralıklar):')
    print(rentals['city'].value_counts().to_string())
    print('')
    print('Fiyat özeti (GBP):')
    print(f'  Min: £{rentals[\"price\"].min():.0f}')
    print(f'  Max: £{rentals[\"price\"].max():.0f}')
    print(f'  Avg: £{rentals[\"price\"].mean():.0f}')
except Exception as e:
    print(f'CSV kontrol hatası: {e}')
    sys.exit(1)
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "📁 Dosyalar:" -ForegroundColor Cyan
        Write-Host "  - property_details.csv (güncel data)" -ForegroundColor Gray
        Write-Host "  - logs/scraper_all_rentals_*.log (detaylı log)" -ForegroundColor Gray
        Write-Host "  - logs/scraper_results_*.json (özet)" -ForegroundColor Gray
    }
    
} else {
    Write-Host "❌ HATA! Exit code: $EXIT_CODE" -ForegroundColor Red
    Write-Host "📝 Log dosyalarını kontrol edin: logs/" -ForegroundColor Yellow
    exit $EXIT_CODE
}

Write-Host ""
Write-Host "✨ Tamamlandı!" -ForegroundColor Green

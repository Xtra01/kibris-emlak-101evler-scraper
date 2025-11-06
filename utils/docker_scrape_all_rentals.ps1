# PowerShell Script - Tüm Kiralık İlanları Docker ile Çek
# Kullanım: .\docker_scrape_all_rentals.ps1

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   101evler.com TÜM KİRALIK İLANLAR - DOCKER               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Konfigürasyonlar
$cities = @('lefkosa', 'girne', 'magusa', 'gazimagusa', 'iskele', 'guzelyurt')
$types = @('kiralik-daire', 'kiralik-villa')

$total = $cities.Count * $types.Count
$current = 0
$success = 0
$failed = 0
$start_time = Get-Date

Write-Host "🎯 Toplam konfigürasyon: $total" -ForegroundColor Green
Write-Host "🏙️  Şehirler: $($cities -join ', ')" -ForegroundColor Green
Write-Host "🏠 Tipler: $($types -join ', ')" -ForegroundColor Green
Write-Host ""

# Her şehir ve tip için döngü
foreach ($city in $cities) {
    foreach ($type in $types) {
        $current++
        
        $name = "$($city.Substring(0,1).ToUpper())$($city.Substring(1)) $($type -replace 'kiralik-', '')"
        
        Write-Host ""
        Write-Host "[$current/$total] 🔄 $name" -ForegroundColor Cyan
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "📍 Şehir: $city"
        Write-Host "🏠 Tip: $type"
        Write-Host ""
        
        # Config güncelle ve scraper çalıştır
        Write-Host "🚀 Scraping başlıyor..." -ForegroundColor Yellow
        
        # Docker command with proper escaping
        $dockerCmd = @"
cd /app && python -c "
import re
with open('src/scraper/config.py', 'r') as f:
    content = f.read()
content = re.sub(r'^CITY = .*', 'CITY = \"$city\"', content, flags=re.MULTILINE)
content = re.sub(r'^PROPERTY_TYPE = .*', 'PROPERTY_TYPE = \"$type\"', content, flags=re.MULTILINE)
with open('src/scraper/config.py', 'w') as f:
    f.write(content)
" && python -m scraper.main
"@
        
        try {
            $output = docker-compose run --rm scraper bash -c $dockerCmd 2>&1
            $exitCode = $LASTEXITCODE
            
            if ($exitCode -eq 0) {
                Write-Host "✅ BAŞARILI: $name" -ForegroundColor Green
                $success++
            } else {
                Write-Host "❌ HATA: $name (exit code: $exitCode)" -ForegroundColor Red
                $failed++
                Write-Host "Son çıktı:" -ForegroundColor Yellow
                Write-Host ($output | Select-Object -Last 10)
            }
        } catch {
            Write-Host "💥 EXCEPTION: $name" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            $failed++
        }
        
        # İlerleme göster
        $elapsed = (Get-Date) - $start_time
        $avg = $elapsed.TotalSeconds / $current
        $remaining = ($total - $current) * $avg
        
        Write-Host ""
        Write-Host "📊 İlerleme: $current/$total (✅$success ❌$failed)" -ForegroundColor Cyan
        Write-Host "⏱️  Geçen: $([int]$elapsed.TotalMinutes)m $($elapsed.Seconds)s | Kalan: ~$([int]$remaining / 60)m $($remaining % 60)s" -ForegroundColor Cyan
        
        # Rate limiting
        if ($current -lt $total) {
            Write-Host "⏸️  3 saniye bekleniyor..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    }
}

# Extraction
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔄 EXTRACTION BAŞLATILIYOR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

try {
    $extractOutput = docker-compose run --rm scraper python -m scraper.extract_data 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Extraction başarılı!" -ForegroundColor Green
        Write-Host ($extractOutput | Select-Object -Last 20)
    } else {
        Write-Host "❌ Extraction hatası" -ForegroundColor Red
        Write-Host $extractOutput
    }
} catch {
    Write-Host "💥 Extraction exception: $($_.Exception.Message)" -ForegroundColor Red
}

# Özet
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📊 ÖZET İSTATİSTİKLER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Başarılı: $success/$total" -ForegroundColor Green
Write-Host "❌ Hatalı: $failed/$total" -ForegroundColor Red

$totalElapsed = (Get-Date) - $start_time
Write-Host "⏱️  Toplam süre: $([int]$totalElapsed.TotalMinutes)m $($totalElapsed.Seconds)s" -ForegroundColor Cyan
Write-Host "⚡ Ortalama: $([int]($totalElapsed.TotalSeconds / $total))s/config" -ForegroundColor Cyan
Write-Host ""

# CSV özeti
if (Test-Path "property_details.csv") {
    Write-Host "📊 CSV ÖZET:" -ForegroundColor Cyan
    
    try {
        python -c @"
import pandas as pd
df = pd.read_csv('property_details.csv')
rentals = df[df['listing_type'] == 'Rent']
print(f'  Toplam kayıt: {len(df)}')
print(f'  Kiralık kayıt: {len(rentals)}')
print()
print('  Şehir dağılımı (kiralıklar):')
for city, count in rentals['city'].value_counts().items():
    print(f'    {city}: {count}')
"@
    } catch {
        Write-Host "  CSV okunamadı: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 İŞLEM TAMAMLANDI!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Dosyalar:" -ForegroundColor Cyan
Write-Host "  - property_details.csv (güncel data)" -ForegroundColor Gray
Write-Host "  - listings/ (HTML dosyaları)" -ForegroundColor Gray
Write-Host "  - pages/ (arama sayfaları)" -ForegroundColor Gray

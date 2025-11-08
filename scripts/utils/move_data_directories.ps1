# Data klasörlerini yeni konumlarına taşıma scripti

Write-Host "📦 Veri klasörleri taşınıyor..." -ForegroundColor Cyan
Write-Host ""

# Listings klasörünü taşı
if (Test-Path "listings") {
    Write-Host "📁 listings/ → data/raw/listings/" -ForegroundColor Yellow
    $count = (Get-ChildItem "listings" -File).Count
    Write-Host "   $count dosya bulundu..."
    
    robocopy "listings" "data/raw/listings" /E /MOVE /NFL /NDL /NJH /NJS
    
    if ($LASTEXITCODE -le 7) {
        Write-Host "   ✅ Listings taşındı" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Hata oluştu (kod: $LASTEXITCODE)" -ForegroundColor Red
    }
}

Write-Host ""

# Pages klasörünü taşı
if (Test-Path "pages") {
    Write-Host "📁 pages/ → data/raw/pages/" -ForegroundColor Yellow
    $count = (Get-ChildItem "pages" -File).Count
    Write-Host "   $count dosya bulundu..."
    
    robocopy "pages" "data/raw/pages" /E /MOVE /NFL /NDL /NJH /NJS
    
    if ($LASTEXITCODE -le 7) {
        Write-Host "   ✅ Pages taşındı" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Hata oluştu (kod: $LASTEXITCODE)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Tüm veri klasörleri taşındı!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Yeni yapı:"
Write-Host "   data/raw/listings/     → $(if (Test-Path 'data/raw/listings') { (Get-ChildItem 'data/raw/listings' -File).Count } else { 0 }) dosya"
Write-Host "   data/raw/pages/        → $(if (Test-Path 'data/raw/pages') { (Get-ChildItem 'data/raw/pages' -File).Count } else { 0 }) dosya"
Write-Host "   data/processed/        → $(if (Test-Path 'data/processed') { (Get-ChildItem 'data/processed' -File).Count } else { 0 }) dosya"
Write-Host "   data/reports/          → $(if (Test-Path 'data/reports') { (Get-ChildItem 'data/reports' -File -Recurse).Count } else { 0 }) dosya"

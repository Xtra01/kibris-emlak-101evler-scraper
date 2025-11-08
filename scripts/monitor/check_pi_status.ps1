#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Raspberry Pi emlak scraper durumunu kontrol eder
.DESCRIPTION
    Container durumu, log özeti, file count, disk kullanımı gibi metrikleri gösterir
.EXAMPLE
    .\check_pi_status.ps1
    .\check_pi_status.ps1 -Detailed
#>

param(
    [switch]$Detailed,
    [switch]$Continuous,
    [int]$IntervalSeconds = 120
)

$PI_HOST = "ekrem@192.168.1.143"
$CONTAINER_NAME = "emlak-scraper-101evler"
$PROJECT_PATH = "/home/ekrem/projects/emlak-scraper"

function Show-Banner {
    Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       🍓 RASPBERRY PI 5 - SCRAPER STATUS MONITOR 🍓          ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "📅 Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
}

function Get-ContainerStatus {
    Write-Host "🐳 CONTAINER STATUS:" -ForegroundColor Yellow
    
    $status = ssh $PI_HOST "docker ps --filter name=$CONTAINER_NAME --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $status -ForegroundColor White
        
        # Health check
        $health = ssh $PI_HOST "docker inspect $CONTAINER_NAME --format='{{.State.Health.Status}}' 2>/dev/null"
        if ($health -match "healthy") {
            Write-Host "   ✅ Health: $health" -ForegroundColor Green
        } elseif ($health -match "unhealthy") {
            Write-Host "   ❌ Health: $health" -ForegroundColor Red
        } else {
            Write-Host "   ⚪ Health: N/A (no healthcheck)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ❌ Container not found or SSH failed!" -ForegroundColor Red
        return $false
    }
    Write-Host ""
    return $true
}

function Get-FileCount {
    Write-Host "📄 DATA FILES:" -ForegroundColor Yellow
    
    # Listings count
    $listings = ssh $PI_HOST "find $PROJECT_PATH/data/raw/listings -name '*.html' 2>/dev/null | wc -l"
    
    # Search pages count
    $pages = ssh $PI_HOST "find $PROJECT_PATH/data/raw/pages -name '*.html' 2>/dev/null | wc -l"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   📋 Listing files: $listings" -ForegroundColor White
        Write-Host "   🔍 Search pages: $pages" -ForegroundColor White
        
        # Progress indicator
        $expected = 20000
        $percentage = [math]::Round(($listings / $expected) * 100, 1)
        
        $progressBar = ""
        $filled = [math]::Floor($percentage / 5)
        for ($i = 0; $i -lt 20; $i++) {
            if ($i -lt $filled) {
                $progressBar += "█"
            } else {
                $progressBar += "░"
            }
        }
        
        Write-Host "   📊 Progress: [$progressBar] $percentage%" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Cannot access data directory!" -ForegroundColor Red
    }
    Write-Host ""
}

function Get-StateInfo {
    Write-Host "📋 SCAN STATE:" -ForegroundColor Yellow
    
    $stateJson = ssh $PI_HOST "cat $PROJECT_PATH/data/cache/scraper_state.json 2>/dev/null"
    
    if ($LASTEXITCODE -eq 0 -and $stateJson) {
        try {
            $state = $stateJson | ConvertFrom-Json
            
            $completed = $state.completed.Count
            $failed = $state.failed.Count
            $total = 72
            
            Write-Host "   ✅ Completed: $completed/$total" -ForegroundColor Green
            Write-Host "   ❌ Failed: $failed" -ForegroundColor Red
            
            if ($state.current) {
                Write-Host "   ⏳ Current: $($state.current.name)" -ForegroundColor Yellow
            } else {
                Write-Host "   ⏸️  Status: Idle or Finished" -ForegroundColor Gray
            }
            
            # Show last 3 completed configs
            if ($completed -gt 0) {
                Write-Host "`n   📝 Last completed:" -ForegroundColor Gray
                $state.completed | Select-Object -Last 3 | ForEach-Object {
                    Write-Host "      • $($_.name)" -ForegroundColor DarkGray
                }
            }
        } catch {
            Write-Host "   ⚠️  State file exists but cannot parse JSON" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  State file not found (scan may not have started)" -ForegroundColor Yellow
    }
    Write-Host ""
}

function Get-LogSummary {
    Write-Host "📜 LOG SUMMARY (last 20 lines):" -ForegroundColor Yellow
    
    $logs = ssh $PI_HOST "docker logs $CONTAINER_NAME 2>&1 | tail -20"
    
    if ($LASTEXITCODE -eq 0) {
        # Color-code important lines
        $logs -split "`n" | ForEach-Object {
            if ($_ -match "ERROR|FAILED|HATA") {
                Write-Host "   $_" -ForegroundColor Red
            } elseif ($_ -match "SUCCESS|COMPLETE|BASARILI") {
                Write-Host "   $_" -ForegroundColor Green
            } elseif ($_ -match "START|BEGIN") {
                Write-Host "   $_" -ForegroundColor Cyan
            } elseif ($_ -match "\[.*?/72\]") {
                Write-Host "   $_" -ForegroundColor Yellow
            } else {
                Write-Host "   $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   ❌ Cannot read container logs!" -ForegroundColor Red
    }
    Write-Host ""
}

function Get-DiskUsage {
    Write-Host "💾 DISK USAGE:" -ForegroundColor Yellow
    
    $disk = ssh $PI_HOST "df -h / | tail -1 | awk '{print \`$3,\`$4,\`$5}'"
    
    if ($LASTEXITCODE -eq 0) {
        $parts = $disk -split " "
        Write-Host "   Used: $($parts[0])" -ForegroundColor White
        Write-Host "   Available: $($parts[1])" -ForegroundColor White
        Write-Host "   Usage: $($parts[2])" -ForegroundColor White
    }
    Write-Host ""
}

function Get-DetailedStatus {
    Write-Host "🔍 DETAILED DIAGNOSTICS:" -ForegroundColor Yellow
    Write-Host ""
    
    # CPU & RAM
    Write-Host "   💻 System Resources:" -ForegroundColor Cyan
    $resources = ssh $PI_HOST "free -h | grep Mem | awk '{print \`$3,\`$2}' && uptime | awk -F'load average:' '{print \`$2}'"
    if ($LASTEXITCODE -eq 0) {
        $lines = $resources -split "`n"
        $mem = $lines[0] -split " "
        Write-Host "      RAM Used: $($mem[0]) / $($mem[1])" -ForegroundColor White
        Write-Host "      Load Average: $($lines[1])" -ForegroundColor White
    }
    Write-Host ""
    
    # Container resource usage
    Write-Host "   📊 Container Resources:" -ForegroundColor Cyan
    $stats = ssh $PI_HOST "docker stats $CONTAINER_NAME --no-stream --format 'CPU: {{.CPUPerc}} | RAM: {{.MemUsage}}' 2>/dev/null"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      $stats" -ForegroundColor White
    }
    Write-Host ""
    
    # Network check
    Write-Host "   🌐 Network Connectivity:" -ForegroundColor Cyan
    $ping = ssh $PI_HOST "ping -c 1 101evler.com >/dev/null 2>&1 && echo 'OK' || echo 'FAILED'"
    if ($ping -match "OK") {
        Write-Host "      ✅ 101evler.com reachable" -ForegroundColor Green
    } else {
        Write-Host "      ❌ 101evler.com unreachable!" -ForegroundColor Red
    }
    Write-Host ""
}

function Show-QuickCommands {
    Write-Host "🔧 QUICK COMMANDS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   View live logs:" -ForegroundColor Cyan
    Write-Host "   ssh $PI_HOST 'docker logs -f $CONTAINER_NAME'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Stop container:" -ForegroundColor Cyan
    Write-Host "   ssh $PI_HOST 'docker stop $CONTAINER_NAME'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Restart container:" -ForegroundColor Cyan
    Write-Host "   ssh $PI_HOST 'docker restart $CONTAINER_NAME'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Download data:" -ForegroundColor Cyan
    Write-Host "   scp -r $PI_HOST`:$PROJECT_PATH/data/raw/listings ./data_backup/" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
do {
    Clear-Host
    Show-Banner
    
    # Core checks
    $containerRunning = Get-ContainerStatus
    
    if ($containerRunning) {
        Get-FileCount
        Get-StateInfo
        Get-LogSummary
        Get-DiskUsage
        
        if ($Detailed) {
            Get-DetailedStatus
        }
    }
    
    Show-QuickCommands
    
    if ($Continuous) {
        Write-Host "🔄 Refreshing in $IntervalSeconds seconds... (Press Ctrl+C to stop)" -ForegroundColor Cyan
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Continuous)

Write-Host "✅ Status check complete!" -ForegroundColor Green
Write-Host ""

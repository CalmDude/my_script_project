# Check Portfolio UI Status
# Run this script to see if the Portfolio Manager UI is currently running

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Portfolio Manager UI Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking port 8501..." -ForegroundColor Gray

# Use curl to test if port is responding (fastest method)
try {
    $response = curl.exe -s -m 2 http://localhost:8501 2>$null
    if ($LASTEXITCODE -eq 0 -or $response) {
        Write-Host "✅ Portfolio UI is RUNNING" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Access URL: http://localhost:8501" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To stop the UI, run: .\scripts\stop_ui.ps1" -ForegroundColor Gray
    }
    else {
        Write-Host "❌ Portfolio UI is NOT running" -ForegroundColor Red
        Write-Host ""
        Write-Host "To start the UI, run: .\scripts\start_ui.ps1" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Portfolio UI is NOT running" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start the UI, run: .\scripts\start_ui.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

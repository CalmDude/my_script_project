# Stop Portfolio UI
$ErrorActionPreference = "Continue"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stopping Portfolio Manager UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stopping Python processes..." -ForegroundColor Gray
$killed = $false
$pythonProcs = Get-Process -Name "python*" -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "Found $($pythonProcs.Count) Python process(es)" -ForegroundColor Yellow
    foreach ($proc in $pythonProcs) {
        Write-Host "  Stopping PID: $($proc.Id)" -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $killed = $true
    }
    if ($killed) {
        Start-Sleep -Milliseconds 500
        Write-Host "All Python processes stopped!" -ForegroundColor Green
    }
} else {
    Write-Host "No Python processes found running." -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Port 8501 is now available." -ForegroundColor Green
Write-Host ""

# Create scheduled task for Portfolio Analysis with Email Support
$ErrorActionPreference = 'Stop'
Write-Host "=" * 80
Write-Host "Portfolio Analysis Automation Setup" -ForegroundColor Cyan
Write-Host "=" * 80

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path
$pythonScript = Join-Path $projectRoot 'src\run_portfolio_analysis.py'
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    Write-Host "[ERROR] Virtual environment not found: $venvPython" -ForegroundColor Red
    Write-Host "[ACTION] Run scripts\setup_repo.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Python: $venvPython"
Write-Host "[OK] Script: $pythonScript"

# Check email config
$emailConfig = Join-Path $projectRoot 'config\email_config.json'
if (-not (Test-Path $emailConfig)) {
    Write-Host "[WARN] Email config not found - emails will not be sent" -ForegroundColor Yellow
    Write-Host "[INFO] See docs\AUTOMATION_SETUP.md to setup email" -ForegroundColor Cyan
}

Write-Host "[INFO] Creating scheduled task..."

$action = New-ScheduledTaskAction -Execute $venvPython -Argument "$pythonScript --email" -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName 'Portfolio Analysis - Daily Report' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Run portfolio analysis and email results daily at 9:00 AM' -Force | Out-Null

Write-Host "[OK] Task created: Portfolio Analysis - Daily Report" -ForegroundColor Green
Write-Host "[OK] Schedule: Daily at 9:00 AM" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] To test: Open Task Scheduler (taskschd.msc) and run manually" -ForegroundColor Cyan
Write-Host "[INFO] Full setup guide: docs\AUTOMATION_SETUP.md" -ForegroundColor Cyan

# Create scheduled task for Portfolio Analysis
$ErrorActionPreference = 'Stop'
Write-Host "Portfolio Analysis Automation Setup" -ForegroundColor Cyan
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptPath 'run_portfolio_analysis.py'
$venvPython = Join-Path $scriptPath '.venv\Scripts\python.exe'
if (Test-Path $venvPython) { $pythonExe = $venvPython } else { $pythonExe = 'python.exe' }
Write-Host "Python: $pythonExe"
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "\"$pythonScript\"" -WorkingDirectory $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'Portfolio Analysis' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Automated portfolio analysis' -Force | Out-Null
Write-Host 'Task created: Portfolio Analysis (Daily at 9:00 AM)' -ForegroundColor Green

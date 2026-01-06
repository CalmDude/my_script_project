# Portfolio Analysis Automation Setup

## Option 1: Run Manually

Execute the analysis on-demand:

```powershell
python run_portfolio_analysis.py
```

Or from VS Code terminal:
```powershell
.\run_portfolio_analysis.py
```

## Option 2: Schedule with Windows Task Scheduler

### Quick Setup (Daily at 9 AM)

Run this PowerShell script to create a scheduled task:

```powershell
# Create scheduled task for daily analysis at 9:00 AM
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "run_portfolio_analysis.py" -WorkingDirectory "C:\workspace\my_script_project"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "Portfolio Analysis" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Automated portfolio analysis and report generation"

Write-Host "✓ Scheduled task created: Portfolio Analysis (Daily at 9:00 AM)"
```

### Custom Schedule Options

**Weekly (Monday at 6 AM)**:
```powershell
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 6:00AM
```

**Multiple times per day**:
```powershell
$trigger1 = New-ScheduledTaskTrigger -Daily -At 9:00AM
$trigger2 = New-ScheduledTaskTrigger -Daily -At 5:00PM
# Add both triggers when registering task
```

### Verify Task

```powershell
Get-ScheduledTask -TaskName "Portfolio Analysis"
```

### Test Task Manually

```powershell
Start-ScheduledTask -TaskName "Portfolio Analysis"
```

### Remove Task

```powershell
Unregister-ScheduledTask -TaskName "Portfolio Analysis" -Confirm:$false
```

## Output

Each run generates timestamped reports in `portfolio_results/`:
- `trading_playbook_YYYYMMDD_HHMMSS.pdf`
- `portfolio_tracker_YYYYMMDD_HHMMSS.xlsx`

Executed notebooks are saved as:
- `portfolio_analysis_executed_YYYYMMDD_HHMMSS.ipynb`

## Prerequisites

Install nbconvert if not already installed:
```powershell
pip install nbconvert
```

## Logs

Task Scheduler logs are in:
- Event Viewer → Task Scheduler Library → Microsoft → Windows → TaskScheduler → Operational

## Troubleshooting

**Issue**: "Python not found"
**Fix**: Use full Python path in task action:
```powershell
$action = New-ScheduledTaskAction -Execute "C:\workspace\my_script_project\.venv\Scripts\python.exe" -Argument "run_portfolio_analysis.py" -WorkingDirectory "C:\workspace\my_script_project"
```

**Issue**: Task runs but no output
**Fix**: Check that VS Code is closed (kernel conflicts) or use `-RunLevel Highest` in principal

**Issue**: Need email notifications
**Fix**: Add email logic to `run_portfolio_analysis.py` using smtplib after successful execution

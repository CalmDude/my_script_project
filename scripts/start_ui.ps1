# Start Portfolio UI
# Run this script to launch the Streamlit portfolio management interface
# Double-click this file or run: .\scripts\start_ui.ps1

$ErrorActionPreference = "Stop"

# Get the script's directory and navigate to project root
$scriptPath = Split-Path -Parent $PSScriptRoot
Set-Location $scriptPath

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Portfolio Manager UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please run setup first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if streamlit is installed
$streamlitCheck = & ".venv\Scripts\python.exe" -c "import streamlit" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Streamlit not installed!" -ForegroundColor Red
    Write-Host "   Installing streamlit..." -ForegroundColor Yellow
    & ".venv\Scripts\pip.exe" install streamlit
}

Write-Host "[OK] Starting Streamlit..." -ForegroundColor Green
Write-Host ""
Write-Host "Portfolio UI will open in your browser" -ForegroundColor Cyan
Write-Host "URL: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Keep this window open!" -ForegroundColor Yellow
Write-Host "   - Minimize (do not close) this window" -ForegroundColor Yellow
Write-Host "   - Press Ctrl+C to stop the UI" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
& ".venv\Scripts\python.exe" -m streamlit run src\portfolio_ui.py

Write-Host ""
Write-Host "UI has been stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"

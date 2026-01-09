# Full Project Backup Script
# Creates a complete backup of your portfolio analyzer

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Portfolio Analyzer - Full Backup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is clean
Write-Host "Checking git status..." -ForegroundColor Yellow
cd C:\workspace\portfolio_analyser
$gitStatus = git status --porcelain

if ($gitStatus) {
    Write-Host ""
    Write-Host "[WARNING] You have uncommitted changes!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Uncommitted files:" -ForegroundColor Gray
    git status --short
    Write-Host ""
    
    $commit = Read-Host "Do you want to commit these changes? (y/n)"
    
    if ($commit -eq "y") {
        $message = Read-Host "Enter commit message"
        git add .
        git commit -m $message
        Write-Host "[OK] Changes committed" -ForegroundColor Green
    }
}

# Push to remote
Write-Host ""
Write-Host "Pushing to remote repository..." -ForegroundColor Yellow
try {
    git push origin main
    Write-Host "[OK] Pushed to GitHub/GitLab" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Could not push to remote" -ForegroundColor Red
    Write-Host "       Make sure you have a remote configured" -ForegroundColor Gray
}

# Create local backup
Write-Host ""
Write-Host "Creating local backup..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "portfolio_analyser_backup_$timestamp"

# Ask for backup location
Write-Host ""
Write-Host "Select backup location:" -ForegroundColor Cyan
Write-Host "  1. Desktop"
Write-Host "  2. Documents"
Write-Host "  3. OneDrive (if available)"
Write-Host "  4. Custom path"
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" { $backupBase = "$env:USERPROFILE\Desktop" }
    "2" { $backupBase = "$env:USERPROFILE\Documents" }
    "3" { 
        if (Test-Path "$env:OneDrive") {
            $backupBase = "$env:OneDrive"
        }
        else {
            Write-Host "[WARNING] OneDrive not found, using Documents" -ForegroundColor Yellow
            $backupBase = "$env:USERPROFILE\Documents"
        }
    }
    "4" { 
        $backupBase = Read-Host "Enter full backup path (e.g., D:\Backups)"
        if (-not (Test-Path $backupBase)) {
            New-Item -ItemType Directory -Path $backupBase -Force | Out-Null
        }
    }
    default { $backupBase = "$env:USERPROFILE\Documents" }
}

$backupPath = Join-Path $backupBase $backupName

# Create backup directory
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# Copy essential files and folders
Write-Host ""
Write-Host "Copying files..." -ForegroundColor Yellow

$itemsToCopy = @(
    "src",
    "data",
    "scripts",
    "docs",
    "config",
    "tests",
    "notebooks",
    ".streamlit",
    ".gitignore",
    ".env.example",
    "README.md",
    "requirements.txt"
)

foreach ($item in $itemsToCopy) {
    $sourcePath = "C:\workspace\portfolio_analyser\$item"
    if (Test-Path $sourcePath) {
        Copy-Item -Path $sourcePath -Destination $backupPath -Recurse -Force
        Write-Host "  [OK] Copied: $item" -ForegroundColor Gray
    }
}

# Create backup info file
$backupInfo = @"
Portfolio Analyzer Backup
=========================
Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Source: C:\workspace\portfolio_analyser
Git Branch: $(git branch --show-current)
Git Commit: $(git rev-parse HEAD)
Git Commit Message: $(git log -1 --pretty=%B)

Restore Instructions:
---------------------
1. Extract/copy this folder to desired location
2. Open terminal in the folder
3. Run: python -m venv .venv
4. Run: .\.venv\Scripts\Activate.ps1
5. Run: pip install -r requirements.txt
6. Your project is ready!

"@

$backupInfo | Out-File -FilePath "$backupPath\BACKUP_INFO.txt" -Encoding UTF8

# Create compressed archive
Write-Host ""
Write-Host "Creating compressed archive..." -ForegroundColor Yellow
$zipPath = "$backupBase\$backupName.zip"

try {
    Compress-Archive -Path $backupPath -DestinationPath $zipPath -Force
    Write-Host "[OK] Archive created: $zipPath" -ForegroundColor Green
    
    # Calculate size
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "    Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Gray
    
    # Remove uncompressed folder
    Remove-Item -Path $backupPath -Recurse -Force
    Write-Host "[OK] Cleaned up temporary files" -ForegroundColor Green
}
catch {
    Write-Host "[WARNING] Could not create archive, kept folder instead" -ForegroundColor Yellow
    Write-Host "          Folder: $backupPath" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Backup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup Locations:" -ForegroundColor Yellow
Write-Host "  1. GitHub/GitLab: origin/main" -ForegroundColor Gray
Write-Host "  2. Local Archive: $zipPath" -ForegroundColor Gray
Write-Host ""
Write-Host "To restore:" -ForegroundColor Cyan
Write-Host "  - From GitHub: git clone <your-repo-url>" -ForegroundColor Gray
Write-Host "  - From Archive: Extract zip and run pip install -r requirements.txt" -ForegroundColor Gray
Write-Host ""

Read-Host "Press Enter to exit"

<#
setup_repo.ps1
Initializes a Git repository in the project folder, ensures a .gitignore exists,
and creates an initial commit. Usage:
  - Open PowerShell in the project folder and run: .\setup_repo.ps1 -Name "Your Name" -Email "you@example.com"
#>
param(
  [string]$Name = "autocommit",
  [string]$Email = "noreply@example.com",
  [switch]$Force
)

function Check-Git {
  return (Get-Command git -ErrorAction SilentlyContinue) -ne $null
}

if (-not (Check-Git)) {
  Write-Error "Git is not installed or not available in PATH. Install Git first: https://git-scm.com/download/win"
  exit 1
}

# Work in the script directory
Set-Location -Path (Split-Path -LiteralPath $PSCommandPath -Parent)

# Ensure .gitignore exists (create or update when -Force passed)
$gitignoreContent = @"
.venv/
__pycache__/
*.pyc
.env
"@

if (-not (Test-Path .gitignore) -or $Force) {
  $gitignoreContent | Out-File -Encoding UTF8 -FilePath .gitignore
  Write-Host ".gitignore created/updated"
} else {
  Write-Host ".gitignore already present"
}

# Initialize repo if needed
if (-not (Test-Path .git)) {
  git init -b main
  Write-Host "Initialized empty Git repository"
} else {
  Write-Host "Git repository already initialized"
}

# Make initial commit
git add .
try {
  git -c user.name="$Name" -c user.email="$Email" commit -m "Initial commit"
  Write-Host "Initial commit created"
} catch {
  Write-Host "Nothing to commit or commit failed: $_"
}

Write-Host "Done. Run 'git status' to verify."

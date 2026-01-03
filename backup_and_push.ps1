<#
backup_and_push.ps1
Safely stage, commit (with timestamp) and push changes to the remote repository.
Prompts for confirmation before doing anything. Intended for novices who want a single
command to back up local changes to GitHub.

Usage:
  1) Open PowerShell in the project folder.
  2) Run: .\backup_and_push.ps1
  3) Optionally pass -Message "your commit message" or -Auto to skip confirmations.
#>
param(
  [string]$Message = "",
  [switch]$Auto
)

function Check-Git {
  return (Get-Command git -ErrorAction SilentlyContinue) -ne $null
}

if (-not (Check-Git)) {
  Write-Error "Git is not installed or not available in PATH. Install Git first: https://git-scm.com/download/win"
  exit 1
}

# Show current branch
$currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
if ($LASTEXITCODE -ne 0) { Write-Error "Not a git repo or git failed."; exit 1 }
Write-Host "Current branch: $currentBranch"

# Show pending changes
$changes = git status --porcelain
if (-not $changes) {
  Write-Host "No local changes detected."
  if (-not $Auto) {
    $confirm = Read-Host "Would you like to create a snapshot tag of the current commit and push it? (y/N)"
    if ($confirm -notin @('y','Y')) { Write-Host "Nothing to do."; exit 0 }
  }
  $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $tag = "backup-$timestamp"
  git tag $tag
  git push origin $tag
  Write-Host "Created and pushed tag: $tag"
  exit 0
}

Write-Host "Local changes:"; git status --short
if (-not $Auto) {
  $confirm = Read-Host "Stage, commit, and push these changes to origin/$currentBranch? (y/N)"
  if ($confirm -notin @('y','Y')) { Write-Host "Aborted."; exit 0 }
}

# Stage everything
git add -A

# Build commit message
if (-not $Message) { $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"; $Message = "Backup: $timestamp" }

# Commit
git commit -m "$Message" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Nothing to commit or commit failed."; exit 0
}

# Create and push a tag with timestamp for extra safety
$tag = "backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
git tag $tag

# Push branch and tag
git push origin $currentBranch
if ($LASTEXITCODE -ne 0) { Write-Warning "Push failed. Please check your remote and credentials."; exit 1 }

git push origin $tag
Write-Host "Backup complete. Pushed branch: origin/$currentBranch and tag: $tag"

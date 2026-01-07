<#
safe_commit.ps1
Lightweight helper to view pending changes, run pre-commit checks, and commit/push interactively.
Usage: .\safe_commit.ps1 -Message "Short message"
#>
param(
  [string]$Message = "",
  [switch]$Auto
)

# Ensure git available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Error "Git not found."; exit 1 }

# Show status
git status --short
if (-not $Auto) {
  $go = Read-Host "Stage and commit these changes? (y/N)"
  if ($go -notin @('y','Y')) { Write-Host "Aborted."; exit 0 }
}

# Run pre-commit hooks if present
if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
  Write-Host "Running pre-commit hooks..."
  pre-commit run --all-files
  if ($LASTEXITCODE -ne 0) { Write-Error "Pre-commit failed. Fix issues before committing."; exit 1 }
} else {
  Write-Host "pre-commit not installed; consider running install_precommit.ps1"
}

# Stage & commit
git add -A
if (-not $Message) { $Message = Read-Host "Commit message" }
git commit -m "$Message"
if ($LASTEXITCODE -ne 0) { Write-Host "Nothing to commit"; exit 0 }

# Push
$currentBranch = git rev-parse --abbrev-ref HEAD
git push origin $currentBranch
Write-Host "Pushed to origin/$currentBranch"

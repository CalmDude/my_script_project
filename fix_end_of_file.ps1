# Script to fix missing end-of-file newlines in the add-tests branch
# This fixes the CI pre-commit failures

$ErrorActionPreference = "Stop"

Write-Host "=== Fixing End-of-File Issues for CI ===" -ForegroundColor Cyan
Write-Host

# Check if we're in the right repository
if (-not (Test-Path "script.py")) {
    Write-Host "Error: This script must be run from the repository root" -ForegroundColor Red
    exit 1
}

# Save current branch
$currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host "Current branch: $currentBranch"

# Check if add-tests branch exists locally
git show-ref --verify --quiet refs/heads/add-tests 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fetching add-tests branch from PR #4..."
    git fetch origin +refs/pull/4/head:add-tests
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to fetch add-tests branch" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Checking out add-tests branch..."
git checkout add-tests
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to checkout add-tests branch" -ForegroundColor Red
    exit 1
}

Write-Host
Write-Host "Installing pre-commit..."
pip install pre-commit --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install pre-commit" -ForegroundColor Red
    git checkout $currentBranch
    exit 1
}

Write-Host
Write-Host "Running pre-commit to fix end-of-file issues..."
pre-commit run --all-files

Write-Host
Write-Host "Checking if there are changes to commit..."
git diff --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ No changes needed - all files already have proper end-of-file newlines!" -ForegroundColor Green
} else {
    Write-Host "Committing fixes..."
    git add -A
    git commit -m "fix: add missing newlines at end of files for pre-commit checks"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host
        Write-Host "✓ Changes committed successfully!" -ForegroundColor Green
        Write-Host
        Write-Host "To push these changes, run:" -ForegroundColor Yellow
        Write-Host "  git push origin add-tests"
        Write-Host
        Write-Host "Or if you're working with a fork:"
        Write-Host "  git push <your-remote> add-tests"
    } else {
        Write-Host "Error: Failed to commit changes" -ForegroundColor Red
        git checkout $currentBranch
        exit 1
    }
}

Write-Host
Write-Host "Switching back to $currentBranch..."
git checkout $currentBranch

Write-Host
Write-Host "=== Done! ===" -ForegroundColor Cyan
Write-Host
Write-Host "The end-of-file issues have been fixed on the add-tests branch."
Write-Host "Push the changes to trigger a new CI build that should pass."

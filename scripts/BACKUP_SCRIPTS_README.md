# Backup Scripts Usage

## Quick Backup & Push to Git

**File:** `backup_and_push.ps1`

### Basic Usage
```powershell
# Interactive mode (prompts for confirmation)
.\scripts\backup_and_push.ps1

# With custom message
.\scripts\backup_and_push.ps1 -Message "Updated portfolio scanner"

# Auto mode (no confirmations)
.\scripts\backup_and_push.ps1 -Auto
```

### What It Does
1. Shows current branch and pending changes
2. Prompts for confirmation
3. Stages all changes (`git add -A`)
4. Commits with timestamp or your message
5. Creates a backup tag (e.g., `backup-20260115-210530`)
6. Pushes branch and tag to GitHub

### When To Use
- Daily/weekly backups to GitHub
- Quick commits after making changes
- Before risky operations

---

## Full Local + Remote Backup

**File:** `backup_full.ps1`

### Usage
```powershell
.\scripts\backup_full.ps1
```

### What It Does
1. Checks for uncommitted changes (offers to commit)
2. Pushes to GitHub
3. Creates compressed local backup (.zip)
4. Lets you choose backup location:
   - Desktop
   - Documents
   - OneDrive
   - Custom path

### Backup Contents
- All source code (`src/`)
- Your data (`data/`)
- Documentation (`docs/`)
- Notebooks (`notebooks/`)
- Scripts (`scripts/`)
- Configuration files
- Requirements.txt

### When To Use
- Before major changes
- Monthly full backups
- Before system updates/reinstalls
- Creating offline archives

---

## Backup Strategy Recommendation

### Daily/Weekly
```powershell
.\scripts\backup_and_push.ps1 -Message "Weekly portfolio update"
```

### Monthly
```powershell
.\scripts\backup_full.ps1
```
Choose OneDrive or external drive for the .zip file.

### Before Major Changes
```powershell
# 1. Full backup first
.\scripts\backup_full.ps1

# 2. Create checkpoint
git tag checkpoint-before-changes
git push origin checkpoint-before-changes

# 3. Make your changes
# 4. Test thoroughly
# 5. Commit when confident
.\scripts\backup_and_push.ps1 -Message "Major update: [description]"
```

---

## Troubleshooting

### "Git is not installed"
- Install Git: https://git-scm.com/download/win
- Restart PowerShell after installation

### "Push failed"
- Check internet connection
- Verify GitHub credentials
- Run manually: `git push origin main`

### "Execution policy error"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## What Gets Backed Up

✅ **Included:**
- Source code
- Documentation
- Your data files
- Configuration files
- Notebooks
- Scripts

❌ **Excluded (by .gitignore):**
- Virtual environment (`.venv/`)
- Cache files (`__pycache__/`)
- Secret files (`.env`)
- Generated reports
- Large data files

---

## Recovery Instructions

### From GitHub
```powershell
git clone https://github.com/yourusername/portfolio_analyser.git
cd portfolio_analyser
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### From .zip Archive
1. Extract the zip file
2. Open PowerShell in extracted folder
3. Run the same commands above

---

## Advanced: Create Backup Before Running Scanner

```powershell
# Quick pre-scan backup
.\scripts\backup_and_push.ps1 -Message "Pre-scan backup: $(Get-Date -Format 'yyyy-MM-dd')"

# Run your scanner
# If anything goes wrong, you can restore
```

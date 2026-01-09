# Backup Guide

## Full Project Backup

### Quick Backup
```powershell
.\scripts\backup_full.ps1
```

This creates a complete backup of your portfolio analyzer project.

## What the Backup Includes

### ✅ Included
- All source code (`src/`)
- Data files (`data/` - your portfolio holdings, targets, transactions)
- Scripts (`scripts/`)
- Documentation (`docs/`)
- Configuration (`config/`, `.streamlit/`)
- Notebooks (`notebooks/`)
- Tests (`tests/`)
- Requirements and README

### ❌ Excluded (Can Rebuild)
- Virtual environment (`.venv/`) - large, recreate with `pip install`
- Cache files (`__pycache__/`, `.scanner_cache/`)
- Generated reports (`portfolio_results/`, `scanner_results/`)

## Backup Process

**Step 1: Git Check**
- Checks for uncommitted changes
- Offers to commit and add message
- Pushes to GitHub/GitLab (cloud backup)

**Step 2: Local Backup**
- Choose location: Desktop, Documents, OneDrive, or custom path
- Creates timestamped backup folder
- Copies all essential files
- Creates `BACKUP_INFO.txt` with restore instructions

**Step 3: Compression**
- Creates `.zip` archive
- Shows file size
- Removes temporary folder

**Result:**
- Cloud backup: GitHub/GitLab repository
- Local backup: `portfolio_analyser_backup_YYYYMMDD_HHMMSS.zip`

## Restore Instructions

### From GitHub (Recommended)
```powershell
# On new computer
git clone <your-repo-url>
cd portfolio_analyser
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### From Local Backup
1. Extract the `.zip` file to desired location
2. Open PowerShell in extracted folder
3. Run:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Backup Strategy

### Daily (During Development)
```powershell
# Quick git backup
git add .
git commit -m "Description of changes"
git push
```

### Weekly (Milestone)
```powershell
# Full backup with local archive
.\scripts\backup_full.ps1
# Copy the .zip to external drive
```

### Before Major Changes
```powershell
# Create checkpoint
git tag -a v1.0 -m "Working version before changes"
git push --tags
.\scripts\backup_full.ps1
```

## Backup Locations

The script lets you choose where to save the local backup:

**Option 1: Desktop**
- `C:\Users\YourName\Desktop\portfolio_analyser_backup_*.zip`
- Quick access, easy to find

**Option 2: Documents**
- `C:\Users\YourName\Documents\portfolio_analyser_backup_*.zip`
- Organized location

**Option 3: OneDrive**
- `C:\Users\YourName\OneDrive\portfolio_analyser_backup_*.zip`
- Automatically synced to cloud

**Option 4: Custom**
- External drive (e.g., `D:\Backups\`)
- Network drive
- USB drive

## Recovery Scenarios

### Hard Drive Failure
1. On new computer, install Python
2. Clone from GitHub: `git clone <repo-url>`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. **All your code is safe!**

### Accidental File Deletion
1. Restore from GitHub: `git checkout -- <filename>`
2. Or extract specific file from `.zip` backup

### Need to Revert Changes
1. Check git history: `git log`
2. Revert to previous commit: `git checkout <commit-hash>`
3. Or restore entire folder from `.zip`

### Computer Stolen/Lost
1. On new computer, clone from GitHub
2. Your code is in the cloud - nothing lost!

## Best Practices

### Multiple Backup Layers

**Layer 1: GitHub/GitLab (Primary)**
- Automatic with `git push`
- Version history
- Accessible from anywhere
- Free unlimited storage for code

**Layer 2: Local Archive**
- Run `backup_full.ps1` weekly
- Keep on external drive
- Fast restore for recent version

**Layer 3: Cloud Storage**
- Copy `.zip` to OneDrive/Dropbox/Google Drive
- Automatic sync
- Additional redundancy

### Backup Schedule

**After each session:**
```powershell
git add .
git commit -m "Session updates"
git push
```

**Weekly:**
```powershell
.\scripts\backup_full.ps1
# Move .zip to external drive
```

**Before major updates:**
```powershell
git tag -a v2.0 -m "Stable version"
git push --tags
.\scripts\backup_full.ps1
```

## File Sizes

**Typical backup sizes:**
- Code only: ~500 KB
- With data files: ~1-2 MB
- Virtual environment (not included): ~200-500 MB

The `.zip` files are small and quick to create/transfer.

## Automation Options

### Auto-backup on Schedule

Create scheduled task to run backup weekly:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Weekly (e.g., every Sunday)
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-File C:\workspace\portfolio_analyser\scripts\backup_full.ps1`

### Pre-commit Hook

Auto-backup before every commit:
1. Create `.git/hooks/pre-commit`
2. Add backup script call
3. Backup runs automatically on `git commit`

## Troubleshooting

### "No remote configured"
```powershell
# Add GitHub/GitLab remote
git remote add origin https://github.com/yourusername/portfolio_analyser.git
git push -u origin main
```

### "Permission denied" when creating zip
- Check you have write permissions to backup location
- Try different backup location
- Run PowerShell as Administrator

### Large backup size
- Virtual environment excluded by default
- Check if result folders have old large files
- Clean up generated reports before backup

### Backup takes too long
- Check internet speed (for git push)
- Exclude additional folders if needed
- Use SSD for faster compression

## Security

### What to Include in Backups
- ✅ Source code
- ✅ Documentation
- ✅ Configuration templates (.example files)
- ⚠️ Data files (your choice - contains holdings)
- ❌ `.env` files (contains secrets - keep separate)

### Sensitive Data
If your data files contain sensitive information:
- Keep separate encrypted backup of `data/` folder
- Add `data/*.csv` to `.gitignore` before pushing to GitHub
- Use private GitHub repository

### Backup Encryption
For extra security:
```powershell
# After creating backup, encrypt it
# Requires 7-Zip
7z a -p -mhe=on backup_encrypted.7z portfolio_analyser_backup_*.zip
# Will prompt for password
```

## Quick Reference

| Task | Command |
|------|---------|
| Full backup | `.\scripts\backup_full.ps1` |
| Quick commit | `git add . && git commit -m "msg" && git push` |
| Check status | `git status` |
| View history | `git log --oneline` |
| Restore file | `git checkout -- <file>` |
| Clone backup | `git clone <repo-url>` |

## Support

If you need to restore and have issues:
1. Check `BACKUP_INFO.txt` inside backup archive
2. Ensure Python is installed
3. Verify requirements.txt exists
4. Run pip install with verbose flag: `pip install -r requirements.txt -v`

Git Setup
=========

1. Install Git (if not installed):
   - Download and install: https://git-scm.com/download/win
   - Or use winget: `winget install --id Git.Git -e --source winget`

2. After installing Git, open PowerShell in the project folder (`my_script_project`) and run:
   - `./setup_repo.ps1 -Name "Your Name" -Email "you@example.com"`

3. Verify:
   - `git status`
   - `git log --oneline`

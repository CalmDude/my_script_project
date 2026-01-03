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

Branch protection & 2FA (recommended):
- Turn on 2FA for your GitHub account: https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa
- To require PRs and passing CI before merges, enable **Branch protection** for `main` in your GitHub repo Settings → Branches → Add Rule. Require:
  - Require pull request reviews before merging
  - Require status checks to pass before merging (select `Pre-commit checks` once CI runs)

Optional: If you'd like, I can create the remote repo for you and enable branch protection using the `gh` CLI — you'll need to authenticate (`gh auth login`).

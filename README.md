# my_script_project

This project runs `script.py` which fetches historical data via `yfinance` and computes SMAs, VPVR, and pivot levels.

Setup (Windows PowerShell):

1. Create virtualenv:
   - python -m venv .venv
2. Install dependencies:
   - .\.venv\Scripts\python.exe -m pip install --upgrade pip
   - .\.venv\Scripts\python.exe -m pip install -r requirements.txt
3. Run script:
   - .\.venv\Scripts\python.exe script.py

Notes:
- Enter a ticker symbol when prompted, e.g., PLTR.

Backup & Version Control ⚠️
- There's a helper script `setup_repo.ps1` to initialize the repo (run it after installing Git).
- Use `./backup_and_push.ps1` to safely stage, commit (timestamped) and push local changes to GitHub. It prompts for confirmation before changing anything.
- Use `./safe_commit.ps1` for a lightweight commit flow that runs `pre-commit` and shows `git status` before committing and pushing.
- To add basic safety checks (detect secrets, format hooks), run `./install_precommit.ps1` to install `pre-commit` and enable the hooks defined in `.pre-commit-config.yaml`.
- A CI workflow (`.github/workflows/ci.yml`) runs pre-commit checks on push/PR to `main`. Consider enabling branch protection in GitHub to require the "Pre-commit checks" workflow to pass before merging to `main`.
- Never store API keys or other secrets in the repo. Use the `.env` file locally (ignored) and GitHub Secrets for CI. See `SECURITY.md` for more details.
- If you want fully automatic backups (watcher that commits and pushes on file change), tell me and I can add one, but I don't recommend it for novices (it can create noisy commits and accidentally push secrets).

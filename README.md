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

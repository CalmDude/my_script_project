"""Quick test to verify notebook code works"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pandas as pd

# Import modules
import technical_analysis as ta
from portfolio_reports import create_trading_playbook_pdf, create_portfolio_tracker_excel

# Setup directories
ROOT = Path.cwd()
RESULTS_DIR = ROOT / 'portfolio_results'
RESULTS_DIR.mkdir(exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")

print("✓ Environment ready")
print(f"✓ Results directory: {RESULTS_DIR}")
print(f"✓ Timestamp: {TIMESTAMP}")

print("\nIf you see this, the notebook code should work fine!")
print("\nTroubleshooting steps for notebook kernel:")
print("1. In VS Code, click 'Select Kernel' at the top right of the notebook")
print("2. Choose 'Python Environments...'")
print("3. Select '.venv (Python 3.14.2)' from the list")
print("4. Try running the first cell again")

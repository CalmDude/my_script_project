# Larsson Line Portfolio

**AI & Crypto Portfolio Analysis System using Larsson Decision Table Signals**

This project provides comprehensive technical analysis for a focused portfolio of AI stocks and cryptocurrencies using the Larsson decision table methodology. It generates actionable buy/sell signals with detailed entry zones, risk management parameters, and multi-format reporting.

## Portfolio Scope
- **13 Individual Stocks**: TSLA, NVDA, MSFT, META, PLTR, MSTR, ASML, AMD, AVGO, ALAB, MRVL
- **2 Cryptocurrencies**: BTC-USD, SOL-USD
- **2 Sector Baskets**: Main AI Basket, Secondary AI Basket

## Core Features

### Technical Analysis Engine (`technical_analysis.py`)
- **Multi-timeframe SMA Analysis**: Daily (D20/D50/D100/D200) + Weekly (W10/W20/W200)
- **Volume Profile (VPVR)**: POC, Value Area High/Low (60-day daily, 52-week weekly)
- **Pivot Points**: Daily and weekly support/resistance levels (S1/S2/S3, R1/R2/R3)
- **Larsson Signals**: 9-state decision table combining weekly/daily trends
- **Confluence Ratings**: EXTENDED, BALANCED, WEAK (price vs key support levels)

### Portfolio Analysis Notebook (`portfolio_analysis.ipynb`)
**11 Cells - Complete Workflow:**
1. **Environment Setup**: Parse watchlist, initialize workspace
2. **Batch Analysis**: Parallel processing (6 concurrent API calls, ~12s for 15 tickers)
3. **Buy Summary**: Console output with conservative entry zones
4. **Sell Summary**: Console output with phased reduction tranches
5. **Buy Summary PDF**: Single-page quick reference (targets, zones, shares)
6. **Buy Detailed PDF**: Multi-page deep dive (1 page per ticker, 5 sections each)
7. **Sell Summary PDF**: Single-page defensive action table
8. **Sell Detailed PDF**: Multi-page exit playbook (1 page per position, 6 sections each)
9. **Excel Export**: 3-sheet workbook (Buy Actions, Sell Actions, Technical Data)
10. **Cleanup**: Auto-delete old files (keeps 2 most recent of each type)

### Output Formats
- **Console**: Markdown tables for quick review
- **PDF Reports**: Professional single/multi-page reports (ReportLab)
- **Excel Workbooks**: Sortable data with auto-adjusted columns
- **Automatic Cleanup**: Maintains recent 2 files per type in Downloads folder

## Setup (Windows PowerShell)

### 1. Create Virtual Environment
```powershell
python -m venv .venv
```powershell
python -m venv .venv
```

### 2. Install Dependencies
```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Configure Portfolio
Edit `stocks.txt` to customize your watchlist:
- Individual tickers (one per line)
- Baskets: `[Basket Name] ticker1, ticker2, ticker3`

Edit `holdings.csv` to track current positions (ticker, shares, avg_cost)
Edit `targets.csv` to set allocation targets (ticker, target_pct, target_value)

### 4. Run Analysis
Open `portfolio_analysis.ipynb` in VS Code or Jupyter and run all cells.

## Project Structure
```
larsson_line_portfolio/
├── portfolio_analysis.ipynb    # Main analysis notebook (11 cells)
├── technical_analysis.py        # Core technical analysis engine
├── stocks.txt                   # Watchlist configuration
├── holdings.csv                 # Current positions
├── targets.csv                  # Allocation targets
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Key Concepts

### Larsson Decision Table
9-state signal system combining weekly trend (bullish/neutral/bearish) × daily trend:
- **FULL HOLD + ADD**: Strong bullish - primary accumulation signal
- **HOLD**: Neutral - maintain positions
- **HOLD MOST → REDUCE**: Early warning - lighten by 20%
- **REDUCE**: Defensive - trim 40%
- **LIGHT / CASH**: Caution - reduce to 40% of position
- **CASH**: Strong warning - keep only 20%
- **FULL CASH / DEFEND**: Full defensive - phased exit (3 tranches)

### Confluence Ratings
- **EXTENDED**: Price >10% above D100 - wait for pullback
- **BALANCED**: Price near D100 (±10%) - healthy entry zone
- **WEAK**: Price <10% below D100 - broken structure, caution

### Entry Strategy
- **Primary Zone (40-50% of gap)**: Lower Value Area or D100/D200
- **Secondary Zone (25-30% of gap)**: Deeper support levels
- **Final Zone (20-25% of gap)**: Capitulation buys only

### Exit Strategy
- **Phased Reductions**: 1-3 tranches depending on signal severity
- **Sell into Strength**: Target resistance levels (R1/R2/R3), never panic sell at lows
- **Re-Entry Criteria**: 5 conditions must ALL be met (detailed in Sell PDFs)

## Daily Workflow
1. Run Cell 1-2: Get latest signals (~12 seconds)
2. Review Cell 3-4: Check buy/sell console summaries
3. Generate Cell 5-9: Export PDFs/Excel as needed
4. Place limit orders at specified entry/exit zones
5. Run Cell 10: Auto-cleanup old files

## Notes
- **API Limits**: yfinance free tier ~2000 calls/hour (sufficient for 15 tickers)
- **Data Freshness**: Uses most recent close price (after-hours/pre-market noted)
- **Basket Analysis**: Sector baskets analyzed as portfolio health indicators
- **Risk Management**: Max 2% loss per entry zone (detailed in Buy PDFs)

---

## Backup & Version Control ⚠️
- There's a helper script `setup_repo.ps1` to initialize the repo (run it after installing Git).
- Use `./backup_and_push.ps1` to safely stage, commit (timestamped) and push local changes to GitHub. It prompts for confirmation before changing anything.
- Use `./safe_commit.ps1` for a lightweight commit flow that runs `pre-commit` and shows `git status` before committing and pushing.
- To add basic safety checks (detect secrets, format hooks), run `./install_precommit.ps1` to install `pre-commit` and enable the hooks defined in `.pre-commit-config.yaml`.
- A CI workflow (`.github/workflows/ci.yml`) runs pre-commit checks on push/PR to `main`. Consider enabling branch protection in GitHub to require the "Pre-commit checks" workflow to pass before merging to `main`.
- Never store API keys or other secrets in the repo. Use the `.env` file locally (ignored) and GitHub Secrets for CI. See `SECURITY.md` for more details.
- If you want fully automatic backups (watcher that commits and pushes on file change), tell me and I can add one, but I don't recommend it for novices (it can create noisy commits and accidentally push secrets).

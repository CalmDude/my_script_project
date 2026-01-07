# Portfolio Analyzer

**Stock Portfolio Analysis System using Larsson Decision Table Signals**

A comprehensive technical analysis tool for portfolio management using the Larsson decision table methodology. Generates actionable buy/sell signals with detailed entry zones, risk management parameters, and professional PDF/Excel reports.

## Features

- **Multi-timeframe Technical Analysis**: Daily & weekly SMAs, volume profile (VPVR), pivot points
- **Larsson Signal System**: 9-state decision table combining macro (weekly) and short-term (daily) trends
- **Portfolio Analysis**: Complete workflow from data load to report generation with position management
- **Market Scanner**: Scan S&P 500, NASDAQ 100, or custom watchlists for FULL HOLD + ADD signals
- **Professional Reports**: PDF trading playbooks and Excel trackers with detailed entry/exit zones
- **24-Hour Caching**: Intelligent rate limiting to prevent Yahoo Finance API throttling

## Project Structure

```
portfolio_analyser/
├── config/                       # Configuration templates
│   ├── email_config.json.example
│   └── protection.json
├── data/                         # User input files
│   ├── holdings.csv             # Current positions
│   ├── stocks.txt               # Portfolio watchlist
│   └── targets.csv              # Target allocations
├── docs/                         # Documentation
│   ├── INTERACTIVE.md           # Notebook usage guide
│   └── SECURITY.md              # Security best practices
├── notebooks/                    # Jupyter notebooks
│   ├── portfolio_analysis.ipynb # Main portfolio analysis
│   └── full_scanner.ipynb       # Market scanner
├── scripts/                      # Automation utilities
│   ├── backup_and_push.ps1      # Git backup automation
│   ├── install_precommit.ps1    # Pre-commit hook setup
│   ├── safe_commit.ps1          # Interactive commit
│   ├── setup_automation.ps1     # Task scheduler setup
│   └── setup_repo.ps1           # Git initialization
├── src/                          # Python source modules
│   ├── technical_analysis.py    # Core analysis engine
│   ├── portfolio_reports.py     # PDF & Excel generation
│   ├── full_scanner.py          # Market scanner
│   └── run_portfolio_analysis.py # Automation runner
├── tests/                        # Unit tests
│   └── test_analyze_ticker.py
├── portfolio_results/archive/    # Portfolio outputs
├── scanner_results/archive/      # Scanner outputs
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
└── requirements.txt              # Python dependencies
```

## Quick Start

### 1. Setup Environment (Windows PowerShell)

```powershell
# Create virtual environment
python -m venv .venv

# Activate and install dependencies
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Your Portfolio

Edit files in `data/` folder:
- **holdings.csv**: Current positions (ticker, quantity, avg_cost)
- **stocks.txt**: Watchlist (one ticker per line)
- **targets.csv**: Target allocations (ticker, target_pct, target_value)

### 3. Run Analysis

Open `notebooks/portfolio_analysis.ipynb` in VS Code or Jupyter and run all cells.

## Core Components

### Larsson Decision Table

9-state signal system combining weekly × daily trends:

- **FULL HOLD + ADD**: Strongest bullish - primary accumulation
- **HOLD**: Neutral - maintain positions
- **HOLD + REDUCE**: Early warning - lighten by 20%
- **SCALE IN**: Building position gradually
- **LIGHT / CASH**: Caution - reduce to 40%
- **CASH**: Strong warning - keep 20%
- **REDUCE**: Defensive - trim 40%
- **FULL CASH / DEFEND**: Maximum defensive - phased exit

### Entry Strategy

Three-tranche approach based on confluence:
- **Primary Zone (40-50%)**: Value Area Low or D100/D200
- **Secondary Zone (25-30%)**: Deeper support levels
- **Final Zone (20-25%)**: Capitulation buys only

### Technical Indicators

- **Moving Averages**: D20/D50/D100/D200 (daily), W10/W20/W200 (weekly)
- **Volume Profile**: POC, VAH/VAL (60-day, 52-week)
- **Pivot Points**: S1/S2/S3, R1/R2/R3 (daily & weekly)
- **Confluence Ratings**: EXTENDED (>10% above D100), BALANCED (±10%), WEAK (<10% below)

## Daily Workflow

1. Open `notebooks/portfolio_analysis.ipynb`
2. Run all cells (~30 seconds for 15 stocks)
3. Review console output for buy/sell signals
4. Check generated PDFs in `portfolio_results/`
5. Place limit orders at specified zones

## Market Scanner

Use `full_scanner.ipynb` to scan:
- **Portfolio stocks**: All signals with detailed breakdown
- **S&P 500**: ~500 stocks, 5-10 minutes
- **NASDAQ 100**: ~100 stocks, 2-5 minutes

Outputs filtered Excel and PDF reports with only FULL HOLD + ADD signals.

## Technical Notes

- **API Rate Limiting**: 2 concurrent threads with 1-2s delays
- **Cache TTL**: 24 hours to minimize API calls
- **Data Source**: Yahoo Finance (yfinance library)
- **Report Formats**: PDF (ReportLab), Excel (openpyxl)

## Documentation

- `docs/INTERACTIVE.md` - Detailed notebook usage guide
- `docs/SECURITY.md` - Best practices for protecting sensitive data

## Git Workflow (Optional)

Use provided PowerShell scripts for Git automation:
- `scripts/backup_and_push.ps1` - Safe commit and push with confirmations
- `scripts/safe_commit.ps1` - Interactive commit with status check
- `scripts/setup_repo.ps1` - Initialize Git repository

## License

MIT License - See LICENSE file for details

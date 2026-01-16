# GHB Strategy Portfolio Analyzer

**Gold-Gray-Blue Weekly Trading System**

A systematic weekly trading system that uses the GHB Strategy (Gold-Gray-Blue) to generate buy/sell/hold signals based on 200-day SMA and 4-week momentum. Run every Friday after market close to get Monday trade signals for a 25-stock S&P 500 optimized universe.

**Expected Performance:** 46.80% CAGR | 62.86% Win Rate (2021-2025 backtest)

## Features

- **GHB Signal System**: 4-state decision table (P1/P2/N1/N2) based on 200-day SMA and 4-week momentum
- **Weekly Trading Rhythm**: Run Friday after 4pm ET, trade Monday morning - simple and disciplined
- **Variable Position Sizing**: Custom allocations per ticker (e.g., TSLA 50%, NVDA 20%, others 10%)
- **S&P 500 Optimized Universe**: 25 carefully selected stocks backtested for 46.80% CAGR
- **Portfolio Tracking**: Automatic position management, P&L calculation, and state change alerts
- **Universe Health Monitoring**: Automatic alerts when it's time to re-optimize your stock list
- **Professional Reports**: PDF and CSV outputs with buy/sell signals and execution prices
- **Backtesting Engine**: Test the strategy on historical data with configurable parameters

## Project Structure

```
portfolio_analyser/
├── backtest/                     # Backtesting engine
│   ├── config.json              # Backtest configuration
│   ├── run_backtest.py          # Main backtest runner
│   ├── screen_stocks.py         # S&P 500 screening
│   ├── data/                    # Stock universe files
│   └── results/                 # Backtest outputs
├── data/                         # Portfolio data
│   ├── ghb_optimized_portfolio.txt  # 25 S&P 500 stocks
│   ├── portfolio_positions.csv      # Current positions
│   └── portfolio_settings.json      # Configuration
├── docs/                         # Documentation
│   ├── BACKTEST_ANALYSIS_REPORT.md  # Performance analysis
│   ├── EXECUTION_GUIDE.md           # Monday execution guide
│   ├── GHB_STRATEGY_GUIDE.md        # Strategy rules
│   ├── PHASE1_QUICKSTART.md         # Getting started
│   └── RE-OPTIMIZATION_GUIDE.md     # Annual universe refresh
├── notebooks/                    # Jupyter notebooks
│   ├── ghb_portfolio_scanner.ipynb       # ⭐ Main weekly scanner
│   └── universe_reoptimization.ipynb     # Annual universe refresh
├── scripts/                      # Utilities
│   ├── backup_and_push.ps1      # Git backup automation
│   ├── backup_full.ps1          # Full backup (local + remote)
│   └── add_position.py          # Add positions to portfolio
├── ghb_scanner_results/          # Scanner outputs
│   ├── ghb_strategy_signals_[date].csv
│   ├── ghb_strategy_signals_[date].pdf
│   └── archive/                 # Old scans
├── archive/                      # Archived old code
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
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

### 3. Your Portfolio Files

The system uses these files in `data/` folder:
- **ghb_optimized_portfolio.txt**: Your 25 S&P 500 optimized stocks (pre-configured)
- *GHB Strategy

### 4-State Signal System

Simple, clear signals based on price vs 200-day SMA and 4-week momentum:

- **P1 (Gold) = BUY**: Price > D200 + Strong momentum (ROC > 5% OR distance > 10%)
- **P2 (Gray) = HOLD**: Price > D200 + Weak momentum (consolidation)
- **N1 (Gray) = HOLD**: Price < D200 but shallow (distance > -5%, shallow pullback)
- **N2 (Blue) = SELL**: Price < D200 + Deep (distance < -5%, trend broken)

### Position Sizing

- **10% per position**: $11,000 per trade (based on $110k portfolio)
- **Max 10 positions**: Fully deployed = $110k invested
- **Weekly discipline**: Only trade on Mondays based on Friday signals

### Technical Indicators

- **200-Day SMA (D200)**: Primary trend indicator
- **4-Week ROC**: Momentum measurement (20 trading days)
- **Distance %**: How far price is from D200 (determines state
- **Secondary Zone (25-30%)**: Deeper support levels
- **Final Zone (20-25%)**: Capitulation buys only

### Technical Indicators

- **Moving Averages**: D20/D50/D100/D200 (daily), W10/W20/W200 (weekly)
- **Volume Profile (VRVP)**: 
  - **POC (Point of Control)**: Price with highest volume - strong S/R level
  - **VAH/VAL (Value Area)**: 70% volume range - fair value zone
  - **HVN (High Volume Nodes)**: Volume clusters - support/resistance
  - **LVN (Low Volume Nodes)**: Low volume zones - breakout/breakdown areas
  - **Timeframes**: 60-day and 52-week analysis
- *Weekly Workflow

### Friday (After 4pm ET)
1. Open `notebooks/ghb_portfolio_scanner.ipynb`
2. Run all cells (~1-2 minutes for 25 stocks)
3. Review signals:
   - **P1 (BUY)**: Enter new positions
   - **P2/N1 (HOLD)**: Keep existing positions
   - **N2 (SELL)**: Exit positions Monday
4. Check PDF in `ghb_scanner_results/`
5. Plan Monday trades

### Monday (9:30-10:30am ET)
1. **9:30-10:00am**: Execute ALL N2 sells (urgent)
   - Limit: Friday close - 1%
2. **10:00-10:30am**: Enter P1 buys (patient)
   - Limit: Friday close + 1.5%
3. **Monday evening**: Update `portfolio_positions.csv` with fills

### Annual (Every January)
1. Open `notebooks/universe_reoptimization.ipynb`
2. Run to screen S&P 500 (~10-15 minutes)
3. Update universe with new top 25 stocks
4. Transition portfolio over 2-8 weeks
- **NASDAQ 100**: ~100 stocks, 2-5 minutes

Outputs filtered Excel and PDF reports with only FULL HOLD + ADD signals.

## Technical Notes

- **API Rate Limiting**: 2 concurrent threads with 1-2s delays
- *Performance

### Backtest Results (2021-2025)
- **CAGR**: 46.80%
- **Total Return**: 586.78% (5 years)
- **Win Rate**: 62.86%
- **Trades Per Year**: ~7
- **Avg Win**: +74%
- **Avg Loss**: -12%
### Getting Started
- [docs/PHASE1_QUICKSTART.md](docs/PHASE1_QUICKSTART.md) - **Start here** - Setup guide
- [docs/GHB_STRATEGY_GUIDE.md](docs/GHB_STRATEGY_GUIDE.md) - Strategy rules explained
- [docs/EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md) - Monday execution details
- [docs/VARIABLE_ALLOCATION_GUIDE.md](docs/VARIABLE_ALLOCATION_GUIDE.md) - Variable position sizing setup

### Advanced
- [docs/BACKTEST_ANALYSIS_REPORT.md](docs/BACKTEST_ANALYSIS_REPORT.md) - Complete backtest results
- [docs/RE-OPTIMIZATION_GUIDE.md](docs/RE-OPTIMIZATION_GUIDE.md) - Annual universe refresh
- [docs/PORTFOLIO_TRACKER_ROADMAP.md](docs/PORTFOLIO_TRACKER_ROADMAP.md) - Automation roadmap

### Backtesting
- [backtest/README.md](backtest/README.md) - How to run backtests
- Run custom backtests with different parameters
- Screen S&P 500 for new candidates

## Backup & Git

Use provided PowerShell scripts:
- `scripts/backup_and_push.ps1` - Quick commit & push to GitHub
- `scripts/backup_full.ps1` - Full local + remote backup
- `scripts/BACKUP_SCRIPTS_README.md` - Detailed usage guide
- [docs/HISTORICAL_BACKTESTING.md](docs/HISTORICAL_BACKTESTING.md) - **Start here to backtest your trading edge**
- [docs/BEST_TRADES_GUIDE.md](docs/BEST_TRADES_GUIDE.md) - Understanding best trades reports
- [docs/FULL_SCANNER_USER_MANUAL.md](docs/FULL_SCANNER_USER_MANUAL.md) - Scanner details and usage
- [docs/INTERACTIVE.md](docs/INTERACTIVE.md) - Detailed notebook usage guide
- [docs/SECURITY.md](docs/SECURITY.md) - Best practices for protecting sensitive data

## Git Workflow (Optional)

Use provided PowerShell scripts for Git automation:
- `scripts/backup_and_push.ps1` - Safe commit and push with confirmations
- `scripts/safe_commit.ps1` - Interactive commit with status check
- `scripts/setup_repo.ps1` - Initialize Git repository

## License

MIT License - See LICENSE file for details

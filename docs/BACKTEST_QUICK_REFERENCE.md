# Historical Backtesting Quick Reference

## Generate Historical Reports

### NASDAQ 100 - 6 Months, Weekly (RECOMMENDED FOR TESTING)
```powershell
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category nasdaq100
```

### NASDAQ 100 - 3 Months, Weekly (Conservative Test)
```powershell
python src/generate_historical_reports.py --start 2025-10-01 --category nasdaq100
```

### S&P 500 - 6 Months, Weekly (Larger Sample)
```powershell
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category sp500
```

### Portfolio - 6 Months, Weekly
```powershell
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category portfolio
```

### All Categories - 3 Months, Weekly (Faster Test)
```powershell
python src/generate_historical_reports.py --start 2025-10-01 --end 2026-01-01 --interval 7 --category all
```

## Run Backtests

### Standard Backtest (30-day holding)
```powershell
python src/backtest_best_trades.py --results-dir scanner_results/historical_simulation --period 30
```

### Longer Hold (60 days)
```powershell
python src/backtest_best_trades.py --results-dir scanner_results/historical_simulation --period 60
```

### Export Detailed Results to CSV
```powershell
python src/backtest_best_trades.py --results-dir scanner_results/historical_simulation --output backtest_results.csv
```

## Test System

### Quick Test (3 tickers, 1 date)
```powershell
python test_historical_scan.py
```

### Single Historical Scan (Manual)
```powershell
python src/full_scanner.py --as-of-date 2025-07-01
```

## Common Workflows

### First-Time Setup (Recommended Path)
1. Test system: `python test_historical_scan.py`
2. Generate 3 months NASDAQ 100: `python src/generate_historical_reports.py --start 2025-10-01 --category nasdaq100`
3. Run backtest: `python src/backtest_watchlist.py --results-dir scanner_results/historical_simulation`
4. Review in notebook: Open `notebooks/backtest_watchlist.ipynb`

### Full 6-Month Analysis
1. Generate data: `python src/generate_historical_reports.py --start 2025-07-01 --category nasdaq100`
2. Backtest: `python src/backtest_watchlist.py --results-dir scanner_results/historical_simulation`
3. Analyze: Review charts in `backtest_watchlist.ipynb`
4. Optimize: Adjust filters based on edge analysis

**Note:** NASDAQ 100 (~100 stocks) is recommended over S&P 500 (~500 stocks) for initial testing to avoid rate limits.

### Strategy Optimization Loop
1. Run initial backtest (30 days)
2. Identify best performing segment (e.g., EXCELLENT + SAFE ENTRY)
3. Re-run with filters: Edit backtest script to filter those only
4. Compare results
5. Iterate until satisfied

## Parameter Reference

### generate_historical_reports.py
| Parameter | Options | Default | Purpose |
|-----------|---------|---------|---------|
| --start | YYYY-MM-DD | Required | Start date |
| --end | YYYY-MM-DD | Today | End date |
| --interval | Integer | 7 | Days between reports |
| --category | sp500, nasdaq100, portfolio, all | nasdaq100 | What to scan (nasdaq100 recommended) |
| --concurrency | 1-4 | 1 | Parallel workers (higher = faster but rate limits) |

### backtest_best_trades.py
| Parameter | Options | Default | Purpose |
|-----------|---------|---------|---------|
| --results-dir | Path | scanner_results | Folder with historical reports |
| --period | Integer | 30 | Days to hold each trade |
| --output | Filename | None | CSV export path |

## File Locations

### Historical Reports
`scanner_results/historical_simulation/`
- `sp500/` - S&P 500 reports
- `nasdaq100/` - NASDAQ 100 reports
- `portfolio/` - Portfolio reports

### Report Naming
`{category}_best_trades_YYYYMMDD_0900.xlsx`
`{category}_best_trades_YYYYMMDD_0900.pdf`

Example: `sp500_best_trades_20250701_0900.xlsx`

## Expected Timing

### Report Generation (with rate limiting protections)
- **NASDAQ 100, 3 months, weekly**: ~20-30 minutes (~1,300 API calls)
- **NASDAQ 100, 6 months, weekly**: ~40-60 minutes (~2,600 API calls)
- **S&P 500, 3 months, weekly**: ~90-120 minutes (~6,500 API calls)
- **S&P 500, 6 months, weekly**: ~3-4 hours (~13,000 API calls)

**Rate Limit Strategy:**
- Default: concurrency=1, 1-2s random delays (safest)
- Aggressive: concurrency=2 (2x faster, higher rate limit risk)
- If limited: Wait 1 hour, resume with later --start date

### Backtesting
- **Analysis of 26 reports**: ~1-2 minutes
- **Analysis of 100 reports**: ~5 minutes

### Rate Limits
- yfinance: ~2000 requests/hour
- If rate limited: Wait 1 hour and resume
- Reduce --concurrency to 1 if persistent issues

## Interpreting Results

### Good Edge
✅ Overall win rate: >55%
✅ EXCELLENT win rate: >60%
✅ SAFE ENTRY win rate: >55%
✅ High Vol R:R (3:1+) win rate: >60%
✅ Avg winner: +10-15% in 30 days
✅ Stop hit rate: <45%

### Needs Work
⚠️ Overall win rate: <50%
⚠️ No difference between EXCELLENT and GOOD
⚠️ No difference between SAFE ENTRY and ACCEPTABLE
⚠️ High Vol R:R performs worse than low
⚠️ Stop hit rate: >55%

## Troubleshooting

### "Rate limit error"
→ Wait 1 hour, reduce --concurrency to 1

### "No results returned"
→ Check date isn't too far in past (need 200 days of prior data)

### "Missing data for ticker XXX"
→ Normal, some tickers lack full history. Skip them.

### Backtest shows no edge
→ Try different holding periods (45, 60 days)
→ Filter by quality (EXCELLENT only)
→ Check market regime (was it a bear market?)

## Documentation Links

- [HISTORICAL_BACKTESTING.md](HISTORICAL_BACKTESTING.md) - Full guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
- [BEST_TRADES_GUIDE.md](BEST_TRADES_GUIDE.md) - Report interpretation
- [FULL_SCANNER_USER_MANUAL.md](FULL_SCANNER_USER_MANUAL.md) - Scanner usage

## Quick Win

**Want to see if your system has edge in 30 minutes?**

```powershell
# 1. Generate 3 months of NASDAQ 100 data (20-30 min)
python src/generate_historical_reports.py --start 2025-10-01 --category nasdaq100

# 2. Run backtest (1-2 min)
python src/backtest_watchlist.py --results-dir scanner_results/historical_simulation

# 3. Open backtest_watchlist.ipynb and check win rate

# If win rate >55% → You have an edge! 🎯
# If win rate <50% → Need optimization ⚙️
```

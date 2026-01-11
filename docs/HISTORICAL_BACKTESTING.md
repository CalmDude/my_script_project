# Historical Backtesting Guide

## Overview

This system allows you to generate historical scanner reports and backtest your trading strategy to measure its edge. Since you just started using the scanner and don't have historical reports, this approach simulates what the scanner would have recommended at various points in the past.

## How It Works

### 1. Historical Data Simulation

The system modifies the scanner to only use data available **as of** a specific historical date. This prevents look-ahead bias.

**Key Changes:**
- `technical_analysis.py`: Added `as_of_date` parameter to `analyze_ticker()`
- `full_scanner.py`: Added `as_of_date` parameter throughout the scanning pipeline
- `generate_historical_reports.py`: Script to generate reports for multiple historical dates

### 2. Data Source

Uses **yfinance** to fetch historical OHLCV data. When you specify `as_of_date="2025-07-01"`, the system:
- Fetches daily data up to July 1, 2025 only
- Calculates all indicators (RSI, moving averages, support/resistance) using only that data
- Generates signals as if you were running the scanner on that date

### 3. Avoiding Look-Ahead Bias

**Critical**: The scanner will NOT use any data from after the `as_of_date`. This ensures:
- Your backtest results are realistic
- You're measuring true predictive edge
- Results match what you would have seen in real-time

## Usage

### Quick Start: Generate 6 Months of Weekly Reports

```powershell
# S&P 500 only (recommended to start)
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category sp500

# NASDAQ 100
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category nasdaq100

# Your portfolio
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category portfolio

# All three (takes longer)
python src/generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category all
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--start` | Start date (YYYY-MM-DD) | **Required** |
| `--end` | End date (YYYY-MM-DD) | Today |
| `--interval` | Days between reports | 7 |
| `--category` | sp500, nasdaq100, portfolio, or all | sp500 |
| `--daily-bars` | Daily bars for analysis | 60 |
| `--weekly-bars` | Weekly bars for analysis | 52 |
| `--concurrency` | Parallel workers (be careful of rate limits) | 2 |

### Output

Reports are saved to: `scanner_results/historical_simulation/`

Structure:
```
scanner_results/
  historical_simulation/
    sp500/
      sp500_best_trades_20250701_0900.xlsx
      sp500_best_trades_20250701_0900.pdf
      sp500_best_trades_20250708_0900.xlsx
      sp500_best_trades_20250708_0900.pdf
      ...
    nasdaq100/
      ...
    portfolio/
      ...
```

## Backtesting the Results

### Option 1: Python Script

```powershell
python src/backtest_best_trades.py --results-dir scanner_results/historical_simulation --period 30
```

Parameters:
- `--results-dir`: Folder with historical reports (default: scanner_results/historical_simulation)
- `--period`: Days to hold each trade (default: 30)
- `--output`: CSV file for detailed results (optional)

### Option 2: Jupyter Notebook (Recommended)

Open `notebooks/backtest_best_trades.ipynb` and:

1. Set the results directory to `scanner_results/historical_simulation`
2. Run all cells
3. View interactive charts and analysis

**Charts Include:**
- Win rate by quality rating (EXCELLENT vs GOOD)
- Win rate by entry flag (SAFE ENTRY, IDEAL, etc.)
- Win rate by Vol R:R tiers (3:1+, 2-3:1, 1-2:1)
- Win rate by position in report (#1, #2-5, #6-10, etc.)
- Return distribution (histogram)
- Stop hit analysis
- Maximum Favorable/Adverse Excursion

## Understanding Your Edge

### Key Metrics to Look For

1. **Overall Win Rate**: Should be >50% to have an edge
   - Target: 55-65% is excellent
   - Minimum: 50%+ to be profitable after costs

2. **Win Rate by Quality**:
   - EXCELLENT: Should be 60%+ win rate
   - GOOD: Should be 50-60% win rate
   - If EXCELLENT isn't better than GOOD, quality scoring needs work

3. **Win Rate by Entry Flag**:
   - SAFE ENTRY: Should be highest win rate (targeting 60%+)
   - IDEAL: Should be 55-60%
   - ACCEPTABLE: Should be 50%+
   - If no difference, entry flags aren't predictive

4. **Vol R:R Performance**:
   - High Vol R:R (3:1+): Should have highest win rate and/or best returns
   - Low Vol R:R (<2:1): May have lower win rate but tighter stops

5. **Stop Hit Rate**:
   - Should be <50% (most positions shouldn't hit stop)
   - If >60%, stops may be too tight

6. **Average Returns**:
   - Winners: Should average 5-15% in 30 days
   - Losers: Should average -5% to -10% (stop-limited)
   - Overall: Should be positive even with 50% win rate

### Improving Your Edge

Based on backtest results:

**If win rate is low (<50%)**:
- Tighten quality filters (EXCELLENT only?)
- Focus on specific entry flags (SAFE ENTRY only?)
- Increase Vol R:R threshold (3:1+ only?)
- Adjust holding period (try 45 or 60 days)

**If win rate is good but returns are poor**:
- Hold winners longer (let them run)
- Tighten stops on losers
- Focus on higher Vol R:R trades (bigger reward potential)

**If top-ranked trades don't outperform**:
- Review ranking algorithm (Vol R:R weighting)
- Check if quality ratings correlate with performance
- Consider additional factors (sector rotation, market regime)

## Important Notes

### Rate Limiting

yfinance can rate limit you if you make too many requests:
- Keep `--concurrency` at 2 (default)
- Generate reports gradually (maybe 3-6 months at a time)
- If rate limited, wait 1 hour and resume

### Data Quality

- yfinance data is delayed and may not match real-time prices exactly
- Some tickers may have missing or incomplete historical data
- Penny stocks and low-volume stocks may have gaps

### Scanner Accuracy

This assumes your scanner logic was static over time. In reality:
- You've improved the scanner since starting
- Your backtest shows what past signals would have predicted
- Future edge may differ as you refine the system

### Market Regime

Historical performance varies by market conditions:
- Bull markets: Higher win rates, bigger winners
- Bear markets: Lower win rates, smaller winners
- Range-bound: Mixed results

Consider filtering backtest by market regime (SPY trend).

## Workflow Example

1. **Generate 6 months of historical reports** (1-2 hours):
   ```powershell
   python src/generate_historical_reports.py --start 2025-07-01 --category sp500
   ```

2. **Run backtest** (1-2 minutes):
   ```powershell
   python src/backtest_best_trades.py --results-dir scanner_results/historical_simulation
   ```

3. **Analyze results in notebook**:
   - Open `notebooks/backtest_best_trades.ipynb`
   - Review charts and statistics
   - Identify strongest filters (EXCELLENT only? SAFE ENTRY only?)

4. **Refine filters**:
   - If EXCELLENT + SAFE ENTRY has 65% win rate, focus there
   - Ignore lower-quality signals
   - Update scanner to rank these higher

5. **Re-test with refined filters**:
   - Run backtest again with new filters
   - Verify edge is maintained
   - Iterate until satisfied

## Next Steps

1. Generate your first batch of historical reports (start with 3 months)
2. Run the backtest
3. Review the edge analysis
4. Identify your strongest signals
5. Focus real-money trading on those high-edge setups

## Questions?

See:
- `docs/BEST_TRADES_GUIDE.md` - Understanding the reports
- `docs/FULL_SCANNER_USER_MANUAL.md` - Scanner details
- `src/backtest_best_trades.py` - Backtest logic

## Troubleshooting

**"No results returned"**:
- Check date is not too far in past (need enough data for 200-day MA)
- Verify tickers existed at that date
- Try a more recent date

**"Rate limit error"**:
- Reduce `--concurrency` to 1
- Wait 1 hour
- Generate fewer dates at a time

**"Missing data"**:
- Some tickers may not have complete history
- Skip those tickers (they'll show as errors)
- Focus on liquid, large-cap stocks

**Backtest shows no edge**:
- Try different holding periods (30, 45, 60 days)
- Filter by quality (EXCELLENT only)
- Check if market was trending during test period
- May need to refine entry quality scoring

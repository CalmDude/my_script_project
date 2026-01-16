# GHB Strategy Backtest

Historical backtesting framework for the GHB (Gold-Gray-Blue) weekly momentum strategy.

## 📁 Structure

```
backtest/
├── config.json              # Backtest configuration
├── data_loader.py           # Historical data fetching
├── strategy_signals.py      # GHB strategy logic
├── portfolio_manager.py     # Position tracking & P&L
├── backtest_engine.py       # Main simulation engine
├── performance_metrics.py   # Advanced statistics
├── run_backtest.py          # Entry point script
├── data/                    # Cached historical data
│   └── cache/
└── results/                 # Backtest outputs
    ├── trades_*.csv         # All executed trades
    ├── equity_curve_*.csv   # Daily portfolio values
    └── summary_*.json       # Performance summary
```

## � Stock Screening (Find Optimal Universe)

Before backtesting a full universe, screen stocks individually to find which ones work best with GHB strategy.

### Screen S&P 100 Stocks

```powershell
python backtest/screen_stocks.py --universe sp100
```

This will:
1. Backtest each stock individually (2021-2025)
2. Calculate volatility metrics (Std Dev, Max Win, Avg Win)
3. Apply qualification criteria:
   - Standard Deviation ≥ 30% OR
   - Max Win ≥ 150% OR
   - Avg Win ≥ 40%
4. Generate report showing top qualified stocks
5. Output recommended 25-stock universe

**Output Files:**
- `stock_screening_*.csv` - All results with metrics
- `qualified_stocks_*.json` - Top 25-30 recommended tickers

**Expected Runtime:** 10-15 minutes for S&P 100

### Why Screen First?

Per GHB Strategy Guide:
- **Volatile stocks:** +601% avg per-trade returns (individual trades), 43% win rate, +74% avg win
- **Non-volatile stocks:** -162% avg returns (losses!), 33% win rate
- **Portfolio Reality:** Achievable CAGR ranges from 21-47% depending on stock selection and configuration

The strategy ONLY works on high-volatility stocks. Screening identifies which stocks qualify.

## �🚀 Quick Start

### 1. Configure Backtest

Edit `config.json`:

```json
{
  "backtest_settings": {
    "start_date": "2021-01-01",
    "end_date": "2025-12-31",
    "universe": "sp100"
  },
  "portfolio_settings": {
    "starting_cash": 110000,
    "position_size_pct": 7,
    "max_positions": 7
  }
}
```

### 2. Run Backtest

**Basic run:**
```powershell
python backtest/run_backtest.py
```

**With detailed report:**
```powershell
python backtest/run_backtest.py --detailed-report
```

**Force data refresh:**
```powershell
python backtest/run_backtest.py --refresh-data
```

### 3. Review Results

Results saved to `backtest/results/`:
- **trades_*.csv**: All buy/sell transactions
- **equity_curve_*.csv**: Weekly portfolio values
- **summary_*.json**: Performance statistics

## 📊 Configuration Options

### Universe Selection

**sp100** (Phase 1 - Recommended)
- 100 major large-cap stocks
- Faster execution (~10-15 min)
- Covers major sectors

**sp500** (Phase 2 - Full Analysis)
- Full S&P 500 universe
- Longer execution (~30-45 min)
- More comprehensive results

### Portfolio Settings

**Conservative:**
```json
"position_size_pct": 5,
"max_positions": 5
```

**Current (Recommended):**
```json
"position_size_pct": 7,
"max_positions": 7
```

**Aggressive:**
```json
"position_size_pct": 10,
"max_positions": 10
```

### Execution Slippage

**Buy Slippage** (1.015 = Friday close + 1.5%)
- Simulates Monday limit order execution
- Accounts for overnight gap

**Sell Slippage** (0.99 = Friday close - 1%)
- Simulates aggressive exit
- Reflects N2 urgency

## 📈 Expected Output

### Console Output

```
================================================================================
BACKTEST RESULTS SUMMARY
================================================================================

📅 PERIOD:
   2021-01-01 to 2025-12-31
   260 weeks (5.0 years)

💰 PERFORMANCE:
   Starting Value:  $   110,000
   Final Value:     $   450,000
   Total Return:         309.09%
   CAGR:                  32.50%
   Max Drawdown:         -25.30%

📊 TRADING STATS:
   Total Trades:            75
   Win Rate:             58.67%
   Avg Win:              45.20%
   Avg Loss:            -11.30%
   Avg Trade:            15.40%

🏆 BEST/WORST:
   Best Trade:          125.50% (NVDA)
   Worst Trade:         -22.10% (NFLX)
```

### Files Generated

**trades_YYYYMMDD_HHMMSS.csv**
```csv
Date,Ticker,Action,Shares,Price,Value,State,Entry_Date,PnL_%,Hold_Days
2021-01-18,NVDA,BUY,50,95.00,4750.00,P1,,,
2021-02-15,NVDA,SELL,50,115.00,5750.00,P1,2021-01-18,21.05,28
```

**equity_curve_YYYYMMDD_HHMMSS.csv**
```csv
Date,Cash,Positions_Value,Portfolio_Value,Return_%,Position_Count
2021-01-18,102250,7750,110000,0.00,1
2021-01-25,102250,8500,110750,0.68,1
```

**summary_YYYYMMDD_HHMMSS.json**
```json
{
  "Performance": {
    "Total_Return_%": 309.09,
    "CAGR_%": 32.50,
    "Max_Drawdown_%": -25.30
  },
  "Trading_Stats": {
    "Total_Trades": 75,
    "Win_Rate_%": 58.67,
    "Avg_Win_%": 45.20,
    "Avg_Loss_%": -11.30
  }
}
```

## 🔬 Testing Individual Modules

Each module can be tested independently:

**Test data loader:**
```powershell
cd backtest
python data_loader.py
```

**Test strategy signals:**
```powershell
python strategy_signals.py
```

**Test portfolio manager:**
```powershell
python portfolio_manager.py
```

**Test performance metrics:**
```powershell
python performance_metrics.py
```

## 🎯 Typical Workflow

### Phase 1: Quick Validation (1 year, SP100)

1. Edit `config.json`:
   ```json
   "start_date": "2024-01-01",
   "end_date": "2024-12-31",
   "universe": "sp100"
   ```

2. Run backtest:
   ```powershell
   python backtest/run_backtest.py
   ```

3. Review results:
   - Verify logic is correct
   - Check trade execution
   - Validate signals match expectations

### Phase 2: Full Analysis (5 years, SP500)

1. Update `config.json`:
   ```json
   "start_date": "2021-01-01",
   "end_date": "2025-12-31",
   "universe": "sp500"
   ```

2. Run with detailed report:
   ```powershell
   python backtest/run_backtest.py --detailed-report
   ```

3. Analyze results:
   - Compare to current watchlist
   - Evaluate across market conditions
   - Identify best performing periods

### Phase 3: Optimization (Multiple Scenarios)

Test different configurations:

**Conservative:**
```json
"position_size_pct": 5,
"max_positions": 5
```

**Aggressive:**
```json
"position_size_pct": 10,
"max_positions": 10
```

**Tighter Exits:**
```json
"exit_states": ["N1", "N2"]
```

## 📝 Performance Metrics Explained

**CAGR** (Compound Annual Growth Rate)
- Annualized return over period
- Accounts for compounding

**Max Drawdown**
- Largest peak-to-trough decline
- Risk measure

**Sharpe Ratio**
- Risk-adjusted return
- Higher is better (>1 is good, >2 is excellent)

**Sortino Ratio**
- Like Sharpe but only penalizes downside volatility
- More relevant for momentum strategies

**Win Rate**
- Percentage of winning trades
- GHB typically 55-65%

**Profit Factor**
- Gross profit / Gross loss
- >2 is excellent, >1.5 is good

**Expectancy**
- Average $ per trade
- Positive means profitable system

## 🚨 Important Notes

### Data Quality
- First run downloads ~5-10 min
- Data cached for subsequent runs
- Use `--refresh-data` to update cache

### Survivorship Bias
- Current implementation uses static stock list
- Real backtest should use point-in-time constituents
- Results may be slightly optimistic

### Market Conditions
- 2021-2025 includes:
  - Bull market (2021, 2023-2024)
  - Bear market (2022)
  - Recovery (2023)
- Good test of strategy robustness

### Comparison Baseline
- S&P 500 (SPY) buy-and-hold: ~12% CAGR
- Target: 20-40% CAGR with <35% max drawdown

## 🎓 Next Steps

After running backtest:

1. **Validate Results**
   - Does it match expected behavior?
   - Are trades executing correctly?
   - Do signals make sense?

2. **Compare to Production**
   - How does it compare to current watchlist?
   - Is SP500 universe better/worse?
   - Validate against known good signals

3. **Optimize Strategy**
   - Test different position sizes
   - Try alternative entry/exit rules
   - Explore sector concentration

4. **Deploy Findings**
   - Update production scanner if needed
   - Adjust position sizing
   - Refine entry/exit timing

## 💡 Tips

**Speed Up Development:**
- Use SP100 for testing (faster)
- Use shorter date ranges for iteration
- Cache data stays valid for days

**Analyze Results:**
- Sort trades by PnL% to find patterns
- Plot equity curve to see drawdown periods
- Group by sector to identify strengths

**Troubleshooting:**
- If no trades: Check date range has enough data
- If errors: Verify yfinance is installed
- If slow: Reduce universe or date range

---

**Built for:** GHB Strategy Portfolio Analysis  
**Version:** 1.0  
**Date:** January 2026

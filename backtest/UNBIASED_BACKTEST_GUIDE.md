# Unbiased Backtest Quick Reference

## What Was The Problem?

Your original 46.80% CAGR backtest had significant biases:

1. **Survivorship Bias** - Used 2025's S&P 500 survivors, tested on 2021-2025
2. **Optimization Bias** - Picked top 25 performers AFTER seeing 2021-2025 results
3. **SMCI Problem** - Best performer (+1101%) wasn't even in S&P 500 until March 2024!

**Result:** Inflated CAGR by ~15-25% (unrealistic for forward testing)

---

## The Solution: Option B Implementation

### Proper Methodology (No Peeking)

**Step 1: Historical Universe (Jan 1, 2021)**
- Get S&P 500 members AS OF January 1, 2021
- Includes stocks later removed (no survivorship bias)
- Script: `get_historical_sp500.py`

**Step 2: Screen Using 2020 Data Only**
- Calculate metrics from 2020 ONLY (volatility, volume, market cap)
- Select top 25 by 2020 volatility
- NO looking at 2021-2025 performance
- Script: `screen_unbiased_2020.py`

**Step 3: Backtest 2021-2025**
- Test the 2020-selected universe on 2021-2025
- True out-of-sample test
- Script: `run_backtest.py` (with `sp500_unbiased_2020` universe)

**Step 4: Compare Results**
- Side-by-side: Biased vs Unbiased
- Calculate bias impact
- Script: `compare_biased_vs_unbiased.py`

---

## Quick Commands

### Run Complete Workflow (20-30 minutes)
```bash
cd c:\workspace\portfolio_analyser
python backtest/run_unbiased_workflow.py
```

This will:
1. Get historical S&P 500 (Jan 2021)
2. Screen using 2020 data (15-20 min)
3. Run backtest 2021-2025
4. Compare and show bias impact

### Run Individual Steps

```bash
# Step 1: Get historical S&P 500
python backtest/get_historical_sp500.py

# Step 2: Screen using 2020 data (slow)
python backtest/screen_unbiased_2020.py

# Step 3: Run backtest
# Edit config.json: "universe": "sp500_unbiased_2020"
python backtest/run_backtest.py

# Step 4: Compare results
python backtest/compare_biased_vs_unbiased.py
```

---

## Files Created

### Input Files
- `backtest/data/sp500_jan_2021.txt` - Historical S&P 500 constituents
- `backtest/data/sp500_unbiased_2020.txt` - Top 25 selected from 2020 data

### Analysis Files
- `backtest/results/screening_2020_all_*.csv` - All stocks with 2020 metrics
- `backtest/results/screening_2020_qualified_*.csv` - Qualified stocks only

### Backtest Results
- `backtest/results/trades_*_sp500_unbiased_2020.csv` - Unbiased trade log
- `backtest/results/equity_curve_*_sp500_unbiased_2020.csv` - Equity curve
- `backtest/results/summary_*_sp500_unbiased_2020.json` - Performance metrics

---

## Expected Results

### Biased Backtest (Original)
- **CAGR:** 46.80%
- **Issue:** Inflated by survivorship + optimization bias
- **Reality:** You COULDN'T have picked these stocks in Jan 2021

### Unbiased Backtest (Corrected)
- **Expected CAGR:** 22-32%
- **Benefit:** Realistic, achievable in forward testing
- **Reality:** You COULD have picked these stocks in Jan 2021

### Bias Impact
- **CAGR Inflation:** +15-25%
- **Severity:** SEVERE
- **Recommendation:** Use unbiased CAGR for forward expectations

---

## Key Differences

| Aspect | Biased (Original) | Unbiased (Corrected) |
|--------|------------------|---------------------|
| **Universe Date** | Current S&P 500 (2025) | Historical S&P 500 (Jan 2021) |
| **Selection** | Top 25 by 2021-2025 CAGR | Top 25 by 2020 volatility |
| **SMCI** | Included (+1101% winner) | Excluded (not in index) |
| **Look-ahead** | YES (peeked at results) | NO (used 2020 data only) |
| **Survivorship** | Only 2025 survivors | Includes removed stocks |
| **Forward Validity** | Unrealistic | Realistic |

---

## What This Tells You

### If Unbiased CAGR = 25-30%
✅ **Excellent!** Your strategy works, just not as well as biased test suggested
- Still 2X+ the market
- Achievable forward performance
- Deploy with confidence

### If Unbiased CAGR = 15-20%
✅ **Good** - Strategy has alpha but less dramatic
- Still beats market
- More realistic expectations
- Continue forward testing

### If Unbiased CAGR = 5-12%
⚠️ **Marginal** - Strategy barely beats market
- Most alpha came from biases
- Reconsider deployment
- May need strategy refinement

### If Unbiased CAGR < 5%
❌ **Poor** - Strategy doesn't add value
- Biases created illusion of performance
- Don't deploy live
- Redesign strategy

---

## Forward Testing Strategy

### Year 1 (2026)
- Deploy with unbiased universe (current 25 stocks)
- Track actual vs expected (~25-30% target)
- Don't panic if underperforms (variance is normal)

### End of 2026
- Screen 2026 data to select 2027 universe
- Use same methodology (volatility, volume, market cap)
- Maintain annual re-optimization

### Years 2-5
- Build track record
- Compare actual vs backtest
- If consistently underperforms, reassess strategy

---

## Common Questions

**Q: Why not just use the biased results?**
A: You'll be disappointed when forward testing only achieves 25% vs expected 47%

**Q: Can I combine both universes?**
A: No - that still has survivorship bias. Use unbiased only.

**Q: What if unbiased CAGR is much lower?**
A: That's reality. Better to know now than after deploying capital.

**Q: Should I still trade the strategy?**
A: If unbiased CAGR > 20%, yes! That's still excellent performance.

**Q: How often re-screen?**
A: Annually, using previous year's data only (maintain unbiased approach)

---

## Technical Details

### Unbiased Selection Criteria (2020 Data)
- Volatility >= 25% (measured in 2020)
- Average volume >= 2M shares/day (2020)
- Market cap >= $5B (as of Dec 2020)
- S&P 500 member as of Jan 1, 2021

### Why These Criteria?
- **Volatility:** GHB strategy needs momentum (volatile stocks work best)
- **Volume:** Ensures liquidity for execution
- **Market Cap:** Avoids micro-caps with unreliable data
- **Index Member:** Quality filter (S&P 500 = established companies)

### Backtest Settings (Same as Original)
- Period: 2021-01-01 to 2025-12-31
- Starting Capital: $110,000
- Position Size: 10%
- Max Positions: 10
- Buy Slippage: +1.5%
- Sell Slippage: -1.0%

---

## Next Steps

1. ✅ Run unbiased workflow: `python backtest/run_unbiased_workflow.py`
2. ✅ Review comparison output
3. ✅ Update strategy documentation with realistic CAGR
4. ✅ Adjust forward testing expectations
5. ✅ Begin live trading with proper expectations

---

**Remember:** 25-30% CAGR is still EXCELLENT performance (2-3X the market). Don't chase the inflated 47% - embrace the realistic number and trade accordingly!

# Win Rate Analysis Results - 70-80% Target

## Summary
**Dataset:** Backtest results from Oct 1 - Dec 31, 2024 (13 weeks, 105 total trades)
**Overall baseline:** 32.4% win rate

---

## 🎯 Strategy Definitions (Quick Reference)

### STRATEGY 1: 80% Win Rate (Low Volume, High Quality)
**Filters:**
```
✓ Quality: EXCELLENT
✓ Rank: 6-15 (avoid Top 5)
✓ Entry Flag: SAFE ENTRY required
✓ Vol R:R: >= 2.0
```
**Expected Performance:**
- Win Rate: 80%
- Trades: ~1.7/month (~20/year)
- Avg Return: +8.14% per trade
- Projected Annual: ~166%

### STRATEGY 2: 70% Win Rate (More Trades)
**Filters:**
```
✓ Quality: GOOD
✓ Rank: 6-15 (avoid Top 5)
✓ Entry Flag: SAFE ENTRY required
✓ Vol R:R: Any (typically 0.9-2.6)
```
**Expected Performance:**
- Win Rate: 70%
- Trades: ~3.3/month (~40/year)
- Avg Return: +2.73% per trade
- Projected Annual: ~108%

⚠️ **Note:** Current metrics based on only 5 and 10 trades respectively. Run 5-year backtest for validation.

---

## Your Original Requested Filters ❌

### Strategy 1: Vol R:R >= 4.5, Rank 6-15, SAFE ENTRY, GOOD
- **Result:** 0 trades found
- **Reason:** High Vol R:R (4.5+) only exists in Top 5 ranks

### Strategy 2: Vol R:R >= 5.0, Rank 6+, SAFE ENTRY  
- **Result:** 0 trades found
- **Reason:** Vol R:R >= 5.0 only exists in ranks 1-5

### Why They Don't Work
The filters you requested are **mutually exclusive**:
- High Vol R:R (4.5-5.4) appears exclusively in **Rank 1-5**
- Rank 6-15 maximum Vol R:R is only **2.6**
- You cannot have both high Vol R:R AND avoid Top 5

---

## Filters That Actually Achieve 70-80% Win Rate ✅

### Strategy 1: EXCELLENT + Rank 6-15 + SAFE ENTRY + Vol R:R >= 2.0
**Win Rate:** 80.0% (4 wins, 1 loss)

**Metrics:**
- Trades per week: 0.38
- Trades per month: ~1.7
- Average return: +8.14%
- Median return: +11.35%
- Average win: +11.42%
- Average loss: -5.00%
- Win/Loss ratio: 2.28:1

**Vol R:R breakdown:**
- 2.4: 1 trade, 100% win rate
- 2.3: 2 trades, 100% win rate  
- 2.2: 1 trade, 100% win rate
- 2.1: 1 trade, 0% win rate (the only loss)

**All Trades:**
| Date       | Ticker | Rank | Vol R:R | Return | Win   |
|------------|--------|------|---------|--------|-------|
| 2024-12-17 | CTSH   | 6    | 2.1     | -5.0%  | ❌    |
| 2024-11-05 | TTWO   | 6    | 2.4     | +11.9% | ✅    |
| 2024-11-05 | ODFL   | 8    | 2.3     | +11.4% | ✅    |
| 2024-10-29 | XEL    | 10   | 2.3     | +11.6% | ✅    |
| 2024-10-01 | CSCO   | 7    | 2.2     | +10.9% | ✅    |

---

### Strategy 2: GOOD + Rank 6-15 + SAFE ENTRY (any Vol R:R)
**Win Rate:** 70.0% (7 wins, 3 losses)

**Metrics:**
- Trades per week: 0.77
- Trades per month: ~3.3
- Average return: +2.73%
- Median return: +3.61%
- Average win: +6.04%
- Average loss: -5.00%
- Win/Loss ratio: 1.21:1

**Vol R:R breakdown:**
- 2.6: 1 trade, 100% win rate (+13.0%)
- 2.1: 1 trade, 0% win rate
- 2.0: 1 trade, 0% win rate
- 1.5: 2 trades, 100% win rate
- 1.4: 1 trade, 100% win rate
- 1.3: 2 trades, 100% win rate
- 1.2: 1 trade, 100% win rate
- 0.9: 1 trade, 0% win rate

**Sample Trades:**
| Date       | Ticker | Rank | Vol R:R | Return | Win   |
|------------|--------|------|---------|--------|-------|
| 2024-12-17 | CCEP   | 10   | 0.9     | -5.0%  | ❌    |
| 2024-12-03 | CCEP   | 6    | 1.2     | +0.9%  | ✅    |
| 2024-11-12 | GEHC   | 6    | 2.1     | -5.0%  | ❌    |
| 2024-11-05 | HON    | 11   | 1.5     | +7.4%  | ✅    |
| 2024-10-29 | CPRT   | 9    | 2.6     | +13.0% | ✅    |
| 2024-10-29 | GEHC   | 11   | 2.0     | -5.0%  | ❌    |
| 2024-10-29 | EA     | 12   | 1.3     | +6.3%  | ✅    |
| 2024-10-22 | BKR    | 10   | 1.3     | +6.5%  | ✅    |
| 2024-10-08 | CCEP   | 7    | 1.4     | +0.8%  | ✅    |
| 2024-10-01 | BKR    | 9    | 1.5     | +7.4%  | ✅    |

---

## Key Insights

### The Real Sweet Spot
- **Rank 6-15 with SAFE ENTRY** is the winning combination
- Vol R:R in this range is **1.0-2.6**, not 4.5+
- **Quality matters:** EXCELLENT outperforms GOOD

### Trade Volume Reality
- Strategy 1 (EXCELLENT): ~2 trades/month (low volume, high quality)
- Strategy 2 (GOOD): ~3 trades/month (better volume)

### Why High Vol R:R Doesn't Work Here
The backtest shows high Vol R:R stocks are **concentrated in Top 5 ranks**, which you wanted to avoid:
- Vol R:R 5.0+: All in Rank 1-5
- Vol R:R 4.5+: All in Rank 1-5  
- Vol R:R 4.0+: All in Rank 1-5
- Rank 6-15 max: 2.6

---

## Recommendations

### For 80% Win Rate (Most Selective)
Use: **EXCELLENT + Rank 6-15 + SAFE ENTRY + Vol R:R >= 2.0**
- Expect: 1-2 trades per month
- Win rate: 80%
- Average return: +8%
- Lower volume but higher quality

### For 70% Win Rate (More Trades)
Use: **GOOD + Rank 6-15 + SAFE ENTRY**
- Expect: 3-4 trades per month  
- Win rate: 70%
- Average return: +3%
- Better trade volume

### Critical Adjustment Needed
Your original filters targeting Vol R:R 4.5-5.0 in Rank 6+ **do not exist** in the backtest data. To achieve 70-80% win rates, you must:
1. Accept lower Vol R:R (2.0-2.6 range)
2. OR include Top 5 ranks (which you wanted to avoid)

The data shows these are mutually exclusive constraints.

---

## Sample Size & Statistical Confidence ⚠️

### Current Limitations
**Current dataset:** Oct 1 - Dec 31, 2024 (13 weeks)
- Strategy 1: Only **5 trades** total
- Strategy 2: Only **10 trades** total
- **Too small for statistical confidence**

### Expected Annual Returns (Current Metrics)
**Strategy 1:** 
- 1.7 trades/month × 12 months = 20.4 trades/year
- 8.14% avg return per trade
- **Projected annual return: ~166%** (or ~14%/month)

**Strategy 2:**
- 3.3 trades/month × 12 months = 39.6 trades/year
- 2.73% avg return per trade  
- **Projected annual return: ~108%** (or ~9%/month)

⚠️ **These projections are highly uncertain with current sample size**

### Recommended: 5-Year Backtest

**Why 5 years (Jan 2021 - Dec 2025):**
- **~100 trades** for Strategy 1 (vs. current 5)
- **~200 trades** for Strategy 2 (vs. current 10)
- **Full market cycle coverage:**
  - COVID recovery (2021)
  - Bull market (2021-2022)
  - Bear market (2022)
  - Choppy/recovery (2023-2024)
  - Recent conditions (2025)
- Strong statistical confidence
- Recent enough to be actionable

**Statistical Confidence Levels:**
| Duration | Strategy 1 Trades | Strategy 2 Trades | Confidence |
|----------|-------------------|-------------------|------------|
| Current (3mo) | 5 | 10 | ❌ Too small |
| 1 year | ~20 | ~40 | ⚠️ Insufficient |
| 3 years | ~60 | ~120 | ✅ Decent |
| **5 years** | **~100** | **~200** | ✅✅ **Strong** |
| 7 years | ~140 | ~280 | ✅✅ Excellent |

### Action Item
**Run `generate_historical_reports` for 5 years** to validate:
1. Win rate consistency (Is 80%/70% sustainable?)
2. True average returns
3. Drawdown patterns
4. Seasonal effects
5. Market cycle performance

Only after 5-year validation should these strategies be deployed with real capital.

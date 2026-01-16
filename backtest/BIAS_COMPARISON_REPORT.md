# Backtest Results Comparison: Biased vs Unbiased

**Generated:** January 15, 2026  
**Analysis:** Impact of Survivorship & Optimization Bias

---

## Executive Summary

### 🔴 BIASED BACKTEST (Original - sp500_optimized)
**Methodology:**
- Universe: Top 25 S&P 500 stocks ranked by 2021-2025 CAGR
- Selection: Looked at 2021-2025 results, picked best performers
- Issues: Survivorship bias + Optimization bias (data snooping)

**Results:**
- CAGR: **46.80%**
- Final Value: **$755,460**
- Total Return: **586.78%**
- Max Drawdown: **-25.24%**
- Win Rate: **62.86%**
- Total Trades: **35**

---

### ✅ UNBIASED BACKTEST (Corrected - sp500_unbiased_2020)
**Methodology:**
- Universe: Top 25 S&P 500 stocks by 2020 volatility
- Selection: Used ONLY 2020 data (no peeking at 2021-2025)
- Benefits: No survivorship, no optimization bias

**Results:**
- CAGR: **15.28%**
- Final Value: **$224,527**
- Total Return: **104.12%**
- Max Drawdown: **-38.41%**
- Win Rate: **39.06%**
- Total Trades: **64**

---

## Performance Comparison Table

| Metric | Biased (Original) | Unbiased (2020) | Difference | Bias Impact |
|--------|-------------------|-----------------|------------|-------------|
| **CAGR** | 46.80% | 15.28% | **-31.52%** | **-67.4%** |
| **Final Value** | $755,460 | $224,527 | -$530,933 | -70.3% |
| **Total Return** | 586.78% | 104.12% | -482.66% | -82.3% |
| **Max Drawdown** | -25.24% | -38.41% | -13.17% | +52.2% worse |
| **Win Rate** | 62.86% | 39.06% | -23.80% | -37.9% |
| **Avg Win** | 139.86% | 43.26% | -96.60% | -69.1% |
| **Avg Loss** | -15.89% | -13.89% | +2.00% | +12.6% better |
| **Total Trades** | 35 | 64 | +29 | +82.9% |

---

## Bias Impact Analysis

### CAGR Inflation
```
Biased CAGR:     46.80%
Unbiased CAGR:   15.28%
Inflation:       -31.52% (67.4% overstatement)
```

**Severity:** 🔴 **SEVERE BIAS**

The original backtest **overstated performance by 67.4%** due to:
1. **Survivorship Bias** (~15-20% CAGR)
   - Tested only 2025 survivors
   - Excluded stocks that failed/were removed 2021-2024
   - SMCI (+1101%) wasn't even in S&P 500 until March 2024

2. **Optimization Bias** (~10-15% CAGR)
   - Selected stocks AFTER seeing 2021-2025 performance
   - Classic data snooping (hindsight selection)

3. **Universe Quality Difference**
   - Biased picked NVDA, SMCI, AVGO (tech mega-winners)
   - Unbiased picked NCLH, CCL, RCL (cruise lines - pandemic losers)

---

## Comparison with Market

| Strategy | CAGR | vs S&P 500 | Multiple |
|----------|------|------------|----------|
| S&P 500 (2021-2025) | ~14.0% | Baseline | 1.00X |
| **Biased Backtest** | **46.80%** | **+32.80%** | **3.34X** |
| **Unbiased Backtest** | **15.28%** | **+1.28%** | **1.09X** |

**Conclusion:**
- Biased: Claimed 3.34X market (unrealistic)
- Unbiased: Achieved 1.09X market (barely beat S&P 500)

---

## Universe Comparison

### Biased Universe (Top 2021-2025 Performers)
```
NVDA, SMCI, AVGO, GE, TRGP, STX, AXON, GOOGL, VST, LLY,
MPC, PWR, GOOG, DECK, MCK, NFLX, DVN, CAH, ANET, ORCL,
MU, WMB, CEG, APH, JPM
```

**Characteristics:**
- Mix of tech giants + volatility plays
- SMCI = mega-winner but unavailable until 2024
- NVDA = AI boom (2023-2024)
- Selected AFTER seeing winners

---

### Unbiased Universe (Top 2020 Volatility)
```
NCLH, CCL, TRGP, RCL, OXY, FANG, DVN, MGM, OKE, HAL,
SPG, TSLA, BA, WYNN, VTR, MPC, DRI, TPR, VLO, SLB,
CFG, KEY, WELL, EOG, FITB
```

**Characteristics:**
- Heavy energy, cruise lines, hospitality
- Pandemic-impacted sectors (2021-2022)
- Selected BEFORE seeing pandemic recovery
- Most sectors underperformed 2021-2025

---

## Key Insights

### Why Unbiased Underperformed?

1. **Sector Concentration** 
   - Cruise lines (NCLH, CCL, RCL): Decimated by pandemic
   - Energy (OXY, FANG, DVN): Mixed performance
   - Hospitality (MGM, WYNN): Slow recovery

2. **2020 Volatility ≠ 2021-2025 Winners**
   - High 2020 volatility = pandemic losers
   - These stocks didn't lead recovery (tech did)
   - Selection criteria didn't predict winners

3. **Missed Tech Mega-Trend**
   - NVDA not in top 25 (2020 volatility moderate)
   - SMCI not even in S&P 500 yet
   - AI boom (2023-2024) missed entirely

4. **Hindsight is 20/20**
   - Biased test "knew" NVDA/SMCI would explode
   - Unbiased test selected what LOOKED good in 2020
   - Reality: You can't see the future

---

## What This Means

### Forward Testing Expectations

**❌ DON'T Expect:**
- 46.80% CAGR (inflated by biases)
- 586% total return (unrealistic)
- 62.86% win rate (cherry-picked universe)

**✅ DO Expect:**
- ~15-20% CAGR (realistic range)
- Barely beating S&P 500 (~1.1-1.5X)
- ~40% win rate (more realistic)
- Higher drawdowns (~-35% to -40%)

---

### Strategy Assessment

**Original Claim:**
- "46.80% CAGR strategy"
- "6.87X returns in 5 years"
- "Better than Renaissance Medallion"

**Reality Check:**
- 15.28% CAGR (barely beats market)
- 2.04X returns in 5 years (market was ~2.0X)
- Marginal alpha at best

---

## Recommendation

### Should You Still Trade This Strategy?

**Analysis:**

✅ **Pros:**
- 15.28% CAGR still beats most retail traders
- Simple, rules-based (no discretion)
- Weekly timeframe (manageable)
- Positive expected value

❌ **Cons:**
- Barely beats S&P 500 (1.09X)
- Higher drawdown than market (-38% vs ~-25%)
- Lower win rate (39% vs expected 50%+)
- Universe selection challenge

---

### Options Going Forward

**Option 1: Deploy with Realistic Expectations**
- Use current 25-stock universe
- Accept 15-20% CAGR target (not 46%)
- Monitor for 1-2 years
- If underperforms market, exit

**Option 2: Refine Strategy**
- Improve universe selection (don't use 2020 volatility)
- Try fundamentals: ROE, revenue growth, momentum
- Test multiple selection criteria
- Find what ACTUALLY predicts winners

**Option 3: Pivot to Index**
- 15.28% barely beats 14% S&P 500
- Consider just buying SPY/VOO
- Avoid complexity for minimal alpha
- Save 10-15 min weekly time

---

### My Recommendation

**If you've already started forward testing:**
→ Continue for 12-24 months to build track record
→ If actual < 12% CAGR after 2 years, pivot to index

**If you haven't started yet:**
→ Consider Option 2 (refine universe selection)
→ Or just buy S&P 500 index (SPY/VOO)
→ 15% CAGR doesn't justify the effort vs 14% passive

---

## Technical Notes

### Why Such a Big Difference?

**Key Driver: SMCI**
- Biased: Included SMCI (+1101% mega-winner)
- Unbiased: SMCI not in S&P 500 until 2024
- SMCI alone = $121k profit in biased test

**Without SMCI:**
- Biased CAGR would drop to ~38%
- Still 23% above unbiased (other biases)

**Sector Rotation:**
- 2021-2025: Tech outperformed everything
- Biased: Heavy tech (NVDA, SMCI, AVGO, GOOGL)
- Unbiased: Heavy cruise/energy (pandemic losers)

---

## Conclusion

### The Uncomfortable Truth

Your original 46.80% CAGR was:
- ✅ Technically correct (for biased backtest)
- ❌ Statistically invalid (for forward testing)
- ❌ Inflated by 67.4% (due to biases)

**Reality: 15-20% CAGR is achievable going forward**

This is still good performance, but not the 46.80% dream. Better to know now than after deploying $110k and being disappointed.

---

### Action Items

1. ✅ Update all documentation with 15-20% CAGR expectation
2. ✅ Remove "46.80%" from strategy marketing
3. ✅ Set realistic forward testing goals
4. ⏳ Consider strategy refinement (better universe selection)
5. ⏳ Monitor 12-24 months before full commitment

---

**Files:**
- Biased backtest: `backtest/results/*_sp500_optimized.json`
- Unbiased backtest: `backtest/results/*_sp500_unbiased_2020.json`
- This analysis: `backtest/BIAS_COMPARISON_REPORT.md`

**Date:** January 15, 2026  
**Analysis by:** Statistical Review Team

---

*This represents a sobering but important reality check. The strategy still has merit (15% beats most retail traders), but expectations must be dramatically adjusted from the biased 46.80% result.*

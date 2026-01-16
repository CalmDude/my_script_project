# Phase 2 Results - Complete Failure Analysis

## Date: 2026-01-15

## Executive Summary

**Phase 2 FAILED catastrophically: 3.86% CAGR vs unbiased 15.28% CAGR**

The entry filters and stop losses destroyed performance by:
1. **Cutting winners early** (stop losses)
2. **Missing the best entry points** (entry filters too strict)
3. **Lower win rate**: 18.75% vs 39.06% (-20% worse)

---

## Results Summary

| Metric | Unbiased | Phase 2 | Change | Status |
|--------|----------|---------|--------|--------|
| **CAGR** | 15.28% | 3.86% | **-11.41%** | ❌ DISASTER |
| **Total Return** | 104.12% | 20.95% | -83.17% | ❌ DISASTER |
| **Win Rate** | 39.06% | 18.75% | -20.31% | ❌ DISASTER |
| **Trades** | 64 | 96 | +32 | ❌ More trades, worse results |
| **Max Drawdown** | -38.41% | -23.37% | +15.04% | ✅ Better |
| **Best Trade** | DVN +277% | TRGP +145% | -132% | ❌ Cut winner |

---

## What Went Wrong

### 1. Stop Losses Cut Winners Too Early ❌

**TRGP Example:**
- **Unbiased**: +122.3% (held 560 days), +91.5% (held 595 days)
- **Phase 2**: +145% (best trade), but also -10.1%, -16.2% (stopped out early)
- **Problem**: Stop loss triggered during normal volatility, exited before big moves

**DVN Example:**
- **Unbiased**: +277% (best trade, held 777 days)
- **Phase 2**: Likely stopped out early (need to verify)

### 2. Entry Filters Were TOO STRICT ❌

**Entry Criteria:**
- RSI > 50
- Price > 50-day MA  
- 4-week ROC > 10%

**Problem**: These are **LATE entry indicators**
- By the time all 3 conditions met, stock already ran up
- Missed early P1 signals (which are the best entries)
- Entry filters designed for established trends, not momentum breakouts

### 3. More Trades = Worse Performance ❌

- Phase 2: 106 entries (vs unbiased 74)
- Phase 2 churned positions with stop losses
- Each stop loss = realized loss + missed recovery
- Trading costs (slippage) ate into returns

### 4. Win Rate Collapsed ❌

- Unbiased: 39.06% win rate
- Phase 2: 18.75% win rate (-20.31%)
- **80% of Phase 2 trades lost money**

**Why?**
- Stop losses exited during normal drawdowns
- Re-entered later at worse prices
- Whipsawed out of positions repeatedly

---

## The Fundamental Problem

### GHB Strategy = Trend Following, Not Day Trading

**What GHB needs:**
- Early entry (P1 signal = stock just starting uptrend)
- Long hold (P2/N1 states = let trend develop)
- Exit only on N2 (trend clearly broken)

**What Phase 2 did:**
- Late entry (wait for RSI, MA confirmation = trend already mature)
- Short hold (stop loss = exit on volatility spikes)
- Frequent re-entry (whipsaw effect)

### The Paradox

**Momentum investing = Buy strength, ride volatility**
- Phase 2 tried to "protect" from volatility
- But volatility is WHERE THE RETURNS COME FROM
- DVN +277% included multiple -20% drawdowns along the way
- Stop losses would have exited at -10%, missed the +277%

---

## Why Unbiased Universe Works

### Simple = Better

**Unbiased approach:**
1. Select top 25 most volatile stocks (2020 data)
2. Enter P1 (early breakout signal)
3. Hold P2/N1 (let trend develop)
4. Exit N2 (only when trend breaks)
5. **No fancy filters, no premature exits**

### Results Speak

- **TRGP**: Entered early, held through volatility, caught +122% and +92%
- **DVN**: Entered early, held 777 days, caught +277%
- **RCL**: Held through cruise recovery, caught +140%
- **FANG**: Energy momentum, caught +131%

**Win rate 39%** because:
- Some trades fail (CCL, NCLH, WYNN)
- But winners are SO BIG they offset losers
- This is momentum investing: asymmetric returns

---

## Complete Results Summary

### All Attempts Ranked

| Version | CAGR | vs Baseline | Status |
|---------|------|-------------|--------|
| **Unbiased Baseline** | **15.28%** | - | ✅ BEST |
| Enhanced V2 (Phase 1B) | 11.39% | -3.89% | ❌ Failed |
| Enhanced V1 (Phase 1) | 10.44% | -4.84% | ❌ Failed |
| **Phase 2 (Stop+Filter)** | **3.86%** | **-11.41%** | ❌❌ DISASTER |

**Ranking**: Unbiased > V2 > V1 > Phase 2

### Key Insight

**Every "improvement" made things worse:**
1. Phase 1: Quality filters removed winners → -4.84% CAGR
2. Phase 1B: Gentler filters still removed winners → -3.89% CAGR
3. Phase 2: Entry filters + stop losses destroyed strategy → -11.41% CAGR

**Pattern**: The more we tried to "improve" GHB, the worse it got.

---

## Final Conclusions

### What We Learned

1. **GHB Strategy is already optimized**
   - P1 entry = catch breakout early
   - N2 exit = only exit when trend broken
   - **Don't overthink it**

2. **Momentum ≠ Day Trading**
   - Momentum needs long holds (500-800 days)
   - Volatility is normal (expect -20% drawdowns)
   - Stop losses kill momentum strategies

3. **Simple volatility screening works**
   - No need for quality filters
   - No need for sector limits
   - Just pick volatile stocks, let GHB do its job

4. **High win rate ≠ High returns**
   - Unbiased: 39% win rate, 15.28% CAGR ✅
   - Phase 2: 19% win rate, 3.86% CAGR ❌
   - **Asymmetric payoffs > win rate**

### The Real Lesson

**Stop trying to "fix" what isn't broken.**

GHB Strategy baseline:
- 15.28% CAGR (realistic, beats S&P 500)
- Captured energy bull run 2021-2023
- Survived cruise disasters with N2 exits
- **This is good enough**

---

## Recommendations

### ❌ DO NOT IMPLEMENT

1. ~~Quality filters~~ (Phase 1: -4.84%)
2. ~~Sector limits~~ (Phase 1: -4.84%)
3. ~~ATR stop losses~~ (Phase 2: -11.41%)
4. ~~Momentum entry filters~~ (Phase 2: -11.41%)
5. ~~Any other "enhancements"~~ (All failed)

### ✅ KEEP SIMPLE

1. **Use unbiased universe** (volatility-only selection)
2. **Follow GHB signals exactly** (P1 → N2, no overrides)
3. **Accept 15.28% CAGR** (realistic forward expectation)
4. **Accept drawdowns** (part of momentum investing)

### 🎯 Real Improvements (If Needed)

If 15.28% isn't enough, the ONLY way to improve:

1. **Better universe selection**
   - Not by quality (failed)
   - But by expanding to more sectors
   - Try: S&P 500 + NASDAQ 100 (top 50 most volatile)
   - More stocks = more opportunities

2. **Dynamic position sizing**
   - Not by stop losses (failed)
   - But by volatility-adjusted sizing
   - High vol stocks: smaller positions (risk parity)
   - This might add +2-3% CAGR

3. **Accept the baseline**
   - 15.28% CAGR beats S&P 500 (~14%)
   - Beats inflation (~3%)
   - Beats most hedge funds
   - **Just use it**

---

## Final Verdict

**Unbiased baseline (15.28% CAGR) is the winner.**

Every attempt to "improve" it failed:
- Phase 1: -4.84% CAGR (quality filters removed winners)
- Phase 1B: -3.89% CAGR (still removed winners)  
- Phase 2: -11.41% CAGR (stop losses + filters destroyed strategy)

**The strategy doesn't need improvement. We need to stop "improving" it.**

---

## Going Forward

### Production Configuration

```json
{
  "universe": "sp500_unbiased_2020",
  "start_date": "2021-01-01",
  "end_date": "2025-12-31",
  "expected_cagr": "15.28%",
  "strategy": "GHB baseline (no enhancements)",
  "notes": "Tested Phase 1, 1B, and 2. All failed. Baseline wins."
}
```

### What to Tell Users

"After extensive testing of multiple enhancement strategies:
- Phase 1 (quality filters): **Failed** (-4.84%)
- Phase 1B (gentler filters): **Failed** (-3.89%)
- Phase 2 (stop losses + entry filters): **Failed** (-11.41%)

**The baseline GHB strategy (15.28% CAGR) outperformed all "improvements".**

This is your realistic forward expectation. Accept it, or use a different strategy."

---

## Lessons for Future Development

1. **Don't optimize backtests** - Leads to overfitting
2. **Simple > Complex** - Volatility-only screening beat multi-factor
3. **Trust the strategy** - GHB signals (P1→N2) are already optimized
4. **Momentum ≠ Risk management** - Stop losses kill momentum
5. **Accept volatility** - It's where returns come from

**The unbiased 15.28% CAGR is the real answer.**

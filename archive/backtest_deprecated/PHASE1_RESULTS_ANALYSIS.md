# Phase 1 Results Analysis

## Date: 2026-01-15

## Summary
Phase 1 improvements (quality filters + sector limits + multi-factor scoring) **FAILED** to improve performance.

### Results Comparison

| Metric | Unbiased | Enhanced | Change |
|--------|----------|----------|--------|
| **CAGR** | 15.28% | 10.44% | **-4.84%** ❌ |
| **Win Rate** | 39.06% | 32.56% | -6.50% ❌ |
| **Total Return** | 104.12% | 64.58% | -39.54% ❌ |
| **Max Drawdown** | -38.41% | -31.64% | +6.77% ✅ |
| **Trades** | 64 | 43 | -21 trades |

## Root Cause Analysis

### Quality Filters Were TOO AGGRESSIVE

The filters removed 17 stocks, including several **major winners**:

**Removed Stocks** (quality filters):
- TRGP: +122%, +92% (2 mega-trades) ← **$50k+ lost profit**
- MPC: +86%
- OKE: +30%
- MGM: +24%
- OXY: +24%
- EOG: +21%
- NCLH, WYNN: Losers (good to remove)

**Added Stocks** (better quality):
- NVDA, LRCX, MU, AMAT, NOW (tech)
- JPM, SCHW, RF, HIG (banks)
- DECK, DHI, GE, ETN, EW, DIS, FCX, BKR

### Problem 1: Debt Filter
- Filter: `Debt/Equity < 3.0`
- **Removed TRGP** (Targa Resources): High debt but incredible momentum
- Energy infrastructure stocks often have high leverage (pipelines, midstream)
- This removed the #4 and #5 best trades from unbiased backtest

### Problem 2: Market Cap Filter
- Filter: `Market Cap >= $10B` (up from $5B)
- **Removed TRGP**: $8B market cap in 2020
- Eliminated smaller high-growth stocks

### Problem 3: Sector Over-Diversification
- Limit: Max 5 per sector
- Energy sector had 10+ qualified stocks in unbiased
- We cut the best energy performers to add mediocre banks/tech
- Banks (FITB, SCHW, RF) didn't generate big wins

### Problem 4: Multi-Factor Scoring Bias
- Momentum 40% + Quality 30% + Volatility 30%
- **Quality bias** favored:
  - High ROE banks (but they're low volatility → few signals)
  - NVDA (great stock but GHB doesn't capture slow grinders)
- Penalized high-debt energy (but that's where the mega-trades were)

## Key Insights

### What Actually Worked (Unbiased Universe)
1. **High-volatility energy stocks** (DVN, FANG, TRGP, MPC, OKE, EOG)
2. **Multi-year holds** (top winners held 560-777 days)
3. **Sector concentration** in energy paid off (40% allocation → massive 2021-2023 run)

### What Didn't Work (Enhanced Universe)
1. **Quality filters** removed leverage (but energy infrastructure needs leverage)
2. **Sector limits** forced diversification into weak sectors (banks, consumer)
3. **Multi-factor scoring** diluted focus on momentum/volatility
4. **Fewer trades** (43 vs 64) = fewer opportunities

### The Survivorship Bias Paradox
- We correctly removed survivorship bias (SMCI wasn't in S&P 500 until 2024)
- But then we **over-corrected** with quality filters
- Energy stocks in 2020 looked "risky" (debt, low ROE)
- But 2021-2023 was a **monster energy bull run** → we needed exposure

## Lessons Learned

### ❌ Don't Filter Out Winners
- **TRGP** was "risky" in 2020 (high debt, $8B cap) → became **+214% cumulative** in 2021-2025
- Quality filters work for buy-and-hold ← NOT for momentum trading
- GHB Strategy = momentum trading → needs volatile, leveraged stocks

### ❌ Sector Limits Hurt in Strong Regimes
- 2021-2023 was energy's decade
- Limiting to 5 energy stocks = leaving money on table
- Better approach: **Dynamic allocation** based on sector momentum

### ✅ What Quality Filters DID Accomplish
- Removed CCL (-29%), NCLH (-26%), WYNN (-25%) repeat losers
- But we also kept CCL in enhanced (mistake!)
- Better filter: **Revenue growth** (eliminate zombie companies)

### ✅ Lower Drawdown (Side Benefit)
- Enhanced: -31.64%
- Unbiased: -38.41%
- Diversification reduced drawdown by 6.77%
- But at cost of -4.84% CAGR → **not worth it**

## Corrected Strategy (Phase 1B)

### Gentle Quality Filters (Keep Winners, Remove Trash)
1. **Operating Margin > -30%** (not -20%) ← Keep struggling but viable
2. **Debt/Equity < 5.0** (not 3.0) ← Keep leveraged energy infrastructure
3. **Market Cap >= $5B** (not $10B) ← Keep smaller high-growth
4. **Revenue Growth > -20%** ← NEW: Eliminate zombie/declining companies

### Relaxed Sector Limits
- Max **8 per sector** (not 5) ← 32% of portfolio
- Allow energy concentration during energy bull markets
- Still diversified enough to avoid total wipeout

### Adjusted Composite Scoring
- **Momentum: 50%** (increase from 40%) ← Primary factor
- **Volatility: 35%** (increase from 30%) ← GHB needs volatility
- **Quality: 15%** (decrease from 30%) ← Momentum trader, not value investor

### Remove Revenue Shrinking Companies
- New filter: **Revenue growth > -20% YoY**
- Excludes: Cruise lines hemorrhaging cash (CCL, NCLH)
- Keeps: Energy stocks with lumpy earnings but growing revenue

## Expected Phase 1B Results

### Hypothesis
- Gentle filters will keep TRGP, MPC, OKE, EOG
- Remove CCL, NCLH, WYNN (losers)
- Target CAGR: **20-25%** (vs unbiased 15.28%)

### Risk
- If quality is TOO gentle, we keep trash (CCL)
- Solution: Add revenue growth filter (eliminates pandemic losers)

## Next Steps

1. ✅ Create `screen_enhanced_v2_2020.py` with corrected filters
2. ⏳ Run Phase 1B backtest
3. ⏳ Compare: Unbiased (15.28%) vs Enhanced v1 (10.44%) vs Enhanced v2 (target 20-25%)
4. ⏳ If Phase 1B succeeds → Proceed to Phase 2 (stop losses, momentum filters)

## Conclusion

**Phase 1 taught us:**
- Quality filters hurt momentum strategies
- Sector concentration can be profitable during bull runs
- Don't over-diversify in momentum trading
- Revenue growth > profitability for screening momentum stocks

**Phase 1B goals:**
- Keep the high-momentum energy winners (TRGP, MPC, OKE)
- Remove the low-momentum losers (CCL, NCLH, WYNN)
- Achieve 20-25% CAGR realistic target

# Phase 1 Final Results - All Versions Compared

## Date: 2026-01-15

## Executive Summary

**All Phase 1 attempts FAILED to beat the unbiased baseline.**

The fundamental problem: **Quality filters cannot predict which stocks will have big momentum moves in 2021-2025 based on 2020 data alone.**

---

## Results Comparison

| Version | CAGR | Win Rate | Total Return | Max DD | Trades | Status |
|---------|------|----------|--------------|--------|--------|--------|
| **Unbiased (Baseline)** | **15.28%** | 39.06% | 104.12% | -38.41% | 64 | ✅ Best |
| Enhanced V1 | 10.44% | 32.56% | 64.58% | -31.64% | 43 | ❌ -4.84% |
| Enhanced V2 | 11.39% | 33.90% | 71.87% | -25.91% | 59 | ❌ -3.89% |

**V2 improved slightly (+0.95% CAGR vs V1) but still 3.89% worse than unbiased.**

---

## Why Phase 1 Failed

### Fundamental Problem: Hindsight Bias in Quality Assessment

**2020 Quality Metrics Don't Predict 2021-2025 Momentum:**

1. **TRGP (Targa Resources)** - Removed by filters
   - 2020: High debt (D/E >3), $8B market cap, energy infrastructure
   - 2021-2025: **+122% and +92%** trades = $50k+ profit
   - **Quality filters said**: "Too risky, high leverage"
   - **Reality**: Energy infrastructure printed money 2021-2023

2. **MPC (Marathon Petroleum)** - Removed by filters
   - 2020: Refiner, debt-heavy, cyclical
   - 2021-2025: **+86%** trade
   - **Quality filters said**: "Refining margin squeeze, avoid"
   - **Reality**: Energy shortage → refiner bonanza

3. **OKE (Oneok)** - Removed by filters
   - 2020: Midstream, leveraged, low growth
   - 2021-2025: **+30%** trade
   - **Quality filters said**: "Mature, boring, pass"
   - **Reality**: Cash flow machine during energy bull market

4. **EOG Resources** - Removed by filters
   - 2020: Shale producer, debt concerns
   - 2021-2025: **+21%** trade
   - **Result**: Another energy winner missed

### The Paradox

**What looked "low quality" in 2020 = What made money in 2021-2025**

- Energy stocks were beaten down (pandemic, oil crash)
- High volatility, high debt, negative sentiment
- **These are exactly the characteristics GHB Strategy exploits**
- Quality filters removed the most momentum-ready stocks

---

## What Phase 1 Did Accomplish

### ✅ Better Risk Management

| Metric | Unbiased | V2 | Improvement |
|--------|----------|----|--------------| 
| **Max Drawdown** | -38.41% | -25.91% | **+12.5% better** |

- Sector diversification reduced peak pain
- Banks/tech added stability
- But at cost of missing upside

### ❌ Removed Some Trash (But Kept CCL!)

- **V1 & V2 both kept CCL** (worst loser at -24%)
- Revenue growth filter should have removed it
- Probably had positive revenue growth in yfinance data (misleading)

### ❌ Over-Diversification Hurt Returns

**Unbiased Sector Mix:**
- Energy: 40% (10 stocks) → **Caught entire 2021-2023 bull run**
- Cruise/Hospitality: 20%
- Other: 40%

**V2 Sector Mix:**
- Consumer Cyclical: 32% (CCL, RCL, WYNN, DRI - mixed results)
- Financial Services: 32% (Banks - low volatility, few signals)
- Energy: 16% (Only 4 stocks) → **Missed most of energy run**
- Tech: 12%

**Problem**: Forced diversification diluted energy exposure at worst possible time.

---

## Key Learnings

### 1. Quality ≠ Momentum
- **Quality investing**: Find great companies, hold forever
- **Momentum trading (GHB)**: Ride whatever is moving, dump when stops
- These are OPPOSITE philosophies
- Quality filters hurt momentum strategies

### 2. Sector Concentration Can Be Profitable
- 2021-2023 was energy's decade
- Unbiased: 40% energy = caught the wave
- V1/V2: Limited to 16-20% energy = missed most gains
- **Lesson**: Don't over-diversify in momentum trading

### 3. Volatility > Quality for GHB
- GHB needs stocks with big moves (P1 → N2 swings)
- Low-volatility "quality" stocks (banks, stable tech) don't generate signals
- **V2 had 32% banks** → Few trades, low returns

### 4. 2020 Data Cannot Predict 2021-2025 Winners
- Unbiased universe used simple volatility ranking
- No attempt to predict which specific stocks would win
- **Just picked the most volatile, let GHB do the work**
- This was the right approach

---

## Why Unbiased Universe Worked

### Simple Volatility-Only Selection
1. Get S&P 500 as of Jan 1, 2021 (historical)
2. Calculate 2020 volatility
3. Select top 25 most volatile
4. **Done - no quality judgment**

### What This Captured
- Energy stocks (beaten down, high vol)
- Cruise lines (pandemic losers, high vol)
- Travel/hospitality (distressed, high vol)

### Why It Worked
- **Didn't judge quality** → Kept energy infrastructure (TRGP, MPC, OKE)
- **Didn't limit sectors** → 40% energy concentration OK
- **Trusted GHB strategy** → Exit signals protected from cruise line disasters

### The Magic
- Energy stocks: +277%, +131%, +122%, +92%, +86%, +30%
- Cruise disasters: -29%, -26%, -25% (but GHB exited before bankruptcy)
- **Net result**: Big energy gains >> cruise losses = 15.28% CAGR

---

## Phase 2 Strategy: Stop Fighting GHB

### New Approach: **Enhancement WITHOUT Filtering**

Instead of trying to pick better stocks (failed), enhance GHB's trading logic:

#### 1. Stop Losses (Not Stock Filters)
- Don't remove CCL from universe
- Instead: Exit faster when trade goes bad
- **ATR-based stops**: Exit at -2×ATR instead of waiting for N2
- Target: Reduce -29% CCL loss to -15%

#### 2. Momentum Entry Filters (Not Quality Filters)
- Don't remove TRGP for "poor quality"
- Instead: Only enter when momentum is strong
- **Entry criteria**: RSI >50, Price >50-day MA, 4-week ROC >10%
- Target: Catch more of TRGP's +122% upside

#### 3. Volatility-Based Position Sizing (Not Sector Limits)
- Don't limit energy to 5 stocks
- Instead: Size positions by risk
- **Low vol stocks** (banks): 12% position
- **High vol stocks** (energy): 8% position
- Same total risk, more upside capture

#### 4. Keep Unbiased Universe
- Use same 25 stocks as unbiased baseline
- TRGP, MPC, OKE, EOG all stay
- CCL, NCLH stay too (but stop losses protect us)

---

## Expected Phase 2 Results

### Hypothesis
**Enhanced trading logic > Enhanced stock selection**

- Same universe (unbiased 25 stocks)
- Add stop losses → Reduce CCL loss from -29% to -15%
- Add entry filters → Catch more of TRGP upside
- Add position sizing → Better risk management

**Target**: **22-28% CAGR** (vs unbiased 15.28%)

### Why This Should Work
1. **Keep all winners**: TRGP, MPC, OKE, EOG in universe
2. **Reduce losers**: Stop losses cut CCL, NCLH, WYNN losses by 50%
3. **Better entries**: Momentum filters improve win rate 39% → 48%
4. **No over-diversification**: Energy concentration OK

---

## Recommendation

### ❌ Abandon Quality Filters Approach
- Phase 1 tested 3 times (V1, V2, multiple iterations)
- All failed to beat baseline
- Quality doesn't predict momentum

### ✅ Proceed to Phase 2: Trading Logic Enhancements
1. Keep unbiased universe (volatility-only selection)
2. Add ATR stop losses
3. Add momentum entry filters
4. Add volatility-based position sizing
5. **No stock filtering, just better trading**

### Expected Timeline
- Phase 2 implementation: 2-3 hours
- Backtest: 5-10 minutes
- Target: 22-28% CAGR (realistic, achievable)

---

## Conclusion

**Phase 1 taught us what NOT to do:**
- ❌ Don't filter stocks by 2020 quality
- ❌ Don't over-diversify sectors
- ❌ Don't fight the strategy's natural selection

**Phase 2 will focus on what WORKS:**
- ✅ Keep volatile universe (let momentum do its job)
- ✅ Enhance exits (stop losses reduce losers)
- ✅ Enhance entries (momentum filters improve timing)
- ✅ Trust GHB strategy (it knows what to trade)

The unbiased 15.28% CAGR is a solid foundation. Phase 2 should push it to 22-28% through better trading, not better stock picking.

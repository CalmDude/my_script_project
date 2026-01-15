# Full Scanner Analysis Guide

## Overview

The Full Scanner is a comprehensive technical analysis system that identifies high-probability buy and sell setups across stock universes (S&P 500, NASDAQ 100, or portfolio holdings). It combines multi-timeframe trend analysis, support/resistance levels, volume profile analysis, and momentum indicators to generate actionable watchlists.

---

## Table of Contents

1. [Scanner Architecture](#scanner-architecture)
2. [Technical Analysis Framework](#technical-analysis-framework)
3. [Signal Classification System](#signal-classification-system)
4. [Quality Rating System](#quality-rating-system)
5. [Market Regime Filtering](#market-regime-filtering)
6. [Watchlist Generation Process](#watchlist-generation-process)
7. [Buy Setup Criteria](#buy-setup-criteria)
8. [Sell Signal Criteria](#sell-signal-criteria)
9. [Ranking Methodology](#ranking-methodology)

---

## Scanner Architecture

### Data Flow
```
Stock Universe → Technical Analysis → Signal Classification → Quality Rating → 
Regime Filtering → Ranking by Vol R:R → Top 15 Watchlist
```

### Caching System
- **Cache Duration:** 24 hours
- **Purpose:** Prevents API rate limiting and speeds up repeat scans
- **Location:** `.scanner_cache/` directory
- **Key:** `{ticker}_{daily_bars}_{weekly_bars}.json`

### Analysis Timeframes
- **Daily:** 60 bars (3 months)
- **Weekly:** 52 bars (1 year)
- **Moving Averages:** 50, 100, 200-day

---

## Technical Analysis Framework

### Core Components

#### 1. **Larsson Trend System**
Multi-timeframe trend identification using SMMA (Smoothed Moving Average):

**States:**
- **P1 (Positive Phase 1):** Strong bull trend
- **P2 (Positive Phase 2):** Weak bull or consolidation
- **N1 (Negative Phase 1):** Weak bear or bounce
- **N2 (Negative Phase 2):** Strong bear trend

**Calculation:**
```
V1 = SMMA(HL2, 15)
M1 = SMMA(HL2, 19)
M2 = SMMA(HL2, 25)
V2 = SMMA(HL2, 29)
```

Where:
- P1: V1 > V2 and no crossover confusion
- P2: Mixed signals or weak trend
- N1: Weak decline
- N2: V1 < V2 with bearish confirmation

**Weekly + Daily Combination:**
- Both timeframes analyzed independently
- Combined to generate 8 possible signal combinations

#### 2. **Support & Resistance (Pivot Points)**
Traditional pivot point calculation:

```
Pivot = (High + Low + Close) / 3
R1 = 2×Pivot - Low
R2 = Pivot + (High - Low)
R3 = High + 2×(Pivot - Low)
S1 = 2×Pivot - High
S2 = Pivot - (High - Low)
S3 = Low - 2×(High - Pivot)
```

**Quality Assessment:**
Each level is graded based on:
- Moving average alignment
- Volume profile backing
- Distance from current price

#### 3. **Volume Profile Analysis (VRVP)**
Visible Range Volume Profile identifies high-volume nodes:

**Key Levels:**
- **POC (Point of Control):** Highest volume price level
- **VAH (Value Area High):** Top of high-volume zone (70th percentile)
- **VAL (Value Area Low):** Bottom of high-volume zone (30th percentile)
- **HVN (High Volume Nodes):** Local volume peaks

**Volume Backing Classification:**
- **STRONG:** Support/resistance at POC or within HVN
- **MODERATE:** Within Value Area (VAL-VAH)
- **WEAK:** Outside Value Area, thin volume zone

#### 4. **Moving Averages**
Simple Moving Averages for trend confirmation:
- **D50:** 50-day SMA
- **D100:** 100-day SMA
- **D200:** 200-day SMA

**MA Positioning Logic:**
- MAs below support = bullish foundation
- MAs above resistance = bearish pressure
- Price vs MA distance determines "extended" conditions

#### 5. **Momentum Indicators**

**RSI (Relative Strength Index):**
- **Period:** 14
- **Interpretation:**
  - < 30: Oversold (buy opportunity boost)
  - < 40: Near oversold (minor boost)
  - > 70: Overbought (caution flag)
  - 40-60: Neutral

**Bollinger Bands:**
- **Period:** 20
- **Std Dev:** 2σ
- **Usage:**
  - Support at lower BB = statistical buy opportunity
  - Resistance at upper BB = statistical sell opportunity
  - Distance from middle band = volatility-adjusted position

#### 6. **Volatility Analysis**
**ATR (Average True Range):**
- 14-period ATR
- Used for:
  - Stop loss placement (2× ATR)
  - Volatility assessment
  - Risk-reward calculations

**Daily Range %:**
```
(High - Low) / Close × 100
```
Identifies compression/expansion patterns

---

## Signal Classification System

### 8 Signal Types (Weekly × Daily Combinations)

#### **BULLISH SIGNALS**

**1. FULL HOLD + ADD (P1 + P1)**
- **Weekly:** P1 (strong bull)
- **Daily:** P1 (strong bull)
- **Meaning:** Perfect bullish alignment - macro and short-term trends fully confirmed
- **Action:** Hold full position, add on dips
- **Strength:** ★★★★★ (Strongest buy signal)

**2. SCALE IN (P2 + P1 or N1 + P1)**
- **Weekly:** P2/N1 (weak/unclear)
- **Daily:** P1 (strong bull)
- **Meaning:** Short-term strength without macro confirmation
- **Action:** Scale in gradually on pullbacks
- **Strength:** ★★★☆☆ (Cautious accumulation)

**3. HOLD (P1 + P2)**
- **Weekly:** P1 (strong bull)
- **Daily:** P2 (weak/consolidating)
- **Meaning:** Macro bull intact, short-term pause
- **Action:** Hold position, no buys/sells
- **Strength:** ★★★☆☆ (Patient holding)

#### **TRANSITIONAL SIGNALS**

**4. HOLD MOST + REDUCE (P1 + N1/N2)**
- **Weekly:** P1 (strong bull)
- **Daily:** N1/N2 (bearish)
- **Meaning:** Macro bull with short-term correction
- **Action:** Hold majority, reduce 20% into strength
- **Strength:** ★★☆☆☆ (Defensive trimming)

**5. LIGHT / CASH (P2 + P2, N1 + N1, etc.)**
- **Weekly:** P2/N1 (unclear)
- **Daily:** P2/N1 (unclear)
- **Meaning:** No clear trend on either timeframe
- **Action:** Mostly cash, tiny probes only
- **Strength:** ★☆☆☆☆ (Wait on sidelines)

#### **BEARISH SIGNALS**

**6. CASH (P2 + N2, N1 + N2)**
- **Weekly:** Weak/unclear
- **Daily:** N2 (strong bear)
- **Meaning:** Strong short-term decline, unclear macro
- **Action:** Mostly cash, reduce exposure
- **Strength:** ☆☆☆☆☆ (Risk off)

**7. REDUCE (N1/N2 + P1/P2)**
- **Weekly:** N1/N2 (bearish)
- **Daily:** Bounce/consolidation
- **Meaning:** Macro bear risk despite bounce
- **Action:** Reduce 40% into rallies
- **Strength:** ☆☆☆☆☆ (Exit into strength)

**8. FULL CASH / DEFEND (N2 + N2)**
- **Weekly:** N2 (strong bear)
- **Daily:** N2 (strong bear)
- **Meaning:** Perfect bearish alignment
- **Action:** Full cash, exit all longs
- **Strength:** ☆☆☆☆☆ (Maximum defense)

---

## Quality Rating System

### Buy Quality Assessment

Quality ratings determine how safe and high-probability a buy setup is.

#### **Evaluation Factors**

**1. Moving Average Positioning (50% weight)**
- All 3 MAs below support → Maximum score
- D100 & D200 below support → High score
- Some MA support → Moderate score
- No MA support → Low score

**2. Volume Profile Backing (30% weight)**
- Support at POC/HVN → STRONG backing
- Support in Value Area → MODERATE backing
- Support outside Value Area → WEAK backing

**3. RSI Enhancement (10% weight)**
- RSI < 30: +2 boost (strong oversold)
- RSI < 40: +1 boost (near oversold)
- RSI > 70: -1 penalty (overbought)

**4. Bollinger Band Enhancement (10% weight)**
- Support at/below lower BB: +2 boost
- Support near lower BB: +1 boost

#### **Quality Ratings**

**EXCELLENT** (★★★★★)
- All MAs below support
- STRONG volume backing (at POC/HVN)
- RSI oversold or near oversold
- Bollinger Band support confirmation
- **Interpretation:** Safest entry with multiple layers of support

**GOOD** (★★★★☆)
- D100 & D200 below support OR all MAs with moderate volume
- MODERATE/STRONG volume backing
- Favorable RSI/BB positioning
- **Interpretation:** Solid entry with good probability

**OK** (★★★☆☆)
- Some MA support with moderate volume OR good MAs with weak volume
- Neutral RSI/BB positioning
- **Interpretation:** Acceptable entry but monitor closely

**CAUTION** (★★☆☆☆)
- No MA support or weak volume backing
- Unfavorable RSI/BB
- **Interpretation:** Higher risk - wait for better setup

**EXTENDED** (★☆☆☆☆)
- Price >10% above all MAs
- Price >10% above Value Area High
- **Interpretation:** Wait for pullback - chase risk too high

#### **Quality Flags**

**✓ SAFE ENTRY**
- EXCELLENT quality with multiple support layers
- Best possible risk/reward

**✓ IDEAL**
- GOOD quality with strong setup
- High probability trade

**✓ ACCEPTABLE**
- OK quality with adequate support
- Monitor position sizing

**✓ BEST R:R**
- Highest Vol R:R in watchlist
- Maximum reward potential relative to risk

**⚠ THIN**
- Limited support structure
- Use tighter stops

**⚠ EXTENDED**
- Price stretched from support
- Wait for pullback

**⏳ WAIT**
- Not ready for entry
- Monitor for improvement

### Sell Quality Assessment

Similar framework but inverted for resistance:

**EXCELLENT/GOOD Resistance:**
- MAs above resistance
- STRONG volume resistance at level
- RSI overbought
- At/above upper Bollinger Band

**Stop-Aware Entry Quality**

The scanner also calculates "Entry Quality" which factors in stop loss positioning:

**Accessible Supports:**
Supports within stop tolerance (default 10%) from current price:
```
Stop Level = Current Price × (1 - Stop Tolerance)
Accessible = Support ≥ Stop Level
```

**Logic:**
- 2+ EXCELLENT supports accessible → EXCELLENT entry quality + "SAFE ENTRY" flag
- 1 EXCELLENT or 2+ GOOD supports → GOOD entry quality + "IDEAL" flag
- 1+ supports accessible → OK entry quality + "ACCEPTABLE" flag
- No accessible supports → CAUTION + "THIN" flag
- Supports exist but below stop → CAUTION + "THIN" (cannot protect)

---

## Market Regime Filtering

The scanner adjusts buy criteria based on the overall market environment (analyzed via QQQ or SPY).

### Regime Tiers

#### **🟢 GREEN Regime: FULL HOLD + ADD**
**Conditions:**
- Market signal: FULL HOLD + ADD (P1 + P1)

**Filter Mode:** Normal
- Includes: EXCELLENT, GOOD, OK quality
- Vol R:R: Any ratio accepted
- Quality Flag: Any flag

**Philosophy:** Full bull market - trade normally with standard quality filters

---

#### **🟡 YELLOW Regime: HOLD or SCALE IN**
**Conditions:**
- Market signal: HOLD or SCALE IN

**Filter Mode:** Ultra-Strict
- **Quality Required:** EXCELLENT only
- **Flag Required:** Must have "SAFE ENTRY" flag
- **Vol R:R Required:** ≥ 3.0 (3:1 reward-to-risk minimum)

**Philosophy:** Selective market - only highest conviction setups with:
- Multiple layers of support (EXCELLENT)
- Safe entry points (accessible supports)
- Exceptional risk/reward (3:1+)

---

#### **🟠 ORANGE Regime: HOLD MOST + REDUCE or LIGHT/CASH**
**Conditions:**
- Market signal: HOLD MOST + REDUCE or LIGHT / CASH

**Filter Mode:** Exits Only
- **No buy signals shown** (returns empty DataFrame)
- Only sell signals displayed for portfolio management

**Philosophy:** Risk-off environment - capital preservation priority

---

#### **🔴 RED Regime: REDUCE, CASH, or FULL CASH/DEFEND**
**Conditions:**
- Market signal: REDUCE, CASH, or FULL CASH / DEFEND

**Filter Mode:** Exits Only
- **No buy signals shown**
- Aggressive exit signals for portfolio liquidation

**Philosophy:** Defensive mode - protect capital, no new positions

---

## Watchlist Generation Process

### Step-by-Step Flow

#### **1. Universe Scan**
- Load stock list (S&P 500, NASDAQ 100, or portfolio)
- Fetch technical data for each stock
- Apply 24-hour cache to avoid rate limits

#### **2. Technical Analysis**
For each stock:
- Calculate Larsson states (weekly + daily)
- Generate signal classification
- Calculate support/resistance levels
- Perform volume profile analysis
- Calculate moving averages
- Calculate RSI & Bollinger Bands
- Assess support/resistance quality
- Calculate stop loss levels
- Determine entry quality (stop-aware)

#### **3. Signal Filtering**
Filter for "FULL HOLD + ADD" signals:
- Weekly: P1
- Daily: P1
- Both timeframes must be bullish

**Defensive Validation:**
Ensures no bearish signals contaminate buy results

#### **4. Market Regime Check**
- Analyze regime ETF (QQQ or SPY)
- Determine regime tier (GREEN/YELLOW/ORANGE/RED)
- Apply regime-specific filters:
  - **GREEN:** Keep EXCELLENT, GOOD, OK
  - **YELLOW:** Keep EXCELLENT + SAFE ENTRY + Vol R:R ≥ 3.0 only
  - **ORANGE/RED:** Return empty (no buys allowed)

#### **5. Quality Filtering**
- Keep only EXCELLENT and GOOD quality entries
- Drops OK quality (not top-tier)
- Applies stop-aware entry quality filter

#### **6. Vol R:R Calculation**
For each remaining stock:
```
Vol R:R = (Target R1 Gain %) / (Vol Stop Loss %)
```

Example:
- Current Price: $100
- Target R1: $110 (10% gain)
- Vol Stop: $95 (5% loss)
- Vol R:R = 10% / 5% = 2:1

#### **7. Ranking**
- Sort stocks by Vol R:R (highest first)
- Assign ranks: #1 = highest Vol R:R
- Take top 15-20 stocks

#### **8. Output Generation**
**Excel Watchlist:**
- Tab 1: Top Buy Setups (ranked by Vol R:R)
- Tab 2: Bearish Signals (for portfolio exits)
- Tab 3: Summary Statistics

**PDF Watchlist:**
- Page 1: Title + Regime Status
- Page 2: Glossary + Summary
- Page 3+: Trade Cards (one per stock)

---

## Buy Setup Criteria

### Required Conditions

#### **1. Signal Match**
✅ Must have "FULL HOLD + ADD" signal
- Weekly Larsson: P1
- Daily Larsson: P1

#### **2. Quality Standard**
✅ Must be EXCELLENT or GOOD quality
- Entry quality (stop-aware) preferred
- Fallback to buy quality if entry quality unavailable

#### **3. Regime Compliance**
✅ Must pass regime filter
- GREEN: EXCELLENT, GOOD, OK (then keep EXCELLENT/GOOD for watchlist)
- YELLOW: EXCELLENT + SAFE ENTRY + Vol R:R ≥ 3.0
- ORANGE/RED: No buys allowed

#### **4. Sufficient Data**
✅ Must have valid support levels
✅ Must have valid stop loss calculation
✅ Must have valid R1 target

### Disqualifying Factors

❌ **Bearish or Neutral Signal**
- Any signal other than FULL HOLD + ADD

❌ **Poor Quality**
- OK quality (after top-tier filter)
- CAUTION quality
- EXTENDED quality

❌ **Regime Violation**
- In YELLOW without all three strict criteria
- In ORANGE/RED environment

❌ **Missing Data**
- No support levels available
- No valid stop loss
- No R1 target

---

## Sell Signal Criteria

### Required Conditions

#### **1. Bearish Signal**
Must have one of these signals:
- HOLD MOST + REDUCE
- REDUCE
- LIGHT / CASH
- CASH
- FULL CASH / DEFEND

#### **2. Optional Quality Filter**
Can filter for resistance quality (disabled by default):
- STRONG R1 quality
- MODERATE R1 quality

**Default Behavior:** Include all bearish signals regardless of quality (matches portfolio analysis logic)

### Signal-Based Reduction Targets

**HOLD MOST + REDUCE:**
- Reduce 20% at R1
- Weekly bull intact, daily correction

**REDUCE:**
- 20% at R1, 15% at R2, 5% at R3
- Macro bearish, bounce opportunity

**LIGHT / CASH:**
- 30% at R1, 20% at R2, 10% at R3
- Both timeframes unclear

**CASH:**
- 40% at R1, 30% at R2, 10% at R3
- Strong daily decline

**FULL CASH / DEFEND:**
- 50% at R1, 30% at R2, 20% at R3
- Perfect bearish alignment

---

## Ranking Methodology

### Vol R:R (Volatility Risk-Reward Ratio)

**Definition:**
The ratio of potential reward to volatility-based risk.

**Formula:**
```
Vol R:R = (Target R1 Gain %) / (Vol Stop Loss %)
```

**Components:**

**Target R1 Gain %:**
```
((R1 - Current Price) / Current Price) × 100
```

**Vol Stop Loss %:**
```
2 × ATR / Current Price × 100
```
(Default: minimum 5% if ATR calculation unavailable)

### Why Vol R:R?

**Traditional R:R Issues:**
- Doesn't account for volatility differences
- 10% move in high-vol stock ≠ 10% move in low-vol stock

**Vol R:R Advantages:**
✅ **Volatility-Adjusted:** Normalized for stock's typical movement
✅ **Fair Comparison:** Can compare across different volatility profiles
✅ **Stop-Aware:** Uses actual volatility for stop placement
✅ **Probability-Weighted:** Higher Vol R:R = better odds of reaching target before stop

### Ranking Order

1. **Calculate Vol R:R** for all EXCELLENT/GOOD quality stocks
2. **Sort descending** (highest Vol R:R first)
3. **Assign ranks:**
   - Rank #1 = Highest Vol R:R
   - Rank #2 = Second highest
   - ...
   - Rank #15 = 15th highest
4. **Take top 15-20** for final watchlist

### Quality Flag Assignment

After ranking, special flags added:

**✓ BEST R:R:**
- Assigned to Rank #1 (highest Vol R:R)

**✓ SAFE ENTRY:**
- Assigned to EXCELLENT quality entries
- 2+ accessible EXCELLENT supports

**✓ IDEAL:**
- Assigned to GOOD quality entries
- Strong setup with good support structure

---

## Summary: What Makes a Top Watchlist Stock?

### The Perfect Setup (Rank #1-3)

1. ✅ **Signal:** FULL HOLD + ADD (P1 + P1)
2. ✅ **Quality:** EXCELLENT (all MAs below, strong volume backing)
3. ✅ **Entry Quality:** SAFE ENTRY (multiple accessible supports)
4. ✅ **Regime:** GREEN (full bull market) OR YELLOW with strict compliance
5. ✅ **Vol R:R:** 3.0+ (3:1 or better reward-to-risk)
6. ✅ **RSI:** < 40 (oversold or near oversold)
7. ✅ **Bollinger Bands:** At/near lower band
8. ✅ **Stop Loss:** Clear, actionable level within 5-10% below entry
9. ✅ **Target R1:** Clear resistance level with good quality

### The Good Setup (Rank #4-10)

1. ✅ **Signal:** FULL HOLD + ADD
2. ✅ **Quality:** GOOD (D100 & D200 support, moderate volume)
3. ✅ **Entry Quality:** IDEAL (1+ accessible supports)
4. ✅ **Regime:** GREEN normal filter
5. ✅ **Vol R:R:** 2.0+ (2:1 or better)
6. ✅ **RSI:** < 60 (not overbought)
7. ✅ **Bollinger Bands:** Below middle band
8. ✅ **Stop Loss:** Clear level
9. ✅ **Target R1:** Valid resistance

### The Acceptable Setup (Rank #11-15)

1. ✅ **Signal:** FULL HOLD + ADD
2. ✅ **Quality:** GOOD or high-end OK (upgraded to GOOD for watchlist)
3. ✅ **Entry Quality:** ACCEPTABLE (1 support accessible)
4. ✅ **Regime:** GREEN normal filter
5. ✅ **Vol R:R:** 1.5+ (1.5:1 or better)
6. ✅ **RSI:** Any (not severely overbought)
7. ✅ **Stop Loss:** Clear level
8. ✅ **Target R1:** Valid resistance

---

## Key Takeaways

### For Traders

1. **Trust the Process:** Watchlist stocks have passed 10+ filters to get ranked
2. **Regime Matters:** Adjust position sizing based on regime color (GREEN = normal, YELLOW = small)
3. **Rank Indicates Quality:** Top 5 ranks are statistically better performers
4. **Quality Flags Guide Risk:** SAFE ENTRY > IDEAL > ACCEPTABLE > THIN
5. **Vol R:R = Probability:** Higher ratio = better odds of target vs stop hit

### For Backtesting

1. **No Additional Filtering Needed:** Watchlist is pre-filtered
2. **All 15 Ranks Tested:** Measures raw edge before cherry-picking
3. **Exit Rules:** Stop first, then R1 target, then hold to end
4. **Performance Segments:** Analyze by quality, rank, Vol R:R tier
5. **Edge Validation:** Win rate > 50% and avg return > 0 = positive edge

### Scanner Philosophy

**"Quality Over Quantity"**
- Scans 100s of stocks
- Filters to 15-20 best opportunities
- Ranks by objective risk/reward
- Adapts to market regime
- Provides clear entry/exit levels

**"Multi-Layer Confirmation"**
- Trend (Larsson weekly + daily)
- Support (pivot points + volume profile)
- Momentum (RSI + Bollinger Bands)
- Stop loss (volatility-based)
- Quality (comprehensive rating system)

---

## Document Version

**Version:** 1.0  
**Date:** January 12, 2026  
**Author:** Portfolio Analyser System  
**Purpose:** Complete technical reference for Full Scanner logic

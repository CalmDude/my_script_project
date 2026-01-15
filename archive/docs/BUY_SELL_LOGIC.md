# BUY/SELL LOGIC DOCUMENTATION

This document explains the technical logic behind buy and sell signals in the Portfolio Analyzer system.

---

## TABLE OF CONTENTS
1. [Buy Signal Logic](#buy-signal-logic)
2. [Buy Quality Assessment](#buy-quality-assessment)
3. [Sell Quality Assessment](#sell-quality-assessment)
4. [All Signal Types](#all-signal-types)

---

## BUY SIGNAL LOGIC

### Primary Buy Signal: "FULL HOLD + ADD"

The **FULL HOLD + ADD** signal is the strongest bullish signal and the primary buy indicator. It requires both weekly and daily timeframes to be in bullish alignment.

### Larsson State Indicator

The signal is generated using the **Larsson State Indicator**, which compares momentum across two timeframes (weekly and daily).

**Calculation Method:**

1. **Calculate 4 SMMA periods** on HL2 (High+Low)/2:
   - `v1` = SMMA(15) - Fast momentum
   - `m1` = SMMA(19) - Fast reference
   - `m2` = SMMA(25) - Slow reference
   - `v2` = SMMA(29) - Slow momentum

2. **State Determination Logic:**

   - **BULL State (+1)**:
     - `v1 > m1` AND
     - `v1 > v2` AND
     - `m2 > v2`
     - *Interpretation: Fast momentum above slow, trend accelerating upward*

   - **BEAR State (-1)**:
     - `v1 < v2`
     - *Interpretation: Fast momentum below slow, trend declining*

   - **NEUTRAL State (0)**:
     - All other conditions
     - *Interpretation: Trend unclear, sideways consolidation*

3. **Signal Mapping Table:**

| Weekly State | Daily State | Signal Result        | Action                          |
|--------------|-------------|----------------------|---------------------------------|
| BULL (+1)    | BULL (+1)   | **FULL HOLD + ADD**  | **✅ BUY SIGNAL**              |
| BULL (+1)    | NEUTRAL (0) | HOLD                 | Hold position, no action        |
| BULL (+1)    | BEAR (-1)   | HOLD MOST + REDUCE   | Consider trimming               |
| NEUTRAL (0)  | BULL (+1)   | SCALE IN             | Small positions only            |
| NEUTRAL (0)  | NEUTRAL (0) | LIGHT / CASH         | Stay in cash                    |
| NEUTRAL (0)  | BEAR (-1)   | CASH                 | Stay in cash                    |
| BEAR (-1)    | BULL (+1)   | REDUCE               | Reduce exposure                 |
| BEAR (-1)    | NEUTRAL (0) | CASH                 | Stay in cash                    |
| BEAR (-1)    | BEAR (-1)   | FULL CASH / DEFEND   | Exit positions                  |

**Key Requirement for Buy Signal:**
```
Weekly State = BULL (+1) + Daily State = BULL (+1) → "FULL HOLD + ADD"
```

Only when **BOTH** timeframes show bullish momentum does the system generate a buy signal.

---

## BUY QUALITY ASSESSMENT

After a "FULL HOLD + ADD" signal is generated, the system evaluates **Buy Quality** for each support level (S1, S2, S3) to determine the best entry points.

### Quality Rating Scale

Buy Quality ranges from **EXCELLENT** (best) to **EXTENDED** (worst):

| Rating      | Meaning                                          |
|-------------|--------------------------------------------------|
| EXCELLENT   | Ideal entry - strong setup with all factors aligned |
| GOOD        | Strong entry - most factors favorable            |
| OK          | Acceptable entry - some concerns                 |
| CAUTION     | Weak entry - significant concerns                |
| EXTENDED    | Do NOT buy - price too far from support         |
| N/A         | Insufficient data to assess                      |

### Assessment Criteria

Buy Quality is determined by **four primary factors**:

1. **Moving Average Confluence** - How many MAs provide support?
2. **Volume Profile Backing** - Is there strong volume at the support level?
3. **RSI (14) Positioning** - Is the stock oversold or overbought? 🆕
4. **Bollinger Bands (20,2) Position** - Is the support at a statistical extreme? 🆕

### Moving Average Support

The system checks which daily moving averages are **below** the support level (providing a cushion):

- **D50** (50-day SMA)
- **D100** (100-day SMA)
- **D200** (200-day SMA)

**Logic:**
- More MAs below support = Stronger support
- MAs act as secondary support if price breaks through primary level

### Volume Profile Backing

Uses **VRVP (Volume Range Visible Price)** analysis to assess volume concentration:

**Volume Quality Levels:**

- **STRONG**: Support aligns with POC or HVN (±3% tolerance)
  - POC = Point of Control (price with highest volume)
  - HVN = High Volume Node (significant volume cluster)
  - *Interpretation: Heavy trading occurred here, level well-established*

- **MODERATE**: Support within Value Area (VAL to VAH range)
  - Value Area = 70% of volume traded
  - *Interpretation: Decent volume support, reasonable confidence*

- **WEAK**: Support in low volume zone or near LVN
  - LVN = Low Volume Node (minimal trading)
  - *Interpretation: Untested level, may not hold*

### RSI (Relative Strength Index) - Momentum Assessment 🆕

**RSI measures momentum on a 0-100 scale:**

**For Buy Quality Enhancement:**

- **RSI < 30**: **+2 boost** - Strong oversold (bounce likely)
  - Enhancement note: "RSI [value] oversold"
  
- **RSI 30-40**: **+1 boost** - Approaching oversold
  - Enhancement note: "RSI [value] near oversold"
  
- **RSI 40-60**: **Neutral** - No adjustment
  
- **RSI > 70**: **-1 penalty** - Overbought (wait for pullback)
  - Enhancement note: "RSI [value] overbought"

**Logic:** Lower RSI at support = better entry timing (oversold bounce potential)

### Bollinger Bands - Statistical Extremes 🆕

**Bollinger Bands (20-period SMA ± 2 standard deviations) identify price extremes:**

**For Buy Quality Enhancement:**

- **Support ≤ Lower Band** (within 2%): **+2 boost** - 2σ statistical support
  - Enhancement note: "S[X] at/below lower BB ([%] from middle)"
  
- **Support near Lower Band** (within 5%): **+1 boost** - Approaching statistical support
  - Enhancement note: "S[X] near lower BB"
  
- **Support in middle range**: **Neutral** - No adjustment

**Logic:** Support at/below lower BB = statistical extreme (mean reversion likely)

### Buy Quality Decision Tree

```
Step 1: Check for EXTENDED conditions
├─ Price >10% above ALL MAs? → EXTENDED
└─ Price >10% above VAH? → EXTENDED

Step 2: Assess Volume Backing
├─ STRONG: Near POC or HVN
├─ MODERATE: In Value Area
└─ WEAK: Low volume zone

Step 3: Count MAs Below Support
├─ All 3 MAs (D50, D100, D200) below support
│   ├─ STRONG volume → Base: EXCELLENT
│   ├─ MODERATE volume → Base: GOOD
│   └─ WEAK volume → Base: OK
│
├─ D100 & D200 below support (2 MAs)
│   ├─ STRONG/MODERATE volume → Base: GOOD
│   └─ WEAK volume → Base: OK
│
├─ Some MA support (1 MA)
│   ├─ WEAK volume → Base: CAUTION
│   └─ STRONG/MODERATE volume → Base: OK
│
└─ No MA support (0 MAs)
    └─ Any volume → Base: CAUTION

Step 4: Apply RSI/BB Enhancements 🆕
├─ Calculate boost from RSI:
│   ├─ RSI < 30: +2
│   ├─ RSI 30-40: +1
│   ├─ RSI > 70: -1
│   └─ RSI 40-70: 0
│
├─ Calculate boost from BB:
│   ├─ Support at/below lower BB (±2%): +2
│   ├─ Support near lower BB (±5%): +1
│   └─ Otherwise: 0
│
├─ Total Boost = RSI boost + BB boost
│
└─ Apply upgrade/downgrade:
    ├─ Boost ≥ 3: Upgrade by 2 levels
    ├─ Boost = 2: Upgrade by 1 level
    ├─ Boost = 1: Upgrade by 1 if currently OK
    ├─ Boost ≤ -1: Downgrade by 1 level
    └─ Boost = 0: No change

Final Rating: CAUTION → OK → GOOD → EXCELLENT
```

### Buy Quality Examples

**EXCELLENT Buy (Enhanced from GOOD):**
```
- Signal: FULL HOLD + ADD ✅
- Support: S2 at $79.06
- D50: $88.00 ❌ (above S2)
- D100: $75.00 ✅ (below S2)
- D200: $70.00 ✅ (below S2)
- Volume: In Value Area (moderate)
- RSI: 38 (near oversold) +1 boost
- BB: S2 below lower band ($81.07) +2 boost
- Base Quality: GOOD (D100, D200 + moderate volume)
- Total Boost: +3
- Final Quality: EXCELLENT ⭐⭐
- Note: "D100, D200 support S2 + S2 $79.06 in Value Area + RSI 38 near oversold + S2 at/below lower BB"
```

**GOOD Buy (Enhanced from OK):**
```
- Signal: FULL HOLD + ADD ✅
- Support: S1 at $81.18
- D50: $88.00 ❌ (above S1)
- D100: $85.00 ❌ (above S1)
- D200: $75.00 ✅ (below S1)
- Volume: In Value Area (moderate)
- RSI: 47 (neutral) 0 boost
- BB: S1 at lower band ($81.07) +2 boost
- Base Quality: OK (D200 only + moderate volume)
- Total Boost: +2
- Final Quality: GOOD ⭐
- Note: "D200 support S1, S1 $81.18 in Value Area + S1 at/below lower BB"
```

**CAUTION Buy:**
```
- Signal: FULL HOLD + ADD ✅
- Support: S2 at $145.00
- D50: $155.00 ❌ (above S2)
- D100: $150.00 ❌ (above S2)
- D200: $148.00 ❌ (above S2)
- Volume: Low volume zone
- Quality: CAUTION
- Note: "No MA support + S2 in low volume zone - weak setup"
```

**EXTENDED (Do Not Buy):**
```
- Signal: FULL HOLD + ADD ✅
- Current Price: $165.00
- D50: $145.00
- D100: $140.00
- D200: $135.00
- Quality: EXTENDED ⚠️
- Note: "Price over 10% above all MAs - wait for pullback"
```

---

## SELL QUALITY ASSESSMENT

Sell Quality evaluates resistance levels (R1, R2, R3) to identify profit-taking opportunities.

### Quality Rating Scale

| Rating      | Meaning                                          |
|-------------|--------------------------------------------------|
| EXCELLENT   | Strong resistance - ideal profit-taking zone     |
| GOOD        | Solid resistance - good exit opportunity         |
| OK          | Moderate resistance - acceptable exit            |
| CAUTION     | Weak resistance - may break through easily       |
| MISSED      | Price already above resistance level             |
| N/A         | Insufficient data to assess                      |

### Assessment Criteria

Sell Quality is determined by **four primary factors**:

1. **Moving Average Resistance** - How many MAs block upside?
2. **Volume Profile Resistance** - Is there strong volume at the resistance level?
3. **RSI (14) Positioning** - Is the stock overbought or oversold? 🆕
4. **Bollinger Bands (20,2) Position** - Is the resistance at a statistical extreme? 🆕

### Moving Average Resistance

The system checks which daily moving averages are **above** the resistance level (blocking upside):

- **D50** (50-day SMA)
- **D100** (100-day SMA)
- **D200** (200-day SMA)

**Logic:**
- More MAs above resistance = Stronger ceiling
- MAs act as barriers that price must overcome

### Volume Profile Resistance

**Volume Quality Levels:**

- **STRONG**: Resistance aligns with POC or HVN (±3% tolerance)
  - *Interpretation: Heavy selling pressure expected at this level*

- **MODERATE**: Resistance within or near Value Area
  - *Interpretation: Moderate selling pressure likely*

- **WEAK**: Resistance in low volume zone or well above VAH
  - *Interpretation: Untested zone, may break through easily*

### RSI - Momentum Assessment for Selling 🆕

**For Sell Quality Enhancement:**

- **RSI > 70**: **+2 boost** - Strong overbought (profit-taking opportunity)
  - Enhancement note: "RSI [value] overbought"
  
- **RSI 60-70**: **+1 boost** - Elevated (good exit timing)
  - Enhancement note: "RSI [value] elevated"
  
- **RSI 30-60**: **Neutral** - No adjustment
  
- **RSI < 30**: **-1 penalty** - Oversold (may rally further)
  - Enhancement note: "RSI [value] oversold"

**Logic:** Higher RSI at resistance = better exit timing (overbought reversal likely)

### Bollinger Bands - Statistical Extremes for Selling 🆕

**For Sell Quality Enhancement:**

- **Resistance ≥ Upper Band** (within 2%): **+2 boost** - 2σ statistical resistance
  - Enhancement note: "R[X] at/above upper BB (+[%] from middle)"
  
- **Resistance near Upper Band** (within 5%): **+1 boost** - Approaching statistical resistance
  - Enhancement note: "R[X] near upper BB"
  
- **Resistance in middle range**: **Neutral** - No adjustment

**Logic:** Resistance at/above upper BB = statistical extreme (mean reversion likely)

### Sell Quality Decision Tree

```
Step 1: Check Price Position
└─ Price already >= resistance? → MISSED

Step 2: Assess Volume Resistance
├─ STRONG: Near POC or HVN (strong ceiling)
├─ MODERATE: In/near Value Area
└─ WEAK: Low volume zone or untested

Step 3: Count MAs Above Resistance
├─ All 3 MAs (D50, D100, D200) above resistance
│   ├─ STRONG volume → Base: EXCELLENT
│   ├─ MODERATE volume → Base: GOOD
│   └─ WEAK volume → Base: OK
│
├─ D100 & D200 above resistance (2 MAs)
│   ├─ STRONG/MODERATE volume → Base: GOOD
│   └─ WEAK volume → Base: OK
│
├─ Some MA resistance (1 MA)
│   ├─ WEAK volume → Base: CAUTION
│   └─ STRONG/MODERATE volume → Base: OK
│
└─ No MA resistance (0 MAs)
    └─ Any volume → Base: CAUTION

Step 4: Apply RSI/BB Enhancements 🆕
├─ Calculate boost from RSI:
│   ├─ RSI > 70: +2
│   ├─ RSI 60-70: +1
│   ├─ RSI < 30: -1
│   └─ RSI 30-60: 0
│
├─ Calculate boost from BB:
│   ├─ Resistance at/above upper BB (±2%): +2
│   ├─ Resistance near upper BB (±5%): +1
│   └─ Otherwise: 0
│
├─ Total Boost = RSI boost + BB boost
│
└─ Apply upgrade/downgrade:
    ├─ Boost ≥ 3: Upgrade by 2 levels
    ├─ Boost = 2: Upgrade by 1 level
    ├─ Boost = 1: Upgrade by 1 if currently OK
    ├─ Boost ≤ -1: Downgrade by 1 level
    └─ Boost = 0: No change

Final Rating: CAUTION → OK → GOOD → EXCELLENT
```

### Sell Quality Examples

**EXCELLENT Sell:**
```
- Resistance: R1 at $180.00
- Current Price: $175.00
- D50: $185.00 ✅ (above R1)
- D100: $190.00 ✅ (above R1)
- D200: $195.00 ✅ (above R1)
- POC: $179.50 ✅ (near R1)
- Quality: EXCELLENT
- Note: "D50, D100, D200 block R1 + R1 aligns with POC - strong ceiling"
```

**CAUTION Sell:**
```
- Resistance: R2 at $185.00
- Current Price: $175.00
- D50: $170.00 ❌ (below R2)
- D100: $165.00 ❌ (below R2)
- D200: $160.00 ❌ (below R2)
- Volume: Well above VAH, untested zone
- Quality: CAUTION
- Note: "No MA resistance above R2 + R2 well above Value Area High - may break through"
```

**MISSED Sell:**
```
- Resistance: R1 at $180.00
- Current Price: $182.00
- Quality: MISSED ⚠️
- Note: "Price $182.00 already above R1 $180.00"
```

---

## ALL SIGNAL TYPES

### Complete Signal Descriptions

| Signal               | Weekly | Daily  | Description |
|---------------------|--------|--------|-------------|
| **FULL HOLD + ADD** | BULL   | BULL   | ✅ **BUY SIGNAL** - Strongest bullish alignment. Hold full position and gradually add on dips. Prioritize capital preservation: adds only in confirmed strength. |
| **HOLD**            | BULL   | NEUTRAL| Hold full position patiently - no action needed. Macro bull intact, short-term inconclusive. Wait for daily resolution back to strength. |
| **HOLD MOST + REDUCE** | BULL | BEAR | Hold majority but make gradual reductions. Macro bull with short-term correction. Lighten to preserve profits - scale out on rallies. |
| **SCALE IN**        | NEUTRAL| BULL   | Potential emerging bull. Scale in gradually on dips in small increments. Stay disciplined: keep significant cash reserve. |
| **LIGHT / CASH**    | NEUTRAL| NEUTRAL| Inconclusive - no clear trend. Remain mostly in cash. Wait patiently for alignment; tiny probes only on extreme conviction. |
| **CASH**            | NEUTRAL/BEAR | BEAR/NEUTRAL | Uncertain/weak conditions. Stay mostly or fully in cash. Make reductions if weakness persists. |
| **REDUCE**          | BEAR   | BULL   | Macro bear risk despite short-term bounce. Make gradual reductions into strength/rallies. De-risk toward majority cash. |
| **FULL CASH / DEFEND** | BEAR | BEAR | Strongest bearish alignment. Full cash position; aggressively protect capital. Exit remaining longs through disciplined reductions. |

### Signal Priority for Action

**Actionable Signals (Ranked by Priority):**

1. **FULL HOLD + ADD** → Active buying on quality support levels
2. **SCALE IN** → Small position building, cautious
3. **HOLD** → No action, maintain positions
4. **HOLD MOST + REDUCE** → Begin trimming into strength
5. **REDUCE** → Active selling into rallies
6. **LIGHT / CASH** → Minimal exposure
7. **CASH** → Exit positions
8. **FULL CASH / DEFEND** → Full exit, capital preservation

---

## TECHNICAL IMPLEMENTATION

### Source Code References

- **Signal Generation**: `src/technical_analysis.py` - `analyze_ticker()` function
- **Larsson State**: `src/technical_analysis.py` - `get_larsson_state()` function (line 518)
- **Buy Quality**: `src/technical_analysis.py` - `assess_buy_quality()` function (line 789)
- **Sell Quality**: `src/technical_analysis.py` - `assess_sell_quality()` function (line 957)
- **Volume Profile**: `src/technical_analysis.py` - `calculate_volume_profile()` function (line 539)

### Key Constants

From `src/constants.py`:
```python
SIGNAL_FULL_HOLD_ADD = "FULL HOLD + ADD"  # Primary buy signal
```

### Data Flow

```
1. Fetch Daily & Weekly Price Data (yfinance)
   ↓
2. Calculate Larsson State (Weekly & Daily)
   ↓
3. Map States to Signal → "FULL HOLD + ADD" = BUY
   ↓
4. Calculate Support/Resistance Levels
   ↓
5. Calculate Volume Profile (POC, VAH, VAL, HVN, LVN)
   ↓
6. Assess Buy Quality for S1, S2, S3
   ↓
7. Assess Sell Quality for R1, R2, R3
   ↓
8. Generate Reports with Quality Ratings
```

---

## USAGE GUIDELINES

### For Buy Decisions:

1. **Wait for "FULL HOLD + ADD" signal** - Only buy when both weekly and daily are bullish
2. **Check Buy Quality rating** - Prioritize EXCELLENT and GOOD ratings
3. **Target support levels** - Enter at S1, S2, or S3 (not at current price)
4. **Avoid EXTENDED stocks** - Wait for pullback if >10% above MAs
5. **Use limit orders** - Place buy orders at support levels, not market orders

### For Sell Decisions:

1. **Target resistance levels** - Plan exits at R1, R2, R3
2. **Check Sell Quality rating** - EXCELLENT/GOOD indicate strong resistance
3. **Scale out gradually** - Don't sell entire position at once
4. **Watch for MISSED** - If price already above resistance, wait for next level
5. **Consider MA blocking** - If D50/D100/D200 between price and resistance, may not reach target

### Risk Management:

- **Position Sizing**: Larger positions for EXCELLENT quality, smaller for OK/CAUTION
- **Stop Losses**: Place below S3 or S2 depending on entry point
- **Portfolio Balance**: Don't allocate all capital to one quality level
- **Signal Changes**: Monitor for signal downgrades (FULL HOLD + ADD → HOLD → REDUCE)

---

## REVISION HISTORY

| Date       | Version | Changes                                    |
|------------|---------|---------------------------------------------|
| 2026-01-10 | 1.1     | Added RSI and Bollinger Bands enhancements |
| 2026-01-10 | 1.0     | Initial documentation of buy/sell logic     |

---

**Document Owner**: Portfolio Analyzer System  
**Last Updated**: January 10, 2026  
**Status**: Active

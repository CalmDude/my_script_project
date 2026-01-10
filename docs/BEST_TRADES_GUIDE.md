# Full Scanner Best Trades Report - User Guide

## Table of Contents
1. [Overview](#overview)
2. [Report Types](#report-types)
3. [Understanding Buy Setups](#understanding-buy-setups)
4. [Understanding Sell Setups](#understanding-sell-setups)
5. [Ranking System](#ranking-system)
6. [Quality Ratings](#quality-ratings)
7. [Key Metrics Explained](#key-metrics-explained)
8. [How to Use the Reports](#how-to-use-the-reports)
9. [Trading Examples](#trading-examples)
10. [Limitations & Warnings](#limitations--warnings)

---

## Overview

The **Best Trades Report** identifies the top 10 buy and sell opportunities from S&P 500, NASDAQ 100, and your portfolio. It ranks stocks by **Risk/Reward ratio** and **quality scores** to highlight the most favorable trading setups.

### What You Get
- **TOP 10 BUY SETUPS**: Best long positions with strong support
- **TOP 10 SELL SETUPS**: Best short opportunities or positions to reduce/exit

### Output Files
- **Excel (.xlsx)**: Detailed data with all metrics
- **PDF (.pdf)**: Visual report with formatted tables
- **Locations**:
  - `scanner_results/sp500/sp500_best_trades_[timestamp].xlsx`
  - `scanner_results/nasdaq100/nasdaq100_best_trades_[timestamp].xlsx`
  - `scanner_results/portfolio/portfolio_best_trades_[timestamp].xlsx`

---

## Report Types

### 1. S&P 500 Best Trades
- Scans all ~503 S&P 500 stocks
- Identifies top institutional-grade opportunities
- Best for diversified, lower-volatility trades

### 2. NASDAQ 100 Best Trades
- Scans all ~101 NASDAQ 100 stocks
- Tech-heavy, growth-focused opportunities
- Higher volatility, higher reward potential

### 3. Portfolio Best Trades
- Scans stocks in your `data/stocks.txt` file
- Personalized to your watchlist
- Includes any ticker you're tracking

---

## Understanding Buy Setups

### What Qualifies as a Buy Setup?

A stock must meet **ALL** these criteria:

1. **Signal: "FULL HOLD + ADD"**
   - Weekly timeframe: Phase 1 (bullish)
   - Daily timeframe: Phase 1 (bullish)
   - Both must align for maximum probability

2. **Quality: EXCELLENT, GOOD, or OK**
   - Support must be backed by:
     - Moving average confluence (50/100/200 day)
     - Volume profile support
     - Technical indicators (RSI, Bollinger Bands)
   - **Excludes**: CAUTION, EXTENDED, WEAK

3. **Technical Requirements**
   - Price near or at support level (S1)
   - Clear upside target (R1) above current price
   - Positive Risk/Reward ratio

### Buy Setup Information

Each buy setup shows:

| Metric | Description | Example |
|--------|-------------|---------|
| **Rank** | Position in top 10 | #1 of 45 |
| **Grade** | Letter grade (A/B/C/D) | A |
| **Ticker** | Stock symbol | AAPL |
| **Signal** | Trading signal | FULL HOLD + ADD |
| **Price** | Current price | $175.50 |
| **S1** | Support level (buy zone) | $170.00 |
| **S1 Quality** | Support strength | EXCELLENT |
| **R1** | Resistance target | $195.00 |
| **R/R Ratio (S1)** | Using S1 stop | 1:5.8 |
| **Entry R/R (5%)** | Using 5% entry stop | 1:3.9 |
| **Score** | Quality score /100 | 87 |
| **Risk %** | Downside to S1 | 3.1% |
| **Reward %** | Upside to R1 | 11.1% |

### How to Read a Buy Setup

**Example: #1. AAPL - Grade: A | Score: 87/100 | R:R: 1:5.8**

```
Grade: A (Elite setup)
Price: $175.50
Support S1: $170.00 (EXCELLENT) - 3.1% risk
Entry Stop (5%): $166.73 - Practical alternative
Target R1: $195.00 - 11.1% reward
R/R (S1): 1:3.6 | Entry R/R (5%): 1:2.2
```

**Interpretation**:
- **Grade A**: Elite technical setup (score 87/100)
- **Entry Zone**: Buy near $170 (support)
- **Current Price**: $175.50 (3.1% above support)
- **Stop Options**: 
  - Technical: $170 at S1 (3.1% risk)
  - Practical: $166.73 at 5% (fixed risk management)
- **Target**: $195 (11.1% upside potential)
- **Quality**: EXCELLENT support = high probability

### Understanding Stop Loss Distance (Critical!)

The distance to S1 determines your **actual risk** and **optimal stop placement**.

#### Tight Stop Setup (0-3% to S1) ✅ IDEAL

**Example: MRVL (Grade A)**
```
Grade: A
Price: $83.22
Support S1: $81.12 (GOOD quality)
Distance to S1: 2.5%
R/R (S1): 1:9.3 | Entry R/R (5%): 1:4.7
Target R1: $102.70 (+23.4%)

STOP LOSS RECOMMENDATION:
✅ Technical Stop (S1): $79.09 (-2.5% below S1 = 5% total risk)
✅ Entry Stop (5%): $79.06 (5% below entry)
✅ Breakeven Stop: $81.12 (at S1, move here after +5% gain)

WHY GREAT SETUP:
✓ Grade A = Elite technical quality
✓ Tight stop = Low risk (2.5%)
✓ High reward (23.4%)
✓ Excellent R/R (9.3:1 with S1 stop, 4.7:1 with entry stop)
✓ GOOD quality support
✓ Easy to size position (small $ risk per share)
```

**Risk Assessment**: 🟢 LOW RISK
- Stop distance manageable
- Can take larger position
- Stop unlikely to be hit on noise
- **Action**: Strong buy candidate

---

#### Moderate Stop Setup (3-7% to S1) ⚠️ ACCEPTABLE

**Example: AAPL (Grade A)**
```
Grade: A
Price: $175.50
Support S1: $170.00 (EXCELLENT quality)
Distance to S1: 3.1%
R/R (S1): 1:3.6 | Entry R/R (5%): 1:2.2
Target R1: $195.00 (+11.1%)

STOP LOSS RECOMMENDATION:
✅ Technical Stop (S1): $165.66 (-2.5% below S1 = 5.6% total risk)
✅ Entry Stop (5%): $166.73 (5% below entry, simpler)
⚠️ Aggressive Stop: $168.33 (-1% below S1 = 4% total risk)

WHY ACCEPTABLE:
✓ Grade A = Elite quality
✓ Moderate risk (3.1%)
✓ EXCELLENT quality support
✓ Good R/R (3.6:1 with S1, 2.2:1 with entry stop)
⚠️ Position size should be moderate
⚠️ May get stopped on volatility
```

**Risk Assessment**: 🟡 MODERATE RISK
- Stop is reasonable but not ideal
- Reduce position size by 25-50%
- Consider waiting for pullback to S1
- **Action**: Buy with caution or wait

---

#### Wide Stop Setup (7-15% to S1) 🚨 RISKY

**Example: QCOM (Grade B - hypothetical)**
```
Grade: B
Price: $180.00
Support S1: $160.00 (OK quality)
Distance to S1: 11.1%
R/R (S1): 1:2.5 | Entry R/R (5%): 1:2.8
Target R1: $205.00 (+13.9%)

STOP LOSS RECOMMENDATION:
🚨 S1 Stop: $156.00 (-2.5% below S1, but 13.3% total risk!)
✅ Entry Stop (5%): $171.00 (5% from entry - USE THIS INSTEAD)
⚠️ Alternative: Use S2 if closer (check report)

WHY RISKY:
🚨 Very wide stop (11.1% to S1)
🚨 Grade B = Solid but not elite
🚨 Large $ risk per share
🚨 Poor R/R after stop adjustment
⚠️ OK quality (not strong support)
🚨 May not reach S1 before reversing

SOLUTION: Use Entry Stop Instead
✅ Entry Stop at $171 (5%) gives 1:2.8 R/R
✅ Much more manageable risk
✅ Simpler position sizing
✅ Better psychological comfort

ALTERNATIVE STRATEGY:
Option 1: Use 5% entry stop ($171.00) - RECOMMENDED
Option 2: Wait for price to drop to $165 (closer to S1)
Option 3: Skip trade, find better A-grade setup
Option 4: Very small position (50% normal size)
```

**Risk Assessment**: 🔴 HIGH RISK
- Stop too wide for most traders
- Position size must be very small
- Better opportunities likely exist
- **Action**: Skip or wait for better entry

---

### Stop Loss Guidelines by Distance to S1

| Distance to S1 | Stop Strategy | Position Size | Risk Rating | Grade Priority |
|----------------|--------------|---------------|-------------|----------------|
| **0-2%** | S1 - 2% | 100% normal | 🟢 Ideal | A-grade ideal |
| **2-3%** | S1 - 2.5% or 5% entry | 100% normal | 🟢 Great | A/B-grade good |
| **3-5%** | S1 - 3% or 5% entry | 75% normal | 🟡 Good | Prefer A-grade |
| **5-7%** | 5% entry stop | 50% normal | 🟡 Caution | A-grade only |
| **7-10%** | 5% entry stop | 33% normal | 🟠 Risky | Skip B/C grade |
| **10%+** | 5% entry or skip | 25% or skip | 🔴 Avoid | Skip unless A |

**Key Insight**: When S1 is extended (>5% away), the **5% Entry Stop** becomes more practical than the technical S1 stop. The Entry R/R often provides better risk management.

### Why S2/S3 Don't Help When S1 is Too Far

**Critical Understanding**: S2 and S3 are **lower** support levels, further away from current price!

**Support Level Hierarchy**:
```
Current Price: $180.00
S1: $160.00 (closest support, 11.1% below)
S2: $150.00 (next support, 16.7% below) ❌ WORSE!
S3: $140.00 (third support, 22.2% below) ❌ EVEN WORSE!
```

**Why This Happens**:
- Stock has rallied significantly above support structure
- S1, S2, S3 are historical levels left behind
- Using S2/S3 as stops would mean accepting 15-25% risk!
- **Never use S2/S3 as stops when S1 is already too far**

### What To Do When S1 is Too Far Away (>7-10%)

When price is extended above S1, you have 4 viable options:

#### Option 1: Use Fixed Percentage Stop (Most Common)

```
Price: $180.00
S1: $160.00 (11.1% away - ignore it)

STOP STRATEGY:
Use 5% fixed stop from entry:
Stop: $171.00 (-5%)
Reasoning: Manageable risk regardless of S1 distance

This transforms:
Risk: 5% (acceptable)
Reward: Still to R1 (target unchanged)
R/R: May decrease but becomes tradeable
Position Size: 50% normal (extended entry)
```

**When to Use**:
- S1 is >10% away
- Quality is EXCELLENT or GOOD (support exists, just far)
- R/R still acceptable after 5% stop
- Willing to accept "chase" entry risk

#### Option 2: Wait for Pullback (Most Patient)

```
Current Price: $180.00
S1: $160.00 (11.1% away)

WAIT FOR:
Price to pull back to $165-168 (within 5% of S1)

Then:
Entry: $167.00
S1: $160.00 (now only 4.2% away)
Stop: $156.00 (-6.6% total risk)
Much better setup!
```

**When to Use**:
- Not urgent to enter
- High conviction in setup
- Multiple opportunities available
- Patient trader style

**How Long to Wait**:
- Set alert at $168
- Re-evaluate if drops to S1 area
- If never pulls back, no trade (acceptable)
- Don't chase if rallies further

#### Option 3: Skip the Trade (Most Disciplined)

```
Current Price: $180.00
S1: $160.00 (11.1% away)

DECISION: Pass on this trade

REASONING:
✗ Extended above support structure
✗ Risk/reward compromised at this entry
✗ Better opportunities likely exist
✓ Capital preserved for better setups
✓ No FOMO (Fear Of Missing Out)
```

**When to Skip**:
- S1 is >10% away
- Multiple other setups available with closer S1
- Not highly confident in the setup
- Risk-averse trader
- **This is often the best choice!**

#### Option 4: Technical Stop (Advanced)

Instead of S1, use technical indicators:

**A) ATR-Based Stop**:
```
Price: $180.00
ATR(14): $8.00
Stop: $180 - (2 × $8) = $164.00 (-8.9%)

Still wide but based on volatility, not arbitrary S1
```

**B) Moving Average Stop**:
```
Price: $180.00
50-day MA: $172.00
Stop: Below 50-day MA = $171.00 (-5%)

Follows market structure, not fixed support
```

**C) Swing Low Stop**:
```
Price: $180.00
Recent swing low (3-5 days ago): $174.00
Stop: $173.00 (-3.9%)

Uses recent price action, more relevant than old S1
```

**When to Use Technical Stops**:
- You have charting software
- Comfortable with technical analysis
- S1 is very old/stale level
- Price action suggests new support forming

---

### Stop Loss Recommendations in Practice

#### Example 1: MRVL (Perfect Setup)

**From Report**:
```
#1. MRVL - Score: 79/100 | R/R: 1:9.3
Price: $83.22
Support S1: $81.12 (GOOD quality) - 2.5% away
Target R1: $102.70 (+23.4%)
RSI: 47.1
Signal: FULL HOLD + ADD
```

**Optimized Stop Strategy**:
```
🎯 PRIMARY RECOMMENDATION:
Entry: $83.22 (current) or $81.50 (wait for S1)
Stop Loss: $79.09 (-5% total risk, S1 - 2.5%)
Target: $102.70 (+23.4%)
Risk per share: $4.13
Reward per share: $19.48

Position Sizing (for $100,000 portfolio):
Max Risk: $2,000 (2% rule)
Shares: $2,000 ÷ $4.13 = 484 shares
Investment: $40,279 (40% of portfolio)
⚠️ Too large! Reduce to 200 shares ($16,644)
Actual Risk: 200 × $4.13 = $826 (0.8% of portfolio) ✓

🎯 ALTERNATIVE (Conservative):
Entry: $81.50 (wait for pullback to S1)
Stop: $79.27 (-2.7%)
Target: $102.70 (+26%)
Better entry, tighter stop!
```

**Why This Works**:
✅ Tight 2.5% to S1 = easy to manage  
✅ Excellent R/R (9.3:1)  
✅ Small $ risk allows proper position sizing  
✅ GOOD quality support = reliable  
✅ Can afford to be patient  

---

#### Example 2: QCOM (Challenging Setup)

**From Report**:
```
#5. QCOM - Score: 65/100 | R/R: 1:3.1
Price: $180.00
Support S1: $160.00 (OK quality) - 11.1% away
Target R1: $210.00 (+16.7%)
RSI: 52.3
Signal: FULL HOLD + ADD
```

**Optimized Stop Strategy**:
```
🚨 PRIMARY CONCERN:
S1 is 11.1% away - TOO FAR for standard stop!

❌ NAIVE APPROACH (Don't do this):
Stop: $156.00 (S1 - 2.5%)
Total Risk: 13.3% - EXCESSIVE!

✅ OPTION 1: Ignore S1, Use 5% Rule
Entry: $180.00
Stop: $171.00 (-5% from entry)
Target: $210.00 (+16.7%)
Risk/Reward: 16.7% ÷ 5% = 3.3:1 (still acceptable)
Position: 50% normal size

✅ OPTION 2: Use Swing Low Stop (Recent Support)
Look at chart for recent swing lows
If recent low: $174.00 (just 3 days ago)
Stop: $173.00 (-3.9% from entry)
More relevant than old S1 at $160.00
⚠️ Not in report - requires chart review

✅ OPTION 3: Wait for Better Entry
Wait for: Price to drop to $165-170
New Entry: $168.00
S1: $160.00 (now only 4.8% away)
Stop: $156.00 (-7.1% total)
Target: $210.00 (+25%)
Much better risk/reward!

✅ OPTION 4: Skip This Trade
Find setups with S1 within 3-5%
Better opportunities exist
```

**Risk Management**:
⚠️ If you must trade QCOM:
- Max position: 33-50% of normal size
- Use 5% stop from entry, ignore S1
- Monitor price action for new support formation
- Exit if breaks recent swing lows with volume
- Consider this a "chase" entry, not ideal setup

---

### Quality-Adjusted Stop Recommendations

Match stop tightness to support quality:

#### EXCELLENT Quality Support
```
Base Stop: S1 - 2%
Reasoning: Strongest support, deserves tight stop
Max Distance to S1: 5%
Position Size: Full (100%)

Example:
S1: $100 (EXCELLENT)
Price: $103 (3% away) ✓
Stop: $98 (S1 - 2%)
Total Risk: 4.9%
```

#### GOOD Quality Support
```
Base Stop: S1 - 2.5%
Reasoning: Strong support, standard stop
Max Distance to S1: 7%
Position Size: 75-100%

Example:
S1: $100 (GOOD)
Price: $105 (5% away) ✓
Stop: $97.50 (S1 - 2.5%)
Total Risk: 7.1%
```

#### OK Quality Support
```
Base Stop: S1 - 3% OR 5% from entry
Reasoning: Weaker support, need cushion
Max Distance to S1: 10%
Position Size: 50-75%

Example:
S1: $100 (OK)
Price: $108 (8% away) ⚠️
Stop: $97 (S1 - 3%) = 10.2% risk
OR: $102.60 (5% from entry) = 5% risk
Choose: $102.60 (better)
Position: 50% normal size
```

---

## Understanding Sell Setups

### What Qualifies as a Sell Setup?

A stock must meet **ALL** these criteria:

1. **Bearish Signal** (any of these):
   - `HOLD MOST + REDUCE` - Start reducing position
   - `REDUCE` - Actively reduce exposure
   - `LIGHT / CASH` - Move mostly to cash
   - `CASH` - Full defensive position
   - `FULL CASH / DEFEND` - Maximum defense

2. **No Quality Filter**
   - All bearish signals included
   - Quality shown but not filtered

3. **Technical Requirements**
   - Price below resistance (R1)
   - Support (S1) below current price for downside target
   - Positive Risk/Reward for short/reduce trades

### Sell Setup Information

Each sell setup shows:

| Metric | Description | Example |
|--------|-------------|---------|
| **Rank** | Position in top 10 | #2 of 51 |
| **Ticker** | Stock symbol | META |
| **Signal** | Trading signal | HOLD MOST + REDUCE |
| **Price** | Current price | $450.00 |
| **R1** | Resistance (risk if long) | $485.00 |
| **R1 Quality** | Resistance strength | STRONG |
| **S1** | Support (downside target) | $420.00 |
| **R/R Ratio** | Reward:Risk ratio | 1:0.5 |
| **Score** | Quality score /100 | 38 |
| **Risk %** | Upside to R1 | 7.8% |
| **Reward %** | Downside to S1 | 6.7% |

### How to Read a Sell Setup

**Example: META - Score: 38/100, R/R: 1:0.5**

```
Signal: HOLD MOST + REDUCE
Price: $450.00
Resistance R1: $485.00 (STRONG)
Stop S1: $420.00
Risk: 7.8% (upside resistance)
Reward: 6.7% (downside potential)
R/R Ratio: 1:0.9
```

**Interpretation**:
- **Action**: Reduce or exit long positions
- **Resistance**: $485 is strong ceiling (7.8% away)
- **Downside Target**: $420 support (6.7% drop potential)
- **Risk/Reward**: Limited upside, downside likely
- **Use Case**: Take profits or avoid entering

---

## Ranking System

### Primary: Letter Grade (A, B, C, D)

Stocks are ranked **primarily by letter grade** derived from their quality score:

| Grade | Score Range | Quality | Color (PDF) |
|-------|-------------|---------|-------------|
| **A** | 70-100 | Elite setups | Green |
| **B** | 50-69 | Solid setups | Blue |
| **C** | 30-49 | Marginal setups | Orange |
| **D** | 0-29 | Poor setups | Red |

### Secondary: Quality Score Within Grade

Within each grade, stocks are ranked by **score** (highest to lowest).

**Example**: All A-grade setups appear first (sorted 85, 79, 75...), then all B-grade setups (69, 58, 53...).

### How Grades Are Calculated

Grades are based on the **quality score (0-100)** which evaluates:
- Support/resistance quality (25pts)
- Distance to technical levels (15pts)
- Reward potential (20pts)
- **R/R ratio using S1/R1 stops** (20pts) - NOT the 5% entry stop
- RSI momentum (12pts)
- Bollinger Band position (8pts)

**Note**: The grade reflects the quality of the technical setup using traditional support/resistance levels (S1/R1), not the practical 5% entry stops.

### Minimum Risk Threshold

To prevent unrealistic ratios when price is at support/resistance:
- **Minimum risk = 2%**
- If actual risk is 0.5%, it's adjusted to 2%
- This happened with EW: actual risk 0.01% → adjusted to 2%

**Example Rankings**:

| Rank | Ticker | R/R Ratio | Score | Why Top Ranked? |
|------|--------|-----------|-------|-----------------|
| #1 | NVDA | 1:8.2 | 92 | Highest R/R + excellent score |
| #2 | AAPL | 1:5.8 | 87 | High R/R + strong quality |
| #3 | MSFT | 1:4.1 | 85 | Good R/R + good quality |
| #10 | AMD | 1:2.3 | 65 | Acceptable R/R, lower score |

---

## Quality Ratings

### Buy Quality (Support Strength)

| Rating | Meaning | Criteria |
|--------|---------|----------|
| **EXCELLENT** | Strongest support | 3 MAs below + volume + RSI oversold |
| **GOOD** | Strong support | 2 MAs below + volume or RSI support |
| **OK** | Adequate support | 1 MA below or volume/RSI support |
| **CAUTION** | Weak support | ⚠️ Limited technical backing |
| **EXTENDED** | Overbought | ⚠️ Price too far above support |
| **WEAK** | Poor setup | ❌ Minimal support, avoid |

### Sell Quality (Resistance Strength)

| Rating | Meaning | Criteria |
|--------|---------|----------|
| **EXCELLENT** | Strongest resistance | 3 MAs above + volume + RSI overbought |
| **STRONG** | Strong ceiling | 2 MAs above + volume or RSI |
| **MODERATE** | Decent resistance | 1 MA above or volume/RSI |
| **WEAK** | Limited resistance | ⚠️ May break through |

**Note**: Buy setups filter by quality (only EXCELLENT/GOOD/OK), but sell setups show all bearish signals regardless of quality.

---

## Key Metrics Explained

### 1. Risk/Reward Ratio (R/R)

**Formula**: `Reward % ÷ Risk %`

**Buy Setup**:
- **Risk**: Distance from current price to support S1
- **Reward**: Distance from current price to target R1

**Sell Setup**:
- **Risk**: Distance from current price to resistance R1 (upside)
- **Reward**: Distance from current price to support S1 (downside)

**Example**:
```
Price: $100
Support S1: $95 (risk = 5%)
Target R1: $120 (reward = 20%)
R/R = 20% ÷ 5% = 4:1 (excellent!)
```

### 2. Quality Score (0-100 points)

**Buy Setup Scoring**:
- Quality (25pts): EXCELLENT=25, GOOD=20, OK=15
- Distance from S1 (15pts): Closer to support = higher score
- Reward potential (20pts): Higher upside = more points
- R/R Ratio (20pts): Better ratio = more points
- RSI (12pts): Oversold = more points
- Bollinger Bands (8pts): At lower band = more points

**Sell Setup Scoring**:
- Similar logic but inverted (near resistance, overbought = higher score)

**Score Interpretation**:
- **80-100**: Exceptional setup
- **60-79**: Strong setup
- **40-59**: Moderate setup
- **20-39**: Weak setup
- **0-19**: Poor setup

### 3. Distance from Support/Resistance

Shows how close price is to key levels:

- **Buy**: `((Price - S1) / Price) × 100`
- **Sell**: `((R1 - Price) / Price) × 100`

**Ideal**:
- Buy: 0-5% above support (in the buy zone)
- Sell: 0-5% below resistance (near ceiling)

### 4. RSI (Relative Strength Index)

Momentum indicator (0-100):

- **RSI < 30**: Oversold (buy opportunity)
- **RSI 30-40**: Moderately oversold
- **RSI 40-60**: Neutral
- **RSI 60-70**: Moderately overbought
- **RSI > 70**: Overbought (sell opportunity)

### 5. Signal Types

**Bullish (Buy)**:
- `FULL HOLD + ADD`: Maximum bullish alignment

**Bearish (Sell)**:
- `HOLD MOST + REDUCE`: Start trimming
- `REDUCE`: Actively reduce exposure
- `LIGHT / CASH`: Move mostly to cash
- `CASH`: Defensive, no clear direction
- `FULL CASH / DEFEND`: Maximum defense

---

## How to Use the Reports

### For Buying (Long Positions)

**Step 1: Review Top 10 Buy Setups**
- Focus on ranks #1-5 for highest probability
- Look for R/R > 3:1
- Prefer EXCELLENT or GOOD quality

**Step 2: Check Entry Price**
- **Current Price vs S1**: How close to support?
- **Ideal**: Within 5% of S1
- **Acceptable**: Within 10% of S1
- **Risky**: More than 10% above S1

**Step 3: Set Your Levels**
- **Entry**: Buy at or near S1 (support)
- **Stop Loss**: 2-5% below S1
- **Target**: R1 (resistance level)
- **Position Size**: Based on risk tolerance

**Example Trade**:
```
Ticker: NVDA
Rank: #1, Score: 92, R/R: 1:8.2

Entry: $850 (at S1 support)
Stop: $830 (-2.4%)
Target: $980 (R1)
Risk: $20/share
Reward: $130/share
Position: Risk 1% of portfolio = [calculate shares]
```

### For Selling (Short or Reduce)

**Step 1: Review Top 10 Sell Setups**
- Check if you own any of these stocks
- Look for bearish signals on holdings
- Review resistance levels

**Step 2: Determine Action**
- **Own the stock?**
  - HOLD MOST + REDUCE: Trim 25-50%
  - REDUCE: Trim 50-75%
  - CASH/DEFEND: Exit 75-100%
- **Looking to short?**
  - Check R/R ratio for short opportunity
  - Use R1 as entry, S1 as target

**Step 3: Execute**
- Reduce positions near resistance (R1)
- Take profits if held from lower levels
- Avoid new long entries

**Example Exit**:
```
Ticker: META (you own 100 shares at $400)
Current: $450 (+12.5% profit)
Signal: HOLD MOST + REDUCE
Resistance R1: $485 (+7.8% from here)
Support S1: $420 (-6.7% from here)

Action: Sell 50 shares at $450
Keep: 50 shares with stop at $440
Reason: Limited upside (R1 close), downside risk increasing
```

---

## Trading Examples

### Example 1: High-Confidence Buy Setup

**NVDA - Rank #1**
```
Score: 92/100
R/R: 1:8.2
Signal: FULL HOLD + ADD
Price: $850
S1: $850 (EXCELLENT)
R1: $980
RSI: 32 (oversold)
```

**Analysis**:
✅ Top-ranked setup  
✅ Excellent R/R ratio  
✅ At support level (ideal entry)  
✅ EXCELLENT quality support  
✅ Oversold RSI  

**Trade Plan**:
- Entry: $850 (right at support)
- Stop: $830 (-2.4%)
- Target: $980 (+15.3%)
- Position: 2% portfolio risk
- **Action**: Strong buy

---

### Example 2: Moderate Buy Setup

**AMD - Rank #8**
```
Score: 68/100
R/R: 1:2.8
Signal: FULL HOLD + ADD
Price: $145
S1: $140 (GOOD)
R1: $160
RSI: 45 (neutral)
```

**Analysis**:
✅ Qualifies for top 10  
⚠️ Lower R/R ratio  
⚠️ Not at support yet (3.4% above)  
✅ GOOD quality support  
⚠️ Neutral RSI  

**Trade Plan**:
- Wait for pullback to $140
- Or enter small position at $145 with tight stop
- Stop: $137 (-5.5%)
- Target: $160 (+10.3%)
- Position: 1% portfolio risk
- **Action**: Wait or small position

---

### Example 3: Sell/Reduce Setup

**META - Rank #3 Sell**
```
Score: 38/100
R/R: 1:0.9
Signal: HOLD MOST + REDUCE
Price: $450
R1: $485 (STRONG)
S1: $420
RSI: 68 (overbought)
```

**Analysis**:
⚠️ Bearish signal  
⚠️ Poor R/R (more upside risk than downside reward)  
⚠️ Near strong resistance  
⚠️ Overbought RSI  

**Trade Plan** (if you own it):
- Sell 50% at $450 (lock in profits)
- Trail stop on remaining 50% at $440
- Full exit if breaks below $440
- **Action**: Reduce exposure

**Trade Plan** (if considering entry):
- **Avoid**: Poor R/R, bearish setup
- Wait for better entry or different ticker

---

### Example 4: Stock Not in Top 10

**MSTR - Rank #33 of 51 (Sell)**
```
Score: 25/100
R/R: 1:0.0
Signal: CASH
Price: $157
R1: $200 (EXCELLENT)
S1: $156
```

**Analysis**:
❌ Not in top 10  
❌ Terrible R/R (0.0)  
⚠️ Neutral signal  
⚠️ Very close to support (1.1%)  

**Why Not Ranked?**:
- Stuck in middle of range
- Too far from resistance ($200 is 27% away)
- Minimal downside reward (1.1% to S1)
- Poor risk/reward for any trade

**Trade Plan**:
- **Action**: Pass, wait for better setup
- Re-evaluate if drops to $156 or rallies to $190

---

## Limitations & Warnings

### ⚠️ Important Disclaimers

1. **Not Financial Advice**
   - These are technical analysis tools only
   - Consult a licensed financial advisor
   - Past performance ≠ future results

2. **Market Risk**
   - All trading involves risk of loss
   - Markets can be irrational
   - News/events can override technical levels

3. **False Signals**
   - Support/resistance can break
   - "FULL HOLD + ADD" doesn't guarantee profit
   - Quality ratings are estimates, not certainties

4. **Ranking Limitations**
   - Compares stocks within same index only
   - Rankings change daily
   - Top 10 doesn't mean all 10 are equally good

5. **Data Limitations**
   - Based on 60-day daily, 52-week weekly data
   - Uses swing pivots and volume profiles
   - May miss recent news/fundamentals

### Best Practices

✅ **Do**:
- Use as one input in trading decisions
- Combine with fundamental analysis
- Set stop losses on all trades
- Size positions based on risk tolerance
- Review holdings against sell signals regularly
- Focus on top 3-5 setups

❌ **Don't**:
- Trade every signal blindly
- Ignore stop losses
- Over-leverage positions
- Chase stocks already extended
- Ignore fundamental changes
- Use as sole decision criteria

### When to Ignore the Report

Skip trades when:
- Major news pending (earnings, Fed meeting)
- Market in extreme volatility
- Stock has fundamental issues
- You don't understand the company
- Position size would be too large
- Can't monitor the trade

---

## Quick Reference

### Buy Setup Checklist
- [ ] Rank in top 10?
- [ ] R/R > 3:1?
- [ ] Quality EXCELLENT or GOOD?
- [ ] Price within 5% of S1?
- [ ] RSI < 40?
- [ ] Signal "FULL HOLD + ADD"?
- [ ] Stop loss planned?
- [ ] Position sized correctly?

### Sell Setup Checklist
- [ ] Own the stock?
- [ ] Signal bearish?
- [ ] Near resistance (R1)?
- [ ] Holding profit to take?
- [ ] Better opportunities elsewhere?
- [ ] Exit plan ready?

### Red Flags
🚩 R/R < 1:1 (poor setup)  
🚩 Quality CAUTION or WEAK  
🚩 Price > 10% from support  
🚩 Score < 40  
🚩 Rank > 10  
🚩 Conflicting signals  

---

## Advanced Stop Loss & Trailing Stop Strategies

### Professional Stop Loss Placement (Buy Setups)

Top traders use the report's support levels (S1, S2, S3) and technical data to place intelligent stops that maximize gains while protecting capital.

#### Strategy 1: Support-Based Stops (Most Common)

**Using S1 (Primary Support)**:
```
Entry: At or near S1
Initial Stop: 2-5% below S1
Reasoning: Allow for normal market noise without getting stopped out
```

**Example from Report**:
```
Ticker: NVDA
Entry: $850 (at S1)
S1: $850 (EXCELLENT quality)
Initial Stop: $830 (-2.4% below S1)

Why 2.4%? 
- EXCELLENT quality = tight stop (2-3%)
- GOOD quality = moderate stop (3-4%)
- OK quality = wider stop (4-5%)
```

**Multi-Level Stop Strategy**:
```
Entry: $850
Stop Level 1: $847 (-0.4%) - Technical break of S1
Stop Level 2: $840 (-1.2%) - 1% cushion below S1
Stop Level 3: $830 (-2.4%) - Final stop, 2% below S1

Use S2 as "disaster stop": 
- S2: $800 (fallback if S1 breaks with high volume)
```

#### Strategy 2: ATR-Based Stops (Volatility-Adjusted)

**Average True Range (ATR) Method**:
- Calculate ATR (14-day typical)
- Stop = Entry - (1.5 × ATR)

**Example**:
```
NVDA Entry: $850
ATR(14): $20
Stop: $850 - (1.5 × $20) = $820 (-3.5%)

Adjustments:
- High quality setup: 1.5 × ATR
- Medium quality: 2.0 × ATR  
- Low quality: 2.5 × ATR
```

**When ATR conflicts with S1**:
- Use the **wider** stop to avoid premature exit
- If ATR stop is $820 but S1 is $850, use $830 (S1 - 2%)

#### Strategy 3: Risk-Based Stops (2% Portfolio Rule)

**The 2% Rule**: Never risk more than 2% of total portfolio on one trade.

**Calculation**:
```
Portfolio: $100,000
Max Risk per Trade: $2,000 (2%)

Entry: $850
Stop: $830
Risk per Share: $20
Position Size: $2,000 ÷ $20 = 100 shares
Total Investment: $85,000 (85% of portfolio - TOO LARGE!)

Correct Approach:
Max Position: 10% of portfolio = $10,000
Shares: $10,000 ÷ $850 = 11 shares
Risk: 11 × $20 = $220 (0.22% of portfolio) ✓
```

**Using Report Data**:
```
From Best Trades Report:
Price: $850
S1: $850
Risk %: 2.4% (adjusted minimum)

Stop: $830 (S1 - 2.4%)
Position Size = Portfolio Risk ÷ (Entry - Stop)
Position Size = $2,000 ÷ $20 = 100 shares or $85,000

If this exceeds 10-15% of portfolio, reduce shares!
```

#### Strategy 4: Time-Based Stops

**Day 1-3**: Use tight stop at S1 - 2%  
**Day 4-10**: Loosen to S1 - 3% (allow position to breathe)  
**After 10 days**: Re-evaluate or use trailing stop

---

### Professional Trailing Stop Strategies

Once a position moves in your favor, protect profits with trailing stops.

#### Strategy 1: Percentage-Based Trailing Stop

**Simple 5-10% Trail**:
```
Entry: $850
Current: $920 (+8.2% gain)
5% Trailing Stop: $874 (protects 2.8% profit)
8% Trailing Stop: $846 (near breakeven)
10% Trailing Stop: $828 (allows pullback)

Recommended for Report Setups:
- R/R > 5:1 → Use 5-7% trail (tight, protect gains)
- R/R 3-5:1 → Use 7-10% trail (moderate)
- R/R < 3:1 → Use 10-12% trail (loose)
```

**Example with NVDA**:
```
Entry: $850
Target R1: $980
Current: $920 (70% of way to target)

Initial Stop: $830 (S1 - 2.4%)
Price hits $900: Move stop to $855 (5% trail, locks 0.6% profit)
Price hits $920: Move stop to $874 (5% trail, locks 2.8% profit)
Price hits $940: Move stop to $893 (5% trail, locks 5% profit)
Hits $960: Move stop to $912 (locks 7.3% profit)
Hits R1 $980: Take profit or trail at $931 (locks 9.5%)
```

#### Strategy 2: Support-Based Trailing Stops

**Use S1, S2, S3 as Dynamic Stops**:
```
Entry: $850 at S1 ($850)
Price rallies to $920

New Support Forms:
- Previous S1 ($850) becomes new S3
- New S1 forms at $900
- Move stop to $882 (S1 $900 - 2%)

Price rallies to $960
- New S1 forms at $940
- Move stop to $920 (S1 $940 - 2%)

Benefits:
✓ Follows market structure
✓ Uses actual support levels
✓ Adaptive to price action
```

**From Report - Update Stops When**:
1. Price moves 5-10% in your favor
2. New support level forms (becomes visible on chart)
3. Weekly timeframe closes above previous resistance
4. RSI crosses back below 70 after being overbought

#### Strategy 3: Chandelier Stop (Volatility-Based Trail)

**Formula**: `Highest High - (ATR × Multiplier)`

**For Buy Positions**:
```
Highest High since entry: $950
ATR(14): $20
Multiplier: 3.0 (standard)

Chandelier Stop: $950 - (3 × $20) = $890

As price makes new highs:
New High: $980
Stop: $980 - $60 = $920
```

**Multiplier Guide** (using Report Quality):
- EXCELLENT quality: 2.5 × ATR (tighter)
- GOOD quality: 3.0 × ATR (standard)
- OK quality: 3.5 × ATR (looser)

#### Strategy 4: Moving Average Trailing Stop

**Use Report's MA Data**:
```
Entry: $850
Price rallies to $950

Stop Options:
- Below 20-day MA: $920 (aggressive, may get whipsawed)
- Below 50-day MA: $900 (moderate, professional standard)
- Below 100-day MA: $860 (conservative, long-term)

Best Practice:
Use 50-day MA as trailing stop after 2-3 weeks in position
Tighten to 20-day MA when near R1 target
```

#### Strategy 5: Fibonacci Retracement Stops

**After Initial Rally**:
```
Entry: $850 (S1)
Rally to: $950 (interim high)
Rally Range: $100

Fibonacci Levels:
23.6% retracement: $927 (aggressive trail)
38.2% retracement: $912 (moderate trail)
50% retracement: $900 (conservative trail)
61.8% retracement: $888 (very conservative)

Professional Choice: 38.2% or 50% depending on volatility
```

---

### Scaling Out Strategy (Maximize Gains)

Top traders don't exit full position at once - they scale out at targets.

#### The 50-30-20 Exit Strategy

**Using Report Data**:
```
Entry: $850 at S1
Target R1: $980 (+15.3%)
Position: 100 shares

Scaling Plan:
1️⃣ Sell 50% (50 shares) at R1 $980
   - Lock in +15.3% on half position
   - Move stop to breakeven on remaining 50

2️⃣ Sell 30% (30 shares) at R2 $1,020 (if exists)
   - Trail stop to $960 on remaining 20 shares
   
3️⃣ Trail final 20% (20 shares) with 8% stop
   - Let winners run
   - Exit when stop is hit

Results:
50 shares: +$130 profit = $6,500
30 shares: +$170 profit = $5,100
20 shares: Variable (let it run)
Average better than selling all at R1!
```

#### The 25-25-25-25 Strategy (Aggressive)

```
Entry: $850 (100 shares)

Exit 25 shares at:
1. Halfway to R1: $915 (+7.6%) - Take early profit
2. At R1: $980 (+15.3%) - Hit target
3. R1 + 50%: $1,045 (+22.9%) - Extended target
4. Trail remaining with 10% stop - Let it run

Benefits:
✓ Take profits early (reduce stress)
✓ Still exposed to big moves
✓ Breakeven faster
```

#### Using Multiple Resistance Levels

**From Report**:
```
S1: $850 (entry)
R1: $980 (first target, +15.3%)
R2: $1,050 (if shown, +23.5%)
R3: $1,100 (if shown, +29.4%)

Exit Strategy:
33% at R1: $980
33% at R2: $1,050 (if momentum continues)
34% trail from R2 with 7% stop

If R2/R3 not in report:
Add Fibonacci extensions:
127.2% extension: $1,050
161.8% extension: $1,100
```

---

### Stop Loss Rules for Different R/R Ratios

#### High R/R Setups (> 5:1)

**Example: R/R 8:1, Entry $850, Target $980**

```
Initial Stop: Very tight (S1 - 2%)
Stop: $832

Why tight?
- Setup has huge upside (8:1)
- If wrong, cut loss quickly
- Don't let 8:1 become 2:1

Trailing: Start trailing at +3% gain
Move to breakeven at +5%
Trail with 5% stop (tight control)
```

#### Medium R/R Setups (2-5:1)

**Example: R/R 3:1, Entry $850, Target $935**

```
Initial Stop: Moderate (S1 - 3%)
Stop: $824

Give more room (R/R not as favorable)
Trailing: Start at +7% gain
Breakeven at +10%
Trail with 7-8% stop
```

#### Low R/R Setups (< 2:1)

**Example: R/R 1.5:1, Entry $850, Target $890**

```
Initial Stop: Wider (S1 - 4%)
Stop: $816

Needs room to work (tight target)
Trailing: Start at +10% gain
Or use time-based: exit after 2 weeks if no progress
Consider skipping trade if R/R < 2:1
```

---

### Position Management After Entry

#### Scenario 1: Position Goes Immediately Against You

**Price drops from $850 to $845 (-0.6%)**

Actions:
1. Review news/fundamentals (any reason?)
2. Check volume (high volume drop = bad, low volume = noise)
3. Check S1 integrity (holding or breaking?)
4. Evaluate S2 distance ($800 = 5.3% lower)

Decisions:
- ✅ S1 holding, low volume: Hold with original stop
- ⚠️ S1 breaking, moderate volume: Exit 50%, stop at S2
- 🚫 S1 breaking, high volume: Exit 100% immediately

#### Scenario 2: Position Moves Sideways

**Price range $845-$855 for 5 days**

Actions:
1. Set time stop (exit if no progress in 10 days)
2. Check weekly timeframe (still bullish?)
3. Opportunity cost (better setups available?)

Professional Approach:
- Give 2 weeks for setup to work
- If still flat, exit and redeploy capital
- Exception: If at strong S1 (EXCELLENT), give 3 weeks

#### Scenario 3: Quick Move to Target

**Price $850 → $980 in 3 days (+15.3%)**

Actions:
1. Take 50% profit at R1 immediately
2. Move stop to $900 on remaining 50%
3. Look for next resistance level
4. Watch for reversal signs (volume spike, long upper wick)

Why:
- Fast moves often retrace
- Lock gains while momentum hot
- Reduce position risk

#### Scenario 4: Slow Grind Higher

**Price $850 → $900 over 15 days (+5.9%)**

Actions:
1. Move stop to $870 (locks 2.4% profit)
2. Continue trailing with 5-7% stop
3. Let position run toward R1
4. Expect 4-6 weeks to reach target

Perfect scenario:
- Strong trend, low volatility
- Trail stops protect gains
- Higher probability of hitting R1

---

### Stop Placement for Sell Setups (Short Positions)

#### Resistance-Based Stops (Inverse of Buy Logic)

**From Report**:
```
Ticker: META (short setup)
Entry: $450 (short near resistance)
R1: $485 (resistance, +7.8%)
S1: $420 (target, -6.7%)

Initial Stop: $485 + 2% = $494 (+9.8% risk)
Trailing: As price drops, trail stop down
At $430: Move stop to $460 (covers 4.4%)
At $420: Move stop to $440 (locks 2.2% profit)
```

#### Risk Management for Shorts

**Key Differences**:
- Unlimited upside risk on shorts
- Use tighter stops (resistance + 2-3%)
- Cover 50% at S1 (target)
- Full exit if breaks above R1 with volume

**Example**:
```
Short Entry: $450
Stop: $466 (R1 $485 - 4%, tighter than longs)
Target S1: $420

Cover Plan:
50% at $435 (-3.3%)
25% at $425 (-5.6%)
25% at $420 (-6.7%)
Stop: $466 (+3.6% loss if wrong)

R/R: 6.7% ÷ 3.6% = 1.86:1
```

---

### Mental Stop Loss Rules

#### Rule 1: Never Move Stop Further Away

**Wrong**:
```
Entry: $850, Stop: $830
Price: $835 (near stop)
You think: "Just needs more room"
Move stop to: $820 ❌ NEVER DO THIS
```

**Right**:
```
Accept the stop out
Loss: $15/share
Re-evaluate setup
Wait for better entry or move on
```

#### Rule 2: Move Stop Only Closer or Breakeven

**Correct Progression**:
```
Entry: $850, Stop: $830 (2.4% risk)
Price: $880 → Move stop to $850 (breakeven)
Price: $900 → Move stop to $874 (5% trail, lock 2.8%)
Price: $920 → Move stop to $893 (5% trail, lock 5%)
Price: $940 → Move stop to $912 (5% trail, lock 7.3%)
```

#### Rule 3: Respect the Stop (No Emotions)

**If stop hit**:
- Exit immediately
- Don't hope for reversal
- Don't add to losing position
- Don't re-enter same day

**Exception**: Flash crash/fat finger (obvious anomaly)

---

### Advanced: Dynamic Stop Adjustment

#### Based on Report Quality Rating

**EXCELLENT Quality (Highest Confidence)**:
```
Initial Stop: S1 - 2% (tight)
Trailing: 5% (aggressive)
Move to Breakeven: At +5% gain (quick)
Time Limit: 4 weeks
```

**GOOD Quality**:
```
Initial Stop: S1 - 3% (moderate)
Trailing: 7% (standard)
Move to Breakeven: At +8% gain
Time Limit: 6 weeks
```

**OK Quality**:
```
Initial Stop: S1 - 4% (wider)
Trailing: 10% (loose)
Move to Breakeven: At +12% gain (patient)
Time Limit: 8 weeks
```

#### Based on Rank Position

**Rank #1-3 (Top Setups)**:
- Tighter stops (higher conviction)
- More aggressive trailing
- Larger position size

**Rank #4-7**:
- Standard stops
- Standard trailing
- Moderate position size

**Rank #8-10**:
- Wider stops (lower conviction)
- Looser trailing
- Smaller position size

---

### Quick Reference: Stop Loss Matrix

| Scenario | Initial Stop | Move to BE | Trailing % | Scale Out |
|----------|-------------|-----------|-----------|-----------|
| **Excellent + Top 3** | S1 - 2% | +5% | 5% | At R1 (50%) |
| **Good + Top 5** | S1 - 3% | +8% | 7% | At R1 (40%) |
| **OK + Top 10** | S1 - 4% | +12% | 10% | At R1 (33%) |
| **High R/R (>5:1)** | S1 - 2% | +3% | 5% | At +10% (50%) |
| **Med R/R (3-5:1)** | S1 - 3% | +7% | 7% | At R1 (40%) |
| **Low R/R (<3:1)** | S1 - 4% | +10% | 10% | At R1 (50%) |
| **Short Position** | R1 + 3% | -5% | 5% up | At S1 (50%) |

**BE** = Breakeven

---

### Common Stop Loss Mistakes to Avoid

❌ **Mistake 1**: No stop at all ("I'll just hold")
- **Fix**: Always set stop before entry

❌ **Mistake 2**: Stop too tight (< 1% for quality setups)
- **Fix**: Use S1 - 2% minimum

❌ **Mistake 3**: Moving stop further away
- **Fix**: Only move stops toward profit

❌ **Mistake 4**: Same stop % for all trades
- **Fix**: Adjust for quality, R/R, volatility

❌ **Mistake 5**: Not trailing stops
- **Fix**: Trail after +5-10% gains

❌ **Mistake 6**: Emotional exits
- **Fix**: Stick to plan, stop is your friend

❌ **Mistake 7**: Ignore time stops
- **Fix**: Exit if no progress in 2-4 weeks

❌ **Mistake 8**: Too large position size
- **Fix**: Risk only 1-2% per trade

❌ **Mistake 9**: No scaling plan
- **Fix**: Scale out 25-50% at targets

❌ **Mistake 10**: Revenge trading after stop
- **Fix**: Take break, analyze what went wrong

---

### Professional Stop Strategy Checklist

**Before Entry**:
- [ ] Stop loss price calculated (S1 - 2-4%)
- [ ] Position size calculated (risk 1-2% portfolio)
- [ ] Risk/reward acceptable (> 2:1)
- [ ] Stop order placed with broker
- [ ] Profit target identified (R1)
- [ ] Scaling exit plan defined

**After Entry**:
- [ ] Monitor S1 support daily
- [ ] Move to breakeven at +5-10% gain
- [ ] Implement trailing stop at +10% gain
- [ ] Scale out 25-50% at R1 target
- [ ] Adjust trail as price rises
- [ ] Exit remaining at trail stop hit

**If Stopped Out**:
- [ ] Review why stop hit
- [ ] Check if setup still valid
- [ ] Document in trading journal
- [ ] Wait 24-48 hours before re-entry
- [ ] Look for better opportunities

---

## Support & Resources

### Related Documentation
- [BUY_SELL_LOGIC.md](BUY_SELL_LOGIC.md) - Signal generation logic
- [TRANSACTION_LOGIC.md](TRANSACTION_LOGIC.md) - Portfolio management rules
- [PORTFOLIO_UI.md](PORTFOLIO_UI.md) - Portfolio tracker guide

### Tools
- **Full Scanner**: `src/full_scanner.py`
- **Ticker Ranking**: `notebooks/ticker_ranking.ipynb`
- **Portfolio Analysis**: `notebooks/portfolio_analysis.ipynb`

### Questions?
Review the code in `src/full_scanner.py` for detailed implementation of:
- `calculate_buy_score()` - Buy scoring logic
- `calculate_sell_score()` - Sell scoring logic
- `create_best_trades_excel()` - Report generation
- `filter_buy_signals()` - Buy filtering
- `filter_sell_signals()` - Sell filtering

---

**Last Updated**: January 2026  
**Version**: 2.1

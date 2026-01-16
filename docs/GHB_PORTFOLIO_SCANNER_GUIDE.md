# GHB Portfolio Scanner - Complete Guide
**Last Updated:** January 16, 2026  
**Version:** 2.0 (Price-Based Staged Entry System)

---

## Table of Contents
1. [What is the GHB Portfolio Scanner?](#what-is-the-ghb-portfolio-scanner)
2. [Initial Setup Guide](#initial-setup-guide)
3. [Weekly Trading Schedule](#weekly-trading-schedule)
4. [GHB Signal System Explained](#ghb-signal-system-explained)
5. [Position Sizing Rules](#position-sizing-rules)
6. [Price-Based Staged Entry System](#price-based-staged-entry-system)
7. [Stock Universe](#stock-universe)
8. [Universe Health Monitoring](#universe-health-monitoring)
9. [How to Run the Scanner](#how-to-run-the-scanner)
10. [Interpreting the Results](#interpreting-the-results)
11. [Trading Rules & Discipline](#trading-rules--discipline)
12. [Configuration Reference](#configuration-reference)

---

## What is the GHB Portfolio Scanner?

The **GHB Portfolio Scanner** is a weekly momentum-based trading system that identifies buy, hold, and sell signals for a curated universe of AI/technology stocks. The system generates a professional PDF report every Friday after market close to guide your Monday trading decisions.

### Key Features
- **Weekly momentum signals** using Gold-Gray-Blue (GHB) state system
- **Price-based staged entry** for conviction positions (scale in as price enters target zones)
- **Custom position sizing** (TSLA 50%, NVDA 20%, others 7.5%)
- **Automated PDF reports** with actionable buy/sell recommendations
- **Portfolio tracking** with P&L and signal monitoring

### Performance
- **Backtest Period:** 2021-2025 (5 years)
- **CAGR:** 34.62%
- **Win Rate:** 36.1%
- **Average Trades:** 8 per year per position
- **Strategy:** Pure momentum (buy strength, sell weakness)

---

## Initial Setup Guide

### Setting Up Your Portfolio Configuration

Before running the scanner for the first time, you need to configure your portfolio settings. This includes your capital, position sizing strategy, custom allocations, and price targets.

#### Step 1: Locate the Configuration File

**File:** `data/portfolio_settings.json`

Open this file in VS Code or any text editor.

#### Step 2: Set Your Total Capital

Find the `starting_cash` field and set your total portfolio capital:

```json
{
    "starting_cash": 110000,
    ...
}
```

**Examples:**
- $50,000 portfolio: `"starting_cash": 50000`
- $250,000 portfolio: `"starting_cash": 250000`
- $1,000,000 portfolio: `"starting_cash": 1000000`

#### Step 3: Configure Default Position Size

Set the default allocation for stocks without custom sizing:

```json
{
    ...
    "position_size_pct": 7.5,
    "max_positions": 10,
    ...
}
```

**Common Configurations:**

| Portfolio Style | position_size_pct | max_positions | Description |
|----------------|-------------------|---------------|-------------|
| **Concentrated** | 10% | 10 | Can deploy 100% in 10 positions |
| **Balanced** | 7.5% | 10 | Some custom, mostly equal weight |
| **Diversified** | 5% | 15 | More positions, smaller sizes |

**Current Setup (Default):**
- `position_size_pct: 7.5` = Each non-custom stock gets 7.5%
- `max_positions: 10` = Maximum 10 holdings allowed

**Math Check:**
- Custom allocations (TSLA 50% + NVDA 20%) = 70%
- Remaining capacity = 30%
- At 7.5% each = 4 additional positions (30% ÷ 7.5%)
- Total positions = 2 custom + 4 default = 6 stocks ✅

#### Step 4: Set Custom Position Allocations (Optional but Recommended)

Use `position_allocations` to assign higher conviction percentages to specific stocks.

**Current Example:**
```json
{
    ...
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20
    },
    ...
}
```

**How to Add More Custom Allocations:**

Let's say you want to add PLTR at 15%:

```json
{
    ...
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20,
        "PLTR": 15
    },
    ...
}
```

**Rules:**
- Total custom allocations should leave room for other positions
- Make sure total ≤ 100% when fully deployed
- Remaining capacity = 100% - (sum of custom allocations)

**Example Capacity Calculation:**
- TSLA 50% + NVDA 20% + PLTR 15% = 85% custom
- Remaining = 15%
- At 7.5% default = 2 more positions (15% ÷ 7.5%)
- Total: 3 custom + 2 default = 5 positions

**Warning:** If custom allocations exceed 100%, the scanner will not be able to deploy all positions!

#### Step 5: Set Price Targets for Staged Entry (Optional)

Use `price_targets` to define ideal buy zones for stocks you want to scale into strategically.

**Current Example:**
```json
{
    ...
    "price_targets": {
        "TSLA": {
            "target_low": 400.0,
            "target_high": 411.0,
            "notes": "Q1 pullback expected, ideal entry zone $400-411"
        },
        "NVDA": {
            "target_low": 130.0,
            "target_high": 145.0,
            "notes": "Scale in on dips to $130s"
        }
    }
}
```

**How to Add Price Targets for Other Stocks:**

Let's say you want to set targets for AMD:

```json
{
    ...
    "price_targets": {
        "TSLA": {
            "target_low": 400.0,
            "target_high": 411.0,
            "notes": "Q1 pullback expected, ideal entry zone $400-411"
        },
        "NVDA": {
            "target_low": 130.0,
            "target_high": 145.0,
            "notes": "Scale in on dips to $130s"
        },
        "AMD": {
            "target_low": 140.0,
            "target_high": 155.0,
            "notes": "Buy zone around $140-155, avoid above $160"
        }
    }
}
```

**How Price Targets Work:**
- **Below target_low:** 50% initial fill (scale in on deeper dip)
- **In target zone:** 75% initial fill (optimal entry)
- **Above target_high:** 25% initial fill (wait for better price)

**When to Use Price Targets:**
- ✅ High conviction stocks you want to scale into carefully
- ✅ Stocks near key support/resistance levels
- ✅ When you expect pullback to specific price zone
- ❌ Don't set targets for all 12 stocks (too complex)
- ❌ Don't set targets if you're not sure about levels

**Stocks Without Targets:**
- Scanner defaults to 100% initial fill
- No staged entry, just normal position sizing

#### Step 6: Configure Conservative Mode (Optional)

```json
{
    ...
    "conservative_mode": true,
    ...
}
```

**What it does:**
- `true`: Scanner recommends lower deployment in bearish conditions
- `false`: Scanner always recommends full deployment if signals available

**Recommendation:** Leave at `true` for most users

#### Step 7: Save and Validate Your Configuration

**Before saving:**
1. Check JSON syntax (no missing commas, brackets)
2. Verify custom allocations don't exceed 100%
3. Ensure price targets have both target_low and target_high
4. Confirm starting_cash matches your actual capital

**Save the file** (Ctrl+S in VS Code)

**Validate by running scanner:**
- Open `notebooks/ghb_portfolio_scanner.ipynb`
- Run the first few cells
- Check console output for "Variable Position Sizing Enabled"
- Verify allocations display correctly

### Complete Configuration Example

Here's a fully configured `portfolio_settings.json` for a $110,000 portfolio with 3 custom allocations and price targets:

```json
{
    "starting_cash": 110000,
    "position_size_pct": 7.5,
    "max_positions": 10,
    "strategy_week": 1,
    "conservative_mode": true,
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20,
        "PLTR": 15
    },
    "price_targets": {
        "TSLA": {
            "target_low": 400.0,
            "target_high": 411.0,
            "notes": "Q1 pullback expected, ideal entry zone $400-411"
        },
        "NVDA": {
            "target_low": 130.0,
            "target_high": 145.0,
            "notes": "Scale in on dips to $130s"
        },
        "PLTR": {
            "target_low": 65.0,
            "target_high": 75.0,
            "notes": "Scale in around $65-75, avoid above $80"
        },
        "ALAB": {
            "target_low": null,
            "target_high": null
        },
        "AMD": {
            "target_low": null,
            "target_high": null
        },
        "ARM": {
            "target_low": null,
            "target_high": null
        },
        "ASML": {
            "target_low": null,
            "target_high": null
        },
        "AVGO": {
            "target_low": null,
            "target_high": null
        },
        "GOOG": {
            "target_low": null,
            "target_high": null
        },
        "MRVL": {
            "target_low": null,
            "target_high": null
        },
        "MU": {
            "target_low": null,
            "target_high": null
        },
        "TSM": {
            "target_low": null,
            "target_high": null
        }
    }
}
```

**This configuration means:**
- Total capital: $110,000
- TSLA: 50% ($55,000) with staged entry $400-411
- NVDA: 20% ($22,000) with staged entry $130-145
- PLTR: 15% ($16,500) with staged entry $65-75
- Remaining: 15% capacity for 2 more stocks at 7.5% each
- Others (ALAB, AMD, etc.): 7.5% each if P1 signal triggers

### Common Setup Scenarios

#### Scenario A: Equal Weight (Simple)
**Goal:** All stocks get same allocation

```json
{
    "starting_cash": 100000,
    "position_size_pct": 10,
    "max_positions": 10,
    "position_allocations": {},
    "price_targets": {}
}
```

**Result:** Each stock gets 10%, up to 10 positions

---

#### Scenario B: Two High Conviction (Current Setup)
**Goal:** Large TSLA + NVDA, others equal

```json
{
    "starting_cash": 110000,
    "position_size_pct": 7.5,
    "max_positions": 10,
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20
    }
}
```

**Result:** TSLA 50%, NVDA 20%, others 7.5% each

---

#### Scenario C: Top 3 Conviction with Price Targets
**Goal:** Three large positions with careful entry timing

```json
{
    "starting_cash": 200000,
    "position_size_pct": 5,
    "max_positions": 12,
    "position_allocations": {
        "TSLA": 30,
        "NVDA": 25,
        "PLTR": 20
    },
    "price_targets": {
        "TSLA": {"target_low": 400, "target_high": 411},
        "NVDA": {"target_low": 130, "target_high": 145},
        "PLTR": {"target_low": 65, "target_high": 75}
    }
}
```

**Result:** 
- 3 custom positions = 75% ($150,000)
- Remaining 25% ($50,000) for 5 more at 5% each
- All custom positions use staged entry

---

## Weekly Trading Schedule

### ⚠️ CRITICAL: Only Run Scanner on **FRIDAY after 4:00 PM ET**

GHB Strategy uses weekly closing prices. Running mid-week produces false signals.

### Your Weekly Routine

#### **FRIDAY (After 4:00 PM ET)**
**Time Required:** 10-15 minutes

1. Open `notebooks/ghb_portfolio_scanner.ipynb` in VS Code
2. Run all cells (Kernel → Run All)
3. Review generated PDF in `ghb_scanner_results/`
4. Note the action items:
   - **SELL signals** (N2 positions - urgent)
   - **BUY signals** (P1 opportunities - prioritize by quality)
   - **HOLD signals** (P2/N1 positions - do nothing)

#### **WEEKEND (Saturday/Sunday)**
**Time Required:** 15-30 minutes

1. Review the PDF report thoroughly
2. Calculate exact position sizes using current prices
3. Verify you have sufficient cash for buys
4. Set up limit orders in your brokerage:
   - **Sells:** Friday close × 0.99 (-1% for slippage)
   - **Buys:** Friday close × 1.015 (+1.5% for slippage)
5. Mentally prepare to execute Monday

#### **MONDAY (Market Open - 9:30 AM ET)**
**Time Required:** 15-30 minutes

**ORDER OF OPERATIONS:**
1. **9:30-10:00 AM - SELL FIRST** ⚠️
   - Execute ALL N2 sell signals immediately
   - Raises cash and prevents further losses
   - Use limit orders at Friday close × 0.99

2. **10:00-10:30 AM - BUY SECOND**
   - Enter new P1 buy positions
   - Be patient, wait for good fills
   - Prioritize by Entry Quality (Pullback Buy > Healthy Buy > Extended)
   - Use limit orders at Friday close × 1.015

3. **After 10:30 AM - Review & Confirm**
   - Verify all orders filled
   - Update `data/portfolio_positions.csv` if manually tracking

---

## GHB Signal System Explained

### The Four States

GHB categorizes stocks into 4 states based on price vs 200-day SMA (D200) and 4-week momentum (ROC):

#### **P1 (GOLD) - Strong Buy Signal** 🟡
- **Price:** Above D200
- **Momentum:** ROC > 5% OR distance from D200 > 10%
- **Action:** BUY (subject to entry quality filter)
- **Meaning:** Strong uptrend, positive momentum

#### **P2 (GRAY) - Hold Signal** ⚪
- **Price:** Above D200
- **Momentum:** ROC ≤ 5% AND distance ≤ 10%
- **Action:** HOLD
- **Meaning:** Consolidation above support, temporary pause

#### **N1 (GRAY) - Hold Signal** ⚪
- **Price:** Below D200 (but within 5%)
- **Momentum:** Shallow pullback
- **Action:** HOLD
- **Meaning:** Minor dip, could recover to P1

#### **N2 (BLUE) - Sell Signal** 🔵
- **Price:** More than 5% below D200
- **Momentum:** Weak/negative
- **Action:** SELL
- **Meaning:** Downtrend confirmed, exit required

### Entry Quality Filter (NEW)

Not all P1 signals are equal. The scanner categorizes P1 opportunities by entry quality:

#### **🔥 PULLBACK BUY** (Priority #1)
- **Criteria:** P1 state BUT negative 4-week ROC
- **Meaning:** Dip-buying opportunity in uptrend
- **Action:** Highest priority buy
- **Example:** Stock pulled back 5% but still above D200

#### **✅ HEALTHY BUY** (Priority #2)
- **Criteria:** RSI < 70 AND distance from D200 < 30%
- **Meaning:** Ideal entry zone, not overextended
- **Action:** Full position size recommended

#### **⚠️ EXTENDED BUY** (Priority #3)
- **Criteria:** RSI 70-80 OR distance 30-40%
- **Meaning:** Running hot, higher risk
- **Action:** Consider 50% position or wait for pullback

#### **🚨 OVERHEATED** (Avoid)
- **Criteria:** RSI > 80 AND distance > 40%
- **Meaning:** Parabolic, high reversal risk
- **Action:** Skip or wait for consolidation

---

## Position Sizing Rules

### Portfolio Configuration
**Total Capital:** $110,000 (configurable in `portfolio_settings.json`)

### Custom Allocations (Conviction Positions)

| Ticker | Allocation | Position Value | Rationale |
|--------|-----------|----------------|-----------|
| **TSLA** | 50% | $55,000 | Core conviction - AI/autonomy thesis |
| **NVDA** | 20% | $22,000 | AI infrastructure leader |
| **Others** | 7.5% each | $8,250 | Diversification |

### Allocation Math

**Remaining Capacity After Custom Allocations:**
- TSLA + NVDA = 70% ($77,000)
- Remaining = 30% ($33,000)
- At 7.5% per position = 4 additional positions possible
- **Max Portfolio:** TSLA + NVDA + 4 others = 6 stocks (within 10 max)

### Position Size Calculation

For **custom allocations** (TSLA, NVDA):
```
Position Value = Total Capital × Allocation %
Example: TSLA = $110,000 × 50% = $55,000
```

For **default allocations** (all others):
```
Position Value = Total Capital × 7.5%
Example: AMD = $110,000 × 7.5% = $8,250
```

### Share Calculation
```
Shares = Position Value ÷ Current Price
Example: TSLA at $445 → 55,000 ÷ 445 = 123 shares
```

---

## Price-Based Staged Entry System

### Overview

For stocks with **price targets** (currently TSLA and NVDA), the scanner uses a staged entry approach to scale into positions as price enters target zones.

### Price Targets (Current)

#### TSLA - Target Zone: $400-$411
- **Thesis:** Q1 pullback expected, ideal entry in low $400s
- **Strategy:** Scale in aggressively at target prices

#### NVDA - Target Zone: $130-$145
- **Thesis:** Scale in on dips to $130s
- **Strategy:** Add on weakness in target range

### Initial Fill Percentage Rules

The scanner automatically calculates initial position size based on **price vs target zone**:

| Price Location | Initial Fill % | Rationale |
|---------------|---------------|-----------|
| **Below Target Low** | 50% | Very aggressive - scale in deeper on dip |
| **In Target Zone** | 75% | Optimal entry - large position |
| **Above Target High** | 25% | Conservative - wait for better entry |

### Example: TSLA at Different Prices

**Scenario 1: TSLA at $390 (Below $400 target)**
- Initial Fill: 50% of $55,000 = $27,500
- Reasoning: Great price, but scale in gradually
- Add-on trigger: If rebounds into $400-411 zone

**Scenario 2: TSLA at $405 (In $400-$411 zone)** ✅ IDEAL
- Initial Fill: 75% of $55,000 = $41,250
- Reasoning: In sweet spot, take large position
- Add-on trigger: If dips below $400 or confirms strength

**Scenario 3: TSLA at $450 (Above $411)**
- Initial Fill: 25% of $55,000 = $13,750
- Reasoning: Too expensive, small toe-hold
- Add-on trigger: If pulls back into $400-411 zone

### Add-On Opportunities

The scanner continuously monitors positions for add-on signals:

**Add-On Triggers:**
- Position currently at 25% or 50% fill
- Price dips into target zone (from above)
- Price breaks below target zone (deeper dip opportunity)

**Add-On Amounts:**
- 25% increment (to reach 75% or 100%)
- 50% increment (to reach 100% from 50%)

---

## Stock Universe

### Current Universe: 12 AI/Technology Stocks

**Investment Thesis:** AI infrastructure buildout 2023-2032

| Ticker | Company | Category | Role in AI |
|--------|---------|----------|------------|
| **ALAB** | Astera Labs | Connectivity | AI data center connectivity |
| **AMD** | Advanced Micro Devices | Chips | AI processors, NVIDIA competitor |
| **ARM** | ARM Holdings | Chips | Mobile/edge AI architecture |
| **ASML** | ASML | Equipment | Chip manufacturing equipment |
| **AVGO** | Broadcom | Infrastructure | AI networking/infrastructure |
| **GOOG** | Google | Cloud/AI | AI models, cloud infrastructure |
| **MRVL** | Marvell | Infrastructure | Data infrastructure/storage |
| **MU** | Micron | Memory | AI memory/storage chips |
| **NVDA** | NVIDIA | Chips | AI GPU leader (best performer) |
| **PLTR** | Palantir | Software | AI/ML software platforms |
| **TSLA** | Tesla | Autonomy | AI-powered autonomy/robotics |
| **TSM** | Taiwan Semi | Manufacturing | AI chip fabrication |

### Universe Selection Criteria

**Volatility Requirements** (must meet ONE):
- Standard Deviation ≥ 30%
- Max Win ≥ 150%
- Average Win ≥ 40%

**Why Volatile Stocks?**
- Momentum strategies thrive on volatility
- Backtest showed +601% avg returns on volatile stocks
- Low volatility stocks averaged -162% (losses)

### Universe Reoptimization

**Frequency:** Quarterly (every 13 weeks) or when alerts trigger  
**Purpose:** Ensure you're trading the best momentum stocks available

The scanner includes **automated health monitoring** that alerts you when universe refresh is needed.

#### When to Reoptimize

**Triggered by Scanner Alerts:**
- 🔴 **Critical:** >30% of universe in N2 state (immediate action required)
- 🟡 **Warning:** >20% in N2 or stale universe (>6 months)
- 🟡 **Warning:** Low opportunity (<20% in P1 signals)
- 🟡 **Warning:** Performance lag >10% below expected

**Scheduled Maintenance:**
- **Quarterly Review:** Every 13 weeks (automatic counter in scanner)
- **Annual Full Refresh:** January each year (mandatory)

#### Quick Reoptimization Process

**Use the Automated Notebook (Recommended):**
1. Open `notebooks/universe_reoptimization.ipynb`
2. Run all cells (10-15 minutes)
3. Review side-by-side comparison
4. Copy/paste generated code if approved

**The notebook automatically:**
- Screens full S&P 500 (~500 stocks)
- Identifies top candidates by CAGR
- Compares new vs current universe
- Shows which stocks to keep/add/drop
- Generates ready-to-paste code updates
- Saves timestamped analysis report

**Files to Update:**
1. `notebooks/ghb_portfolio_scanner.ipynb` - Update `GHB_UNIVERSE` list
2. `data/ghb_optimized_portfolio.txt` - Update stock list (alphabetical)

#### Transition Strategies

**Option A - Hybrid (Recommended):**
- Exit removed stocks that are P2/N1/N2 (weak)
- Keep removed stocks that are P1 until N2 exit
- Prioritize entering new universe stocks
- Complete transition over 2-4 weeks

**Option B - Gradual (Conservative):**
- Keep all existing positions until N2
- Only enter new positions from updated universe
- Complete transition over 4-8 weeks

**Option C - Immediate (Aggressive):**
- Sell all stocks not in new universe Monday 9:30am
- Enter new P1 signals same day
- Complete transition in 1 week

---
Universe Health Monitoring

### Automated Alert System

The scanner continuously monitors 4 key health metrics and generates alerts in the PDF report when action is needed.

### Alert Levels

#### ✅ GREEN - Healthy
- No action needed
- Universe performing as expected
- Continue weekly trading normally

#### 🟡 YELLOW - Warning
- Re-optimization recommended within 1-2 months
- Plan screening but not urgent
- Monitor conditions weekly

#### 🔴 RED - Critical
- Re-optimization REQUIRED before next trade
- Do not ignore
- Action needed immediately

### Monitored Conditions

#### 1. Universe Degradation
**Metric:** Percentage of stocks in N2 (SELL) state

**Thresholds:**
- 🟡 Warning: >20% in N2
- 🔴 Critical: >30% in N2

**Why it matters:** Too many weak stocks indicates universe selection may be broken

**Actions:**
- Check if market-wide correction or stock-specific weakness
- If market-wide: Wait for recovery
- If stock-specific: Re-screen S&P 500 immediately

**Example Alert:**
```
🔴 CRITICAL: 35% of universe in N2 state (7/12 stocks)
Action: Re-screen S&P 500 for new candidates
```

#### 2. Performance Lag
**Metric:** Portfolio return vs expected (based on backtest CAGR)

**Thresholds:**
- 🟡 Warning: >10% below expected (after 12+ weeks)

**Why it matters:** Persistent underperformance suggests wrong stocks selected

**Actions:**
- Review which stocks are dragging performance
- Consider replacing worst performers
- Re-screen if gap persists 2+ months

**Example Alert:**
```
🟡 WARNING: Performance -12.5% below expected
Expected: +15.2% | Actual: +2.7% | Gap: -12.5%
Action: Review underperforming holdings
```

**Note:** Only triggers after 12+ weeks to avoid false alarms from normal volatility

#### 3. Low Opportunity Environment
**Metric:** Percentage of stocks showing P1 (BUY) signals

**Thresholds:**
- 🟡 Warning: <20% in P1
- Watch: <30% in P1

**Why it matters:** Few opportunities may indicate:
- Market rotation away from your sectors
- Universe too concentrated in declining sectors
- Bear market requiring defensive positioning

**Actions:**
- Check sector concentration
- Consider broader universe or different sectors
- May need to add defensive/value stocks

**Example Alert:**
```
🟡 WARNING: Only 8% of universe showing P1 signals (1/12 stocks)
Market may be rotating away from AI/tech
Action: Consider sector diversification
```

#### 4. Stale Universe
**Metric:** Time since last universe refresh

**Thresholds:**
- 🟡 Warning: >6 months (26 weeks) since last update
- 🔴 Critical: >12 months (52 weeks) since last update

**Why it matters:**
- Company fundamentals change over time
- New winners emerge (e.g., ALAB in 2024)
- Old winners fade (e.g., MRNA post-2021)

**Actions:**
- 6+ months: Plan re-screen within 4-8 weeks
- 12+ months: Execute re-screen immediately

**Example Alert:**
```
🟡 WARNING: Universe last updated 28 weeks ago
Action: Schedule re-optimization within next month
```

### How to Respond to Alerts

#### Single Alert (🟡 Yellow)
- **Action:** Note it, monitor weekly
- **Timeline:** Re-optimize within 1-2 months
- **Trading:** Continue normally

#### Multiple Alerts (🟡 Yellow)
- **Action:** Plan re-optimization soon
- **Timeline:** Re-optimize within 2-4 weeks
- **Trading:** Be more selective with entries

#### Any Critical Alert (🔴 Red)
- **Action:** Re-optimize immediately
- **Timeline:** This weekend or next
- **Trading:** Pause new entries until refresh complete

### Where to Find Alerts

**In PDF Report - Section: "Universe Health Alerts"**

Located after market sentiment section, before action items.

Shows:
- Alert severity (🔴/🟡/✅)
- Specific condition triggered
- Current metrics
- Recommended action

**Example:**
```
Universe Health Alerts

• 🟡 WARNING: 25% of universe in N2 state (3/12 stocks)
  Current: AMD, MU, ARM showing weakness
  Action: Monitor for further deterioration

• 🟡 WARNING: Universe age 30 weeks
  Action: Plan re-screen within 1 month
```

---

## 
## How to Run the Scanner

### Prerequisites

1. **Python Environment**
   - Python 3.8+ with virtual environment
   - Required packages: `pandas`, `yfinance`, `reportlab`

2. **VS Code Setup**
   - Jupyter extension installed
   - Python extension installed

3. **Configuration Files**
   - `data/portfolio_settings.json` - Portfolio settings
   - `data/portfolio_positions.csv` - Current holdings (optional)

### Step-by-Step Execution

#### 1. Open the Notebook
```
File: notebooks/ghb_portfolio_scanner.ipynb
```

#### 2. Verify It's Friday After 4 PM ET
The notebook has a warning at the top. **Do not run mid-week!**

#### 3. Run All Cells
- Click "Run All" or press `Ctrl+Shift+P` → "Run All Cells"
- Execution time: ~2-3 minutes

#### 4. Review Console Output
Monitor for:
- ✅ Data downloaded successfully
- ✅ Signals calculated
- ✅ PDF generated successfully

#### 5. Open the Generated PDF
```
Location: ghb_scanner_results/ghb_weekly_report_YYYYMMDD_HHMM.pdf
```

---

## Interpreting the Results

### PDF Report Structure

#### **Section 1: Market Sentiment**
- Overall universe health (% P1, P2, N1, N2)
- Bullish/Neutral/Bearish classification
- Portfolio deployment recommendation

#### **Section 2: Top Buy Candidates (P1 Signals)**
Organized by Entry Quality:

**PULLBACK BUY:** (Highest priority)
- Stocks showing strength but pulling back
- Example: `• TSLA (50%), 75% partial fill (In zone $400-$411), 31 shares @ $445.15 = $13,800`

**HEALTHY BUY:** (Good entries)
- RSI healthy, not overextended
- Example: `• NVDA (20%), 25% partial fill (Above target $145), 29 shares @ $189.86 = $5,506`

**EXTENDED BUY:** (Proceed with caution)
- Already had a big run, consider smaller size

#### **Section 3: Action Items for Monday**

**1. SELL Signals**
- Lists N2 positions to exit
- Shows current P&L on each position

**2. BUY Signals**
- Grouped by quality (Pullback Buy / Healthy Buy / Extended Buy)
- Shows allocation, fill %, target zone info, shares, and cost
- Total capital to deploy

**3. MONITOR Signals**
- Existing positions in P1/P2/N1 (healthy holds)

#### **Section 4: Current Portfolio Holdings**
- All positions with entry price, current price, P&L
- Total portfolio value and deployment %
- Cash remaining

#### **Section 5: P2/N1 Signals (Hold)**
- Stocks in consolidation or shallow pullback
- Monitor for upgrade to P1 or downgrade to N2

#### **Section 6: N2 Signals (Sell)**
- Stocks in downtrend
- Sell if you own them

---

## Trading Rules & Discipline

### Mandatory Rules

#### **Rule 1: Only Trade on Fridays/Mondays**
- **Scanner:** Friday after 4 PM ET only
- **Execution:** Monday market hours only
- **Why:** Weekly strategy requires weekly discipline

#### **Rule 2: Sell Before You Buy**
- Always execute N2 sells first (9:30-10:00 AM)
- Then execute P1 buys (10:00-10:30 AM)
- **Why:** Risk management and cash availability

#### **Rule 3: Follow Entry Quality Priority**
1. Pullback Buys (highest priority)
2. Healthy Buys (full size)
3. Extended Buys (reduced size or skip)
4. Overheated (skip entirely)

#### **Rule 4: Respect Position Limits**
- **Max positions:** 10
- **Custom allocations:** TSLA 50%, NVDA 20%
- **Default allocation:** 7.5% for others
- **Never exceed:** 100% portfolio deployment

#### **Rule 5: Honor Staged Entry Rules**
- Follow initial fill % based on price vs target
- Wait for add-on triggers before scaling in
- Don't rush to 100% fill immediately

### Exit Discipline

#### **When to Sell (N2 Signal Appears)**
- Price > 5% below D200
- Weak momentum confirmed
- **Action:** Sell 100% of position Monday morning

#### **When NOT to Sell**
- P2 state (consolidation) - this is normal
- N1 state (shallow dip) - could bounce back
- Minor RSI overbought (not an exit signal)

#### **Why Exit Discipline Matters**
- Average holding: 45.8 weeks (~1 year)
- Winners average +74% gains
- Premature exit = missed gains

### Position Management

#### **When to Add to Positions**
- Scanner shows add-on opportunity
- Price enters target zone from above
- Signal upgrades (P2 → P1, N1 → P1)

#### **When to Trim Positions**
- **Never trim on GHB strategy**
- Let winners run until N2 appears
- Momentum strategies need time to develop

---

## Configuration Reference

### File: `data/portfolio_settings.json`

```json
{
    "starting_cash": 110000,
    "position_size_pct": 7.5,
    "max_positions": 10,
    "strategy_week": 1,
    "conservative_mode": true,
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20
    },
    "price_targets": {
        "TSLA": {
            "target_low": 400.0,
            "target_high": 411.0,
            "notes": "Q1 pullback expected, ideal entry zone $400-411"
        },
        "NVDA": {
            "target_low": 130.0,
            "target_high": 145.0,
            "notes": "Scale in on dips to $130s"
        }
    }
}
```

### Configuration Fields Explained

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `starting_cash` | Number | Total portfolio capital | 110000 |
| `position_size_pct` | Number | Default allocation for non-custom positions | 7.5 |
| `max_positions` | Number | Maximum holdings allowed | 10 |
| `strategy_week` | Number | Reoptimization counter (internal) | 1 |
| `conservative_mode` | Boolean | Conservative deployment logic | true |
| `position_allocations` | Object | Custom allocations per ticker | `{"TSLA": 50}` |
| `price_targets` | Object | Price-based staging targets | See above |

### Editing Configuration

1. Open `data/portfolio_settings.json` in VS Code
2. Modify values as needed
3. Save file
4. Re-run scanner to apply changes

**Common Changes:**
- Adjust `starting_cash` for different capital levels
- Change `position_allocations` for different conviction levels
- Update `price_targets` for new entry zones
- Modify `max_positions` for portfolio concentration

---

## Troubleshooting

### Scanner Won't Run
**Error:** Kernel not connected  
**Solution:** Select Python environment in VS Code (Ctrl+Shift+P → "Select Interpreter")

### Data Download Fails
**Error:** Yahoo Finance timeout  
**Solution:** Check internet connection, wait 5 minutes, retry

### PDF Generation Error
**Error:** reportlab import error  
**Solution:** Install missing package: `pip install reportlab`

### Signals Look Wrong
**Error:** Getting mid-week signals  
**Solution:** Only run Friday after 4 PM ET. Mid-week data is incomplete.

---

## Quick Reference Card

### Weekly Checklist
- [ ] Friday 4 PM ET: Run scanner
- [ ] Friday evening: Review PDF report
- [ ] Weekend: Plan trades, set up limit orders
- [ ] Monday 9:30 AM: Execute sells first
- [ ] Monday 10:00 AM: Execute buys second
- [ ] Monday after trades: Update positions CSV (if tracking manually)

### Signal Quick Reference
- **P1 (GOLD)** → Buy (if entry quality good)
- **P2 (GRAY)** → Hold (consolidation)
- **N1 (GRAY)** → Hold (shallow dip)
- **N2 (BLUE)** → Sell immediately

### Entry Quality Priority
1. 🔥 Pullback Buy (best)
2. ✅ Healthy Buy (good)
3. ⚠️ Extended Buy (caution)
4. 🚨 Overheated (avoid)

### Position Sizing Cheat Sheet
- TSLA: 50% = $55,000
- NVDA: 20% = $22,000
- Others: 7.5% = $8,250
- Max positions: 10

---

## Version History

### Version 2.0 (January 16, 2026)
- ✅ Price-based staged entry system
- ✅ Custom position allocations (TSLA 50%, NVDA 20%)
- ✅ Entry quality categorization
- ✅ PDF report with grouped buy recommendations
- ✅ Add-on opportunity detection

### Version 1.0 (January 2026)
- Initial release
- Basic GHB signal generation
- Equal allocation (10% per position)
- Simple PDF reports

---

## Support & Documentation

### Related Files
- **Notebook:** `notebooks/ghb_portfolio_scanner.ipynb`
- **Settings:** `data/portfolio_settings.json`
- **Positions:** `data/portfolio_positions.csv`
- **Results:** `ghb_scanner_results/` (PDF reports)

### Additional Guides (Archived)
- `docs/archive_backtest/` - Historical backtest documentation
- `docs/archive/` - Outdated strategy guides

### Questions?
Review this guide thoroughly. All trading rules, position sizing, and signal interpretation are documented above.

---

**Last Updated:** January 16, 2026  
**Document Status:** Active (Master Reference)

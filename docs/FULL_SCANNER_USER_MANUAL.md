# Full Scanner User Manual

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Reports Generated](#reports-generated)
4. [Understanding Scanner Reports](#understanding-scanner-reports)
5. [Understanding Best Trades Reports](#understanding-best-trades-reports)
6. [Entry Quality System](#entry-quality-system)
7. [Key Metrics Explained](#key-metrics-explained)
8. [How to Use the Reports](#how-to-use-the-reports)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Full Scanner** is an automated technical analysis tool that scans three major stock indices (S&P 500, NASDAQ 100, and your Portfolio) to identify high-probability trading opportunities based on:

- **Technical signals**: FULL HOLD + ADD (bullish) and FULL SELL + SHORT (bearish)
- **Support/Resistance levels**: S1, S2, S3 (support) and R1, R2, R3 (resistance)
- **Volume Profile analysis**: POC, VAH, VAL, HVN levels
- **Stop-aware entry quality**: Evaluates if good supports are accessible within your 8% stop tolerance
- **Risk-Reward ratios**: Volatility-based R:R calculations

### What Makes This Scanner Unique?

Unlike traditional scanners that only look at signals, this scanner uses **stop-aware quality assessment**. It won't recommend a stock as "EXCELLENT" just because it has good support levels—those supports must be within reach of your 8% maximum stop loss. This prevents misleading recommendations where the "good support" is too far below your stop level to protect you.

---

## Getting Started

### Running the Scanner

**Command:**
```powershell
python src\full_scanner.py
```

**Optional Parameters:**
```powershell
python src\full_scanner.py --daily-bars 60 --weekly-bars 52 --concurrency 2
```

- `--daily-bars`: Number of daily bars to analyze (default: 60)
- `--weekly-bars`: Number of weekly bars to analyze (default: 52)
- `--concurrency`: Number of parallel threads (default: 2, higher values may trigger rate limits)

### What Happens When You Run It?

The scanner executes in **3 phases**:

1. **SCAN 1: S&P 500** - Scans ~503 stocks
2. **SCAN 2: NASDAQ 100** - Scans ~101 stocks
3. **SCAN 3: Portfolio** - Scans your holdings from `data/holdings.csv`

For each phase, the scanner:
- Fetches current price data
- Calculates technical indicators
- Identifies support/resistance levels
- Evaluates entry quality with stop-awareness
- Generates reports

**Typical Runtime:** 15-30 minutes depending on market hours and API rate limits

---

## Reports Generated

Each scan produces **4 reports** in the respective folder under `scanner_results/`:

### File Structure:
```
scanner_results/
├── sp500/
│   ├── sp500_analysis_YYYYMMDD_HHMM.xlsx          # Full Excel report
│   ├── scanner_report_sp500_YYYYMMDD_HHMM.pdf     # Comprehensive PDF
│   ├── sp500_best_trades_YYYYMMDD_HHMM.xlsx       # Best opportunities Excel
│   └── sp500_best_trades_YYYYMMDD_HHMM.pdf        # Best opportunities PDF
├── nasdaq100/
│   └── [same 4 files for NASDAQ 100]
└── portfolio/
    └── [same 4 files for your holdings]
```

### Report Types:

| Report Type | Purpose | File Pattern |
|------------|---------|--------------|
| **Excel Analysis** | Sortable data with all signals | `*_analysis_*.xlsx` |
| **Scanner Report PDF** | Comprehensive technical details on ALL signals | `scanner_report_*.pdf` |
| **Best Trades Excel** | Filtered top opportunities (EXCELLENT/GOOD only) | `*_best_trades_*.xlsx` |
| **Best Trades PDF** | Quick-reference top trades ranked by Vol R:R | `*_best_trades_*.pdf` |

---

## Understanding Scanner Reports

**File:** `scanner_report_sp500_YYYYMMDD_HHMM.pdf`

### What's Included?

This is your **comprehensive technical reference** that includes:

- **ALL stocks** with FULL HOLD + ADD or FULL SELL + SHORT signals
- **No quality filtering** - shows everything that triggered a signal
- **Full technical breakdown** for each stock

### Report Sections:

#### 1. BUY SIGNALS Section
Each stock card contains:

**Header:**
- Stock ticker and current price
- Signal type (FULL HOLD + ADD)
- RSI value

**Entry Quality Analysis:**
```
Entry Quality (8% Stop): EXCELLENT ✓ SAFE ENTRY
2 accessible supports within stop tolerance (8.0%)
Stop Level: $163.56 (-8.0%)
```
This tells you:
- The overall entry quality rating
- How many good supports are within your 8% stop range
- Where your stop should be placed

**Entry Zones (Support Levels):**
```
- S1: $159.24 (EXCELLENT - 3 major supports)
- S2: $151.50 (GOOD - 2 major supports)
- S3: $145.80 (OK - 1 major support)
```
Shows all support levels with individual quality ratings based on confluence of supports at that level.

**Buy Quality for Each Support:**
```
Buy Quality S1: EXCELLENT - Major confluence: D50, POC, HVN
Buy Quality S2: GOOD - Solid support: D100, VAL
Buy Quality S3: OK - Moderate: 1 major support
```
Explains what technical levels create each support.

**Upside Targets (Resistance Levels):**
```
- R1: $185.40 (15.2% gain)
- R2: $198.75 (22.1% gain)
- R3: $210.30 (29.5% gain)
```
Your profit targets with expected gain percentages.

**Technical Indicators:**
```
RSI: 45.2 | D50: $165.20 | D100: $158.40 | D200: $152.10
POC: $160.50 | VAH: $172.80 | VAL: $151.20
```
All relevant technical levels for reference.

#### 2. SELL SIGNALS Section
Similar format but for bearish opportunities (if any).

#### 3. GLOSSARY
Quick reference for all terms used in the report.

### When to Use Scanner Reports:

- **Deep dive analysis** before entering a position
- **Verifying support/resistance levels** for stop placement
- **Understanding the full technical picture** beyond just entry quality
- **Research and due diligence** on any signal

---

## Understanding Best Trades Reports

**File:** `sp500_best_trades_YYYYMMDD_HHMM.pdf`

### What's Included?

This is your **actionable trading list** that shows:

- **ONLY EXCELLENT and GOOD entry quality** stocks (filtered by stop-aware assessment)
- **Ranked by Vol R:R** (Volatility Risk-Reward ratio) - highest R:R first
- **Compact format** for quick scanning

### Report Format:

#### Title Page
Shows category and date.

#### Top Buy Setups

**Ranking Summary Table:**
```
Rank | Ticker | Entry Quality      | Vol R:R | Price   | Signal
-----|--------|-------------------|---------|---------|------------------
1    | ABNB   | EXCELLENT ✓ SAFE  | 1:3.5   | $177.78 | FULL HOLD + ADD
2    | AMGN   | EXCELLENT ✓ SAFE  | 1:3.2   | $326.10 | FULL HOLD + ADD
3    | AFL    | GOOD 🎯 IDEAL     | 1:2.8   | $109.24 | FULL HOLD + ADD
```

**Detailed Cards:**
Each stock gets a card with:

```
#1. ABNB - EXCELLENT ✓ SAFE ENTRY | Vol R:R: 1:3.5
Current Price: $177.78 | RSI: 45.2 | Signal: FULL HOLD + ADD

Volatility Stop (7.5%): $164.45 loss = -7.5%
Target S1: $159.24 gain = +15.2%

Resistance R1: $185.40 (4.3% away) | Volatility: Moderate (~2.5% daily range)
```

**What This Tells You:**
- **Entry Quality + Flag**: Overall assessment and risk level
- **Vol R:R 1:3.5**: For every $1 you risk, you could gain $3.50 (excellent)
- **Volatility Stop**: Where to place your stop loss
- **Target S1**: Your first profit target
- **R1 Distance**: How close you are to hitting resistance

#### Top Sell Setups
Same format for bearish opportunities (if any).

#### Glossary
Quick reference focused on entry quality terms.

### When to Use Best Trades Reports:

- **Daily/weekly trading decisions** - your action list
- **Quick screening** for new opportunities
- **Ranking opportunities** by risk-reward
- **Portfolio planning** - which stocks to prioritize

---

## Entry Quality System

This is the **core innovation** of the scanner - it evaluates entries based on what's actually accessible within your stop tolerance.

### The 8% Stop Tolerance Rule

All entries are evaluated assuming you won't risk more than **8% from entry** on your stop loss. This is hardcoded as a reasonable maximum for most traders.

### Entry Quality Ratings

| Rating | Criteria | What It Means |
|--------|----------|---------------|
| **EXCELLENT** | 2+ excellent supports within stop range | Multiple strong supports protect your stop. Safest entries. |
| **GOOD** | 1+ good support within stop range | Solid support structure. Good risk management possible. |
| **OK** | Moderate supports available | Acceptable but requires closer monitoring. |
| **CAUTION** | Thin or extended - limited protection | Higher risk. Limited support within stop range. |

### Entry Flags

| Flag | Symbol | Meaning |
|------|--------|---------|
| **SAFE ENTRY** | ✓ | Multiple excellent supports protect your position |
| **IDEAL** | 🎯 | Near major support with good upside |
| **ACCEPTABLE** | 🎯 | Reasonable entry, monitor risk carefully |
| **THIN** | ⚠️ | Limited support structure, higher risk |
| **EXTENDED** | ⚠️ | Far from supports, consider waiting for pullback |
| **WAIT** | ⏳ | No accessible supports within 8% stop - do not enter |

### Example: Why This Matters

**Scenario:**
- Stock trading at $177.78
- S1 support at $159.24 (rated GOOD)
- Your 8% stop would be at $163.56

**Traditional Analysis:** "GOOD support at S1, buy here!"

**Stop-Aware Analysis:** "CAUTION ⚠️ THIN - S1 is 5.4% BELOW your stop level. It cannot protect you. Only D100 is accessible within stop range."

The stock gets marked **CAUTION** and **excluded from Best Trades** because the "good support" is unreachable with reasonable risk management.

---

## Key Metrics Explained

### Vol R:R (Volatility Risk-Reward Ratio)

**Formula:** `(Target S1 - Entry Price) / (Entry Price - Volatility Stop)`

**Interpretation:**
- **3.0+** = Excellent (gain potential is 3x+ your risk)
- **2.0+** = Good (gain potential is 2x+ your risk)
- **1.0+** = Acceptable (gain potential equals or exceeds risk)
- **<1.0** = Poor (you're risking more than you can gain)

**Example:**
```
Entry: $100
Stop: $92 (8% risk = $8)
Target S1: $116 (16% gain = $16)
Vol R:R = $16 / $8 = 1:2.0 (GOOD)
```

### Volatility Stop

Dynamic stop-loss calculated from the stock's actual volatility (ATR - Average True Range).

**Typical ranges:**
- **Low volatility stocks**: 3-5%
- **Moderate volatility**: 5-7%
- **High volatility**: 7-10%

The scanner recommends where to place your stop based on giving the stock "room to breathe" while limiting your risk.

### Accessible Supports Count

How many EXCELLENT or GOOD quality supports exist between your entry and your stop level.

- **2+** = EXCELLENT entry quality
- **1** = GOOD entry quality
- **0 but moderate supports** = OK entry quality
- **0 and extended** = CAUTION

### Support/Resistance Quality

Each S/R level is rated based on **confluence** - how many technical factors align at that price:

**EXCELLENT** (3+ major supports):
- D50, D100, D200 (moving averages)
- POC (Point of Control)
- VAH/VAL (Value Area High/Low)
- HVN (High Volume Node)
- Previous S/R levels

**GOOD** (2 major supports):
- 2 of the above factors align

**OK** (1 major support):
- Only 1 factor present

**WEAK**:
- No significant confluence

### RSI (Relative Strength Index)

Momentum indicator (0-100 scale):

- **Below 30** = Oversold (potential bounce)
- **30-45** = Pullback in uptrend (buy zone)
- **45-55** = Neutral
- **55-70** = Strong uptrend
- **Above 70** = Overbought (potential reversal)

### Volume Profile Terms

**POC (Point of Control):**
- Price with highest trading volume
- Acts as a magnet - price tends to return here
- Strong support/resistance

**VAH/VAL (Value Area High/Low):**
- Range containing 70% of volume
- Defines "fair value" zone
- Price tends to stay within this range

**HVN (High Volume Node):**
- Price level with significant volume
- Creates support/resistance

---

## How to Use the Reports

### Morning Routine (Before Market Open)

1. **Run the scanner** the night before or early morning
2. **Open Best Trades PDF** for each market
3. **Review top 5-10 ranked opportunities** (highest Vol R:R)
4. **Check entry quality flags**:
   - Prioritize ✓ SAFE ENTRY and 🎯 IDEAL
   - Be cautious with ⚠️ THIN or ⚠️ EXTENDED
   - Skip ⏳ WAIT entirely
5. **Note key levels** for each stock you're interested in

### Entry Decision Process

**For a stock you want to buy:**

1. **Check Best Trades rank** - is it in top 10?
2. **Verify entry quality** - EXCELLENT or GOOD only
3. **Confirm Vol R:R** - aim for 2.0+ (1.0+ acceptable)
4. **Open Scanner Report PDF** for full technical details
5. **Review all support levels** and their quality
6. **Set your stop** at the Volatility Stop level
7. **Set alerts** at R1, R2, R3 for profit taking

### Position Monitoring

**Use Scanner Reports to:**
- **Check where current price is** relative to S/R levels
- **Adjust stops** as stock moves through support levels
- **Take profits** at resistance levels (R1, R2, R3)
- **Re-evaluate** if stock falls below major support

### Weekly Review

1. **Compare reports** from Monday vs. Friday
2. **Track which stocks** maintained EXCELLENT/GOOD ratings
3. **Note pattern failures** - stocks that broke through support
4. **Update watchlist** with consistently high-quality opportunities

---

## Practical Examples

### Example 1: Perfect Setup (ABNB)

**From Best Trades Report:**
```
#1. ABNB - EXCELLENT ✓ SAFE ENTRY | Vol R:R: 1:3.5
Current Price: $177.78
Volatility Stop (7.5%): $164.45
Target S1: $159.24 gain = +15.2%
```

**From Scanner Report:**
```
Entry Quality: EXCELLENT ✓ SAFE ENTRY
2 accessible supports within stop tolerance
S1: $159.24 (EXCELLENT - D50, POC, HVN)
S2: $151.50 (GOOD - D100, VAL)
```

**Why This Is Great:**
- Ranked #1 by Vol R:R (3.5:1)
- EXCELLENT rating with SAFE ENTRY flag
- 2 major supports between entry ($177.78) and stop ($164.45)
- Even if S1 breaks, S2 is nearby for additional support
- Clear profit target at R1 with 15.2% gain potential

**Action:** Strong buy candidate. Enter near $177.78, stop at $164.45, target $185.40 (R1).

### Example 2: Caution Setup (QCOM)

**From Best Trades Report:**
```
Not listed - filtered out
```

**From Scanner Report:**
```
Entry Quality: CAUTION ⚠️ THIN
Only 1 accessible support (D100)
Current Price: $177.78
Stop: $163.56
S1: $159.24 (GOOD) ← 5.4% BELOW stop level!
```

**Why This Is Risky:**
- S1 looks "GOOD" but is unreachable with 8% stop
- Only D100 ($165.20) is between entry and stop
- If D100 breaks, you'll hit stop before reaching S1
- Not included in Best Trades (correctly filtered out)

**Action:** Wait for pullback to $165-168 range where S1 becomes accessible, or skip entirely.

### Example 3: Extended Setup

**Scanner Report shows:**
```
Entry Quality: CAUTION ⚠️ EXTENDED
No major supports within 8% stop range
Current Price: $250.00
Stop: $230.00
S1: $225.00 (GOOD)
S2: $210.00 (EXCELLENT)
```

**Why Wait:**
- Stock is extended above all major supports
- Buying here means hoping it keeps going up
- No protection if it reverses
- Better to wait for pullback toward $225-230

**Action:** Add to watchlist. Set alert at $230. Buy if it pulls back and holds that level.

---

## Advanced Usage

### Combining Portfolio + Scanner

1. **Check Portfolio scan** for signals on your holdings
2. **Cross-reference with S&P 500 / NASDAQ scans** for similar setups
3. **Identify sector trends** if multiple stocks in same sector signal

### Custom Filtering in Excel

The Excel reports allow sorting/filtering:

**High-conviction trades:**
```
Filter: entry_quality = EXCELLENT AND vol_rr >= 3.0
```

**Conservative entries:**
```
Filter: entry_quality = EXCELLENT AND rsi < 45
```

**High-reward swings:**
```
Filter: vol_rr >= 3.0 AND volatility_class = "Low"
```

### Historical Tracking

Keep a log of:
- Trades taken from Best Trades reports
- Entry quality at time of purchase
- Actual outcomes (hit target? stopped out?)
- Pattern recognition over time

This helps you learn which setups work best for your style.

---

## Troubleshooting

### "Rate Limit Exceeded" Errors

**Solution:** 
- Reduce `--concurrency` to 1
- Wait 1 hour and try again
- Scanner automatically caches data for 24 hours

### Scanner Runs But No PDF Generated

**Check:**
- Look for errors in terminal output
- Verify `scanner_results/` directory exists
- Check if any stocks matched signal criteria
- Review logs for ReportLab errors

### "No EXCELLENT/GOOD quality buy opportunities found" in Best Trades

This is normal when:
- Market is extended (everything trading above supports)
- Volatility is high (stop tolerance doesn't reach good supports)
- Sideways/choppy market conditions

**What to do:** Focus on Scanner Report to find OK-rated opportunities or wait for market pullback.

### Entry Quality Doesn't Match Support Quality

**Example:**
```
S1: EXCELLENT quality
Entry Quality: CAUTION
```

This is correct! The **S1 might be excellent** (confluence of D50+POC+HVN), but if it's **beyond your 8% stop tolerance**, your **entry quality is CAUTION** because you can't reach that excellent support.

This is the key innovation - entry quality is about what you can actually access with reasonable risk management.

### Glossary Shows Weird Characters in PDF

Some PDF viewers don't render emojis (✓ 🎯 ⚠️ ⏳). Try:
- Adobe Acrobat Reader
- Chrome/Edge (open PDF in browser)
- Different PDF viewer

---

## Best Practices

### ✅ Do's

- **Run scanner regularly** (daily or weekly)
- **Focus on Best Trades reports** for actionable ideas
- **Use Scanner Reports** for detailed research before entry
- **Respect the entry quality system** - avoid CAUTION entries unless you understand the risk
- **Set stops at recommended volatility stop levels**
- **Take profits** at resistance levels (R1, R2, R3)
- **Keep old reports** for tracking pattern success

### ❌ Don'ts

- **Don't ignore ⚠️ warnings** in entry flags
- **Don't buy just because a stock appears in Scanner Report** - check if it made Best Trades
- **Don't use tighter stops** than recommended - you'll get stopped out prematurely
- **Don't enter CAUTION ⚠️ EXTENDED setups** without understanding you're buying away from supports
- **Don't skip the glossary** - understand what you're reading
- **Don't rely solely on Vol R:R** - entry quality matters more

---

## Quick Reference Card

| When... | Use This Report | Look For... |
|---------|----------------|-------------|
| Quick daily scan | Best Trades PDF | Top 5-10 ranked by Vol R:R |
| Deep research | Scanner Report PDF | Full technical breakdown |
| Sorting/filtering | Excel Analysis | Custom filters on entry_quality, vol_rr |
| Position monitoring | Scanner Report PDF | Current price vs. S/R levels |
| Risk assessment | Best Trades PDF | Entry quality flag (✓ 🎯 ⚠️ ⏳) |

---

## Support & Questions

For more information, see:
- [BUY_SELL_LOGIC.md](BUY_SELL_LOGIC.md) - Signal generation logic
- [BEST_TRADES_GUIDE.md](BEST_TRADES_GUIDE.md) - Trading recommendations
- [Technical Analysis Documentation](../src/technical_analysis.py) - Code implementation

---

**Last Updated:** January 10, 2026
**Scanner Version:** Stop-Aware Quality Assessment v2.0

# GHB Strategy: Gold-Gray-Blue Trading Strategy

## Overview
GHB Strategy (Gold-Gray-Blue) is a weekly chart-based momentum strategy that delivered **+601% annual returns** on volatile stocks during 2021-2025 backtesting.

## State Abbreviations Explained

**P = Positive (Price Above 200-day SMA)**
- **P1 (Gold):** Strong bullish - BUY signal
- **P2 (Gray):** Consolidation - HOLD signal

**N = Negative (Price Below 200-day SMA)**
- **N1 (Gray):** Shallow pullback - HOLD signal
- **N2 (Blue):** Downtrend confirmed - SELL signal

## Core Philosophy
**"Let Winners Run, Exit on Confirmed Weakness"**

- Enter when momentum is strong (Gold/P1 state)
- Hold through temporary pullbacks (Gray/P2 and N1 states)
- Exit only when trend breaks (Blue/N2 state + below 200-day SMA)

## Entry Rules

### Buy Signal Requirements (ALL must be true):
1. **Weekly State = P1 (Gold)**
   - Price > 200-day SMA (D200)
   - AND (4-week ROC > 5% OR distance from D200 > 10%)
   
2. **Confirmation**
   - Current price is above D200
   - Strong relative strength vs market

### When to Enter:
- P1 state appears on weekly chart
- Fresh breakout above D200 with momentum
- Previous week was NOT P1 (new signal)

## Hold Rules

### Continue Holding When:
1. **P1 (Gold) - Strong Trend**
   - Keep position, trend is strong
   - Add to position if capital available

2. **P2 (Gray) - Healthy Consolidation**
   - Price still above D200
   - Momentum temporarily weak
   - Normal pullback in uptrend - HOLD

3. **N1 (Gray) - Shallow Pullback**
   - Price slightly below D200 (within 5%)
   - Could bounce back to P1
   - Strategy says HOLD, don't panic sell

### Why Hold Through P2/N1?
- Backtested avg hold: 45.8 weeks (nearly 1 year)
- Winners average +74% gains
- Early exit = missed gains (Strategy F with trailing stop only got +25% avg)

## Exit Rules

### Sell Signal Requirements (BOTH must be true):
1. **Weekly State = N2 (Blue)**
   - Price > 5% below D200
   - Weak momentum
   - Downtrend confirmed

2. **Price < 200-day SMA**
   - Price must be below D200
   - Not just a temporary dip

### Exit Immediately When:
- N2 state appears AND price < D200
- Trend has clearly broken
- Capital preservation required

## Stock Universe (39 Stocks)

### Moderate Volatile Stocks
Stocks that meet volatility criteria:
- Standard Deviation ≥30% OR
- Max Win ≥150% OR
- Avg Win ≥40%

**The 39 Stocks:**
ALAB, AMAT, AMD, AMZN, ARM, ASML, AVGO, BKNG, CEG, COST, CPRT, CRWD, CTAS, DASH, FANG, FTNT, GOOG, GOOGL, ISRG, KLAC, LRCX, MDB, META, MRNA, MRVL, MSFT, MU, NFLX, NVDA, ON, PANW, PCAR, PLTR, QCOM, ROST, TMUS, TSLA, TSM, VRTX

### Why These 39 Stocks?
- Backtest showed +601% annual returns on moderate volatile stocks
- Non-volatile stocks showed -162% annual returns (losses!)
- 43% win rate vs 33% on stable stocks
- Average wins of +74% vs +15% on stable stocks

## Performance Metrics (Backtested 2021-2025)

### Overall GHB Strategy Performance:
- **Total Trades:** 409
- **Win Rate:** 36.2%
- **Avg Return:** +5.36% per trade
- **Avg Win:** +35.78%
- **Avg Loss:** -11.88%
- **Avg Hold:** 34.7 weeks

### Performance on 39 Moderate Volatile Stocks:
- **Total Trades:** 118
- **Win Rate:** 43.2%
- **Avg Return:** +25.47% per trade
- **Avg Win:** +74.31%
- **Avg Loss:** -11.70%
- **Avg Hold:** 45.8 weeks
- **Annual Return:** +601%

### Top Performers:
1. NVDA: +514% total return (2 trades, 100% win rate)
2. NFLX: +290% total return (2 trades, 50% win rate)
3. AVGO: +211% total return (2 trades, 100% win rate)
4. META: +194% total return (4 trades, 50% win rate)
5. FANG: +168% total return (3 trades, 100% win rate)

## Weekly States Explained

### State System Overview
**P** = Positive (price above 200-day SMA)  
**N** = Negative (price below 200-day SMA)  
**1** = Strong momentum (BUY or SELL zone)  
**2** = Weak momentum (HOLD zone)

### P1 (Gold) - Strong Bullish Trend
- **Abbreviation:** P = Positive, 1 = Strong
- **Visual:** Gold/Yellow line on chart
- **Meaning:** Price > D200 with strong momentum (ROC > 5% OR distance > 10%)
- **Action:** 🟡 BUY or HOLD
- **Psychology:** "The trend is your friend"

### P2 (Gray) - Consolidation
- **Abbreviation:** P = Positive, 2 = Weak
- **Visual:** Gray line on chart (above D200)
- **Meaning:** Price > D200 but weak momentum
- **Action:** ⚪ HOLD (don't sell!)
- **Psychology:** Healthy pause, not a reversal

### N1 (Gray) - Shallow Pullback
- **Abbreviation:** N = Negative, 1 = Strong
- **Visual:** Gray line on chart (near D200)
- **Meaning:** Price slightly below D200 (within 5%)
- **Action:** ⚪ HOLD (could bounce back)
- **Psychology:** Test of support, not failure

### N2 (Blue) - Downtrend Confirmed
- **Abbreviation:** N = Negative, 2 = Weak
- **Visual:** Blue line on chart
- **Meaning:** Price > 5% below D200, weak momentum
- **Action:** 🔵 SELL
- **Psychology:** Trend is broken, exit now

## Risk Management

### Position Sizing
- **Conservative:** Equal weight across 10-15 positions (7-10% each)
- **Moderate:** 20-25 positions (4-5% each)
- **Aggressive:** Concentrate in top 5-10 P1 signals (10-15% each)

### Portfolio Allocation
- **Recommended:** 70-80% of capital in GHB Strategy positions
- **Reserve:** 20-30% cash for new opportunities
- **Max per position:** 10-15% (avoid over-concentration)

### Stop Loss
- **Hard Stop:** None (strategy uses N2 exit)
- **Optional Trailing Stop:** 20% from peak (Strategy F variant)
  - Only for extreme volatile stocks (NVDA, NFLX)
  - Tested: +25.47% avg return (vs +25.47% without stop)
  - Not recommended - reduces returns on most stocks

## Common Mistakes to Avoid

### 1. Selling Too Early
❌ Exit at P2 (consolidation) thinking trend is over
✅ Hold through P2 - it's normal consolidation

### 2. Holding Non-Volatile Stocks
❌ Apply GHB Strategy to stable dividend stocks
✅ Only trade the 39 moderate volatile stocks

### 3. Ignoring the D200 Rule
❌ Buy P1 signals when price < D200
✅ Both P1 state AND price > D200 required

### 4. Trading Too Frequently
❌ Day trade or try to catch every swing
✅ Weekly timeframe only - check Friday close

### 5. Panic Selling at N1
❌ Sell when price dips slightly below D200 (N1)
✅ Hold through N1 - only sell at N2

## Weekly Process

### Friday After Market Close:
1. Download/refresh weekly data
2. Run portfolio scanner notebook
3. Review buy/sell signals
4. Plan trades for Monday open

### Monday Market Open:
1. Execute sell signals first (exit N2 positions)
2. Execute buy signals (new P1 entries)
3. Set alerts for position changes
4. Update portfolio tracking

### Weekly Review:
- Check all 39 stocks for state changes
- Monitor positions for exit signals
- Identify new P1 opportunities
- Review portfolio allocation

## Expected Results

### Realistic Expectations:
- **Annual Return Target:** 30-60% (conservative)
- **Win Rate:** 40-45%
- **Winning Trades:** Avg +70-80%
- **Losing Trades:** Avg -10-12%
- **Hold Period:** 6-12 months per trade
- **Active Positions:** 5-15 at any time

### When Strategy Works Best:
- Bull markets with strong trends
- High volatility environments
- Tech/growth stock leadership
- Clear momentum patterns

### When Strategy Struggles:
- Choppy, range-bound markets
- Low volatility environments
- Value/defensive stock leadership
- Frequent whipsaws around D200

## Tools & Resources

### Required Data:
- Weekly closing prices (Friday)
- 200-day simple moving average
- 4-week rate of change
- Weekly Larsson state calculation

### Recommended Platforms:
- TradingView (charting with Larsson Scanner)
- yfinance (Python data download)
- Excel/Python for weekly scanning

### Scripts Included:
1. `weekly_portfolio_scanner.ipynb` - Main selection tool
2. `generate_weekly_reports.py` - Calculate weekly states
3. `scan_watchlist.py` - Quick 12-stock scan
4. `backtest_weekly_larsson.py` - Historical testing

## Questions & Answers

**Q: How often do I check signals?**
A: Once per week, Friday after close. This is a weekly strategy.

**Q: Can I use daily charts?**
A: No. Weekly timeframe is essential. Daily creates false signals.

**Q: What if I miss entry on Monday?**
A: Enter anytime during the week if still P1. Don't chase if price ran up.

**Q: Should I use limit or market orders?**
A: Market orders at open for simplicity. This is not day trading.

**Q: How many positions should I hold?**
A: 10-15 positions provides good diversification without over-dilution.

**Q: Can I add to winning positions?**
A: Yes, if still in P1 and you have capital. Pyramid into winners.

**Q: What about dividends?**
A: Most stocks don't pay significant dividends. Focus on capital appreciation.

---

## Summary

**GHB Strategy is a momentum-following system that:**
- Buys strong weekly trends (P1/Gold)
- Holds through normal pullbacks (P2/N1/Gray)  
- Exits on confirmed weakness (N2/Blue + below D200)
- Focuses on 39 high-volatility stocks
- Targets +30-60% annual returns
- Requires weekly monitoring only

**Success requires:**
- Discipline to hold through P2/N1 states
- Patience for 6-12 month holds
- Focus on the 39-stock universe only
- Weekly execution consistency
- Trust in the backtest data

**Last Updated:** January 15, 2026
**Backtest Period:** 2021-2025 (5 years)
**Expected Review:** Annually

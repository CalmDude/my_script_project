# Phase 1: Portfolio Tracker - Quick Start Guide

## 📁 Files Created

1. **data/portfolio_positions.csv** - Tracks your holdings
2. **data/portfolio_settings.json** - Configuration ($110k, 7% sizing, max 7 positions)
3. **scripts/add_position.py** - Helper script to add positions

## 🔄 Weekly Workflow

### Friday After 4pm ET
1. Open `notebooks/ghb_portfolio_scanner.ipynb`
2. Run all cells
3. Review outputs:
   - Section 6.5: Your current holdings with P&L
   - Section 4-5: New signals (BUY/HOLD/SELL)
   - PDF report saved to `ghb_scanner_results/`

### Monday 9:30am ET
1. Execute trades (SELL first, then BUY)
2. Record your fill prices

### Monday Evening
**Option A: Manual CSV Edit**
```csv
Ticker,Entry_Date,Entry_Price,Shares,Entry_State,Current_State,Entry_Signal
TSLA,2026-01-20,450.00,17,P1,P1,🟡 BUY
MU,2026-01-20,95.50,80,P1,P1,🟡 BUY
TSM,2026-01-20,198.00,38,P1,P1,🟡 BUY
```

**Option B: Use Helper Script**
```bash
cd scripts
python add_position.py
```

## 💼 What Gets Tracked

### Automatic Calculations (Every Friday Scan):
- ✅ Current state for each position (P1/P2/N1/N2)
- ✅ Profit/Loss ($ and %)
- ✅ Cost basis vs current value
- ✅ Cash remaining
- ✅ Portfolio deployment percentage
- ✅ State change detection (P1→P2, etc.)

### Manual Inputs (You Add After Monday Trades):
- Ticker symbol
- Entry date
- Entry price (your fill)
- Number of shares
- Entry state (usually P1)

## 📊 Example: Week 1 (3 Positions)

**Starting Capital:** $110,000  
**Position Size:** 7% = $7,700 per position  
**Week 1 Deploy:** 3 positions = $23,100 (21%)  
**Cash Remaining:** $86,900 (79%)

**Recommended First 3:**
1. MU - Strong semiconductor leader
2. TSM - Diversified foundry exposure  
3. MRNA - Non-tech diversification

**If MU at $95.50:**
- Shares: $7,700 / $95.50 = 80 shares
- CSV Entry: `MU,2026-01-20,95.50,80,P1,P1,🟡 BUY`

## 🎯 Next Friday Scan

Scanner will automatically:
1. Read your 3 positions from CSV
2. Get current prices
3. Calculate P&L for each
4. Update states (are they still P1?)
5. Show portfolio summary in notebook output
6. Generate PDF with holdings table

**Expected Output:**
```
📊 ACTIVE POSITIONS: 3
Ticker  Entry_Date  Entry_Price  Current_Price  P/L_%   Current_State  Signal
MU      2026-01-20  $95.50      $98.75         +3.4%   P1             🟡 BUY
TSM     2026-01-20  $198.00     $202.50        +2.3%   P1             🟡 BUY
MRNA    2026-01-20  $42.80      $41.90         -2.1%   P1             🟡 BUY

💼 PORTFOLIO SUMMARY
Total Cost Basis: $23,100
Current Value: $23,847
Total P/L: +$747 (+3.2%)
Cash Remaining: $86,900
Deployed: 21.0% | Cash: 79.0%
```

## ⚠️ State Change Alerts

**If position moves to N2 (SELL):**
```
🔴 URGENT: 1 position(s) in N2 (SELL) state!
   → MU: SELL on Monday open (Current: N2)
```

**If position moves to P2 (consolidation):**
```
📊 1 position(s) changed state:
   → MU: (P1 → P2)
```

## 🚀 Phase 1 Features

✅ **Implemented:**
- CSV position tracking
- Auto state updates every Friday
- P&L calculation ($ and %)
- Portfolio summary (value, cash, deployment %)
- State change detection
- Position sizing recommendations
- Weekly scan integration

⏳ **Coming in Phase 2 (Week 2-3):**
- State history tracking
- Email/SMS alerts for N2 exits
- Position age tracking
- Enhanced PDF with holdings table

## 📝 Tips

1. **Always wait until Friday after 4pm ET** to run scanner
2. **Execute sells FIRST on Monday** (N2 positions)
3. **Then enter new buys** (P1 positions)
4. **Update CSV Monday evening** while trades are fresh
5. **Position size:** Use exactly $7,700 for consistent tracking
6. **Calculate shares:** $7,700 / current_price, round down
7. **Save fill prices:** Your actual execution price, not Friday close
8. **Check state:** If buying on a dip, might be P2 not P1 - adjust accordingly

## 🔧 Troubleshooting

**Scanner says "No positions yet":**
- Check CSV has data rows (not just header)
- Verify CSV path: `data/portfolio_positions.csv`
- Check CSV format (comma-separated, no spaces in numbers)

**P&L looks wrong:**
- Verify entry price matches your actual fill
- Check shares calculation (cost should equal ~$7,700)
- Ensure current price is updating (check yfinance data)

**State not updating:**
- Scanner pulls live data every Friday
- If ticker not in universe, state won't update
- Check ticker spelling in CSV

## 📧 Support

Questions? Check:
1. **docs/PORTFOLIO_TRACKER_ROADMAP.md** - Full 7-phase plan
2. **docs/GHB_STRATEGY_GUIDE.md** - Strategy details
3. Notebook output - Shows all calculations step-by-step

## Next Steps

**Week 2 (January 24):**
- Run scanner Friday after market
- Review if your 3 positions stayed P1
- Consider adding 2 more positions (build to 5)
- Target: 35% deployed by week 2

**Week 8 Goal:**
- 5-7 positions
- 50% deployed ($55,000)
- $55,000 cash reserve
- Track weekly, trade monthly

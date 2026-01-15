# GHB Portfolio Tracker - Implementation Roadmap

## Vision: Option C - Full Portfolio Manager

Transform GHB Strategy from signal generator to complete portfolio management system.

**Goal:** Track positions, monitor state changes, calculate P&L, automate recommendations.

---

## Phase 1: Simple CSV Tracker ✅ CURRENT PHASE

**Timeline:** Week 1 (January 15-17, 2026)  
**Effort:** 2-3 hours  
**Status:** In Progress

### What We're Building

**File Structure:**
```
data/
  ├─ portfolio_positions.csv      # Current holdings
  └─ portfolio_settings.json      # Portfolio configuration
```

**portfolio_positions.csv columns:**
```csv
Ticker,Entry_Date,Entry_Price,Shares,Entry_State,Current_State,Entry_Signal
MU,2026-01-20,333.35,23,P1,P1,BUY
TSM,2026-01-20,327.11,24,P1,P1,BUY
MRNA,2026-01-20,40.58,190,P1,P1,BUY
```

**portfolio_settings.json:**
```json
{
  "starting_cash": 110000,
  "position_size_pct": 7,
  "max_positions": 7,
  "strategy_week": 1,
  "conservative_mode": true
}
```

### Scanner Enhancements

**New functionality:**
1. Read existing positions from CSV
2. Update Current_State for each holding
3. Calculate unrealized P&L
4. Flag state changes (P1→P2, P2→N2)
5. Show position summary in PDF

**PDF Report Changes:**

**Page 1 additions:**
- **Current Portfolio Status** (before action items)
  - Holdings table: Ticker, Shares, Entry Price, Current Price, P&L%, State
  - Total portfolio value
  - Cash available
  - Deployment %

**Page 2 additions:**
- **BUY Signals** enhanced with:
  - Dollar allocation column ($7,700 for top 3)
  - "Action" column: BUY THIS WEEK, HOLD, WAIT
  
### User Workflow

**Week 1 (January 17):**
1. Run scanner Friday → Gets 14 P1 signals
2. PDF shows: "No existing positions, start with 3"
3. Recommended: MU, TSM, MRNA @ $7,700 each

**Monday (January 20):**
1. Execute trades: Buy MU, TSM, MRNA
2. Manually add to `portfolio_positions.csv`:
   ```csv
   MU,2026-01-20,333.35,23,P1,P1,BUY
   TSM,2026-01-20,327.11,24,P1,P1,BUY
   MRNA,2026-01-20,40.58,190,P1,P1,BUY
   ```

**Week 2 (January 24):**
1. Run scanner Friday
2. Scanner reads CSV, updates states
3. PDF shows:
   - "Current Holdings: 3 positions, $23,100 invested"
   - State status: MU P1 (HOLD), TSM P1 (HOLD), MRNA P2 (HOLD)
   - "Available: $86,900 to add 2 more positions"
   - New P1 signals: NVDA, PLTR suggested

### Deliverables

- ✅ `portfolio_positions.csv` template
- ✅ `portfolio_settings.json` with $110k starting capital
- ✅ Scanner reads and updates CSV
- ✅ PDF shows existing positions + P&L
- ✅ Position sizing calculator (7% x $110k = $7,700)
- ✅ State change alerts in PDF

### Success Criteria

- Can track 3 positions from Week 1
- PDF clearly shows: HOLD these, BUY these
- P&L calculated correctly
- State changes detected (P1→P2→N2)

---

## Phase 2: Auto State Updates & Alerts

**Timeline:** Week 2-3 (January 24-31)  
**Effort:** 1-2 hours  
**Status:** Not Started

### What We're Building

**Enhanced state monitoring:**
- Auto-detect when positions change state
- Alert system for critical changes
- Historical state tracking

**New features:**
1. **State Change Log**
   - Track: Ticker, Date, Old_State, New_State, Price
   - Alert when P1→P2 (consolidation - monitor)
   - **CRITICAL ALERT** when ANY→N2 (exit required!)

2. **PDF Alerts Section**
   - Page 1 top: Red box if ANY positions are N2
   - "⚠️ SELL REQUIRED: ARM moved to N2 - exit Monday!"
   - Green box: "✅ All positions healthy"

3. **Position Risk Summary**
   - How many positions near N2? (within 3% of threshold)
   - Concentration risk (% in semiconductors)
   - Average days in position

**New file:**
```
data/
  └─ position_state_history.csv
     Ticker,Date,State,Price,Alert_Type
```

### Deliverables

- State change detection logic
- Alert system (N2 = critical, P2 = info)
- Historical tracking of all state changes
- PDF alert box on page 1

### Success Criteria

- N2 exit signals impossible to miss
- Can see state progression over time
- Alerts guide Monday actions clearly

---

## Phase 3: Trade Execution History

**Timeline:** Week 4-5 (February)  
**Effort:** 2 hours  
**Status:** Not Started

### What We're Building

**Complete trade log:**
- Record every entry and exit
- Calculate returns per trade
- Win rate and strategy performance

**New file:**
```
data/
  └─ trades_history.csv
     Ticker,Entry_Date,Entry_Price,Exit_Date,Exit_Price,Shares,Return_Pct,Return_Dollars,Hold_Days,Win
```

**Automatic logging:**
1. When you add position to CSV → Log as BUY trade
2. When position hits N2 and you exit → Log as SELL trade
3. Calculate return, hold period, win/loss

**Performance metrics:**
- Total return ($)
- Win rate (%)
- Average win vs average loss
- Best/worst trades
- Compare to backtest (expected 46.80% CAGR with S&P 500 optimized universe)

### Deliverables

- Trade history CSV with full transaction log
- Performance calculation engine
- PDF Page 4: Performance dashboard
  - YTD return
  - Win rate
  - Avg hold period
  - Best/worst performers

### Success Criteria

- Every trade logged automatically
- Can prove strategy is working (or not)
- Track actual vs expected performance
- Identify what's working best

---

## Phase 4: Position Sizing & Cash Management

**Timeline:** Week 6-7 (February-March)  
**Effort:** 1 hour  
**Status:** Not Started

### What We're Building

**Intelligent position recommendations:**
- Calculate available cash
- Suggest number of new positions to add
- Enforce max position limits
- Rebalancing suggestions

**Logic:**
```python
current_value = sum(position_values)
cash_available = starting_cash - current_value + realized_gains
target_deployment = 50% (by week 8)
positions_needed = (target_deployment - current_deployment) / position_size_pct
```

**PDF Enhancement:**
```
PORTFOLIO STATUS
Current: 3 positions, $23,100 (21%)
Target: 5-7 positions, $55,000 (50%)
Available Cash: $86,900

RECOMMENDATION: Add 2 positions this week
Suggested allocation: $7,700 x 2 = $15,400
After deployment: 5 positions, $38,500 (35%)
```

**Risk checks:**
- Max 10% per position (alert if over)
- Max 40% per sector (alert if concentrated)
- Min 20% cash reserve (alert if too deployed)

### Deliverables

- Cash management calculator
- Progressive deployment tracker
- Risk alerts (concentration, overweight)
- Clear "add X positions" recommendations

### Success Criteria

- Never over-deploy capital
- Gradual build from 21% → 50% over 8 weeks
- Clear guidance on how many to add
- Risk warnings if imbalanced

---

## Phase 5: Enhanced PDF Report

**Timeline:** Week 8-10 (March)  
**Effort:** 2 hours  
**Status:** Not Started

### What We're Building

**Professional 4-page PDF:**

**Page 1: Executive Summary**
- Portfolio snapshot (value, return, positions)
- Critical alerts (N2 exits!)
- Action items for Monday
- Market sentiment

**Page 2: Current Holdings**
- Full position table with P&L
- State status for each
- Days held, entry/current price
- Position sizing (% of portfolio)

**Page 3: Trading Opportunities**
- BUY signals with $ amounts
- HOLD signals monitoring
- SELL signals with urgency

**Page 4: Performance Dashboard**
- YTD return vs target
- Win rate vs expected
- Best/worst performers
- Strategy health score

### Deliverables

- 4-page professional PDF
- Complete trading plan in one document
- Performance tracking
- Ready to print/review offline

### Success Criteria

- Can make all decisions from PDF alone
- Clear actionable guidance
- Performance transparency
- Professional presentation

---

## Phase 6: SQLite Database (Optional)

**Timeline:** Month 4+ (April+)  
**Effort:** 3-4 hours  
**Status:** Future Consideration

### Why SQLite?

**Current CSV limitations:**
- Can't easily query "show all trades from MU"
- Can't aggregate "total semiconductor returns"
- No data integrity checks
- Manual CSV editing prone to errors

**SQLite benefits:**
- Fast queries
- Data validation
- Historical analysis
- Multi-user safe (if needed)

### Database Schema

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    entry_date DATE,
    entry_price REAL,
    shares INTEGER,
    entry_state TEXT,
    current_state TEXT,
    status TEXT  -- OPEN, CLOSED
);

CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    entry_date DATE,
    entry_price REAL,
    exit_date DATE,
    exit_price REAL,
    shares INTEGER,
    return_pct REAL,
    hold_days INTEGER
);

CREATE TABLE state_history (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    date DATE,
    state TEXT,
    price REAL,
    alert_type TEXT
);
```

### Migration Plan

- Keep CSV as backup
- Migrate gradually (test in parallel)
- Build query tools
- Optional: Keep CSV export for Excel users

**Decision point:** Only migrate if CSV becomes painful (> 50 trades?)

---

## Phase 7: Advanced Features (Future)

**Timeline:** Month 6+ (June+)  
**Effort:** Variable  
**Status:** Ideas for Future

### Potential Enhancements

**1. Streamlit Dashboard**
- Web UI for position management
- Interactive charts (P&L over time)
- One-click trade logging
- Mobile responsive

**2. Broker Integration**
- Import trades from Interactive Brokers, TD Ameritrade
- Auto-sync positions daily
- No manual CSV editing

**3. Mobile Alerts**
- SMS/email when position hits N2
- Weekly scan completion notification
- Performance milestone alerts

**4. Tax Reporting**
- Track cost basis per lot
- Wash sale detection
- Annual 1099 reconciliation

**5. Multi-Strategy Support**
- Run GHB + other strategies
- Compare performance
- Allocate capital across strategies

**6. Paper Trading Mode**
- Test strategy without real money
- Simulate portfolio growth
- Learn before committing capital

### Decision Criteria

Only build if:
- Phase 1-5 working perfectly
- Real need identified through usage
- Time/complexity justified by value

---

## Implementation Notes

### Technology Stack

**Current (Phase 1-5):**
- Python 3.x
- pandas (data manipulation)
- yfinance (price data)
- reportlab (PDF generation)
- CSV files (data storage)
- Jupyter notebook (execution)

**Future (Phase 6+):**
- SQLite (database)
- Streamlit (web UI)
- Plotly (interactive charts)
- APScheduler (automation)

### Development Principles

1. **Incremental delivery** - Each phase adds value independently
2. **User feedback** - Test with real trading before next phase
3. **Keep it simple** - Don't over-engineer
4. **Data integrity** - Backup before changes
5. **Documentation** - Update this roadmap as we build

### Testing Strategy

**Phase 1-3:** Manual testing with real trades  
**Phase 4-5:** Paper trading validation  
**Phase 6+:** Full test suite with historical data

### Backup Strategy

**Weekly backups:**
- Git commit after each Friday scan
- Archive CSV files weekly
- Keep 3 months of history

**Before major changes:**
- Full backup to archive/
- Test on copy first
- Document rollback procedure

---

## Success Metrics

### Phase 1 Success (Week 1-2)
- [ ] Can track 3 positions
- [ ] PDF shows holdings + P&L
- [ ] States update automatically
- [ ] Position sizing works

### Overall Success (Month 3)
- [ ] All trades logged automatically
- [ ] Performance matches expectations
- [ ] No missed N2 exits
- [ ] Clear decision-making process
- [ ] < 30 minutes per week time commitment

### Ultimate Success (Month 6)
- [ ] Meeting/beating backtest performance (46.80% CAGR target)
- [ ] 5-10 concurrent positions managed smoothly
- [ ] Complete audit trail of all trades
- [ ] Confident in strategy execution
- [ ] System runs reliably every Friday

---

## Current Status

**Date:** January 15, 2026  
**Phase:** Phase 1 - Implementation Starting  
**Next Milestone:** Week 1 scanner with position tracking (January 17)  

**Immediate Tasks:**
1. Create portfolio_positions.csv template
2. Create portfolio_settings.json  
3. Update scanner to read positions
4. Add current holdings to PDF
5. Test with 3 sample positions

**Next Friday (Jan 17):**
- Run enhanced scanner
- Review PDF output
- Plan Monday trade execution

---

**Last Updated:** January 15, 2026  
**Document Owner:** Portfolio Management System  
**Review Frequency:** Weekly until Phase 5 complete, then monthly

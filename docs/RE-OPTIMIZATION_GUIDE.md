# Universe Re-Optimization Guide

## Automated Alert System

The weekly scanner now includes **automatic monitoring** that flags when your stock universe needs refresh.

---

## 🚦 Alert Levels

### ✅ GREEN - Healthy
- No action needed
- Universe performing as expected
- Continue weekly trading

### 🟡 YELLOW - Warning
- Re-optimization recommended soon
- Plan to re-screen within 1-2 months
- Monitor conditions

### 🔴 RED - Critical
- Re-optimization REQUIRED
- Action needed before next week
- Do not ignore

---

## 📊 Monitored Conditions

### 1. Universe Degradation
**What:** Percentage of stocks in N2 (SELL) state

**Thresholds:**
- 🟡 **Warning:** >20% in N2
- 🔴 **Critical:** >30% in N2

**Why it matters:** If too many stocks show weakness, universe selection may be broken

**Action if triggered:**
- Check if market-wide issue or stock-specific
- If stock-specific: Re-screen S&P 500 immediately
- If market-wide: Wait for recovery or find defensive sectors

---

### 2. Performance Lag
**What:** Portfolio return vs expected (46.80% CAGR / 0.90% per week)

**Thresholds:**
- 🟡 **Warning:** >10% below expected (after 12+ weeks)
- Performance gap = Actual return - Expected return

**Why it matters:** Persistent underperformance suggests wrong stocks selected

**Action if triggered:**
- Review which stocks are dragging performance
- Consider replacing worst performers
- Re-screen if gap persists 2+ months

**Note:** Only triggers after 3+ months to avoid false alarms

---

### 3. Low Opportunity Environment
**What:** Percentage of stocks showing P1 (BUY) signals

**Thresholds:**
- 🟡 **Warning:** <20% in P1
- Watch: <30% in P1

**Why it matters:** Few opportunities may indicate:
- Market rotation away from your sectors
- Universe too tech-heavy during tech crash
- Bear market requiring defensive positioning

**Action if triggered:**
- Check sector concentration
- Consider adding defensive/value stocks
- May need broader universe or different sectors

---

### 4. Stale Universe
**What:** Time since last universe refresh

**Thresholds:**
- 🟡 **Warning:** >6 months since update
- 🔴 **Critical:** >12 months since update

**Why it matters:** 
- Company fundamentals change over time
- New winners emerge (like SMCI in 2024)
- Old winners fade

**Action if triggered:**
- Plan re-screen (6+ months)
- Execute re-screen immediately (12+ months)

---

## 🔧 How to Re-Optimize

### ⚡ AUTOMATED WAY (Recommended)

**Use the Re-Optimization Notebook:**

1. Open `notebooks/universe_reoptimization.ipynb`
2. Run all cells (takes 10-15 minutes)
3. Review the analysis and recommendations
4. Copy/paste the generated code if you approve

**What it does automatically:**
- ✅ Loads your current 25-stock universe
- ✅ Screens full S&P 500 (~500 stocks)
- ✅ Identifies top 25 by CAGR
- ✅ Compares new vs current universe
- ✅ Shows exactly which stocks to keep/add/drop
- ✅ Analyzes sector diversification
- ✅ Generates ready-to-paste code for both files
- ✅ Saves detailed report for reference
- ✅ Provides decision framework (keep/partial/full refresh)

**Advantages:**
- All steps automated in one place
- Side-by-side comparison with explanations
- Catches issues (concentration, missing stocks)
- Non-destructive (you approve before updating)
- Creates audit trail (timestamped reports)

---

### 🔧 MANUAL WAY (If you prefer command line)

### Step 1: Run Full S&P 500 Screen
```bash
cd c:\workspace\portfolio_analyser
python backtest/screen_stocks.py --universe sp500 --refresh-data
```

**Time:** 10-15 minutes  
**Output:** `backtest/results/stock_screening_[date].csv`

---

### Step 2: Review Results
Open the CSV file and review:
- How many stocks qualified? (Should be 100-120, or 20-25%)
- What are top 25 by CAGR?
- How many overlap with current universe?
- What sectors are represented?

**Compare:**
- Current universe: 25 stocks
- New top 25: ?
- Overlap: ?
- Need to replace: ?

---

### Step 3: Decide on Changes

**Option A: Full Refresh (Recommended annually)**
- Replace all 25 stocks with new top 25
- Clean break, no legacy bias
- Most responsive to market changes

**Option B: Partial Update**
- Keep top 15-20 that still qualify
- Replace bottom 5-10 with new winners
- Maintains some continuity

**Option C: Emergency Additions**
- Keep current 25
- Add 5-10 clear winners if space allows
- Only if current universe mostly healthy

---

### Step 4: Update Code

**File 1: notebooks/ghb_portfolio_scanner.ipynb**

Find the cell with `GHB_UNIVERSE = [...]` (around line 71-81):

```python
# Replace with new list
GHB_UNIVERSE = [
    'ANET', 'APH', 'AXON', ...  # Your new 25 stocks
]
```

**File 2: data/ghb_optimized_portfolio.txt**

Update the text file with new stocks (alphabetically):
```
ANET
APH
AXON
...
```

---

### Step 5: Backtest New Universe (Optional)

```bash
# Update backtest/data_loader.py if creating new universe
# Add to get_universe() method

python backtest/run_backtest.py
```

**Check:**
- CAGR >40%?
- Max drawdown <30%?
- Win rate >55%?

If yes → Deploy  
If no → Review stock selection

---

### Step 6: Transition Portfolio

**For existing positions:**

**Option A: Immediate Exit (Aggressive)**
1. Sell all stocks not in new universe (Monday 9:30am)
2. Enter new P1 signals from updated universe
3. Complete transition in 1 week

**Option B: Gradual Transition (Conservative)**
1. Keep existing positions until N2 exit signal
2. Only enter new positions from updated universe
3. Complete transition over 4-8 weeks

**Option C: Hybrid (Recommended)**
1. Exit removed stocks that are P2/N1/N2 (weak states)
2. Keep removed stocks that are P1 (strong) until N2
3. Prioritize entering new universe stocks
4. Complete transition over 2-4 weeks

---

## 📅 Recommended Schedule

### Annual (Required)
- **When:** January each year
- **What:** Full S&P 500 re-screen
- **Result:** New top 25 universe for the year

### Semi-Annual (Optional Check)
- **When:** July mid-year
- **What:** Quick review - are 80%+ stocks still qualified?
- **Result:** Keep or update if degraded

### Quarterly (Health Check)
- **When:** End of each quarter
- **What:** Review performance vs expected
- **Result:** Identify any lagging stocks

### Weekly (Automatic)
- **When:** Every Friday scan
- **What:** Automated alert system checks 4 conditions
- **Result:** Flags if action needed

---

## 🎯 Expected Outcomes

### After Re-Optimization:
✅ More P1 signals (better opportunities)  
✅ Improved performance vs benchmark  
✅ Reduced N2 percentage (fewer weak stocks)  
✅ Fresh universe timestamp  
✅ Better sector balance  

### Timeline:
- **Week 1:** Screen and analyze (10-15 min)
- **Week 2:** Update code and backtest (30 min)
- **Weeks 3-6:** Transition portfolio gradually
- **Months 1-3:** Monitor vs new expectations

---

## 📋 Re-Optimization Checklist

**Pre-Screen:**
- [ ] Decide: Full refresh or partial update?
- [ ] Check current universe age
- [ ] Review recent performance vs expected
- [ ] Note any obvious missing winners

**Screening:**
- [ ] Run screen_stocks.py on full S&P 500
- [ ] Review qualification rate (expect 20-25%)
- [ ] Identify top 25 by CAGR
- [ ] Check sector diversification

**Analysis:**
- [ ] Compare to current universe
- [ ] Note overlap (typically 40-60%)
- [ ] Identify exciting new additions
- [ ] Check for any surprising removals

**Updates:**
- [ ] Update GHB_UNIVERSE in scanner notebook
- [ ] Update ghb_optimized_portfolio.txt
- [ ] Optional: Backtest new universe
- [ ] Update documentation with change date

**Transition:**
- [ ] Decide transition strategy (immediate/gradual/hybrid)
- [ ] Exit removed stocks per strategy
- [ ] Enter new P1 signals from updated universe
- [ ] Track progress over 2-8 weeks

**Validation:**
- [ ] First week: Verify scanner uses new universe
- [ ] First month: Track P1 signal count
- [ ] First quarter: Monitor performance vs expected
- [ ] Document: What changed and why

---

## ❓ FAQ

**Q: How often should I re-optimize?**
A: Annually (January) is sufficient. Scanner alerts you if sooner needed.

**Q: Can I wait longer than 1 year?**
A: Not recommended. Universe will degrade. Scanner flags as CRITICAL after 12 months.

**Q: What if I'm in the middle of trades?**
A: Use gradual transition (Option B). Let current positions exit naturally at N2.

**Q: Do I need to exit ALL old stocks immediately?**
A: No. Keep strong (P1) positions from old universe. Only replace weak ones.

**Q: What if screening finds <100 qualified stocks?**
A: Check criteria. May need to lower thresholds or expand to Russell 1000.

**Q: Can I keep my favorite stocks even if they don't qualify?**
A: Not recommended. Strategy tested on volatile stocks only. Non-volatile = losses.

**Q: How do I know if re-optimization worked?**
A: Monitor for 3 months. Should see:
- More P1 signals weekly
- Better win rate (>55%)
- Performance tracking toward 46.80% CAGR

**Q: What if new universe performs worse?**
A: Give it 6 months. Short-term variance expected. If still worse, review selection criteria.

---

## 🚨 When NOT to Re-Optimize

**Don't re-optimize if:**

1. **Market-wide crash** - All stocks weak (30%+ in N2)
   - Wait for recovery or find defensive sectors
   - Not a universe issue, it's market conditions

2. **Only 1-2 months of underperformance**
   - Too soon to judge
   - Strategy has variance
   - Wait for 3+ months

3. **Universe is <6 months old**
   - Too frequent changes = chasing
   - Let strategy work
   - Only if CRITICAL alert triggered

4. **Strong P1 opportunities available**
   - Universe still working
   - Keep trading
   - Re-optimize only when few opportunities

5. **You recently changed trading discipline**
   - Give new habits time to work
   - Don't confuse execution issues with universe issues

---

**Last Updated:** January 15, 2026  
**Next Required Re-Screen:** January 2027  
**Alert System:** Automated in weekly scanner

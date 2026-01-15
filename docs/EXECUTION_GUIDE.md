# GHB Strategy - Monday Execution Guide

## 📋 Quick Summary

**Timing:**
- SELLS: 9:30-10:00am (First 30 minutes - URGENT)
- BUYS: 10:00-10:30am (After market settles - PATIENT)

**Limit Orders:**
- SELLS: Friday close - 1% (Aggressive exit)
- BUYS: Friday close + 1.5% (Balanced entry)

**Mid-Week Rule:**
- If BUY doesn't fill Monday: WAIT for next Friday (don't chase)
- If SELL signal given Friday: MUST execute Monday (never wait)

---

## ⏰ Monday Morning Schedule

### 9:30am - OPEN BELL

**1. Check Pre-Market (9:15-9:30am)**
- Review overnight news on your positions
- Check if any stocks gapping significantly
- Prepare sell orders first

**2. SELLS FIRST (9:30-10:00am) - URGENT**

**Why first 30 minutes?**
- N2 = Trend broken, losses compound
- Often gap down on Monday if weakness continued
- Get ahead of the selling pressure
- Price is secondary to execution

**How to execute:**
```
Order Type: Limit Order
Price: Friday close × 0.99 (1% below)
Time: 9:30am sharp
Good-til: Day

Example:
Stock: NFLX
Friday Close: $776.77
Limit Sell: $769.00
Shares: 10 (from portfolio)
```

**What if it gaps down?**
- Your limit will execute at market price (lower than your limit)
- This is GOOD - you're out even faster
- Don't try to "wait for a bounce"

**What if it gaps up?**
- Rare for N2 stocks, but possible
- Your limit will execute around your price
- Still sell - don't second-guess the signal

---

### 10:00am - MARKET SETTLES

**3. Wait 30 Minutes Before Buying**

**Why wait?**
- Opening 30 minutes = highest volatility
- Wide bid-ask spreads (costs you money)
- Overnight news gets digested
- Algos and stop losses create noise

**What to do 9:30-10:00am:**
- Monitor sell executions
- Check P1 stocks' opening prices
- Adjust buy limits if needed (see guidelines below)

---

### 10:00-10:30am - BUY TIME

**4. BUYS SECOND (10:00-10:30am) - PATIENT**

**How to execute:**
```
Order Type: Limit Order
Price: Friday close × 1.015 (1.5% above)
Time: 10:00am onward
Good-til: Day

Example:
Stock: MU
Friday Close: $95.50
Limit Buy: $96.93
Shares: 80 (= $7,700 / $95.50)
```

**Limit Order Logic:**
- Gives room for normal overnight gap (+0-2%)
- Protects against chasing big moves (+3%+)
- ~90% fill rate vs 60% at exact Friday close

**Decision Tree:**

**If stock opens at $93 (below Friday close):**
- ✅ Your limit will likely fill immediately
- ✅ Great entry - got it cheaper than Friday

**If stock opens at $96 (within 1.5%):**
- ✅ Your limit will likely fill at ~$96
- ✅ Good entry - normal volatility

**If stock opens at $98 (above your limit):**
- ❌ Limit won't fill unless it pulls back
- ⏳ Wait until 11am to see if it comes back
- ⏳ If still above $97 by 11am, SKIP IT
- ✅ Enter the next position on your list instead

**If stock opens at $101 (+5%+ gap):**
- ❌ Don't chase - too expensive
- ❌ Don't raise your limit "just to get in"
- ✅ Move to next P1 stock on your list
- ✅ Or wait for next Friday - might still be P1

---

## 🚫 What NOT To Do

### Tuesday-Friday Trading (DON'T)

**Scenario: Stock gapped above your Monday limit, now pulled back Tuesday**

❌ **DON'T buy mid-week because:**
- Signal based on FRIDAY weekly close only
- Tuesday price is "noise" - not a signal
- You don't know if it's still P1 until Friday
- Deviates from backtested methodology

✅ **DO wait for next Friday:**
- If still P1 next Friday, enter Monday after that scan
- If not P1 anymore, you saved yourself a bad trade
- Weekly discipline > trying to "catch the dip"

**Exception: Missed Monday SELL**
- If you somehow missed Monday, sell Tuesday 9:30am
- N2 signal already happened - don't delay further
- Selling is urgent, buying is patient

---

## 📊 Limit Order Guidelines

### SELL Orders (Aggressive Exit)

**Standard: Friday × 0.99 (1% below)**

Why aggressive?
- Priority is getting out, not price optimization
- N2 stocks often gap down (you want to beat the crowd)
- Backtested avg loss = -11%, saving 1% won't change outcome

**Example:**
- Friday close: $100.00
- Your limit: $99.00
- Opens at $97: Fills at $97 ✅
- Opens at $102: Fills at ~$100-101 ✅

### BUY Orders (Balanced Entry)

**Standard: Friday × 1.015 (1.5% above)**

Why 1.5%?
- Normal overnight gaps = 0-2%
- Gives room without chasing
- 90% fill rate vs 60% at exact Friday close

**Adjustments:**

**Conservative (exact Friday close):**
```
Limit: Friday × 1.00 (no premium)
Pro: Don't overpay
Con: ~60% fill rate, miss more entries
```

**Aggressive (Friday + 2-3%):**
```
Limit: Friday × 1.02-1.03
Pro: ~95% fill rate
Con: Paying 2-3% premium, worse entry
```

**Recommendation: Stick with 1.5%** - Best balance of fills and price

---

## 🎯 Weekly Discipline > Perfect Execution

### The Backtest Assumption

The 46.80% CAGR (2021-2025 backtest) assumes:
- Trades executed at "reasonable" prices
- Weekly signals only (not daily)
- Some slippage expected (~1.5% buy, -1% sell)
- Not trying to time perfect entries
- S&P 500 optimized universe (25 stocks)
- 10% position size, 10 max holdings

### Missing an Entry is OK

**~7 trades per year means:**
- Missing 1-2 entries won't kill returns
- Better to skip than chase +5% gaps
- Better to wait than trade mid-week

**Remember:**
- Strategy edge = Weekly momentum signals
- NOT perfect Monday morning execution
- Maintain the weekly discipline

---

## 💡 Real-World Examples

### Example 1: Clean Execution

**Friday Jan 17:**
- MU closes at $95.50 (P1 signal)
- TSM closes at $198.00 (P1 signal)
- MRNA closes at $42.80 (P1 signal)

**Monday Jan 20, 10:00am:**
- MU trading at $96.20 → Your limit $96.93 → FILLS at $96.25 ✅
- TSM trading at $200.50 → Your limit $200.97 → FILLS at $200.55 ✅
- MRNA trading at $43.10 → Your limit $43.44 → FILLS at $43.15 ✅

**Result:** All 3 positions entered, slight premium (~0.8%) is normal

---

### Example 2: One Gaps Too High

**Friday Jan 17:**
- MU closes at $95.50 (P1 signal)
- NVDA closes at $140.00 (P1 signal)
- MRNA closes at $42.80 (P1 signal)

**Monday Jan 20, 10:00am:**
- MU trading at $96.20 → Limit $96.93 → FILLS at $96.25 ✅
- NVDA trading at $145.00 → Limit $142.10 → NO FILL ❌
- MRNA trading at $43.10 → Limit $43.44 → FILLS at $43.15 ✅

**Options:**
1. Enter next P1 stock (ASML) at $849.76 limit ✅ RECOMMENDED
2. Wait until 11am - if NVDA pulls back to $142, fill it ✅ OK
3. Skip NVDA, only take 2 positions this week ✅ OK

**DON'T:**
- ❌ Chase NVDA by raising limit to $145
- ❌ Buy NVDA Tuesday when it pulls back to $143
- ❌ Try to "time" NVDA throughout the week

**Next Friday Jan 24:**
- If NVDA still P1, you get another chance
- If NVDA moved to P2, you avoided chasing a fade

---

### Example 3: Stock You Own Goes N2

**Friday Jan 24:**
- You own MU (entered Jan 20 at $96.25)
- MU closes Friday at $88.00 (N2 signal)

**Monday Jan 27, 9:30am:**
- MU opens at $87.50
- Your limit sell: $88.00 × 0.99 = $87.12
- Order FILLS at $87.50 ✅

**Calculate:**
- Entry: $96.25 × 80 shares = $7,700
- Exit: $87.50 × 80 shares = $7,000
- Loss: -$700 (-9.1%)

**This is NORMAL:**
- Avg loss = -11% (you did better!)
- Strategy has 57% win rate (43% are losses)
- Avg win = +64% will make up for this

**What you did RIGHT:**
- Executed sell signal immediately
- Didn't "hope for a bounce"
- Preserved $7,000 for next P1 opportunity
- Followed the strategy discipline

---

## 📝 Monday Execution Checklist

**9:00am - Pre-Market**
- [ ] Review overnight news
- [ ] Check positions for any N2 sells
- [ ] Prepare sell orders (Friday × 0.99)

**9:30am - SELL Phase**
- [ ] Execute ALL N2 sell orders immediately
- [ ] Monitor fills
- [ ] Confirm all sells executed by 10:00am

**10:00am - BUY Phase**
- [ ] Check P1 stocks' current prices
- [ ] Enter buy orders (Friday × 1.015)
- [ ] Prioritize by Friday ROC% (top positions first)

**10:30am - Review**
- [ ] Check which buys filled
- [ ] If 1-2 didn't fill, enter next P1 stocks OR
- [ ] Wait until 11am to see if they pull back
- [ ] By 11am, finalize all entries for the week

**Monday Evening**
- [ ] Update portfolio_positions.csv with new entries
- [ ] Record actual fill prices (not estimates)
- [ ] Remove sold positions from CSV
- [ ] Calculate remaining cash

**Next Friday**
- [ ] Run scanner again
- [ ] Review state changes for your positions
- [ ] Plan next Monday's trades

---

## 🎓 Key Principles

1. **Asymmetric Execution:**
   - Hurry to stop losses (9:30am sells)
   - Patient to enter winners (10:00am buys)

2. **Weekly Discipline:**
   - Trade ONLY on Mondays based on Friday signals
   - No mid-week improvisation
   - Missing an entry > chasing a gap

3. **Limit Orders:**
   - Sells: Aggressive (Friday -1%)
   - Buys: Balanced (Friday +1.5%)
   - Don't chase, don't hope

4. **Position Sizing:**
   - Each position: $7,700 (7% of $110k)
   - Calculate shares: $7,700 / Friday close
   - Round down to whole shares

5. **Trust The Process:**
   - 46.80% CAGR expected over time (backtested 2021-2025)
   - Individual wins/losses don't matter
   - System edge = Weekly signals, not perfect timing
   - Configuration: 10% positions, 10 max holdings, S&P 500 optimized universe

---

## ❓ FAQ

**Q: What if I miss Monday entirely?**
A: For buys, wait until next Friday. For sells, execute Tuesday 9:30am.

**Q: Stock gapped up 8%, should I chase it?**
A: No. Move to next P1 stock or wait for next Friday.

**Q: Stock pulled back Tuesday after gapping Monday, should I buy?**
A: No. Wait for Friday scan. Mid-week trading breaks the methodology.

**Q: What if news comes out mid-week on a position I own?**
A: Wait for Friday scan. Let the strategy decide, not the news.

**Q: Should I use market orders instead of limits?**
A: No for buys (too risky). Maybe for sells if urgent (N2 is already urgent).

**Q: What if I get partial fills?**
A: For Week 1, enter what fills. For future, adjust shares or skip that stock.

**Q: Can I trade pre-market or after-hours?**
A: No. Regular hours only (9:30am-4pm ET). Liquidity and spreads are worse outside hours.

---

**Remember:** The strategy's edge comes from WEEKLY momentum signals, not perfect Monday execution. Maintain discipline, trust the process, and the returns will follow. 📈

# Support/Resistance Level Guide

## Overview
The GHB scanner now automatically calculates support and resistance levels for all stocks to help with scaled entry decisions.

## What's Calculated

### Support Levels
- **Recent Support**: Lowest price in last 60 days (swing low)
- **52-Week Low**: Lowest price in past year
- **SMA 50**: 50-day moving average (dynamic support)
- **SMA 100**: 100-day moving average
- **D200**: 200-day moving average (primary trend)

### Resistance Levels
- **Recent Resistance**: Highest price in last 60 days (swing high)
- **52-Week High**: Highest price in past year

### Risk Assessment
The scanner calculates your distance from support:
- **< 3% above support**: LOW risk (near support)
- **3-5% above support**: MODERATE risk
- **5-10% above support**: MODERATE-HIGH risk
- **> 10% above support**: HIGH risk (far from support)

## Scaled Entry Recommendations

### Auto-Generated Entry Plans

The scanner provides position sizing based on distance from support:

```
Distance from Support  →  Recommended Entry Size
=====================     =======================
< 3%                   →  100% (Full position)
3-5%                   →  75% (Strong entry)
5-10%                  →  50% (Pilot position)
> 10%                  →  25-40% (Small pilot or WAIT)
```

### Example Output

```
TSLA: ⚠️ 50% PILOT - 9.8% above support, consider scaling
   Entry Plan: 50% now @ $456.00, add on dip to $418.92-$433.17

Current: $456.00
Support: $411.35 (Recent 60-day low)
To Support: -9.8%
Resistance: $488.50
To Resistance: +7.1%
```

## How to Use This Data

### Strategy 1: Risk-Adjusted Entry (Recommended)
**Monday execution based on support distance:**

```python
TSLA Example (50% target = $55,000):

Current Price: $456
Support: $411
Distance: 10% above support

Week 1 Action:
- Enter: $27,500 (50% of target) @ Monday open
- Why: Too far from support for full position
- Limit: $462 (Friday close + 1.5%)

Add-On Triggers:
- If dips to $411-$425: Add $27,500 (complete to 50%)
- If Week 2 still P1: Consider adding $13,750 (75% total)
```

### Strategy 2: Limit Orders at Support (Advanced)
**Place scaled limit orders:**

```python
TSLA (50% target = $55,000):

Limit Order 1: $18,333 @ $456 (market/current)
Limit Order 2: $18,333 @ $420 (near support +2%)
Limit Order 3: $18,333 @ $411 (at support)

All orders: Monday only, cancel end of day if not filled
```

### Strategy 3: Wait for Support Test (Conservative)
**Skip current price if too extended:**

```python
NVDA Example (20% target = $22,000):

Current: $1,450
Support: $1,350
Distance: 7.4% above support

Decision: WAIT for dip closer to $1,350-$1,380
- Set alert for support test
- Only enter if:
  1. Tests support ($1,350-$1,380) AND
  2. Still shows P1 signal on next Friday scan
```

## Integration with GHB Rules

### Key Principle
**Support levels help with ENTRIES, but GHB signals control EXITS**

✅ **Entry flexibility**: Can wait for support tests
❌ **Exit rigidity**: Must exit on N2 signal regardless of support

### Example Scenario

**Week 1**:
- TSLA: P1 @ $456, support @ $411
- Your action: Enter 50% ($27,500) pilot position

**Week 2**:
- TSLA dips to $420 (near support), still P1
- Your action: Add 50% ($27,500), now full position

**Week 3**:
- TSLA drops to N2 @ $398 (broke support)
- Your action: **EXIT ALL** - Support broken AND N2 signal

### Why This Works
1. **Better entries**: Lower cost basis improves risk/reward
2. **Maintains discipline**: Still uses GHB exit signals
3. **Risk management**: Reduces immediate drawdown
4. **Psychological**: Easier to hold when entered near support

## Practical Examples

### Low Risk Entry (< 3% from support)
```
AMD: ✅ FULL POSITION - Near support $160.50, low downside risk
Current: $164.00
Support: $160.50 (-2.1%)
Action: Enter full 10% position Monday
```

### Moderate Risk (5-8% from support)
```
NVDA: 🟡 50% PILOT - 7.4% above support, consider scaling
Current: $1,450
Support: $1,350 (-6.9%)
Action: Enter 50% pilot Monday, add 50% if dips to $1,350-$1,380
```

### High Risk (> 10% from support)
```
TSLA: ⚠️ 25-40% PILOT - 10.9% above support, high risk or WAIT
Current: $456
Support: $411 (-9.9%)
Action: Either enter 25-30% pilot OR wait for dip closer to $411
```

## Support Level Validation

### Quality Checks
Strong support levels have:
- ✅ **Multiple bounces**: Price tested and held 2-3+ times
- ✅ **Volume confirmation**: High volume at support
- ✅ **Recency**: Within last 60 days (not stale)
- ✅ **Aligns with SMAs**: Near 50/100/200-day moving averages

### Red Flags
Weak support if:
- ❌ Only tested once
- ❌ No volume spike at level
- ❌ Very old (6+ months)
- ❌ No SMA confluence

## Advanced: Multi-Level Support Strategy

### Identify Support Zones (Not just lines)
```
TSLA Support Zone Analysis:
Primary: $411 (60-day low)
Secondary: $398 (D200 moving average)
Strong: $385 (100-day SMA)
Critical: $365 (52-week low)

Entry Strategy:
- 25% @ current $456 (pilot)
- 25% @ $420-$430 (if dips, still P1)
- 25% @ $405-$415 (near primary support)
- 25% @ $390-$400 (near D200)

Exit Trigger: N2 signal (regardless of level)
```

## Weekly Workflow

### Friday Evening (After scan)
1. Review P1 signals
2. Note support distances for each
3. Plan Monday execution:
   - Full positions (< 5% from support)
   - Pilots (5-10% from support)
   - Wait list (> 10% from support)

### Monday 10:00-10:30am
4. Execute planned positions
5. Place limit orders for add-ons (if using)
6. Set alerts for support tests

### During Week (Optional)
7. If support tested AND still P1:
   - Can add to pilot positions
   - Only if GHB signal remains P1

### Next Friday
8. Re-scan: Check if P1 signals still valid
9. Complete partial positions if appropriate

## Key Takeaways

1. **Support levels improve entry timing** but don't override GHB exit rules
2. **Distance from support = Position size** (further = smaller)
3. **Wait for dips to support** if currently extended (> 10% above)
4. **Always exit on N2** regardless of support levels
5. **Use support for adds**, not for holding losing positions

## Risk Warning

⚠️ **Support levels can break!**
- They are guidance, not guarantees
- Always use GHB N2 signal as ultimate exit
- Support broken + N2 signal = SELL IMMEDIATELY
- Don't "wait for bounce" if N2 triggered

Remember: **Support helps you enter better, GHB gets you out safely.**

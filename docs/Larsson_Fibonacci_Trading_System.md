# Larsson-Fibonacci Trading System

**Complete Trading Rules & Logic Documentation**

---

## System Overview

The Larsson-Fibonacci Trading System combines two powerful technical analysis methods:

1. **Larsson Line** - A trend-following system using 4 RMA (Running Moving Average) periods to identify trend strength and direction
2. **Fibonacci Retracements** - Entry zones calculated from swing high/low over 100-day lookback period

This system is designed for **trend-following entries with precise risk management**, focusing on Weekly timeframe trend confirmation with Daily timeframe execution.

---

## Larsson Line Logic

### Four RMA Periods
- **V1 (Fast)**: 15-period RMA
- **M1**: 19-period RMA
- **M2**: 25-period RMA
- **V2 (Slow)**: 29-period RMA

### Trend Status (Weekly & Daily)

**GOLD (Bullish - Perfect Alignment)**
- All 4 lines aligned in ascending order
- Condition: `V1 > V2 AND V1 > M1 AND M1 > M2 AND M2 > V2`
- Visual: Yellow/Gold color
- Interpretation: Strong bullish trend, all moving averages aligned

**BLUE (Bearish - Perfect Reversal)**
- All 4 lines aligned in descending order
- Condition: `V1 < V2 AND V1 < M1 AND M1 < M2 AND M2 < V2`
- Visual: Blue color
- Interpretation: Strong bearish trend, complete reversal

**GRAY (Neutral - Mixed Alignment)**
- Lines are mixed (neither all ascending nor descending)
- Condition: Does not meet GOLD or BLUE criteria
- Visual: Gray color
- Interpretation: Weakening trend, consolidation, or transition phase

---

## Fibonacci Retracement Levels

### Calculation Method
- **Lookback Period**: 100 days (on Daily timeframe)
- **Swing High**: Highest high over lookback period
- **Swing Low**: Lowest low over lookback period
- **Formula**: `Level = Swing High - (Swing High - Swing Low) × Percentage`

### Three Key Levels
1. **38.2%** - Shallowest retracement (strong trend continuation)
2. **50.0%** - Mid-level retracement (balanced support)
3. **61.8%** - Golden ratio (deepest acceptable pullback)

---

## Entry Rules

### Two Entry Types

#### 1. PULLBACK Entry (Strong Buy Signal)
**Direction**: Price crossing DOWN from above Fibonacci level

**Detection Logic**:
- Previous bar was ABOVE the Fib level
- Current price is within 2% tolerance of the Fib level
- Example: Stock pulls back from $150 to $145 (50% Fib level)

**Position Sizing**:
- 38.2% Level: **20% of capital**
- 50.0% Level: **30% of capital**
- 61.8% Level: **50% of capital**

**Why Strong**: Price respected the level from above, showing support

---

#### 2. RECOVERY Entry (Confirmation Required)
**Direction**: Price crossing UP from below Fibonacci level

**Detection Logic**:
- Previous bar was BELOW the Fib level
- Price must cross ABOVE a **confirmation buffer** (+1.5% above the Fib level)
- Example: 50% Fib at $145 requires price to reach $147.18 for confirmation

**Position Sizing**:
- 38.2% Level: **20% of capital**
- 50.0% Level: **30% of capital**
- 61.8% Level: **50% of capital**

**Why Buffer Required**: Prevents false signals when price just touches the level from below without real strength

---

### Complete BUY Conditions (All Required)

1. ✓ **Weekly Larsson = GOLD** (Strong bullish trend on Weekly timeframe)
2. ✓ **Price Above Weekly 200 SMA** (Long-term weekly support confirmed)
   - *Note: For stocks without 200 weeks of history (NaN), this requirement is waived*
3. ✓ **Price Above Daily 200 SMA** (Daily support confirmed)
4. ✓ **Price At Fibonacci Level** (Either pullback OR recovery with confirmation)
5. ✓ **Volume Declining** (3-period volume SMA < 20-period volume SMA)

**When ALL conditions met**: Dashboard shows **"BUY"** in bright green with entry details

---

## Exit Rules

### EXIT 50% (Partial Exit)
**Trigger**: Weekly Larsson turns **GRAY**

**Logic**: 
- Trend is weakening but not yet reversed
- Take profits on 50% of position
- Keep 50% in case trend resumes

**Dashboard Display**: Orange background, "EXIT 50%"

---

### EXIT 100% (Full Exit)
**Triggers** (Either condition):
1. Weekly Larsson turns **BLUE** (bearish reversal)
2. Price breaks below **Weekly 200 SMA**

**Logic**:
- Trend has reversed OR long-term support broken
- Exit entire position to preserve capital

**Dashboard Display**: Red background, "EXIT 100%"

---

## Signal Types

### 1. BUY
- **Color**: Bright Green (Lime)
- **Meaning**: All 5 conditions met, enter position
- **Action**: Buy at current Fibonacci level with specified allocation
- **Details Shown**: 
  - Which Fibonacci level triggered (38.2%, 50%, 61.8%)
  - Entry type (Pullback or Recovery)
  - Position size percentage
  - Stop loss price and risk %

---

### 2. WAIT
- **Color**: Yellow (Semi-transparent)
- **Meaning**: Weekly Larsson is GOLD but other conditions not met
- **Common Reasons**:
  - Price not at Fibonacci level yet
  - Volume not declining (still rising)
  - Price below Daily 200 SMA
- **Action**: Monitor, do not enter yet
- **Note**: Green arrow (◄) may appear next to Fibonacci level showing proximity

---

### 3. EXIT 50%
- **Color**: Orange
- **Trigger**: Weekly Larsson = GRAY
- **Action**: Sell 50% of position, hold 50%

---

### 4. EXIT 100%
- **Color**: Red
- **Trigger**: Weekly Larsson = BLUE OR price below Weekly 200 SMA
- **Action**: Sell entire position immediately

---

### 5. NO SETUP
- **Color**: Yellow (Semi-transparent)
- **Meaning**: Weekly Larsson is not GOLD (either GRAY or BLUE)
- **Action**: No trade opportunity, stay in cash

---

## Volume Analysis

### Purpose
Confirms that selling pressure is exhausting before entry

### Calculation
- **Short-term Average**: 3-period SMA of volume
- **Long-term Average**: 20-period SMA of volume

### Declining Volume (Required for BUY)
- **Condition**: `3-period SMA < 20-period SMA`
- **Dashboard**: "Declining ✓" in green
- **Interpretation**: Recent volume lower than average, selling exhaustion

### Rising Volume (Blocks BUY)
- **Condition**: `3-period SMA >= 20-period SMA`
- **Dashboard**: "Rising ✗" in red
- **Interpretation**: Active selling still occurring, wait for exhaustion

---

## 200 SMA Requirements

### Daily 200 SMA
- **Calculation**: 200-period Simple Moving Average on **Daily** timeframe
- **Required**: Price must be ABOVE this level
- **Purpose**: Confirms intermediate-term uptrend
- **Dashboard Display**: "D:+10.3%✓" (example: 10.3% above)

### Weekly 200 SMA
- **Calculation**: 200-period Simple Moving Average on **Weekly** timeframe
- **Required**: Price must be ABOVE this level (or NaN for newer stocks)
- **Purpose**: Confirms long-term uptrend
- **Special Rule**: If NaN (stock doesn't have 200 weeks of history), requirement is automatically passed
- **Dashboard Display**: "W:+227.5%✓" (example: 227.5% above)

---

## Stop Loss Calculation

### Formula
```
Stop Loss = MAX(Daily 200 SMA × 0.90, 61.8% Fib Level × 0.93)
```

### Components
1. **Daily 200 SMA × 0.90**: 10% below Daily 200 SMA
2. **61.8% Fib × 0.93**: 7% below the deepest Fibonacci level

### Selection
Use whichever is HIGHER (less aggressive stop)

### Risk Calculation
```
Risk % = ((Current Price - Stop Loss) / Current Price) × 100
```

Displayed in dashboard when BUY signal appears

---

## Dashboard Indicators

### Larsson Status Row
**Format**: `W:GOLD✓ | D:GRAY`
- **W**: Weekly Larsson status (primary trend)
- **D**: Daily Larsson status (entry timing)
- **✓**: Appears only when Weekly is GOLD

---

### 200 SMA Row
**Format**: `W:+227.5%✓ | D:+10.3%✓`
- **W**: Distance from Weekly 200 SMA
- **D**: Distance from Daily 200 SMA
- **+**: Above SMA (bullish)
- **-**: Below SMA (bearish)
- **✓**: Price is above SMA
- **✗**: Price is below SMA
- **NaN**: Insufficient data (newer stocks)

---

### Volume Row
**Format**: `Declining ✓` or `Rising ✗`
- **Declining**: 3-period < 20-period (ready for entry)
- **Rising**: 3-period >= 20-period (wait)

---

### Fibonacci Levels
**Format**: `38.2% (20%): $152.16 (+43.8%)`
- **38.2%**: Fibonacci level percentage
- **(20%)**: Position allocation if triggered
- **$152.16**: Actual price level
- **(+43.8%)**: Distance from current price (+ = above, - = below)
- **◄**: Green arrow indicates current price is AT this level

---

## Trading Workflow

### 1. Check Weekly Larsson
- If not GOLD → **NO SETUP** → Stay in cash
- If GOLD → Continue evaluation

### 2. Check 200 SMAs
- Weekly: Must be above (or NaN for new stocks)
- Daily: Must be above
- If either fails → **WAIT**

### 3. Check Fibonacci Levels
- Is price at any of the three levels?
- Green arrow (◄) indicates proximity
- If not at level → **WAIT**

### 4. Check Volume
- Is volume declining (3-period < 20-period)?
- If rising → **WAIT**
- If declining → **BUY** signal appears

### 5. Execute Entry
- Note the Fibonacci level hit (38.2%, 50%, 61.8%)
- Check entry type (Pullback or Recovery)
- Use specified position size (20%, 30%, or 50%)
- Set stop loss at calculated price

### 6. Monitor Position
- **Weekly Larsson turns GRAY** → Exit 50%
- **Weekly Larsson turns BLUE** → Exit 100%
- **Price breaks Weekly 200 SMA** → Exit 100%

---

## Key Strategy Principles

### 1. Weekly Trend is King
- Only take trades when Weekly Larsson = GOLD
- Weekly trend determines position direction
- Daily timeframe only for entry timing

### 2. Fibonacci Levels are Entry Zones
- Not exact prices, but zones with tolerance
- Deeper pullbacks = larger position sizes
- Recovery entries need confirmation buffer

### 3. Volume Confirms Entry
- Wait for volume to decline before entry
- Rising volume = continued selling pressure
- Declining volume = exhaustion, ready to bounce

### 4. Risk Management is Mandatory
- Stop loss calculated automatically
- Based on Daily 200 SMA and 61.8% Fib
- Risk % displayed before entry

### 5. Partial Exits Preserve Capital
- GRAY = weakening trend, take 50% profit
- BLUE = reversal, exit completely
- Never hold through Weekly BLUE

---

## Common Scenarios Explained

### Scenario 1: "Why WAIT when at Fibonacci level?"
**Answer**: Check other conditions:
- Volume may be rising (not declining yet)
- Price may be below Daily 200 SMA
- Weekly 200 SMA may be broken

All 5 conditions must be met for BUY signal.

---

### Scenario 2: "Green arrow but no BUY signal?"
**Answer**: Green arrow (◄) only indicates price is AT a Fibonacci level. Other conditions (Weekly GOLD, volume declining, above 200 SMAs) must also be met.

---

### Scenario 3: "EXIT 100% but Weekly is GOLD?"
**Answer**: Check Weekly 200 SMA. If price broke below it, EXIT 100% triggers regardless of Larsson status. Long-term support is broken.

---

### Scenario 4: "Should I add to position at deeper Fib level?"
**Answer**: System allocates progressively:
- First entry: 20% at 38.2%
- If continues down: 30% more at 50%
- If continues down: 50% more at 61.8%
- Total: 100% allocated across three levels

---

### Scenario 5: "Stock is new, showing NaN for Weekly SMA?"
**Answer**: System automatically passes Weekly 200 SMA requirement for newer stocks (like ALAB). Can still generate BUY signals based on Weekly Larsson GOLD and other conditions.

---

## Visual Indicators on Chart

### Fibonacci Lines
- **Green Lines**: Price is ABOVE the level (support held)
- **Red Lines**: Price is BELOW the level (support broken)
- **Labels**: Show percentage and exact price
- **Line Width**: Adjustable in settings

### 200 SMA Lines (Optional Display)
- **Red Line**: Daily 200 SMA
- **Black Line**: Weekly 200 SMA
- Toggle on/off in Display settings

### Larsson Bands (Cloud)
- **Yellow Cloud**: Larsson lines on chart (optional)
- **Blue Cloud**: Bearish Larsson alignment
- Shows the RMA band structure visually

---

## Settings & Customization

### Larsson Line Settings
- V1 (Fast): Default 15
- M1: Default 19
- M2: Default 25
- V2 (Slow): Default 29

### Fibonacci Settings
- Lookback Period: Default 100 days
- Fib Tolerance: Default 2% (for pullback detection)
- Recovery Buffer: Default 1.5% (above level for confirmation)
- Manual Override: Can set manual swing high/low

### Position Sizing
- **Pullback Allocations**: 20% / 30% / 50%
- **Recovery Allocations**: 20% / 30% / 50%
- Customizable per level

### Volume Settings
- Short Period: Default 3
- Long Period: Default 20

### Display Settings
- Dashboard Position: Top Right / Top Left / Bottom Right / Bottom Left
- Dashboard Size: Small / Normal / Large
- Show Fibonacci Lines: On/Off
- Show 200 SMA Lines: On/Off

---

## Alert Configuration

### Available Alerts
1. **BUY Signal** - All 5 conditions met
2. **EXIT 50%** - Weekly Larsson turned GRAY
3. **EXIT 100%** - Weekly BLUE or Weekly 200 SMA broken
4. **Approaching Fib 38.2%** - Within 3% of level
5. **Approaching Fib 50.0%** - Within 3% of level
6. **Approaching Fib 61.8%** - Within 3% of level

### Setup in TradingView
1. Click "Alert" button
2. Select "Larsson-Fibonacci Trading Dashboard v2"
3. Choose condition from dropdown
4. Set notification preferences
5. Name the alert

---

## Quick Reference Card

### BUY Checklist (All Required)
☐ Weekly Larsson = GOLD  
☐ Above Weekly 200 SMA (or NaN)  
☐ Above Daily 200 SMA  
☐ At Fibonacci Level (green ◄)  
☐ Volume Declining (✓)  

### Exit Triggers
- **50%**: Weekly → GRAY
- **100%**: Weekly → BLUE OR break Weekly 200 SMA

### Position Sizing
- **38.2%**: 20%
- **50.0%**: 30%
- **61.8%**: 50%

### Entry Types
- **Pullback**: From above (strong)
- **Recovery**: From below (needs +1.5% buffer)

---

## Risk Disclaimer

This trading system is for educational purposes. Past performance does not guarantee future results. Always:
- Use proper position sizing
- Set stop losses
- Never risk more than you can afford to lose
- Consider your risk tolerance
- Consult a financial advisor

---

**Document Version**: 1.0  
**Last Updated**: January 18, 2026  
**System Name**: Larsson-Fibonacci Trading Dashboard v2  
**Platform**: TradingView (PineScript v5)

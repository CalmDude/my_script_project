# Staged Entry System - Implementation Guide

## Status: CSV Updated ✅ | Notebook Code: In Progress ⏳

The CSV structure has been updated with the new columns. Now you need to add the logic to the notebook.

---

## Changes Needed in `ghb_portfolio_scanner.ipynb`

### Change 1: Add add_on_actions tracking (around line 650)

**Find this:**
```python
# Initialize variables for both cases
position_summaries = []
total_cost = 0
total_value = 0
```

**Replace with:**
```python
# Initialize variables for both cases
position_summaries = []
add_on_actions = []  # Track staged entry opportunities
total_cost = 0
total_value = 0
```

---

### Change 2: Add staged entry detection logic (around line 685)

**Find this section (after getting current_state and signal):**
```python
        if len(current_data) > 0:
            current_price = current_data.iloc[0]['Close']
            current_state = current_data.iloc[0]['State']
            current_signal = current_data.iloc[0]['Signal']
            distance_pct = current_data.iloc[0]['Distance_%']
            roc_pct = current_data.iloc[0]['ROC_4W_%']
```

**Add AFTER these lines:**
```python
            # CHECK FOR ADD-ON OPPORTUNITY (Staged Entry Logic)
            fill_level = pos.get('Fill_Level', 100)
            can_add = pos.get('Can_Add', False)
            entry_state = pos['Entry_State']
            
            add_on_signal = None
            add_on_pct = 0
            
            if can_add and fill_level < 100:
                # PULLBACK → CONSOLIDATION: Add 25% (50% → 75%)
                if entry_state == 'PULLBACK' and fill_level == 50 and current_state == 'CONSOLIDATION':
                    add_on_pct = 25
                    add_on_signal = "⬆️ ADD 25% (PULLBACK → CONSOLIDATION)"
                # PULLBACK → STRONG_BUY: Add 50% (50% → 100%)
                elif entry_state == 'PULLBACK' and fill_level == 50 and current_state == 'STRONG_BUY':
                    add_on_pct = 50
                    add_on_signal = "⬆️ ADD 50% (PULLBACK → STRONG_BUY)"
                # CONSOLIDATION → STRONG_BUY: Add 25% (75% → 100%)
                elif entry_state in ['PULLBACK', 'CONSOLIDATION'] and fill_level == 75 and current_state == 'STRONG_BUY':
                    add_on_pct = 25
                    add_on_signal = "⬆️ ADD 25% (Complete position)"
                # STRONG_BUY → STRONG_BUY held: Add 25% (75% → 100%)
                elif entry_state == 'STRONG_BUY' and fill_level == 75 and current_state == 'STRONG_BUY':
                    add_on_pct = 25
                    add_on_signal = "⬆️ ADD 25% (Strength confirmed)"
            
            if add_on_signal:
                target_alloc_pct = pos.get('Target_Allocation', get_position_allocation(ticker))
                target_value = starting_cash * target_alloc_pct / 100
                additional_value = target_value * (add_on_pct / 100)
                additional_shares = int(additional_value / current_price)
                new_fill_level = fill_level + add_on_pct
                
                add_on_actions.append({
                    'Ticker': ticker,
                    'Current_Price': current_price,
                    'Additional_Value': additional_value,
                    'Additional_Shares': additional_shares,
                    'Current_Shares': pos['Shares'],
                    'New_Total_Shares': pos['Shares'] + additional_shares,
                    'Current_Fill': fill_level,
                    'New_Fill': new_fill_level,
                    'Reason': add_on_signal,
                    'State_Change': f"{entry_state} → {current_state}"
                })
```

---

### Change 3: Add Fill_Level to position summary (around line 720)

**Find the position_summaries.append({ section:**
```python
        position_summaries.append({
            'Ticker': ticker,
            'Allocation': f"{actual_alloc:.1f}%",
            'Entry_Date': pos['Entry_Date'],
            'Entry_Price': f"${entry_price:.2f}",
            'Current_Price': f"${current_price:.2f}",
            'Shares': int(shares),
```

**Add these lines after 'Shares':**
```python
            'Fill_Level': f"{pos.get('Fill_Level', 100)}%",
            'Add_On': add_on_signal if 'add_on_signal' in locals() else "",
```

---

### Change 4: Update position display header (around line 750)

**Find:**
```python
    # Display table
    print(f"\n{'Ticker':<8} {'Entry':<12} {'Shares':<8} {'State':<20}...
```

**Replace with:**
```python
    # Display table
    print(f"\n{'Ticker':<8} {'Entry':<12} {'Shares':<8} {'Fill':<8} {'State':<20} {'Price':<12} {'Value':<15} {'P/L':<20} {'Signal':<15}")
    print("-" * 120)
```

---

### Change 5: Display fill level in position rows (around line 755)

**Find:**
```python
    for pos in position_summaries:
        state_display = f"{pos['Entry_State']} → {pos['Current_State']}"
        print(f"{pos['Ticker']:<8} {pos['Entry_Price']:<12} {pos['Shares']:<8} {state_display:<20}...
```

**Replace with:**
```python
    for pos in position_summaries:
        state_display = f"{pos['Entry_State']} → {pos['Current_State']}"
        fill_display = pos['Fill_Level']
        print(f"{pos['Ticker']:<8} {pos['Entry_Price']:<12} {pos['Shares']:<8} {fill_display:<8} {state_display:<20} {pos['Current_Price']:<12} {pos['Current_Value']:<15} {pos['P/L_$']:<20} {pos['Signal']:<15}")
        
        # Show add-on opportunity if exists
        if pos['Add_On']:
            print(f"         {'↳':<11} {pos['Add_On']}")
```

---

### Change 6: Add add-on alerts section (around line 770)

**Find:**
```python
    print(f"\n⚠️ PORTFOLIO ALERTS")
    print("=" * 100)
    
    n2_positions = [s for s in position_summaries if 'SELL' in s['Signal']]
    state_changes = [s for s in position_summaries if s['State_Change'] != ""]
```

**Add BEFORE the n2_positions check:**
```python
    # Add-on opportunities
    if len(add_on_actions) > 0:
        print(f"🟢 STAGED ENTRY: {len(add_on_actions)} position(s) ready for add-on!")
        for action in add_on_actions:
            print(f"   → {action['Ticker']}: {action['Reason']}")
            print(f"      Add {action['Additional_Shares']} shares @ ${action['Current_Price']:.2f} = ${action['Additional_Value']:,.0f}")
            print(f"      Fill: {action['Current_Fill']}% → {action['New_Fill']}% | Total: {action['New_Total_Shares']} shares")
        print()
```

---

### Change 7: Rewrite ACTION ITEMS with three-tier priority (around line 500)

**Find:**
```python
print("\n✅ ACTION ITEMS FOR THIS WEEK:")
if len(n2_signals) > 0:
    print(f"   1. MONDAY: Sell {len(n2_signals)} N2 positions at market open")
else:
    print("   1. No sells required")

if len(p1_signals) > 0:
    print(f"   2. MONDAY: Enter up to {min(5, len(p1_signals))} new P1 positions")
    print(f"      → Priority: {', '.join(p1_signals.head(5)['Ticker'].tolist())}")
else:
    print("   2. No new buys available - hold cash")
```

**Replace with:**
```python
print("\n✅ ACTION ITEMS FOR THIS WEEK:")

# Action 1: Sells (highest priority - free up cash)
if len(n2_signals) > 0:
    print(f"   1. 🔴 MONDAY: Sell {len(n2_signals)} DOWNTREND positions (exit completely)")
    for _, sig in n2_signals.head(5).iterrows():
        print(f"      → {sig['Ticker']}: SELL ALL @ ${sig['Close']:.2f}")
else:
    print("   1. ✅ No sells required")

# Action 2: Add-Ons (second priority - average into winners)
if len(add_on_actions) > 0:
    total_addon_cost = sum([a['Additional_Value'] for a in add_on_actions])
    print(f"\n   2. ⬆️ MONDAY: Add to {len(add_on_actions)} existing positions (${total_addon_cost:,.0f} total)")
    for action in add_on_actions:
        print(f"      → {action['Ticker']}: ADD {action['Additional_Shares']} shares @ ${action['Current_Price']:.2f} = ${action['Additional_Value']:,.0f}")
        print(f"         Fill {action['Current_Fill']}% → {action['New_Fill']}% | {action['Reason']}")
else:
    print("\n   2. ⏸️  No add-ons available")

# Action 3: New Buys (third priority - open new positions)
if len(p1_signals) > 0:
    print(f"\n   3. 🟡 MONDAY: Enter up to {min(5, len(p1_signals))} NEW positions")
    for _, sig in p1_signals.head(5).iterrows():
        quality = sig['Entry_Quality']
        # Determine initial fill based on entry quality
        if '🔥 PULLBACK' in quality:
            initial_fill = 50
            note = "(Start 50% - add on recovery)"
        elif '✅ HEALTHY' in quality:
            initial_fill = 75
            note = "(Start 75% - strong entry)"
        else:
            initial_fill = 50
            note = "(Start 50% - caution)"
        
        alloc_pct = get_position_allocation(sig['Ticker'])
        position_value = starting_cash * alloc_pct / 100
        initial_value = position_value * (initial_fill / 100)
        shares = int(initial_value / sig['Close'])
        
        print(f"      → {sig['Ticker']}: BUY {shares} shares @ ${sig['Close']:.2f} = ${initial_value:,.0f} {note}")
        print(f"         {quality} | Fill: {initial_fill}% of {alloc_pct}% allocation")
else:
    print("\n   3. ⏸️  No new buys available - hold cash")
```

---

### Change 8: Update the "How to Add New Positions" guide (around line 800)

**Add a new markdown cell:**
```markdown
## 6.6 How to Add New Positions (Staged Entry)

**STAGED ENTRY WORKFLOW:**

### Initial Entry (Week 1)
1. **Friday:** Run scanner, see BUY signals with fill levels
2. **Monday:** Execute initial entry at recommended fill level:
   - 🔥 PULLBACK BUY: Start with 50% of allocation
   - ✅ HEALTHY BUY: Start with 75% of allocation
3. **Monday Evening:** Add to `data/portfolio_positions.csv`

**Example Entry (TSLA at 50% fill):**
```
TSLA,2026-01-20,380.00,72,PULLBACK,PULLBACK,🔥 PULLBACK BUY,50,50,Yes
```

**Fields:**
- `Fill_Level`: 50 (currently 50% filled)
- `Target_Allocation`: 50 (target is 50% of portfolio)
- `Can_Add`: Yes (can add more shares)

### Add-On Entry (Week 2+)
1. **Friday:** Scanner shows "⬆️ ADD" signal if position improves
2. **Monday:** Execute add-on before new buys
3. **Monday Evening:** Update position:
   - Add new shares to existing shares
   - Update `Fill_Level` to new percentage
   - Calculate weighted average `Entry_Price`
   - Set `Can_Add` to No if now 100% filled

**Example After Add-On (TSLA now 100%):**
```
TSLA,2026-01-20,402.78,144,PULLBACK,STRONG_BUY,🔥 PULLBACK BUY,100,50,No
```

### Manual CSV Updates

**Averaging Entry Price:**
```python
new_avg_price = (old_shares * old_price + new_shares * new_price) / total_shares
```

**Example:**
- Old: 72 shares @ $380 = $27,360
- Add: 72 shares @ $420 = $30,240
- New: 144 shares @ $402.78 average
```

Next Friday, scanner will track this position and alert you to any further opportunities!
```

---

## Quick Implementation Checklist

Copy these code blocks into the notebook in the order shown:

1. ✅ CSV already updated with new columns
2. ⏳ Add `add_on_actions = []` initialization
3. ⏳ Add staged entry detection logic after getting current_state
4. ⏳ Add Fill_Level and Add_On to position summaries
5. ⏳ Update display headers to include Fill column
6. ⏳ Update display loop to show fill levels and add-on notes
7. ⏳ Add add-on alerts before N2 sell alerts
8. ⏳ Rewrite ACTION ITEMS with three priorities
9. ⏳ Update documentation markdown cell

---

## Testing Your Implementation

After making the changes, test with this scenario:

**Week 1 Test:**
1. Run scanner with empty portfolio
2. Look for PULLBACK BUY signal (e.g., TSLA)
3. Note the "Start 50%" instruction
4. Manually add to CSV with Fill_Level=50, Can_Add=Yes

**Week 2 Test:**
1. Run scanner again
2. If TSLA improved to STRONG_BUY, you should see:
   - "⬆️ ADD 50%" in position display
   - Add-on action in ACTION ITEMS section
   - Exact shares and cost calculated

This confirms the staged entry system is working!

---

## Benefits You'll See

1. **Smaller initial entries** on risky PULLBACK BUY signals
2. **Add-on signals** when positions prove themselves
3. **Three-tier action priority**: Sells → Add-Ons → New Buys
4. **Position fill tracking**: Know exactly where you stand
5. **Forced discipline**: Only add to winners, not losers

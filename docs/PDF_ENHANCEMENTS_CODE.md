# PDF Enhancement Implementation Guide

## Overview
Add 3 integrated features to the PDF report:
1. **Traffic Light Summary** - Market-level risk assessment
2. **Entry Risk Analysis Table** - Stock-level support/resistance 
3. **Enhanced Action Items** - Risk-adjusted pilot positions

## Implementation Locations

All changes go in **Cell 29** (`#VSC-6f7cf5ed`) - the PDF generation cell.

---

## INSERTION POINT 1: After Market Sentiment (Line ~1130)

**Find this code:**
```python
story.append(Paragraph(f"<b>Market Sentiment:</b> {sentiment}", styles['Normal']))
story.append(Spacer(1, 0.2*inch))

# Re-optimization alerts
```

**INSERT THIS CODE between the Spacer and Re-optimization alerts:**

```python
# === FEATURE 3: TRAFFIC LIGHT SUMMARY (Market Entry Conditions) ===
if len(p1_signals) > 0:
    story.append(Paragraph("Market Entry Conditions", summary_style))
    
    # Count P1 stocks by risk level
    safe_entries = len(p1_signals[p1_signals['To_Support_%'] < 5])
    moderate_entries = len(p1_signals[(p1_signals['To_Support_%'] >= 5) & (p1_signals['To_Support_%'] < 10)])
    extended_entries = len(p1_signals[(p1_signals['To_Support_%'] >= 10) & (p1_signals['To_Support_%'] < 15)])
    very_extended = len(p1_signals[p1_signals['To_Support_%'] >= 15])
    
    # Determine market status
    if safe_entries + moderate_entries >= len(p1_signals) * 0.6:
        market_status = "FAVORABLE - Many safe entry points"
        status_color = colors.HexColor('#d4edda')
    elif moderate_entries + extended_entries >= len(p1_signals) * 0.6:
        market_status = "EXTENDED - Use caution with position sizing"
        status_color = colors.HexColor('#fff3cd')
    else:
        market_status = "VERY EXTENDED - Consider 25-50% pilots or wait"
        status_color = colors.HexColor('#f8d7da')
    
    traffic_data = [
        ['Risk Level', 'Count', 'Recommendation'],
        ['🟢 SAFE (< 5% above support)', str(safe_entries), 'Full position OK (75-100%)'],
        ['🟡 MODERATE (5-10% above)', str(moderate_entries), 'Scaled entry (50-75%)'],
        ['🔴 EXTENDED (10-15% above)', str(extended_entries), 'Small pilot (25-40%)'],
        ['⚫ VERY EXTENDED (> 15%)', str(very_extended), 'WAIT for dip']
    ]
    
    traffic_table = Table(traffic_data, colWidths=[2.3*inch, 0.7*inch, 2.5*inch])
    traffic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), status_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    story.append(traffic_table)
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph(f"<b>MARKET STATUS:</b> {market_status}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

# === FEATURE 2: ENTRY RISK ANALYSIS TABLE ===
if len(p1_signals) > 0:
    story.append(Paragraph("Entry Risk Analysis", summary_style))
    
    risk_data = [['Stock', 'Current', 'Support', 'Distance', 'Risk', 'Entry Strategy']]
    
    for _, row in p1_signals.head(min(10, len(p1_signals))).iterrows():
        ticker = row['Ticker']
        current = row['Close']
        support = row['Support']
        distance = row['To_Support_%']
        
        # Determine risk indicator and strategy
        if distance < 3:
            risk_icon = '🟢 LOW'
            strategy = '100% Full'
        elif distance < 5:
            risk_icon = '🟢 LOW-MOD'
            strategy = '75-80%'
        elif distance < 10:
            risk_icon = '🟡 MODERATE'
            strategy = '50% Pilot'
        elif distance < 15:
            risk_icon = '🔴 HIGH'
            strategy = '30% Pilot'
        else:
            risk_icon = '⚫ V.HIGH'
            strategy = 'WAIT'
        
        risk_data.append([
            ticker,
            f'${current:.2f}',
            f'${support:.2f}',
            f'{distance:+.1f}%',
            risk_icon,
            strategy
        ])
    
    risk_table = Table(risk_data, colWidths=[0.6*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.9*inch, 0.9*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph("<b>Legend:</b> 🟢 < 5% | 🟡 5-10% | 🔴 10-15% | ⚫ > 15% from support", 
                          ParagraphStyle('Legend', parent=styles['Normal'], fontSize=7)))
    story.append(Spacer(1, 0.2*inch))
```

---

## INSERTION POINT 2: Replace BUY Action Items Section (Line ~1217)

**Find this code:**
```python
# Point 2: BUY - Show specific positions with limit prices and shares (variable allocations)
if len(p1_signals) > 0:
    current_positions = len(df_positions)
    positions_to_add = min(max_positions - current_positions, len(p1_signals))
    if strategy_week == 1 and current_positions == 0:
        positions_to_add = min(3, len(p1_signals))  # Week 1: Start with 3
    
    top_buys = p1_signals.head(positions_to_add)
    
    # Calculate total deployment with variable allocations
    total_deploy = sum([get_position_value(row['Ticker']) for _, row in top_buys.iterrows()])
    
    action_items.append(f"2. BUY {positions_to_add} new P1 position(s) (10:00-10:30am, Total: ${total_deploy:,.0f})")
    
    # List specific positions with limit prices and shares (using custom allocations)
    for _, row in top_buys.iterrows():
        ticker = row['Ticker']
        friday_close = row['Close']
        
        # Get position value for this ticker (custom or default)
        ticker_position_value = get_position_value(ticker)
        ticker_allocation_pct = get_position_allocation(ticker)
        
        # Calculate shares from position size (based on Friday close)
        shares = int(ticker_position_value / friday_close)
        # Limit buy: Friday close + 1.5% (balanced approach)
        limit_price = friday_close * 1.015
        actual_cost = shares * limit_price
        
        # Show allocation if different from default
        alloc_note = f" [{ticker_allocation_pct}%]" if ticker_allocation_pct != position_size_pct else ""
        action_items.append(f"   - {ticker}{alloc_note}: BUY {shares} shares, Limit ${limit_price:.2f} (Fri: ${friday_close:.2f}) = ${actual_cost:,.0f}")
else:
    action_items.append("2. No new buys available - hold cash")
```

**REPLACE WITH THIS CODE:**

```python
# === FEATURE 1: ENHANCED BUY ACTION ITEMS (Risk-Adjusted with Pilots) ===
if len(p1_signals) > 0:
    current_positions = len(df_positions)
    positions_to_add = min(max_positions - current_positions, len(p1_signals))
    if strategy_week == 1 and current_positions == 0:
        positions_to_add = min(3, len(p1_signals))  # Week 1: Start with 3
    
    top_buys = p1_signals.head(positions_to_add)
    
    # Calculate risk-adjusted deployment
    conservative_deploy = 0
    full_deploy = 0
    buy_details = []
    
    for _, row in top_buys.iterrows():
        ticker = row['Ticker']
        friday_close = row['Close']
        support = row['Support']
        distance = row['To_Support_%']
        
        # Get position value for this ticker
        ticker_position_value = get_position_value(ticker)
        ticker_allocation_pct = get_position_allocation(ticker)
        full_deploy += ticker_position_value
        
        # Determine pilot sizing based on distance from support
        if distance < 3:
            pilot_pct = 100
            risk_label = '🟢 LOW'
        elif distance < 5:
            pilot_pct = 75
            risk_label = '🟢 LOW-MOD'
        elif distance < 10:
            pilot_pct = 50
            risk_label = '🟡 MODERATE'
        elif distance < 15:
            pilot_pct = 30
            risk_label = '🔴 HIGH'
        else:
            pilot_pct = 0
            risk_label = '⚫ V.HIGH'
        
        # Calculate pilot position
        pilot_value = ticker_position_value * pilot_pct / 100
        conservative_deploy += pilot_value
        
        # Calculate shares and prices
        if pilot_pct > 0:
            shares = int(pilot_value / friday_close)
            limit_price = friday_close * 1.015
            actual_cost = shares * limit_price
            
            # Add-on levels (near support)
            addon_low = support * 1.02
            addon_high = support * 1.05
            remaining_value = ticker_position_value - pilot_value
            
            alloc_note = f" [{ticker_allocation_pct}%]" if ticker_allocation_pct != position_size_pct else ""
            
            buy_details.append({
                'ticker': ticker,
                'alloc_note': alloc_note,
                'shares': shares,
                'limit_price': limit_price,
                'friday_close': friday_close,
                'actual_cost': actual_cost,
                'risk_label': risk_label,
                'distance': distance,
                'support': support,
                'pilot_pct': pilot_pct,
                'addon_low': addon_low,
                'addon_high': addon_high,
                'remaining': remaining_value
            })
    
    # Build action items with risk-adjusted sizing
    if conservative_deploy > 0:
        action_items.append(f"2. BUY {len(buy_details)} new P1 position(s) - RISK-ADJUSTED ENTRY")
        action_items.append(f"   Conservative: ${conservative_deploy:,.0f} | Full Target: ${full_deploy:,.0f}")
        action_items.append("")
        
        for detail in buy_details:
            action_items.append(f"   {detail['risk_label']} {detail['ticker']}{detail['alloc_note']}: BUY {detail['shares']} shares @ ${detail['limit_price']:.2f} = ${detail['actual_cost']:,.0f}")
            action_items.append(f"      • Risk: {detail['distance']:.1f}% above ${detail['support']:.2f} support")
            action_items.append(f"      • Strategy: PILOT {detail['pilot_pct']}% position Monday")
            if detail['remaining'] > 0:
                action_items.append(f"      • Add-on: ${detail['remaining']:,.0f} if dips to ${detail['addon_low']:.2f}-${detail['addon_high']:.2f} (still P1)")
            action_items.append("")
        
        # Add scaling reference
        action_items.append("   SCALING GUIDE: <5%=Full | 5-10%=50% | 10-15%=30% | >15%=Wait")
        action_items.append("   EXIT RULE: Sell ALL on N2 signal (regardless of pilot %)")
    else:
        action_items.append("2. BUY signals available but ALL > 15% extended - WAIT for dips")
        action_items.append("   Stocks too far from support. Consider waiting for pullbacks.")
else:
    action_items.append("2. No new buys available - hold cash")
```

---

## Testing

After adding the code, run the full notebook (cells 1-29) and check the generated PDF for:

✅ **Traffic Light Summary** - Shows counts of safe/moderate/extended stocks
✅ **Entry Risk Analysis** - Table with support distances and risk levels  
✅ **Enhanced Action Items** - Pilot position sizing with add-on triggers

## Expected Output Example

```
MARKET ENTRY CONDITIONS
Risk Level                    Count  Recommendation
🟢 SAFE (< 5%)               0      Full position OK
🟡 MODERATE (5-10%)          2      Scaled entry (50-75%)
🔴 EXTENDED (10-15%)         4      Small pilot (25-40%)
⚫ VERY EXTENDED (> 15%)     3      WAIT for dip

MARKET STATUS: EXTENDED - Use caution with position sizing

ENTRY RISK ANALYSIS
Stock  Current   Support   Distance  Risk         Entry Strategy
TSLA   $438.57   $382.78   +12.7%    🔴 HIGH     30% Pilot
NVDA   $187.05   $169.54   +9.4%     🟡 MODERATE 50% Pilot

ACTION ITEMS FOR MONDAY
2. BUY 3 new P1 positions - RISK-ADJUSTED ENTRY
   Conservative: $43,401 | Full Target: $88,000
   
   🔴 HIGH TSLA [50%]: BUY 60 shares @ $446.35 = $26,781
      • Risk: 12.7% above $382.78 support
      • Strategy: PILOT 50% position Monday
      • Add-on: $27,219 if dips to $390.44-$401.92 (still P1)
```

---

## Notes

- Uses existing support/resistance data from cell 7 calculation
- Respects variable position allocations (TSLA 50%, NVDA 20%, etc.)
- Automatically adjusts pilot sizing based on market conditions
- Maintains GHB exit discipline (N2 = sell all)
- PDF length increases by ~0.5-1 page (acceptable)

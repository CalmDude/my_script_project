# Portfolio Transaction Logic - Complete Guide

## Overview

This document explains the detailed logic behind buying and selling stocks in the Portfolio Manager system, including how average costs are calculated, how realized gains/losses are tracked, and how data flows through the system.

## Data Structure

### holdings.csv
Stores your current stock positions:
```csv
ticker,quantity,avg_cost,last_updated,min_quantity
TSLA,72,310.60,2026-01-04,0
NVDA,10,145.50,2026-01-08,0
```

**Fields:**
- `ticker`: Stock symbol (e.g., TSLA, NVDA, BTC-USD)
- `quantity`: Total shares owned (can have decimals for crypto)
- `avg_cost`: Average cost per share/unit
- `last_updated`: Date of last transaction (YYYY-MM-DD)
- `min_quantity`: Minimum position to maintain (usually 0)

### transactions.csv
Complete log of all buy/sell transactions:
```csv
date,type,ticker,quantity,price,total_value,notes
2026-01-08 10:30:15,BUY,NVDA,10,145.50,1455.00,New position
2026-01-09 14:22:33,SELL,NVDA,5,150.00,750.00,Realized P/L: $22.50 (+3.08%)
```

**Fields:**
- `date`: Timestamp of transaction
- `type`: BUY or SELL
- `ticker`: Stock symbol
- `quantity`: Shares bought/sold
- `price`: Price per share
- `total_value`: Quantity × Price
- `notes`: Additional information (realized P/L for sells)

## Buy Logic (Purchasing Stocks)

### Process Flow

1. **User Input**
   - Ticker symbol (e.g., NVDA)
   - Quantity to buy (e.g., 10 shares)
   - Purchase price per share (e.g., $145.50)
   - Date (defaults to today)

2. **Check Existing Position**
   ```python
   if ticker in holdings:
       # Update existing position
   else:
       # Create new position
   ```

3. **Calculate New Average Cost**
   - If new position: average cost = purchase price
   - If existing position: weighted average calculation

4. **Update Holdings**
   - Add quantity to existing quantity
   - Update average cost
   - Update last_updated date

5. **Log Transaction**
   - Write to transactions.csv with type=BUY

### Average Cost Calculation

**Formula:**
```
New Average Cost = (Old Total Cost + New Purchase Cost) / New Total Quantity

Where:
- Old Total Cost = Old Quantity × Old Average Cost
- New Purchase Cost = New Quantity × New Price
- New Total Quantity = Old Quantity + New Quantity
```

**Python Implementation:**
```python
def calculate_new_average(old_qty, old_cost, new_qty, new_price):
    if old_qty == 0:
        return new_price
    
    total_qty = old_qty + new_qty
    total_cost = (old_qty * old_cost) + (new_qty * new_price)
    return total_cost / total_qty
```

### Buy Examples

#### Example 1: First Purchase (New Position)
**Action:** Buy 10 NVDA @ $145.50

**Before:**
```csv
ticker,quantity,avg_cost
NVDA,0,0.00
```

**Calculation:**
- Old quantity: 0
- New quantity: 10
- Purchase price: $145.50
- Average cost: $145.50 (first purchase)

**After:**
```csv
ticker,quantity,avg_cost,last_updated
NVDA,10,145.50,2026-01-08
```

**Transaction Log:**
```csv
2026-01-08 10:30:00,BUY,NVDA,10,145.50,1455.00,New position
```

#### Example 2: Adding to Existing Position
**Action:** Buy 5 more NVDA @ $150.00

**Before:**
```csv
ticker,quantity,avg_cost
NVDA,10,145.50
```

**Calculation:**
```
Old Total Cost = 10 × $145.50 = $1,455.00
New Purchase Cost = 5 × $150.00 = $750.00
Total Cost = $1,455.00 + $750.00 = $2,205.00
Total Quantity = 10 + 5 = 15 shares
New Average Cost = $2,205.00 / 15 = $147.00
```

**After:**
```csv
ticker,quantity,avg_cost,last_updated
NVDA,15,147.00,2026-01-09
```

**Transaction Log:**
```csv
2026-01-09 11:15:00,BUY,NVDA,5,150.00,750.00,Updated position
```

#### Example 3: Buying at Lower Price (Dollar-Cost Averaging)
**Action:** Buy 10 more NVDA @ $140.00

**Before:**
```csv
ticker,quantity,avg_cost
NVDA,15,147.00
```

**Calculation:**
```
Old Total Cost = 15 × $147.00 = $2,205.00
New Purchase Cost = 10 × $140.00 = $1,400.00
Total Cost = $2,205.00 + $1,400.00 = $3,605.00
Total Quantity = 15 + 10 = 25 shares
New Average Cost = $3,605.00 / 25 = $144.20
```

**After:**
```csv
ticker,quantity,avg_cost,last_updated
NVDA,25,144.20,2026-01-10
```

**Note:** Buying at a lower price brings down the average cost!

## Sell Logic (Selling Stocks)

### Process Flow

1. **User Input**
   - Select ticker from dropdown (only shows holdings with quantity > 0)
   - Quantity to sell (cannot exceed current holdings)
   - Sell price per share
   - Date (defaults to today)

2. **Validation**
   - Verify ticker exists in holdings
   - Check quantity to sell ≤ current quantity
   - Ensure sell price > 0

3. **Calculate Realized Gain/Loss**
   ```
   Cost Basis = Average Cost × Quantity Sold
   Proceeds = Sell Price × Quantity Sold
   Realized Gain/Loss = Proceeds - Cost Basis
   Realized % = (Gain/Loss / Cost Basis) × 100
   ```

4. **Update Holdings**
   - Subtract quantity from current quantity
   - **Average cost remains unchanged**
   - Update last_updated date

5. **Log Transaction**
   - Write to transactions.csv with type=SELL
   - Include realized P/L in notes

### Why Average Cost Stays the Same

**Important:** When you sell shares, your average cost per share **does not change**. 

**Reason:** Average cost represents what you paid for the shares you still own. Selling doesn't change what you originally paid for the remaining shares.

**Example:**
- You own 100 shares @ $50 average cost
- You sell 40 shares @ $60
- You still own 60 shares @ $50 average cost (unchanged)
- The $10 profit per share ($60 - $50) is your realized gain

### Realized vs Unrealized Gains

**Realized Gain/Loss (Locked In)**
- Occurs when you SELL
- Actual profit/loss in your account
- Used for tax reporting
- Recorded in transactions.csv

**Unrealized Gain/Loss (Paper Gain/Loss)**
- Calculated on holdings you still own
- Current market value - cost basis
- Changes with market prices
- Shown in Holdings tab

### Sell Examples

#### Example 1: Partial Sale with Gain
**Action:** Sell 5 NVDA @ $150.00

**Before:**
```csv
ticker,quantity,avg_cost
NVDA,15,147.00
```

**Calculation:**
```
Quantity Sold: 5 shares
Average Cost: $147.00 per share
Sell Price: $150.00 per share

Cost Basis = 5 × $147.00 = $735.00
Proceeds = 5 × $150.00 = $750.00
Realized Gain = $750.00 - $735.00 = $15.00
Realized Gain % = ($15.00 / $735.00) × 100 = +2.04%
```

**After:**
```csv
ticker,quantity,avg_cost,last_updated
NVDA,10,147.00,2026-01-11
```

**Transaction Log:**
```csv
2026-01-11 14:30:00,SELL,NVDA,5,150.00,750.00,Realized P/L: $15.00 (+2.04%)
```

**Result:**
- Remaining position: 10 shares @ $147.00 avg cost
- Realized profit: $15.00

#### Example 2: Partial Sale with Loss
**Action:** Sell 5 NVDA @ $140.00

**Before:**
```csv
ticker,quantity,avg_cost
NVDA,10,147.00
```

**Calculation:**
```
Cost Basis = 5 × $147.00 = $735.00
Proceeds = 5 × $140.00 = $700.00
Realized Loss = $700.00 - $735.00 = -$35.00
Realized Loss % = (-$35.00 / $735.00) × 100 = -4.76%
```

**After:**
```csv
ticker,quantity,avg_cost,last_updated
NVDA,5,147.00,2026-01-12
```

**Transaction Log:**
```csv
2026-01-12 09:45:00,SELL,NVDA,5,140.00,700.00,Realized P/L: -$35.00 (-4.76%)
```

#### Example 3: Complete Position Exit
**Action:** Sell all 5 remaining NVDA @ $155.00

**Before:**
```csv
ticker,quantity,avg_cost
NVDA,5,147.00
```

**Calculation:**
```
Cost Basis = 5 × $147.00 = $735.00
Proceeds = 5 × $155.00 = $775.00
Realized Gain = $775.00 - $735.00 = $40.00
Realized Gain % = ($40.00 / $735.00) × 100 = +5.44%
```

**After:**
```csv
ticker,quantity,avg_cost,last_updated
NVDA,0,147.00,2026-01-13
```

**Transaction Log:**
```csv
2026-01-13 15:20:00,SELL,NVDA,5,155.00,775.00,Realized P/L: $40.00 (+5.44%)
```

**Note:** Quantity is now 0, but average cost is preserved for record-keeping.

## Complex Example: Complete Trading Scenario

Let's track a complete series of transactions for TSLA:

### Transaction 1: Initial Buy
**Date:** Jan 1, 2026  
**Action:** Buy 50 TSLA @ $200.00

**Holdings:**
```csv
ticker,quantity,avg_cost
TSLA,50,200.00
```

**Cost Basis:** $10,000.00

---

### Transaction 2: Add to Position
**Date:** Jan 5, 2026  
**Action:** Buy 30 TSLA @ $210.00

**Calculation:**
```
Old Cost: 50 × $200.00 = $10,000.00
New Cost: 30 × $210.00 = $6,300.00
Total: $16,300.00
Shares: 50 + 30 = 80
Avg: $16,300 / 80 = $203.75
```

**Holdings:**
```csv
ticker,quantity,avg_cost
TSLA,80,203.75
```

---

### Transaction 3: Partial Sale (Profit)
**Date:** Jan 10, 2026  
**Action:** Sell 30 TSLA @ $220.00

**Calculation:**
```
Cost Basis: 30 × $203.75 = $6,112.50
Proceeds: 30 × $220.00 = $6,600.00
Realized Gain: $6,600.00 - $6,112.50 = $487.50 (+7.97%)
```

**Holdings:**
```csv
ticker,quantity,avg_cost
TSLA,50,203.75
```

**Remaining Cost Basis:** 50 × $203.75 = $10,187.50

---

### Transaction 4: Average Down
**Date:** Jan 15, 2026  
**Action:** Buy 40 TSLA @ $190.00 (market dipped)

**Calculation:**
```
Old Cost: 50 × $203.75 = $10,187.50
New Cost: 40 × $190.00 = $7,600.00
Total: $17,787.50
Shares: 50 + 40 = 90
Avg: $17,787.50 / 90 = $197.64
```

**Holdings:**
```csv
ticker,quantity,avg_cost
TSLA,90,197.64
```

**Note:** Average cost decreased from $203.75 to $197.64 by buying at lower price!

---

### Transaction 5: Final Sale (Loss)
**Date:** Jan 20, 2026  
**Action:** Sell 90 TSLA @ $195.00 (exit position)

**Calculation:**
```
Cost Basis: 90 × $197.64 = $17,787.60
Proceeds: 90 × $195.00 = $17,550.00
Realized Loss: $17,550.00 - $17,787.60 = -$237.60 (-1.34%)
```

**Holdings:**
```csv
ticker,quantity,avg_cost
TSLA,0,197.64
```

---

### Summary of All TSLA Transactions

| Date | Type | Qty | Price | Total $ | Holdings After | Avg Cost | Realized P/L |
|------|------|-----|-------|---------|----------------|----------|--------------|
| Jan 1 | BUY | 50 | $200 | $10,000 | 50 | $200.00 | - |
| Jan 5 | BUY | 30 | $210 | $6,300 | 80 | $203.75 | - |
| Jan 10 | SELL | 30 | $220 | $6,600 | 50 | $203.75 | +$487.50 |
| Jan 15 | BUY | 40 | $190 | $7,600 | 90 | $197.64 | - |
| Jan 20 | SELL | 90 | $195 | $17,550 | 0 | $197.64 | -$237.60 |

**Total Invested:** $10,000 + $6,300 + $7,600 = $23,900  
**Total Proceeds:** $6,600 + $17,550 = $24,150  
**Net Profit:** $24,150 - $23,900 = **+$250.00**

**Individual Trade Results:**
- Trade 1 realized: +$487.50
- Trade 2 realized: -$237.60
- **Total realized: +$249.90** (rounding difference)

## Edge Cases and Special Scenarios

### Fractional Shares (Crypto)

**Example:** Bitcoin
```
Buy 0.5 BTC @ $50,000
Buy 0.3 BTC @ $48,000
```

**Calculation:**
```
Total Cost: (0.5 × $50,000) + (0.3 × $48,000)
         = $25,000 + $14,400 = $39,400
Total BTC: 0.5 + 0.3 = 0.8 BTC
Avg Cost: $39,400 / 0.8 = $49,250 per BTC
```

The logic works identically for fractional quantities!

### Zero Position After Sell

When you sell all shares:
- Quantity becomes 0
- Average cost is **preserved** for historical reference
- Position no longer shows in "active holdings"
- If you buy again, it creates a "new" position with new average

### Multiple Buys/Sells in One Day

Each transaction is logged separately:
```csv
2026-01-15 09:30:00,BUY,TSLA,10,200,2000,Morning buy
2026-01-15 14:45:00,SELL,TSLA,5,205,1025,Realized P/L: $25.00
2026-01-15 15:30:00,BUY,TSLA,3,198,594,Afternoon buy
```

Average cost updates with each transaction sequentially.

### Wash Sales (Tax Consideration)

**Important:** The system does NOT automatically track wash sales for tax purposes.

**Wash Sale Rule:** If you sell at a loss and repurchase the same stock within 30 days, the loss may be disallowed for taxes.

**Example:**
1. Jan 1: Sell 100 NVDA @ loss of -$500
2. Jan 15: Buy 100 NVDA again (within 30 days)
3. Result: The $500 loss may not be tax-deductible

**Recommendation:** Track wash sales manually or consult tax software.

## Data Flow Diagram

```
User Input (Buy/Sell)
        ↓
Validation & Calculations
        ↓
    ┌───────────────────┐
    ↓                   ↓
holdings.csv      transactions.csv
(Updated)         (New entry)
    ↓                   ↓
Holdings Tab      History Tab
Charts Tab        Reports
```

## Implementation Details

### File Updates

**Buy Transaction:**
1. Read holdings.csv
2. Calculate new average cost
3. Update quantity and avg_cost
4. Write holdings.csv
5. Append to transactions.csv

**Sell Transaction:**
1. Read holdings.csv
2. Calculate realized P/L
3. Update quantity (avg_cost unchanged)
4. Write holdings.csv
5. Append to transactions.csv with P/L notes

### Concurrency

**Single User:** No locking needed (you're the only user)

**If Multi-User (Future):** Would need:
- File locking mechanisms
- Transaction atomicity
- Conflict resolution

### Error Handling

**Invalid Inputs:**
- Negative quantity → Error
- Sell more than owned → Error
- Invalid ticker → Warning
- Price ≤ 0 → Error

**File Errors:**
- CSV not found → Create with headers
- Corrupt CSV → Log error, prompt restore from backup
- Write permission denied → Alert user

## Tax Reporting

### Information Available

From **transactions.csv** you can extract:
- All buy transactions (cost basis)
- All sell transactions (proceeds)
- Realized gains/losses per transaction
- Dates for short-term vs long-term determination

### Generating Tax Report

**Short-term gains** (held ≤ 1 year):
- Taxed as ordinary income
- Compare buy date to sell date in transactions.csv

**Long-term gains** (held > 1 year):
- Preferential tax rates
- Requires matching sells to specific buys (FIFO, LIFO, etc.)

### FIFO (First-In-First-Out)

**Current System:** Uses **average cost method**, NOT FIFO

**FIFO Example:**
```
Buy 10 shares @ $100 (Jan 1)
Buy 10 shares @ $120 (Feb 1)
Sell 10 shares @ $150 (Mar 1)

FIFO: Uses first purchase ($100 basis)
Avg Cost: Uses blended ($110 basis)
```

**Important:** For tax purposes, you may need to recalculate using FIFO or specific lot identification. Consult with tax professional.

## Performance Tracking

### Metrics Calculated

**Unrealized Gain/Loss** (in Holdings):
```
For each position:
  Current Value = Quantity × Current Price
  Cost Basis = Quantity × Average Cost
  Unrealized = Current Value - Cost Basis
  Unrealized % = (Unrealized / Cost Basis) × 100
```

**Realized Gain/Loss** (from History):
```
Sum all SELL transactions' realized P/L from notes
```

**Total Portfolio Return:**
```
Total Gain/Loss = Realized + Unrealized
Total Invested = Sum of all BUY amounts - Sum of all SELL proceeds
Return % = (Total Gain/Loss / Total Invested) × 100
```

## Best Practices

### Recording Transactions

1. **Record immediately** after execution
2. **Use actual prices** from broker confirmation
3. **Include fees** in price if desired (adjust price up/down by fee per share)
4. **Keep broker confirmations** as backup

### Review Periodically

1. **Daily:** Check unrealized P/L
2. **Weekly:** Review transaction history
3. **Monthly:** Reconcile with broker statements
4. **Quarterly:** Analyze realized gains for tax planning

### Backup

1. **Before large transactions:** Run backup script
2. **Weekly:** Backup transactions.csv
3. **Monthly:** Full project backup

## Troubleshooting

### Average Cost Doesn't Look Right

**Check:**
1. Review all BUY transactions for that ticker in History tab
2. Manually calculate: Total $ Spent / Total Shares
3. Compare with holdings.csv avg_cost field

**Common Issues:**
- Forgot to record a purchase
- Entered wrong price
- Commission/fees not included

### Realized P/L Doesn't Match Broker

**Reasons:**
1. **Broker uses FIFO**, we use average cost
2. **Commission/fees** included in broker calc
3. **Wash sale adjustment** applied by broker
4. **Different purchase dates** recorded

**Solution:** Track method in notes for tax time

## Summary

### Key Principles

1. **Average Cost Method:** Simplest and most common for individual investors
2. **Average Cost Doesn't Change on Sell:** It represents what you paid for remaining shares
3. **Realized vs Unrealized:** Only sells create realized (taxable) gains/losses
4. **Complete Logging:** Every transaction recorded with timestamp
5. **Historical Accuracy:** Even zero positions keep their average cost

### Formula Quick Reference

**Buy Average Cost:**
```
New Avg = (Old Qty × Old Avg + New Qty × New Price) / (Old Qty + New Qty)
```

**Sell Realized P/L:**
```
Realized P/L = (Sell Price - Avg Cost) × Quantity Sold
Realized % = (Realized P/L / (Avg Cost × Qty Sold)) × 100
```

**Unrealized P/L:**
```
Unrealized P/L = (Current Price - Avg Cost) × Quantity Owned
Unrealized % = (Unrealized P/L / (Avg Cost × Qty Owned)) × 100
```

---

## Related Documentation

- [Portfolio UI Guide](PORTFOLIO_UI.md) - Using the web interface
- [Backup Guide](BACKUP.md) - Protecting your data
- [README.md](../README.md) - Project overview

## Version

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**System Version:** Portfolio Analyzer v2.0

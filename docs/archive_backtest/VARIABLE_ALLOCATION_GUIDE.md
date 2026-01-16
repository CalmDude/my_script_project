# Variable Position Sizing Guide

## Overview
The GHB Portfolio Scanner now supports **variable position sizing** with custom allocations per ticker, allowing you to implement conviction-weighted portfolios.

## Configuration

### 1. Portfolio Settings File
Edit `data/portfolio_settings.json`:

```json
{
    "starting_cash": 110000,
    "position_size_pct": 10,
    "max_positions": 10,
    "strategy_week": 1,
    "conservative_mode": true,
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20
    }
}
```

### 2. Key Fields

| Field | Description | Example |
|-------|-------------|---------|
| `starting_cash` | Total portfolio capital | $110,000 |
| `position_size_pct` | **Default** allocation for stocks without custom sizing | 10% |
| `max_positions` | Maximum number of holdings | 10 |
| `position_allocations` | **Custom** allocations per ticker | TSLA: 50%, NVDA: 20% |

## How It Works

### Allocation Logic
1. **Custom Allocations**: If a ticker is in `position_allocations`, use that percentage
2. **Default Allocation**: Otherwise, use `position_size_pct` (10%)

### Example Portfolio Build

With the above configuration on $110,000 capital:

| Ticker | Allocation | Position Value | Type |
|--------|-----------|----------------|------|
| TSLA | 50% | $55,000 | Custom |
| NVDA | 20% | $22,000 | Custom |
| AMD | 10% | $11,000 | Default |
| GOOG | 10% | $11,000 | Default |
| ARM | 10% | $11,000 | Default |

**Total Deployed**: 100% ($110,000) across 5 positions

### Capacity Planning

- **Custom allocations**: 70% ($77,000) - TSLA + NVDA
- **Remaining capacity**: 30% ($33,000)
- **Additional 10% positions**: 3 more stocks

## Scanner Output

### Console Display
```
⚖️  Variable Position Sizing Enabled:
   TSLA: 50% allocation ($55,000)
   NVDA: 20% allocation ($22,000)
   Others: 10% default allocation
```

### Position Recommendations
```
💡 Top 3 Candidates with Allocations:
   1. TSLA: 50% = $55,000 @ $456.00 - 🔥 PULLBACK BUY
   2. NVDA: 20% = $22,000 @ $1,450.00 - ✅ HEALTHY BUY
   3. AMD: 10% = $11,000 @ $164.00 - ✅ HEALTHY BUY

🎯 Total to Deploy: $88,000
📊 New Portfolio Allocation: 80.0%
💵 Remaining Cash: $22,000
```

### PDF Report
Buy recommendations will show allocation if different from default:
```
2. BUY 3 new P1 position(s) (10:00-10:30am, Total: $88,000)
   - TSLA [50%]: BUY 120 shares, Limit $462.84 = $55,540
   - NVDA [20%]: BUY 15 shares, Limit $1,471.75 = $22,076
   - AMD: BUY 67 shares, Limit $166.46 = $11,152
```

## Best Practices

### 1. Conviction-Based Sizing
Use larger allocations (30-50%) for:
- **High conviction** stocks (TSLA, NVDA)
- **Portfolio core** holdings
- **Dominant position** thesis stocks

### 2. Risk Management
- **Don't exceed 50%** in any single stock (even with high conviction)
- **Keep 20-30% in cash** for new opportunities
- **Monitor total exposure**: Custom + Default allocations should not exceed 100%

### 3. Gradual Building
Week 1 example with variable sizing:
1. Enter TSLA (50% = $55,000) - Core position
2. Enter NVDA (20% = $22,000) - Secondary position
3. Enter 1 default stock (10% = $11,000)

**Total Week 1**: 80% deployed ($88,000), 20% cash reserve

### 4. Rebalancing
- **Stick to entry allocations**: Don't chase winners
- **Sell when N2 signal**: Exit full position regardless of size
- **Re-enter at same allocation**: If stock returns to P1

## Implementation Examples

### Conservative Portfolio (Moderate Concentration)
```json
"position_allocations": {
    "TSLA": 25,
    "NVDA": 20,
    "GOOG": 15
}
```
- Top 3 = 60%, remaining 40% for 4x 10% positions

### Aggressive Portfolio (High Concentration)
```json
"position_allocations": {
    "TSLA": 50,
    "NVDA": 20,
    "AMD": 15
}
```
- Top 3 = 85%, remaining 15% for 1-2 default positions

### Equal-Weight Portfolio (No Concentration)
```json
"position_allocations": {}
```
- All positions = 10% (legacy behavior)

## Portfolio Metrics

### With Variable Sizing ($110,000 capital)

| Configuration | TSLA | NVDA | Others | Total Stocks |
|---------------|------|------|--------|--------------|
| Example Setup | 50% ($55k) | 20% ($22k) | 3x 10% ($33k) | 5 positions |
| Max Capacity | 50% | 20% | 3x 10% | 5 positions |
| Week 1 Start | 50% | 20% | 1x 10% | 3 positions (80% deployed) |

### Without Variable Sizing (Legacy)
- All positions: 10% ($11,000 each)
- Max capacity: 10 positions
- Week 1 start: 3 positions (30% deployed)

## Monitoring & Tracking

The scanner automatically:
1. ✅ Calculates correct share quantities per allocation
2. ✅ Shows allocation percentages in recommendations
3. ✅ Tracks actual vs. target allocations
4. ✅ Generates PDF with custom sizing details
5. ✅ Applies GHB signals (P1/N2) equally to all position sizes

## Limitations

1. **Maximum 50% allocation recommended** (risk management)
2. **Must manually ensure allocations ≤ 100%** total
3. **Can't change allocation mid-position** (sell then re-enter at new size)
4. **Variable sizing doesn't change GHB signals** (same buy/sell rules apply)

## Migration from Equal-Weight

To transition from equal 10% positions:

1. **Review current holdings**: Which are core vs. satellite?
2. **Set target allocations**: 50% core, 20% secondary, 10% others
3. **Wait for P1 signals**: Don't force rebalancing
4. **Build gradually**: As you add new positions, use variable sizing
5. **Exit N2 normally**: When sold, re-enter at new allocation if/when P1 returns

---

## Quick Start

1. Edit `data/portfolio_settings.json`
2. Add `position_allocations` with your desired tickers and percentages
3. Run `ghb_portfolio_scanner.ipynb`
4. Scanner will automatically use custom allocations in all calculations
5. Monitor PDF reports for allocation-adjusted recommendations

**Remember**: Larger allocations = larger gains AND larger losses. Use variable sizing to express conviction, but maintain disciplined risk management.

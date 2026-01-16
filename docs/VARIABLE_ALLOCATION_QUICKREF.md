# Variable Allocation Quick Reference

## Configuration (data/portfolio_settings.json)

```json
{
    "starting_cash": 110000,
    "position_size_pct": 10,
    "position_allocations": {
        "TSLA": 50,
        "NVDA": 20
    }
}
```

## Results with $110,000 Capital

| Ticker | Allocation | $ Value | Type |
|--------|-----------|---------|------|
| TSLA | 50% | $55,000 | Custom |
| NVDA | 20% | $22,000 | Custom |
| AMD | 10% | $11,000 | Default |
| GOOG | 10% | $11,000 | Default |
| ARM | 10% | $11,000 | Default |

## Rules

✅ **DO**:
- Use 30-50% for high conviction stocks
- Keep some cash (20-30%) for opportunities
- Follow GHB signals (P1=BUY, N2=SELL) regardless of position size

❌ **DON'T**:
- Exceed 50% in any single stock
- Let total allocations exceed 100%
- Change allocation mid-position (exit then re-enter)

## Example Scenarios

### Conservative (Balanced)
```json
"position_allocations": {
    "TSLA": 25,
    "NVDA": 20
}
```
Result: 2 custom (45%) + 5-6 default (55%)

### Aggressive (Concentrated)
```json
"position_allocations": {
    "TSLA": 50,
    "NVDA": 20,
    "AMD": 15
}
```
Result: 3 custom (85%) + 1-2 default (15%)

### Equal Weight (Legacy)
```json
"position_allocations": {}
```
Result: All stocks 10% each

---

**Remember**: Variable sizing amplifies both gains AND losses. Use for conviction, not speculation.

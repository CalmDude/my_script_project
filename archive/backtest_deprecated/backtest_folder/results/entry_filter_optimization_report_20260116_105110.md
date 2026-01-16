# Entry Filter Optimization Report
Generated: 2026-01-16 10:51:10

## Test Configuration
- **Period**: 2021-01-01 to 2025-12-31 (4.5 years)
- **Universe**: 12 AI/Tech stocks
- **Variable Allocation**: TSLA 50%, NVDA 20%, Others 3.75%

## Results Summary

| Rank | Configuration | Threshold | CAGR | Total Return | Win Rate | Trades/Year | Max DD |
|------|--------------|-----------|------|--------------|----------|-------------|---------|
| 1 | Very Conservative | 7% | **2.48%** | 11.6% | 44.4% | 2.0 | -5.1% |
| 2 | Conservative (Current) | 10% | **0.54%** | 2.5% | 25.0% | 3.6 | -6.0% |
| 3 | Aggressive | 16% | **-0.48%** | -2.1% | 33.3% | 4.7 | -7.5% |
| 4 | No Filter | None | **-0.48%** | -2.1% | 33.3% | 4.7 | -7.5% |
| 5 | Moderate | 13% | **-0.95%** | -4.2% | 26.3% | 4.2 | -5.8% |

## Key Findings

### Winner: Very Conservative
- **Entry Filter**: To_Support_% < 7
- **CAGR**: 2.48%
- **Total Return**: 11.6%
- **Win Rate**: 44.4%
- **Trade Frequency**: 2.0 per year
- **Max Drawdown**: -5.1%

### Improvement vs Current (10% threshold)
- **CAGR Change**: +1.94 percentage points
- **Trade Frequency Change**: -1.6 trades/year
- **Win Rate Change**: +19.4 percentage points

## Recommendations

1. **Consider tightening entry filter** from 10% to 7%
   - Improves CAGR by 1.94 percentage points
   - Trade frequency: 2.0/year

---
*Full results saved to: backtest\results\entry_filter_optimization_20260116_105110.csv*
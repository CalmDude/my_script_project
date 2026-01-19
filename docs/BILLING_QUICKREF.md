# Copilot+ Billing Calculator - Quick Reference

## What It Does

Calculates your **next billing charge** for Copilot+ membership based on:
- **Base membership fee** (monthly subscription)
- **Overuse charges** (usage beyond included quota)

## Quick Start

```bash
# Run the calculator
python scripts/copilot_billing_calculator.py
```

## Example Output

```
COPILOT+ MEMBERSHIP BILLING REPORT
============================================================
Membership Tier: COPILOT_PLUS
Next Billing Date: 2026-02-01
Days Until Billing: 13

CHARGES BREAKDOWN
Base Membership Fee: USD 10.00
Overuse Charges:     USD 2.50
TOTAL CHARGE:        USD 12.50
```

## How It Calculates

1. **Base Fee**: Your monthly subscription (e.g., $10/month)
2. **Overuse**: 
   - If you use more than included requests (e.g., 1,000)
   - Charge per extra request (e.g., $0.01 per request)
   - Example: 1,250 used - 1,000 included = 250 × $0.01 = $2.50
3. **Total**: Base Fee + Overuse = $10.00 + $2.50 = **$12.50**

## Configuration Files

### Your Membership Settings
**File**: `data/copilot_billing_config.json`
```json
{
  "membership_tier": "copilot_plus",
  "monthly_fee": 10.00,
  "included_requests": 1000,
  "overage_rate_per_request": 0.01
}
```

### Your Usage Data
**File**: `data/copilot_usage.json`
```json
{
  "current_period_start": "2026-01-01",
  "total_requests": 1250
}
```

## Use Cases

1. **Before Billing**: Check upcoming charges
2. **Usage Monitoring**: Track if you're over quota
3. **Cost Planning**: Forecast monthly expenses
4. **Tier Comparison**: Compare different plans

## Warnings

- ✓ **Green** (0-80%): Within quota, you're good!
- ⚠️ **Yellow** (80-100%): Approaching limit
- ⚠️ **Red** (>100%): Over quota, extra charges apply

## Full Documentation

- **Complete Guide**: [docs/COPILOT_BILLING_GUIDE.md](../docs/COPILOT_BILLING_GUIDE.md)
- **Example Walkthrough**: [docs/BILLING_EXAMPLE.md](../docs/BILLING_EXAMPLE.md)
- **Main README**: [README.md](../README.md)

## Programmatic Usage

```python
from scripts.copilot_billing_calculator import CopilotBillingCalculator

# Create calculator
calc = CopilotBillingCalculator()

# Get charges
charges = calc.calculate_total_charges()
print(f"Total: ${charges['total_charge']:.2f}")

# Get full report
report = calc.generate_billing_report()
print(f"Next billing: {report['billing_summary']['next_billing_date']}")
```

## Support Different Tiers

Edit config for Pro tier:
```json
{
  "membership_tier": "copilot_pro",
  "monthly_fee": 25.00,
  "included_requests": 5000,
  "overage_rate_per_request": 0.005
}
```

## Common Questions

**Q: Where do I update my usage?**  
A: Edit `data/copilot_usage.json` and change `total_requests`

**Q: Can I change my billing day?**  
A: Yes, edit `billing_cycle_start` in config (1-28 recommended)

**Q: What if I'm under quota?**  
A: You'll only pay the base fee, no overuse charges

**Q: How do I test different scenarios?**  
A: Run `python scripts/test_copilot_billing.py` to see 5 examples

## Files Overview

```
scripts/
├── copilot_billing_calculator.py  # Main calculator
└── test_copilot_billing.py        # Test suite

data/
├── copilot_billing_config.json    # Your membership settings
└── copilot_usage.json              # Your usage tracking

docs/
├── COPILOT_BILLING_GUIDE.md       # Full documentation
├── BILLING_EXAMPLE.md             # Detailed example
└── BILLING_QUICKREF.md            # This file
```

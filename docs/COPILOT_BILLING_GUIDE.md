# Copilot+ Membership Billing Calculator Guide

## Overview

The Copilot+ Membership Billing Calculator helps you understand your upcoming charges based on:
- **Base membership fee**: Your monthly subscription cost
- **Overuse charges**: Additional charges for usage beyond your included quota

## Quick Start

### 1. Run the Calculator

```bash
# Activate your virtual environment (if using one)
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run the billing calculator
python scripts/copilot_billing_calculator.py
```

### 2. Sample Output

```
============================================================
COPILOT+ MEMBERSHIP BILLING REPORT
============================================================

Membership Tier: COPILOT_PLUS
Next Billing Date: 2026-02-01
Days Until Billing: 13

------------------------------------------------------------
CHARGES BREAKDOWN
------------------------------------------------------------
Base Membership Fee: USD 10.00
Overuse Charges:     USD 2.50
------------------------------------------------------------
TOTAL CHARGE:        USD 12.50
------------------------------------------------------------

------------------------------------------------------------
USAGE DETAILS
------------------------------------------------------------
Included Requests:   1,000
Requests Used:       1,250
Overuse Requests:    250
Overuse Rate:        USD 0.0100 per request
------------------------------------------------------------

Usage: 125.0% of included quota
⚠️  Warning: You are using 25.0% over your included quota

============================================================
```

## Configuration

### Billing Configuration (`data/copilot_billing_config.json`)

Customize your membership settings:

```json
{
  "membership_tier": "copilot_plus",
  "monthly_fee": 10.00,
  "included_requests": 1000,
  "overage_rate_per_request": 0.01,
  "billing_cycle_start": 1,
  "currency": "USD"
}
```

**Parameters:**
- `membership_tier`: Name of your membership plan (e.g., "copilot_plus", "copilot_pro")
- `monthly_fee`: Base monthly subscription cost
- `included_requests`: Number of requests included in the base plan
- `overage_rate_per_request`: Cost per request beyond included quota
- `billing_cycle_start`: Day of month when billing occurs (1-28)
- `currency`: Currency code (USD, EUR, GBP, etc.)

### Usage Data (`data/copilot_usage.json`)

Track your actual usage:

```json
{
  "current_period_start": "2026-01-01",
  "total_requests": 1250,
  "features_used": [
    "code_completion",
    "chat",
    "code_review"
  ],
  "daily_usage": {
    "2026-01-01": 45,
    "2026-01-02": 52
  }
}
```

**Parameters:**
- `current_period_start`: Start date of current billing period
- `total_requests`: Total requests used in current period
- `features_used`: List of features you've used
- `daily_usage`: Optional breakdown by day

## Membership Tiers

### Copilot Plus (Default)
- **Monthly Fee**: $10.00
- **Included Requests**: 1,000
- **Overage Rate**: $0.01 per request
- **Best For**: Individual developers with moderate usage

### Example Custom Tier (Pro)
```json
{
  "membership_tier": "copilot_pro",
  "monthly_fee": 25.00,
  "included_requests": 5000,
  "overage_rate_per_request": 0.005,
  "billing_cycle_start": 1,
  "currency": "USD"
}
```

## Billing Calculations

### Base Charge
Your base membership fee is charged every billing cycle regardless of usage.

### Overuse Calculation
```
Overuse Requests = Total Requests Used - Included Requests
Overuse Charge = Overuse Requests × Overage Rate
```

**Example:**
- Included: 1,000 requests
- Used: 1,250 requests
- Overuse: 250 requests
- Rate: $0.01 per request
- Overuse Charge: 250 × $0.01 = $2.50

### Total Charge
```
Total Charge = Base Membership Fee + Overuse Charge
```

**Example:**
- Base Fee: $10.00
- Overuse: $2.50
- **Total: $12.50**

## Usage Warnings

The calculator provides helpful warnings:

- **✓ Within Quota**: Using ≤80% of included requests
- **⚠️ Approaching Limit**: Using 80-100% of included requests  
- **⚠️ Over Quota**: Using >100% of included requests

## Integration with Your Workflow

### Option 1: Manual Check
Run the script periodically to check your charges:
```bash
python scripts/copilot_billing_calculator.py
```

### Option 2: Automated Updates
Update `data/copilot_usage.json` with your actual usage data:

```python
import json
from datetime import datetime

# Update usage
usage_data = {
    "current_period_start": "2026-01-01",
    "total_requests": 1500,  # Your actual usage
    "features_used": ["code_completion", "chat"],
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

with open('data/copilot_usage.json', 'w') as f:
    json.dump(usage_data, f, indent=2)
```

### Option 3: API Integration
Extend the calculator to fetch usage from an API:

```python
from scripts.copilot_billing_calculator import CopilotBillingCalculator

# Create calculator and update usage
calculator = CopilotBillingCalculator()
calculator.usage["total_requests"] = fetch_usage_from_api()
calculator.print_billing_report()
```

## Programmatic Usage

Use the calculator in your own scripts:

```python
from scripts.copilot_billing_calculator import CopilotBillingCalculator

# Initialize calculator
calculator = CopilotBillingCalculator()

# Get billing report
report = calculator.generate_billing_report()

# Access specific data
next_billing = report["billing_summary"]["next_billing_date"]
total_charge = report["charges"]["total_charge"]
overuse = report["usage_details"]["overuse_requests"]

print(f"Next billing: {next_billing}")
print(f"Total charge: ${total_charge:.2f}")
print(f"Overuse: {overuse} requests")

# Calculate charges
charges = calculator.calculate_total_charges()
print(f"Membership fee: ${charges['membership_fee']:.2f}")
print(f"Overuse charge: ${charges['overuse_charge']:.2f}")
```

## Common Scenarios

### Scenario 1: Within Included Quota
```
Included: 1,000 requests
Used: 750 requests
Overuse: 0 requests
Total Charge: $10.00 (base fee only)
```

### Scenario 2: Exactly at Limit
```
Included: 1,000 requests
Used: 1,000 requests
Overuse: 0 requests
Total Charge: $10.00 (base fee only)
```

### Scenario 3: Moderate Overuse
```
Included: 1,000 requests
Used: 1,250 requests
Overuse: 250 requests
Overuse Charge: 250 × $0.01 = $2.50
Total Charge: $10.00 + $2.50 = $12.50
```

### Scenario 4: Heavy Overuse
```
Included: 1,000 requests
Used: 2,500 requests
Overuse: 1,500 requests
Overuse Charge: 1,500 × $0.01 = $15.00
Total Charge: $10.00 + $15.00 = $25.00
```

## Tips for Managing Costs

1. **Monitor Regularly**: Check your usage weekly to avoid surprises
2. **Set Alerts**: Create reminders when you reach 80% of quota
3. **Upgrade if Needed**: If consistently over quota, consider a higher tier
4. **Track Patterns**: Use `daily_usage` to identify high-usage days
5. **Optimize Usage**: Review which features consume most requests

## Troubleshooting

### Configuration Not Found
If config file is missing, the calculator uses default values:
- Monthly Fee: $10.00
- Included Requests: 1,000
- Overage Rate: $0.01 per request

### Usage Data Not Found
If usage file is missing, the calculator assumes:
- Total Requests: 0
- No overuse charges

### Custom Billing Day
To change your billing day, update `billing_cycle_start` in config:
```json
{
  "billing_cycle_start": 15  // Bill on 15th of each month
}
```

### Different Currency
Update the `currency` field:
```json
{
  "currency": "EUR"  // or GBP, CAD, etc.
}
```

## Support

For questions or issues:
1. Check this documentation
2. Review sample configuration files
3. Run with default values to test
4. Verify JSON files are valid

## License

MIT License - See main README.md for details

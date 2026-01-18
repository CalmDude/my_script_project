# Example: Calculate Your Next Billing Charge

This example demonstrates how to use the Copilot+ billing calculator to determine
how much you will be charged at the next billing date.

## Scenario

You have a Copilot+ membership with:
- **Monthly fee**: $10.00
- **Included requests**: 1,000 per month
- **Overuse rate**: $0.01 per additional request

You've used **1,250 requests** this billing period (250 over your quota).

## Question

**"I have a copilot+ membership and I want to know how much I will be charged 
at the next billing date based on membership fee and overuse"**

## Answer

Run the billing calculator:

```bash
python scripts/copilot_billing_calculator.py
```

## Result

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
```

## Calculation Breakdown

1. **Base Membership Fee**: $10.00
   - This is your monthly subscription cost

2. **Overuse Calculation**:
   - Included requests: 1,000
   - Total used: 1,250
   - Overuse: 1,250 - 1,000 = 250 requests
   - Overuse charge: 250 × $0.01 = $2.50

3. **Total Charge**: $10.00 + $2.50 = **$12.50**

## Customization

To customize for your specific membership and usage:

1. Edit `data/copilot_billing_config.json`:
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

2. Edit `data/copilot_usage.json`:
   ```json
   {
     "current_period_start": "2026-01-01",
     "total_requests": 1250
   }
   ```

3. Run the calculator again to see your personalized charges!

## More Information

See [COPILOT_BILLING_GUIDE.md](../docs/COPILOT_BILLING_GUIDE.md) for:
- Different membership tiers
- Advanced configuration options
- Integration with your workflow
- Cost optimization tips

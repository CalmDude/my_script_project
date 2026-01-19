"""
Copilot+ Membership Billing Calculator

Calculate total charges for Copilot+ membership based on:
- Base membership fee
- Overuse/overage charges beyond included quota

Usage:
    python copilot_billing_calculator.py
    
Configuration:
    Reads from ../data/copilot_billing_config.json
    Reads usage from ../data/copilot_usage.json
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class CopilotBillingCalculator:
    """Calculate Copilot+ membership billing charges"""
    
    def __init__(self, config_path=None, usage_path=None):
        """
        Initialize billing calculator
        
        Args:
            config_path: Path to billing configuration JSON
            usage_path: Path to usage data JSON
        """
        script_dir = Path(__file__).parent
        
        if config_path is None:
            config_path = script_dir.parent / 'data' / 'copilot_billing_config.json'
        if usage_path is None:
            usage_path = script_dir.parent / 'data' / 'copilot_usage.json'
            
        self.config = self._load_config(config_path)
        self.usage = self._load_usage(usage_path)
        
    def _load_config(self, path):
        """Load billing configuration"""
        if not os.path.exists(path):
            # Return default configuration
            return {
                "membership_tier": "copilot_plus",
                "monthly_fee": 10.00,
                "included_requests": 1000,
                "overage_rate_per_request": 0.01,
                "billing_cycle_start": 1,  # Day of month
                "currency": "USD"
            }
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def _load_usage(self, path):
        """Load usage data"""
        if not os.path.exists(path):
            # Return default usage
            return {
                "current_period_start": datetime.now().strftime("%Y-%m-%d"),
                "total_requests": 0,
                "features_used": []
            }
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def calculate_next_billing_date(self):
        """Calculate the next billing date"""
        today = datetime.now()
        billing_day = self.config.get("billing_cycle_start", 1)
        
        # Validate billing_day is in safe range (1-28)
        if not isinstance(billing_day, int) or billing_day < 1 or billing_day > 28:
            billing_day = 1  # Default to 1st of month if invalid
        
        # If today's day is before billing day, next billing is this month
        if today.day < billing_day:
            try:
                next_billing = datetime(today.year, today.month, billing_day)
            except ValueError:
                # Handle invalid date (e.g., Feb 30), use last day of month
                if today.month == 12:
                    next_billing = datetime(today.year + 1, 1, 1)
                else:
                    next_billing = datetime(today.year, today.month + 1, 1)
        else:
            # Otherwise, next billing is next month
            try:
                if today.month == 12:
                    next_billing = datetime(today.year + 1, 1, billing_day)
                else:
                    next_billing = datetime(today.year, today.month + 1, billing_day)
            except ValueError:
                # Handle invalid date, use first day of following month
                if today.month == 12:
                    next_billing = datetime(today.year + 1, 2, 1)
                else:
                    next_billing = datetime(today.year, today.month + 2, 1) if today.month < 11 else datetime(today.year + 1, 1, 1)
        
        return next_billing
    
    def calculate_overuse(self):
        """Calculate overuse charges"""
        included = self.config.get("included_requests", 1000)
        total_used = self.usage.get("total_requests", 0)
        overage_rate = self.config.get("overage_rate_per_request", 0.01)
        
        overuse_requests = max(0, total_used - included)
        overuse_charge = overuse_requests * overage_rate
        
        return {
            "included_requests": included,
            "total_requests": total_used,
            "overuse_requests": overuse_requests,
            "overuse_rate": overage_rate,
            "overuse_charge": overuse_charge
        }
    
    def calculate_total_charges(self):
        """Calculate total charges for next billing date"""
        membership_fee = self.config.get("monthly_fee", 10.00)
        overuse_data = self.calculate_overuse()
        overuse_charge = overuse_data["overuse_charge"]
        
        total_charge = membership_fee + overuse_charge
        
        return {
            "membership_fee": membership_fee,
            "overuse_charge": overuse_charge,
            "total_charge": total_charge,
            "currency": self.config.get("currency", "USD"),
            "overuse_details": overuse_data
        }
    
    def generate_billing_report(self):
        """Generate detailed billing report"""
        next_billing_date = self.calculate_next_billing_date()
        charges = self.calculate_total_charges()
        
        report = {
            "billing_summary": {
                "membership_tier": self.config.get("membership_tier", "copilot_plus"),
                "next_billing_date": next_billing_date.strftime("%Y-%m-%d"),
                "days_until_billing": (next_billing_date - datetime.now()).days,
                "currency": charges["currency"]
            },
            "charges": {
                "base_membership_fee": charges["membership_fee"],
                "overuse_charge": charges["overuse_charge"],
                "total_charge": charges["total_charge"]
            },
            "usage_details": {
                "included_requests": charges["overuse_details"]["included_requests"],
                "requests_used": charges["overuse_details"]["total_requests"],
                "overuse_requests": charges["overuse_details"]["overuse_requests"],
                "overuse_rate_per_request": charges["overuse_details"]["overuse_rate"]
            }
        }
        
        return report
    
    def print_billing_report(self):
        """Print formatted billing report"""
        report = self.generate_billing_report()
        currency = report["billing_summary"]["currency"]
        
        print("=" * 60)
        print("COPILOT+ MEMBERSHIP BILLING REPORT")
        print("=" * 60)
        print()
        
        print(f"Membership Tier: {report['billing_summary']['membership_tier'].upper()}")
        print(f"Next Billing Date: {report['billing_summary']['next_billing_date']}")
        print(f"Days Until Billing: {report['billing_summary']['days_until_billing']}")
        print()
        
        print("-" * 60)
        print("CHARGES BREAKDOWN")
        print("-" * 60)
        print(f"Base Membership Fee: {currency} {report['charges']['base_membership_fee']:.2f}")
        print(f"Overuse Charges:     {currency} {report['charges']['overuse_charge']:.2f}")
        print("-" * 60)
        print(f"TOTAL CHARGE:        {currency} {report['charges']['total_charge']:.2f}")
        print("-" * 60)
        print()
        
        print("-" * 60)
        print("USAGE DETAILS")
        print("-" * 60)
        print(f"Included Requests:   {report['usage_details']['included_requests']:,}")
        print(f"Requests Used:       {report['usage_details']['requests_used']:,}")
        print(f"Overuse Requests:    {report['usage_details']['overuse_requests']:,}")
        if report['usage_details']['overuse_requests'] > 0:
            print(f"Overuse Rate:        {currency} {report['usage_details']['overuse_rate_per_request']:.4f} per request")
        print("-" * 60)
        print()
        
        # Usage percentage
        usage_pct = (report['usage_details']['requests_used'] / 
                    report['usage_details']['included_requests'] * 100)
        print(f"Usage: {usage_pct:.1f}% of included quota")
        
        if usage_pct > 100:
            print(f"⚠️  Warning: You are using {usage_pct - 100:.1f}% over your included quota")
        elif usage_pct > 80:
            print("⚠️  Warning: You are approaching your included quota limit")
        else:
            print("✓ You are within your included quota")
        
        print()
        print("=" * 60)


def main():
    """Main function to run billing calculator"""
    print("Copilot+ Membership Billing Calculator")
    print()
    
    calculator = CopilotBillingCalculator()
    calculator.print_billing_report()


if __name__ == "__main__":
    main()

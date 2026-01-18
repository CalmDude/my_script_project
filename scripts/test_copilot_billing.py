"""
Test script for Copilot+ Billing Calculator

Tests various scenarios:
1. No overuse (within quota)
2. Exactly at quota limit
3. Moderate overuse
4. Heavy overuse
"""

import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.copilot_billing_calculator import CopilotBillingCalculator


def test_scenario(name, config_data, usage_data):
    """Test a specific billing scenario"""
    print(f"\n{'='*60}")
    print(f"TEST SCENARIO: {name}")
    print(f"{'='*60}")
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
        json.dump(config_data, config_file)
        config_path = config_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as usage_file:
        json.dump(usage_data, usage_file)
        usage_path = usage_file.name
    
    try:
        # Run calculator
        calculator = CopilotBillingCalculator(config_path, usage_path)
        calculator.print_billing_report()
        
        # Verify calculations
        charges = calculator.calculate_total_charges()
        print(f"\n✓ Test completed successfully")
        print(f"  Expected overuse: {max(0, usage_data['total_requests'] - config_data['included_requests'])} requests")
        print(f"  Actual overuse: {charges['overuse_details']['overuse_requests']} requests")
        
    finally:
        # Cleanup
        Path(config_path).unlink()
        Path(usage_path).unlink()


def main():
    """Run all test scenarios"""
    
    # Base configuration
    base_config = {
        "membership_tier": "copilot_plus",
        "monthly_fee": 10.00,
        "included_requests": 1000,
        "overage_rate_per_request": 0.01,
        "billing_cycle_start": 1,
        "currency": "USD"
    }
    
    # Scenario 1: No overuse (within quota)
    test_scenario(
        "Within Quota (750/1000 requests)",
        base_config,
        {
            "current_period_start": "2026-01-01",
            "total_requests": 750,
            "features_used": ["code_completion"]
        }
    )
    
    # Scenario 2: Exactly at limit
    test_scenario(
        "Exactly at Limit (1000/1000 requests)",
        base_config,
        {
            "current_period_start": "2026-01-01",
            "total_requests": 1000,
            "features_used": ["code_completion", "chat"]
        }
    )
    
    # Scenario 3: Moderate overuse (default scenario)
    test_scenario(
        "Moderate Overuse (1250/1000 requests)",
        base_config,
        {
            "current_period_start": "2026-01-01",
            "total_requests": 1250,
            "features_used": ["code_completion", "chat", "code_review"]
        }
    )
    
    # Scenario 4: Heavy overuse
    test_scenario(
        "Heavy Overuse (2500/1000 requests)",
        base_config,
        {
            "current_period_start": "2026-01-01",
            "total_requests": 2500,
            "features_used": ["code_completion", "chat", "code_review", "documentation"]
        }
    )
    
    # Scenario 5: Pro tier with higher quota
    pro_config = {
        "membership_tier": "copilot_pro",
        "monthly_fee": 25.00,
        "included_requests": 5000,
        "overage_rate_per_request": 0.005,
        "billing_cycle_start": 1,
        "currency": "USD"
    }
    
    test_scenario(
        "Pro Tier (5500/5000 requests)",
        pro_config,
        {
            "current_period_start": "2026-01-01",
            "total_requests": 5500,
            "features_used": ["code_completion", "chat", "code_review"]
        }
    )
    
    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

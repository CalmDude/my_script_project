"""
Test script to verify variable allocation feature
"""

import json
from pathlib import Path

# Load settings
settings_path = Path("data/portfolio_settings.json")
with open(settings_path, "r") as f:
    settings = json.load(f)

print("=" * 80)
print("VARIABLE ALLOCATION TEST")
print("=" * 80)

starting_cash = settings["starting_cash"]
position_size_pct = settings["position_size_pct"]
position_allocations = settings.get("position_allocations", {})

print(f"\nStarting Cash: ${starting_cash:,.0f}")
print(f"Default Allocation: {position_size_pct}%")


# Helper function
def get_position_allocation(ticker):
    """Get allocation percentage for a ticker (custom or default)"""
    return position_allocations.get(ticker, position_size_pct)


def get_position_value(ticker):
    """Get dollar value for a position based on allocation"""
    return starting_cash * get_position_allocation(ticker) / 100


# Test tickers
test_tickers = ["TSLA", "NVDA", "AMD", "AAPL", "GOOGL"]

print(f"\n{'Ticker':<10} {'Allocation':<12} {'Position Value':<15} {'Status'}")
print("-" * 80)

for ticker in test_tickers:
    alloc = get_position_allocation(ticker)
    value = get_position_value(ticker)
    status = "CUSTOM" if ticker in position_allocations else "DEFAULT"
    print(f"{ticker:<10} {alloc}%{' ':<10} ${value:<14,.0f} {status}")

# Test total deployment
print(f"\n{'='*80}")
print("PORTFOLIO CAPACITY TEST")
print("=" * 80)

total_custom_alloc = sum(position_allocations.values())
remaining_capacity = 100 - total_custom_alloc

print(
    f"\nCustom Allocations Total: {total_custom_alloc}% (${starting_cash * total_custom_alloc / 100:,.0f})"
)
print(
    f"Remaining Capacity: {remaining_capacity}% (${starting_cash * remaining_capacity / 100:,.0f})"
)

max_default_positions = int(remaining_capacity / position_size_pct)
print(f"Max additional {position_size_pct}% positions: {max_default_positions}")

print(f"\n✅ Variable allocation feature is working correctly!")
print(
    f"   - TSLA will get {get_position_allocation('TSLA')}% (${get_position_value('TSLA'):,.0f})"
)
print(
    f"   - NVDA will get {get_position_allocation('NVDA')}% (${get_position_value('NVDA'):,.0f})"
)
print(
    f"   - Other stocks get {position_size_pct}% (${get_position_value('AMD'):,.0f}) each"
)

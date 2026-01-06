"""Test Phase 2: Portfolio Position Management"""
from technical_analysis import (
    calculate_position_gap,
    calculate_buy_tranches,
    calculate_sell_tranches,
    determine_portfolio_action
)

print("=" * 80)
print("PHASE 2 TEST: Portfolio Position Management")
print("=" * 80)

# Test scenario
portfolio_total = 100000  # $100k portfolio
target_pct = 0.30  # Want 30% in TSLA
current_value = 20000  # Currently have $20k

print("\n=== Scenario ===")
print(f"Portfolio Total: ${portfolio_total:,}")
print(f"Target Allocation: {target_pct*100}%")
print(f"Current Position: ${current_value:,}")

# 1. Calculate position gap
print("\n=== 1. Position Gap Analysis ===")
gap = calculate_position_gap(current_value, target_pct, portfolio_total)
print(f"Current %: {gap['current_pct']*100:.1f}%")
print(f"Target $: ${gap['target_value']:,}")
print(f"Gap: ${gap['gap_value']:,} ({gap['gap_pct']*100:+.1f}%)")
print(f"Action Needed: {gap['action']}")

# 2. Calculate buy tranches
print("\n=== 2. Buy Tranches (if signal = FULL HOLD + ADD) ===")
s1, s2, s3 = 440, 420, 400
current_price = 450
buy_quality = "EXCELLENT"

buy_tranches = calculate_buy_tranches(gap['gap_value'], s1, s2, s3, current_price, buy_quality)
print(f"Need to buy: ${gap['gap_value']:,}")
print(f"Current price: ${current_price}")
print(f"Buy quality: {buy_quality}")
print("\nTranches:")
for price, amount, level, status in buy_tranches:
    if price == "WAIT":
        print(f"  → {status}")
    else:
        print(f"  → ${amount:,.0f} at ${price:.2f} ({level}) - {status}")

# 3. Calculate sell tranches
print("\n=== 3. Sell Tranches (if signal = REDUCE) ===")
signal = "REDUCE"
r1, r2, r3 = 488, 474, 470
adjusted_r1, adjusted_r2, adjusted_r3 = 488, 474, 470  # No MA blocking

sell_tranches = calculate_sell_tranches(current_value, signal, r1, r2, r3, adjusted_r1, adjusted_r2, adjusted_r3)
print(f"Signal: {signal}")
print(f"Current position: ${current_value:,}")
print("\nTranches:")
total_reduction = 0
for price, amount, pct, level, status in sell_tranches:
    print(f"  → ${amount:,.0f} ({pct*100:.0f}%) at ${price:.2f} ({level}) - {status}")
    total_reduction += amount
print(f"\nTotal Reduction: ${total_reduction:,.0f} ({total_reduction/current_value*100:.0f}%)")
print(f"Remaining: ${current_value - total_reduction:,.0f}")

# 4. Determine action
print("\n=== 4. Action Determination ===")
for test_signal in ["FULL HOLD + ADD", "REDUCE", "HOLD", "CASH"]:
    action = determine_portfolio_action(test_signal, gap, buy_quality)
    print(f"{test_signal:20s} → {action}")

print("\n" + "=" * 80)
print("✅ Phase 2 Complete!")
print("=" * 80)

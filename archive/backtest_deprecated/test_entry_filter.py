"""
Quick test to verify entry filter is working
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Test with 7% threshold
print("=" * 80)
print("TEST 1: 7% threshold (conservative)")
print("=" * 80)

config_path = Path("backtest/config.json")
with open(config_path, "r") as f:
    config = json.load(f)

config["strategy_settings"]["max_support_distance"] = 7

with open("backtest/test_config_7pct.json", "w") as f:
    json.dump(config, f, indent=2)

from run_ghb_scanner_backtest import ScannerBacktestEngine

engine = ScannerBacktestEngine("backtest/test_config_7pct.json")
try:
    result = engine.run(force_refresh_data=False)
    print(f"\n✅ Test 1 complete - check results file: {result.get('summary_file')}")
except Exception as e:
    print(f"\n⚠️ Test 1 warning: {str(e)}")
    result = None

# Cleanup
Path("backtest/test_config_7pct.json").unlink(missing_ok=True)

# Test with 15% threshold
print("\n" + "=" * 80)
print("TEST 2: 15% threshold (moderate)")
print("=" * 80)

with open(config_path, "r") as f:
    config = json.load(f)

config["strategy_settings"]["max_support_distance"] = 15

with open("backtest/test_config_15pct.json", "w") as f:
    json.dump(config, f, indent=2)

# Need to reimport to clear cached module
import importlib
import run_ghb_scanner_backtest

importlib.reload(run_ghb_scanner_backtest)

from run_ghb_scanner_backtest import ScannerBacktestEngine as Engine2

engine2 = Engine2("backtest/test_config_15pct.json")
try:
    result2 = engine2.run(force_refresh_data=False)
    print(f"\n✅ Test 2 complete - check results file: {result2.get('summary_file')}")
except Exception as e:
    print(f"\n⚠️ Test 2 warning: {str(e)}")
    result2 = None

# Cleanup
Path("backtest/test_config_15pct.json").unlink(missing_ok=True)

print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)

if result and result2:
    # Load both summary files
    with open(result.get("summary_file"), "r") as f:
        summary1 = json.load(f)

    with open(result2.get("summary_file"), "r") as f:
        summary2 = json.load(f)

    trades1 = summary1.get("Trading_Stats", {}).get("Total_Trades", 0)
    trades2 = summary2.get("Trading_Stats", {}).get("Total_Trades", 0)
    cagr1 = summary1.get("Performance", {}).get("CAGR_%", 0)
    cagr2 = summary2.get("Performance", {}).get("CAGR_%", 0)

    print(f"7% threshold:  CAGR = {cagr1:.2f}%, Trades = {trades1}")
    print(f"15% threshold: CAGR = {cagr2:.2f}%, Trades = {trades2}")

    if trades1 == trades2:
        print(
            "\n❌ FAIL: Both tests produced same number of trades - filter not working!"
        )
    else:
        print("\n✅ PASS: Different trade counts - filter is working correctly")
else:
    print("Cannot compare - one or both tests failed")

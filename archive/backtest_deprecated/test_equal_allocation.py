"""
Test entry filter with EQUAL allocation (no TSLA 50%)
This will show the true impact of the entry filter
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

# Test configurations with equal allocation
test_configs = [
    {"threshold": 10, "name": "10% Filter + Equal Allocation"},
    {"threshold": 15, "name": "15% Filter + Equal Allocation"},
    {"threshold": 999, "name": "No Filter + Equal Allocation"},
]

results = []

print("=" * 80)
print("ENTRY FILTER TEST - EQUAL ALLOCATION (No TSLA 50%)")
print("=" * 80)

for i, config in enumerate(test_configs, 1):
    threshold = config["threshold"]
    name = config["name"]

    print(f"\n[{i}/{len(test_configs)}] Testing: {name}")

    # Load config and remove variable allocation
    config_path = Path("backtest/config.json")
    with open(config_path, "r") as f:
        base_config = json.load(f)

    # REMOVE variable allocation
    base_config["portfolio_settings"]["position_allocations"] = {}

    # Set entry filter threshold
    if "strategy_settings" not in base_config:
        base_config["strategy_settings"] = {}
    base_config["strategy_settings"]["max_support_distance"] = threshold

    # Save temp config
    temp_config_path = Path(f"backtest/test_equal_{threshold}.json")
    with open(temp_config_path, "w") as f:
        json.dump(base_config, f, indent=2)

    # Run backtest
    try:
        from run_ghb_scanner_backtest import ScannerBacktestEngine
        import importlib
        import run_ghb_scanner_backtest

        importlib.reload(run_ghb_scanner_backtest)
        from run_ghb_scanner_backtest import ScannerBacktestEngine as Engine

        engine = Engine(str(temp_config_path))
        result = engine.run(force_refresh_data=False)

        # Load summary
        with open(result.get("summary_file"), "r") as f:
            summary = json.load(f)

        perf = summary.get("Performance", {})
        trades = summary.get("Trading_Stats", {})

        result_data = {
            "name": name,
            "threshold": threshold,
            "cagr": perf.get("CAGR_%", 0),
            "final_value": perf.get("Final_Value", 0),
            "total_trades": trades.get("Total_Trades", 0),
            "win_rate": trades.get("Win_Rate_%", 0),
            "trades_per_year": trades.get("Total_Trades", 0) / 4.5,
        }

        results.append(result_data)

        print(f"  CAGR: {result_data['cagr']:.2f}%")
        print(
            f"  Trades: {result_data['total_trades']} ({result_data['trades_per_year']:.1f}/year)"
        )
        print(f"  Win Rate: {result_data['win_rate']:.1f}%")

    except Exception as e:
        print(f"  ERROR: {str(e)}")

    # Cleanup
    temp_config_path.unlink(missing_ok=True)

print("\n" + "=" * 80)
print("SUMMARY: Entry Filter Impact with EQUAL Allocation")
print("=" * 80)

import pandas as pd

df = pd.DataFrame(results)
print(df.to_string(index=False))

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("This shows the REAL impact of the entry filter without the")
print("TSLA 50% allocation dragging down performance.")
print("=" * 80)

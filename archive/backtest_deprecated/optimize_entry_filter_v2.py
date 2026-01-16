"""
Entry Filter Optimization for GHB Portfolio Scanner (v2 - Simple ASCII)
Tests different To_Support_% thresholds to find optimal risk/return balance
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys

# Add backtest directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test configurations
test_configs = [
    {"threshold": 7, "name": "Very Conservative"},
    {"threshold": 10, "name": "Conservative (Current)"},
    {"threshold": 13, "name": "Moderate"},
    {"threshold": 16, "name": "Aggressive"},
    {"threshold": 999, "name": "No Filter"},
]

# Results storage
results = []

print("=" * 80)
print("GHB ENTRY FILTER OPTIMIZATION")
print("=" * 80)
print(f"Testing {len(test_configs)} entry filter configurations")
print(f"Period: 2021-2025 (4.5 years)")
print("=" * 80)

# Run backtest for each configuration
for i, config in enumerate(test_configs, 1):
    threshold = config["threshold"]
    name = config["name"]

    print(f"\n[{i}/{len(test_configs)}] Testing: {name} (threshold={threshold}%)")

    # Load base config
    config_path = Path("backtest/config.json")
    with open(config_path, "r") as f:
        base_config = json.load(f)

    # Update threshold in strategy_settings
    if "strategy_settings" not in base_config:
        base_config["strategy_settings"] = {}
    base_config["strategy_settings"]["max_support_distance"] = threshold

    # Save temporary config
    temp_config_path = Path("backtest/temp_config.json")
    with open(temp_config_path, "w") as f:
        json.dump(base_config, f, indent=2)

    # Run backtest
    try:
        from run_ghb_scanner_backtest import ScannerBacktestEngine

        engine = ScannerBacktestEngine(str(temp_config_path))
        try:
            backtest_results = engine.run(force_refresh_data=False)

            # Load saved summary file
            summary_file = backtest_results.get("summary_file")
            if summary_file and Path(summary_file).exists():
                with open(summary_file, "r") as f:
                    summary = json.load(f)

                # Extract metrics from summary (use nested structure)
                perf = summary.get("Performance", {})
                trades = summary.get("Trading_Stats", {})

                result = {
                    "threshold": threshold,
                    "name": name,
                    "final_value": perf.get("Final_Value", 0),
                    "total_return_pct": perf.get("Total_Return_%", 0),
                    "cagr": perf.get("CAGR_%", 0),
                    "max_drawdown": perf.get("Max_Drawdown_%", 0),
                    "win_rate": trades.get("Win_Rate_%", 0),
                    "total_trades": trades.get("Total_Trades", 0),
                    "avg_trades_per_year": trades.get("Total_Trades", 0) / 4.5,
                }

                results.append(result)

                print(
                    f"    COMPLETE: CAGR {result['cagr']:.2f}% | {result['total_trades']} trades | Win Rate {result['win_rate']:.1f}%"
                )
            else:
                print(f"    ERROR: Could not find summary file")

        except KeyError as ke:
            # Handle case where backtest produced no trades
            print(f"    SKIPPED: Too few trades (threshold too strict)")
            result = {
                "threshold": threshold,
                "name": name,
                "final_value": 0,
                "total_return_pct": 0,
                "cagr": 0,
                "max_drawdown": 0,
                "win_rate": 0,
                "total_trades": 0,
                "avg_trades_per_year": 0,
            }
            results.append(result)

    except Exception as e:
        print(f"    ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        continue

    # Clean up temp config
    if temp_config_path.exists():
        temp_config_path.unlink()

# Create results DataFrame
if len(results) == 0:
    print("\nNo results to analyze!")
    sys.exit(1)

df_results = pd.DataFrame(results)

# Sort by CAGR
df_results_sorted = df_results.sort_values("cagr", ascending=False).reset_index(
    drop=True
)

# Display results
print("\n" + "=" * 80)
print("OPTIMIZATION RESULTS (Ranked by CAGR)")
print("=" * 80)
print(df_results_sorted.to_string(index=False))

# Save detailed results
results_dir = Path("backtest/results")
results_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_file = results_dir / f"entry_filter_optimization_{timestamp}.csv"
df_results_sorted.to_csv(csv_file, index=False)

# Generate analysis report
best = df_results_sorted.iloc[0]
current = (
    df_results_sorted[df_results_sorted["threshold"] == 10].iloc[0]
    if len(df_results_sorted[df_results_sorted["threshold"] == 10]) > 0
    else None
)

report = []
report.append("# Entry Filter Optimization Report")
report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("")
report.append("## Test Configuration")
report.append("- **Period**: 2021-01-01 to 2025-12-31 (4.5 years)")
report.append("- **Universe**: 12 AI/Tech stocks")
report.append("- **Variable Allocation**: TSLA 50%, NVDA 20%, Others 3.75%")
report.append("")

report.append("## Results Summary")
report.append("")
report.append(
    "| Rank | Configuration | Threshold | CAGR | Total Return | Win Rate | Trades/Year | Max DD |"
)
report.append(
    "|------|--------------|-----------|------|--------------|----------|-------------|---------|"
)

for idx, row in df_results_sorted.iterrows():
    threshold_str = f"{row['threshold']:.0f}%" if row["threshold"] < 900 else "None"
    report.append(
        f"| {idx+1} | {row['name']} | {threshold_str} | **{row['cagr']:.2f}%** | {row['total_return_pct']:.1f}% | {row['win_rate']:.1f}% | {row['avg_trades_per_year']:.1f} | {row['max_drawdown']:.1f}% |"
    )

report.append("")
report.append("## Key Findings")
report.append("")

# Identify best performer
report.append(f"### Winner: {best['name']}")
report.append(
    f"- **Entry Filter**: {'To_Support_% < ' + str(best['threshold']) if best['threshold'] < 900 else 'No filter'}"
)
report.append(f"- **CAGR**: {best['cagr']:.2f}%")
report.append(f"- **Total Return**: {best['total_return_pct']:.1f}%")
report.append(f"- **Win Rate**: {best['win_rate']:.1f}%")
report.append(f"- **Trade Frequency**: {best['avg_trades_per_year']:.1f} per year")
report.append(f"- **Max Drawdown**: {best['max_drawdown']:.1f}%")
report.append("")

# Compare to current (10%)
if current is not None and not current.empty and best["threshold"] != 10:
    cagr_improvement = best["cagr"] - current["cagr"]
    trades_change = best["avg_trades_per_year"] - current["avg_trades_per_year"]

    report.append(f"### Improvement vs Current (10% threshold)")
    report.append(f"- **CAGR Change**: {cagr_improvement:+.2f} percentage points")
    report.append(f"- **Trade Frequency Change**: {trades_change:+.1f} trades/year")
    report.append(
        f"- **Win Rate Change**: {best['win_rate'] - current['win_rate']:+.1f} percentage points"
    )
    report.append("")

report.append("## Recommendations")
report.append("")

if best["threshold"] < 10:
    report.append(
        f"1. **Consider tightening entry filter** from 10% to {best['threshold']:.0f}%"
    )
    if current is not None and not current.empty:
        report.append(
            f"   - Improves CAGR by {best['cagr'] - current['cagr']:.2f} percentage points"
        )
    report.append(f"   - Trade frequency: {best['avg_trades_per_year']:.1f}/year")
elif best["threshold"] > 10 and best["threshold"] < 900:
    report.append(
        f"1. **Consider loosening entry filter** from 10% to {best['threshold']:.0f}%"
    )
    if current is not None and not current.empty:
        report.append(
            f"   - Improves CAGR by {best['cagr'] - current['cagr']:.2f} percentage points"
        )
    report.append(
        f"   - Increases opportunity: {best['avg_trades_per_year']:.1f} trades/year"
    )
elif best["threshold"] >= 900:
    report.append("1. **Consider removing entry filter completely**")
    if current is not None and not current.empty:
        report.append(
            f"   - Improves CAGR by {best['cagr'] - current['cagr']:.2f} percentage points"
        )
    report.append(
        f"   - Maximum opportunity: {best['avg_trades_per_year']:.1f} trades/year"
    )
else:
    report.append("1. **Current 10% threshold appears optimal**")

report.append("")
report.append("---")
report.append(f"*Full results saved to: {csv_file}*")

# Save report
report_file = results_dir / f"entry_filter_optimization_report_{timestamp}.md"
with open(report_file, "w") as f:
    f.write("\n".join(report))

print("\n" + "=" * 80)
print("OPTIMIZATION COMPLETE")
print("=" * 80)
print(f"Results CSV: {csv_file}")
print(f"Analysis Report: {report_file}")
print("")
print(f"Best Configuration: {best['name']}")
print(
    f"   Threshold: {'To_Support_% < ' + str(best['threshold']) if best['threshold'] < 900 else 'None'}"
)
print(f"   CAGR: {best['cagr']:.2f}%")
print(f"   Trades/Year: {best['avg_trades_per_year']:.1f}")
print("=" * 80)

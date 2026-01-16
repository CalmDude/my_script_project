"""
Entry Filter Optimization for GHB Portfolio Scanner
Tests different To_Support_% thresholds to find optimal risk/return balance

Tests:
- 5%: Very conservative (only LOW risk entries)
- 10%: Current scanner setting (LOW + LOW-MOD + MOD)
- 15%: Moderate (includes HIGH risk)
- 20%: Aggressive (includes extended entries)
- None: No filter (all P1 signals)
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from run_ghb_scanner_backtest import ScannerBacktestEngine

# Test configurations
test_configs = [
    {
        "threshold": 5,
        "name": "Very Conservative",
        "description": "Only LOW risk (<3%) and LOW-MOD (3-5%)",
    },
    {
        "threshold": 10,
        "name": "Conservative (Current)",
        "description": "LOW + LOW-MOD + MOD (<10%)",
    },
    {"threshold": 15, "name": "Moderate", "description": "Includes HIGH risk (10-15%)"},
    {
        "threshold": 20,
        "name": "Aggressive",
        "description": "Includes very extended entries",
    },
    {
        "threshold": None,
        "name": "No Filter",
        "description": "All P1 signals (maximum opportunity)",
    },
]

# Results storage
results = []

print("=" * 80)
print("GHB ENTRY FILTER OPTIMIZATION")
print("=" * 80)
print(f"Testing {len(test_configs)} entry filter configurations")
print(f"Period: 2021-2025 (4.5 years)")
print(f"Universe: 12 AI/Tech stocks")
print(f"Variable Allocation: TSLA 50%, NVDA 20%, Others 3.75%")
print("=" * 80)

# Run backtest for each configuration
for i, config in enumerate(test_configs, 1):
    threshold = config["threshold"]
    name = config["name"]

    print(f"\n[{i}/{len(test_configs)}] Testing: {name}")
    print(
        f"    Filter: {'To_Support_% < ' + str(threshold) if threshold else 'None (All P1 signals)'}"
    )

    # Load base config
    with open("backtest/config.json", "r") as f:
        base_config = json.load(f)

    # Update threshold in strategy_settings
    if "strategy_settings" not in base_config:
        base_config["strategy_settings"] = {}
    base_config["strategy_settings"]["max_support_distance"] = (
        threshold if threshold else 999
    )

    # Save temporary config
    temp_config_path = "backtest/temp_config.json"
    with open(temp_config_path, "w") as f:
        json.dump(base_config, f, indent=2)

    # Run backtest
    try:
        engine = ScannerBacktestEngine(temp_config_path)
        backtest_results = engine.run(force_refresh_data=False)

        # Load saved summary file
        summary_file = backtest_results.get("summary_file")
        if summary_file and Path(summary_file).exists():
            with open(summary_file, "r") as f:
                summary = json.load(f)

            # Extract metrics from summary
            result = {
                "threshold": threshold if threshold else 999,
                "name": name,
                "description": config["description"],
                "final_value": summary.get("final_value", 0),
                "total_return_pct": summary.get("total_return_pct", 0),
                "cagr": summary.get("cagr", 0),
                "max_drawdown": summary.get("max_drawdown", 0),
                "win_rate": summary.get("win_rate", 0),
                "total_trades": summary.get("total_trades", 0),
                "avg_trades_per_year": summary.get("total_trades", 0) / 4.5,
                "sharpe_ratio": summary.get("sharpe_ratio", 0),
                "profit_factor": summary.get("profit_factor", 0),
            }

            results.append(result)

            print(
                f"    ✅ Complete: CAGR {result['cagr']:.2f}% | {result['total_trades']} trades | Win Rate {result['win_rate']:.1f}%"
            )
        else:
            print(f"    ❌ Error: Could not find summary file")

    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        continue

    # Clean up temp config
    Path(temp_config_path).unlink(missing_ok=True)

# Create results DataFrame
df_results = pd.DataFrame(results)

# Sort by CAGR
df_results_sorted = df_results.sort_values("cagr", ascending=False).reset_index(
    drop=True
)

# Display results
print("\n" + "=" * 80)
print("OPTIMIZATION RESULTS (Ranked by CAGR)")
print("=" * 80)
print(
    df_results_sorted[
        [
            "name",
            "threshold",
            "cagr",
            "total_return_pct",
            "win_rate",
            "total_trades",
            "avg_trades_per_year",
            "max_drawdown",
        ]
    ].to_string(index=False)
)

# Save detailed results
results_dir = Path("backtest/results")
results_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_file = results_dir / f"entry_filter_optimization_{timestamp}.csv"
df_results_sorted.to_csv(csv_file, index=False)

# Generate analysis report
report = []
report.append("# Entry Filter Optimization Report")
report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("")
report.append("## Test Configuration")
report.append(f"- **Period**: 2021-01-01 to 2025-12-31 (4.5 years)")
report.append(
    f"- **Universe**: 12 AI/Tech stocks (ALAB, AMD, ARM, ASML, AVGO, GOOG, MRVL, MU, NVDA, PLTR, TSLA, TSM)"
)
report.append(f"- **Starting Cash**: $110,000")
report.append(f"- **Variable Allocation**: TSLA 50%, NVDA 20%, Others 3.75% each")
report.append(
    f"- **Risk-Adjusted Sizing**: Yes (100%/75%/50%/30%/0% based on distance)"
)
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
    threshold_str = f"{row['threshold']:.0f}%" if row["threshold"] < 999 else "None"
    report.append(
        f"| {idx+1} | {row['name']} | {threshold_str} | **{row['cagr']:.2f}%** | {row['total_return_pct']:.1f}% | {row['win_rate']:.1f}% | {row['avg_trades_per_year']:.1f} | {row['max_drawdown']:.1f}% |"
    )

report.append("")
report.append("## Key Findings")
report.append("")

# Identify best performer
best = df_results_sorted.iloc[0]
report.append(f"### 🏆 Optimal Configuration: {best['name']}")
report.append(
    f"- **Entry Filter**: {'To_Support_% < ' + str(best['threshold']) if best['threshold'] < 999 else 'No filter (all P1 signals)'}"
)
report.append(f"- **CAGR**: {best['cagr']:.2f}%")
report.append(f"- **Total Return**: {best['total_return_pct']:.1f}%")
report.append(f"- **Win Rate**: {best['win_rate']:.1f}%")
report.append(f"- **Trade Frequency**: {best['avg_trades_per_year']:.1f} per year")
report.append(f"- **Max Drawdown**: {best['max_drawdown']:.1f}%")
report.append("")

# Compare to current (10%)
current = (
    df_results_sorted[df_results_sorted["threshold"] == 10].iloc[0]
    if len(df_results_sorted[df_results_sorted["threshold"] == 10]) > 0
    else None
)
if current is not None and best["threshold"] != 10:
    cagr_improvement = best["cagr"] - current["cagr"]
    trades_change = best["avg_trades_per_year"] - current["avg_trades_per_year"]

    report.append(f"### 📊 Improvement vs Current (10% threshold)")
    report.append(f"- **CAGR Change**: {cagr_improvement:+.2f} percentage points")
    report.append(f"- **Trade Frequency Change**: {trades_change:+.1f} trades/year")
    report.append(
        f"- **Win Rate Change**: {best['win_rate'] - current['win_rate']:+.1f} percentage points"
    )
    report.append("")

# Risk-Return Analysis
report.append("### ⚖️ Risk-Return Trade-offs")
report.append("")

most_conservative = (
    df_results_sorted[df_results_sorted["threshold"] == 5].iloc[0]
    if len(df_results_sorted[df_results_sorted["threshold"] == 5]) > 0
    else None
)
no_filter = (
    df_results_sorted[df_results_sorted["threshold"] >= 999].iloc[0]
    if len(df_results_sorted[df_results_sorted["threshold"] >= 999]) > 0
    else None
)

if most_conservative is not None and no_filter is not None:
    report.append(f"**Conservative (5%) vs No Filter:**")
    report.append(
        f"- CAGR difference: {abs(most_conservative['cagr'] - no_filter['cagr']):.2f} percentage points"
    )
    report.append(
        f"- Trade opportunity cost: {no_filter['avg_trades_per_year'] - most_conservative['avg_trades_per_year']:.1f} trades/year lost"
    )
    report.append(
        f"- Risk reduction: Max DD {most_conservative['max_drawdown']:.1f}% vs {no_filter['max_drawdown']:.1f}%"
    )
    report.append("")

report.append("## Recommendations")
report.append("")

if best["threshold"] < 10:
    report.append(
        f"1. **Consider tightening entry filter** from 10% to {best['threshold']:.0f}%"
    )
    report.append(
        f"   - Improves CAGR by {best['cagr'] - current['cagr']:.2f} percentage points"
    )
    report.append(f"   - Reduces drawdown risk")
    report.append(
        f"   - Trade frequency: {best['avg_trades_per_year']:.1f}/year (fewer but better quality)"
    )
elif best["threshold"] > 10:
    report.append(
        f"1. **Consider loosening entry filter** from 10% to {best['threshold']:.0f}% {'or removing it' if best['threshold'] >= 999 else ''}"
    )
    report.append(
        f"   - Improves CAGR by {best['cagr'] - current['cagr']:.2f} percentage points"
    )
    report.append(
        f"   - Increases opportunity: {best['avg_trades_per_year']:.1f} trades/year"
    )
    report.append(f"   - Accept higher risk: Max DD {best['max_drawdown']:.1f}%")
else:
    report.append("1. **Current 10% threshold appears optimal**")
    report.append("   - Good balance between opportunity and risk management")
    report.append(
        f"   - {current['avg_trades_per_year']:.1f} trades/year is sustainable"
    )

report.append("")
report.append("2. **Implementation Notes**")
report.append(f"   - Update `max_support_distance` in scanner configuration")
report.append(f"   - Monitor win rate to ensure quality remains high")
report.append(f"   - Consider adaptive thresholds based on market volatility")
report.append("")
report.append("---")
report.append(f"*Full results saved to: {csv_file}*")

# Save report
report_file = results_dir / f"entry_filter_optimization_report_{timestamp}.md"
with open(report_file, "w") as f:
    f.write("\n".join(report))

print("\n" + "=" * 80)
print("✅ OPTIMIZATION COMPLETE")
print("=" * 80)
print(f"📊 Results CSV: {csv_file}")
print(f"📄 Analysis Report: {report_file}")
print("")
print(f"🏆 Best Configuration: {best['name']}")
print(
    f"   Threshold: {'To_Support_% < ' + str(best['threshold']) if best['threshold'] < 999 else 'None'}"
)
print(f"   CAGR: {best['cagr']:.2f}%")
print(f"   Trades/Year: {best['avg_trades_per_year']:.1f}")
print("=" * 80)

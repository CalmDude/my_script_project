"""
Optimize portfolio configuration to maximize CAGR
Test different position sizes and max holdings combinations
"""

import json
import subprocess
from pathlib import Path
import pandas as pd
from datetime import datetime

# Test configurations
configs = [
    # Current configurations (already tested)
    {"position_size": 7, "max_positions": 7, "name": "7/7 (baseline)"},
    {"position_size": 10, "max_positions": 10, "name": "10/10 (current)"},
    # Larger positions, same count
    {"position_size": 12, "max_positions": 10, "name": "12/10"},
    {"position_size": 15, "max_positions": 10, "name": "15/10"},
    # More positions
    {"position_size": 8, "max_positions": 12, "name": "8/12"},
    {"position_size": 10, "max_positions": 12, "name": "10/12"},
    {"position_size": 7, "max_positions": 15, "name": "7/15"},
    # Concentrated portfolios
    {"position_size": 15, "max_positions": 6, "name": "15/6"},
    {"position_size": 20, "max_positions": 5, "name": "20/5"},
    # Smaller positions, more diversification
    {"position_size": 5, "max_positions": 15, "name": "5/15"},
    {"position_size": 6, "max_positions": 15, "name": "6/15"},
]


def update_config(position_size, max_positions):
    """Update config.json with new settings"""
    config_path = Path("backtest/config.json")

    with open(config_path, "r") as f:
        config = json.load(f)

    config["backtest_settings"]["universe"] = "sp500_optimized"
    config["portfolio_settings"]["position_size_pct"] = position_size
    config["portfolio_settings"]["max_positions"] = max_positions
    config["portfolio_settings"][
        "comment"
    ] = f"{position_size}% position size with max {max_positions} holdings"

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def run_backtest():
    """Run backtest and read results from JSON file"""
    subprocess.run(
        ["python", "backtest/run_backtest.py"], capture_output=True, text=True
    )

    # Find latest summary file
    results_dir = Path("backtest/results")
    summary_files = list(results_dir.glob("summary_*.json"))
    latest_file = max(summary_files, key=lambda p: p.stat().st_mtime)

    # Read JSON results
    with open(latest_file, "r") as f:
        return json.load(f)


def parse_results(summary_json):
    """Extract metrics from JSON summary"""
    results = {
        "final_value": summary_json["Performance"]["Final_Value"],
        "total_return": summary_json["Performance"]["Total_Return_%"],
        "cagr": summary_json["Performance"]["CAGR_%"],
        "max_drawdown": summary_json["Performance"]["Max_Drawdown_%"],
        "win_rate": summary_json["Trading_Stats"]["Win_Rate_%"],
        "trades": summary_json["Trading_Stats"]["Total_Trades"],
    }

    return results


# Run optimization
results_list = []

print("=" * 80)
print("PORTFOLIO OPTIMIZATION - MAXIMIZING CAGR")
print("=" * 80)
print(f"Universe: sp500_optimized (25 stocks)")
print(f"Testing {len(configs)} configurations...")
print("=" * 80)

for i, cfg in enumerate(configs, 1):
    print(
        f"\n[{i}/{len(configs)}] Testing {cfg['name']}: {cfg['position_size']}% positions, max {cfg['max_positions']} holdings"
    )

    # Update config
    update_config(cfg["position_size"], cfg["max_positions"])

    # Run backtest
    output = run_backtest()

    # Parse results
    metrics = parse_results(output)

    # Store results
    result_row = {
        "Config": cfg["name"],
        "Position %": cfg["position_size"],
        "Max Holdings": cfg["max_positions"],
        "CAGR %": metrics["cagr"],
        "Final Value $": metrics["final_value"],
        "Total Return %": metrics["total_return"],
        "Max DD %": metrics["max_drawdown"],
        "Win Rate %": metrics["win_rate"],
        "Trades": metrics["trades"],
    }
    results_list.append(result_row)

    print(
        f"   ✅ CAGR: {metrics['cagr']:.2f}%  |  Final: ${metrics['final_value']:,.0f}  |  Win Rate: {metrics['win_rate']:.1f}%"
    )

# Create results dataframe
df = pd.DataFrame(results_list)
df = df.sort_values("CAGR %", ascending=False)

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"backtest/results/portfolio_optimization_{timestamp}.csv"
df.to_csv(output_path, index=False)

# Display results
print("\n" + "=" * 80)
print("OPTIMIZATION RESULTS (Sorted by CAGR)")
print("=" * 80)
print(df.to_string(index=False))

print("\n" + "=" * 80)
print("TOP 3 CONFIGURATIONS:")
print("=" * 80)
for i, row in df.head(3).iterrows():
    print(f"\n{i+1}. {row['Config']}")
    print(f"   CAGR: {row['CAGR %']:.2f}%")
    print(f"   Final Value: ${row['Final Value $']:,.0f}")
    print(f"   Max Drawdown: {row['Max DD %']:.2f}%")
    print(f"   Win Rate: {row['Win Rate %']:.1f}%")
    print(f"   Total Trades: {row['Trades']}")

print(f"\n✅ Full results saved to: {output_path}")
print("=" * 80)

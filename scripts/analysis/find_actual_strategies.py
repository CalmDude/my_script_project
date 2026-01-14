"""
Analyze ACTUAL filter combinations in historical backtest data

This script explores what quality/rank/flag/vol_rr combinations
actually exist in the 5 years of historical data to find realistic
high win-rate strategies.
"""

import pandas as pd
from pathlib import Path
import sys

# Add src to path (script is in scripts/analysis/)
ROOT = Path(__file__).parent.parent.parent
src_path = ROOT / "src"
sys.path.insert(0, str(src_path))

from backtest_watchlist import WatchlistBacktest

# Configuration
CATEGORY = "nasdaq100"
HOLDING_PERIOD = 30
MAX_REPORTS = 260  # ~5 years

print("=" * 80)
print("ANALYZING ACTUAL FILTER COMBINATIONS IN HISTORICAL DATA")
print("=" * 80)

# Initialize and run backtest
results_dir = ROOT / "scanner_results" / "historical_simulation"
backtester = WatchlistBacktest(results_dir)

print(f"\nRunning backtest on {MAX_REPORTS} reports...")
results = backtester.run_backtest(
    category=CATEGORY, max_reports=MAX_REPORTS, holding_period=HOLDING_PERIOD
)

if results.empty:
    print("\n[ERROR] No backtest results!")
    exit(1)

print(f"\n[OK] Total trades: {len(results)}")

# Calculate win rate
return_col = f"return_{HOLDING_PERIOD}d"
returns = results[return_col].dropna()
winners = returns[returns > 0]
win_rate = (len(winners) / len(returns) * 100) if len(returns) > 0 else 0

print(f"Overall win rate: {win_rate:.1f}%")
print(f"Average return: {returns.mean():.2f}%")

# Analyze distribution
print("\n" + "=" * 80)
print("DISTRIBUTION OF FILTERS")
print("=" * 80)

print("\nQUALITY:")
print(results["quality"].value_counts())

print("\nQUALITY FLAG:")
# Handle encoding issues with checkmark on Windows
try:
    print(results["quality_flag"].value_counts())
except UnicodeEncodeError:
    flag_counts = results["quality_flag"].value_counts()
    for flag, count in flag_counts.items():
        # Replace checkmark with 'v'
        safe_flag = flag.replace("✓", "v") if pd.notna(flag) else "None"
        print(f"  {safe_flag}: {count}")

print("\nRANK TIERS:")
rank_tiers = pd.cut(
    results["rank"], bins=[0, 5, 10, 15, 100], labels=["1-5", "6-10", "11-15", "16+"]
)
print(rank_tiers.value_counts().sort_index())

print("\nVOL R:R TIERS:")
vol_rr_tiers = pd.cut(
    results["vol_rr"],
    bins=[0, 2, 3, 4, 100],
    labels=["<2.0", "2.0-3.0", "3.0-4.0", "4.0+"],
)
print(vol_rr_tiers.value_counts().sort_index())

# Find actual combinations with good win rates
print("\n" + "=" * 80)
print("ANALYZING COMBINATIONS WITH 70%+ WIN RATE")
print("=" * 80)

# Test various combinations
combinations = []

# 1. EXCELLENT + SAFE ENTRY (any rank)
combo1 = results[
    (results["quality"] == "EXCELLENT")
    & (results["quality_flag"].str.contains("SAFE ENTRY", na=False))
].copy()

if len(combo1) > 0:
    combo1_returns = combo1[return_col].dropna()
    combo1_win_rate = (
        len(combo1_returns[combo1_returns > 0]) / len(combo1_returns) * 100
    )
    combinations.append(
        {
            "name": "EXCELLENT + SAFE ENTRY (any rank)",
            "trades": len(combo1),
            "win_rate": combo1_win_rate,
            "avg_return": combo1_returns.mean(),
            "filters": "Quality=EXCELLENT, Flag=SAFE ENTRY",
        }
    )

# 2. EXCELLENT + SAFE ENTRY + Vol R:R >= 2.0
combo2 = results[
    (results["quality"] == "EXCELLENT")
    & (results["quality_flag"].str.contains("SAFE ENTRY", na=False))
    & (results["vol_rr"] >= 2.0)
].copy()

if len(combo2) > 0:
    combo2_returns = combo2[return_col].dropna()
    combo2_win_rate = (
        len(combo2_returns[combo2_returns > 0]) / len(combo2_returns) * 100
    )
    combinations.append(
        {
            "name": "EXCELLENT + SAFE ENTRY + Vol R:R ≥ 2.0",
            "trades": len(combo2),
            "win_rate": combo2_win_rate,
            "avg_return": combo2_returns.mean(),
            "filters": "Quality=EXCELLENT, Flag=SAFE ENTRY, Vol R:R≥2.0",
        }
    )

# 3. EXCELLENT + SAFE ENTRY + Vol R:R >= 2.5
combo3 = results[
    (results["quality"] == "EXCELLENT")
    & (results["quality_flag"].str.contains("SAFE ENTRY", na=False))
    & (results["vol_rr"] >= 2.5)
].copy()

if len(combo3) > 0:
    combo3_returns = combo3[return_col].dropna()
    combo3_win_rate = (
        len(combo3_returns[combo3_returns > 0]) / len(combo3_returns) * 100
    )
    combinations.append(
        {
            "name": "EXCELLENT + SAFE ENTRY + Vol R:R ≥ 2.5",
            "trades": len(combo3),
            "win_rate": combo3_win_rate,
            "avg_return": combo3_returns.mean(),
            "filters": "Quality=EXCELLENT, Flag=SAFE ENTRY, Vol R:R≥2.5",
        }
    )

# 4. EXCELLENT + Rank 1-5 + SAFE ENTRY + Vol R:R >= 2.0
combo4 = results[
    (results["quality"] == "EXCELLENT")
    & (results["rank"] <= 5)
    & (results["quality_flag"].str.contains("SAFE ENTRY", na=False))
    & (results["vol_rr"] >= 2.0)
].copy()

if len(combo4) > 0:
    combo4_returns = combo4[return_col].dropna()
    combo4_win_rate = (
        len(combo4_returns[combo4_returns > 0]) / len(combo4_returns) * 100
    )
    combinations.append(
        {
            "name": "EXCELLENT + Rank 1-5 + SAFE ENTRY + Vol R:R ≥ 2.0",
            "trades": len(combo4),
            "win_rate": combo4_win_rate,
            "avg_return": combo4_returns.mean(),
            "filters": "Quality=EXCELLENT, Rank=1-5, Flag=SAFE ENTRY, Vol R:R≥2.0",
        }
    )

# 5. GOOD + SAFE ENTRY + Vol R:R >= 3.0
combo5 = results[
    (results["quality"] == "GOOD")
    & (results["quality_flag"].str.contains("SAFE ENTRY", na=False))
    & (results["vol_rr"] >= 3.0)
].copy()

if len(combo5) > 0:
    combo5_returns = combo5[return_col].dropna()
    combo5_win_rate = (
        len(combo5_returns[combo5_returns > 0]) / len(combo5_returns) * 100
    )
    combinations.append(
        {
            "name": "GOOD + SAFE ENTRY + Vol R:R ≥ 3.0",
            "trades": len(combo5),
            "win_rate": combo5_win_rate,
            "avg_return": combo5_returns.mean(),
            "filters": "Quality=GOOD, Flag=SAFE ENTRY, Vol R:R≥3.0",
        }
    )

# 6. Any quality + SAFE ENTRY + Vol R:R >= 3.5
combo6 = results[
    (results["quality_flag"].str.contains("SAFE ENTRY", na=False))
    & (results["vol_rr"] >= 3.5)
].copy()

if len(combo6) > 0:
    combo6_returns = combo6[return_col].dropna()
    combo6_win_rate = (
        len(combo6_returns[combo6_returns > 0]) / len(combo6_returns) * 100
    )
    combinations.append(
        {
            "name": "Any Quality + SAFE ENTRY + Vol R:R ≥ 3.5",
            "trades": len(combo6),
            "win_rate": combo6_win_rate,
            "avg_return": combo6_returns.mean(),
            "filters": "Flag=SAFE ENTRY, Vol R:R≥3.5",
        }
    )

# Sort by win rate
combinations_df = pd.DataFrame(combinations)
combinations_df = combinations_df.sort_values("win_rate", ascending=False)

# Save to CSV (avoid encoding issues)
output_dir = ROOT / "backtest_results"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "actual_strategy_combinations.csv"
combinations_df.to_csv(output_file, index=False)
print(f"\n[OK] Results saved to: backtest_results/{output_file.name}")

print("\nSORTED BY WIN RATE (Top 10):")
for idx, row in combinations_df.head(10).iterrows():
    print(f"\n{idx+1}. {row['name']}")
    print(f"   Trades: {row['trades']}")
    print(f"   Win Rate: {row['win_rate']:.1f}%")
    print(f"   Avg Return: {row['avg_return']:+.2f}%")

# Find strategies meeting 70-80% win rate target
print("\n" + "=" * 80)
print("STRATEGIES MEETING 70-80% WIN RATE TARGET")
print("=" * 80)

target_strategies = combinations_df[
    (combinations_df["win_rate"] >= 70)
    & (combinations_df["win_rate"] <= 85)
    & (combinations_df["trades"] >= 20)  # Minimum sample size
]

if not target_strategies.empty:
    for idx, row in target_strategies.iterrows():
        print(f"\nSTRATEGY: {row['name']}")
        print(f"  Trades: {row['trades']}")
        print(f"  Win Rate: {row['win_rate']:.1f}%")
        print(f"  Avg Return: {row['avg_return']:+.2f}%")
else:
    print("\n[WARNING] No strategies found with 70-80% win rate AND 20+ trades")
    print("Showing closest matches...")

    # Show strategies with 20+ trades sorted by win rate
    min_trades = combinations_df[combinations_df["trades"] >= 20]
    if not min_trades.empty:
        print("\nStrategies with 20+ trades:")
        for idx, row in min_trades.iterrows():
            print(f"\n  {row['name']}")
            print(f"    Trades: {row['trades']}")
            print(f"    Win Rate: {row['win_rate']:.1f}%")
            print(f"    Avg Return: {row['avg_return']:+.2f}%")

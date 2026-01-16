"""
Diagnostic script to understand why trade counts are so low
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from strategy_signals import GHBStrategy
import json

# Load config
with open("backtest/config.json", "r") as f:
    config = json.load(f)

# Load data
print("Loading data...")
loader = DataLoader("backtest/config.json")
tickers = loader.get_universe()
data_dict = loader.download_historical_data(tickers, force_refresh=False)

print(f"\nLoaded {len(data_dict)} stocks")

# Test signal generation for first few weeks
strategy = GHBStrategy()

# Generate Friday schedule
start = pd.Timestamp(config["backtest_settings"]["start_date"])
end = pd.Timestamp(config["backtest_settings"]["end_date"])
all_dates = pd.date_range(start, end, freq="D")
fridays = all_dates[all_dates.dayofweek == 4]

print(f"\nTotal Fridays: {len(fridays)}")
print(f"First Friday: {fridays[0].date()}")
print(f"Last Friday: {fridays[-1].date()}")

# Test first 10 weeks
print("\n" + "=" * 80)
print("SIGNAL GENERATION TEST - First 10 Weeks")
print("=" * 80)

total_p1 = 0
total_filtered_5 = 0
total_filtered_10 = 0
total_filtered_15 = 0

for i, friday in enumerate(fridays[:10]):
    df_signals = strategy.scan_universe(data_dict, target_date=friday)

    if not df_signals.empty:
        p1_signals = df_signals[df_signals["State"] == "P1"]

        if len(p1_signals) > 0:
            # Apply different filters
            filtered_5 = strategy.filter_safe_entries(df_signals, max_distance=5)
            filtered_10 = strategy.filter_safe_entries(df_signals, max_distance=10)
            filtered_15 = strategy.filter_safe_entries(df_signals, max_distance=15)

            total_p1 += len(p1_signals)
            total_filtered_5 += len(filtered_5)
            total_filtered_10 += len(filtered_10)
            total_filtered_15 += len(filtered_15)

            print(f"\nWeek {i+1} - {friday.date()}")
            print(f"  P1 signals: {len(p1_signals)}")
            print(f"  After 5% filter: {len(filtered_5)}")
            print(f"  After 10% filter: {len(filtered_10)}")
            print(f"  After 15% filter: {len(filtered_15)}")

            if len(p1_signals) > 0:
                print(f"  Sample P1 tickers: {p1_signals['Ticker'].head(3).tolist()}")
                print(
                    f"  Sample distances: {p1_signals['To_Support_%'].head(3).tolist()}"
                )

print("\n" + "=" * 80)
print("SUMMARY - First 10 Weeks")
print("=" * 80)
print(f"Total P1 signals: {total_p1}")
print(
    f"After 5% filter: {total_filtered_5} ({total_filtered_5/max(total_p1,1)*100:.1f}% pass rate)"
)
print(
    f"After 10% filter: {total_filtered_10} ({total_filtered_10/max(total_p1,1)*100:.1f}% pass rate)"
)
print(
    f"After 15% filter: {total_filtered_15} ({total_filtered_15/max(total_p1,1)*100:.1f}% pass rate)"
)

# Now test full period
print("\n" + "=" * 80)
print("FULL PERIOD ANALYSIS")
print("=" * 80)

weeks_with_p1 = 0
weeks_with_filtered_10 = 0

for friday in fridays:
    df_signals = strategy.scan_universe(data_dict, target_date=friday)

    if not df_signals.empty:
        p1_signals = df_signals[df_signals["State"] == "P1"]

        if len(p1_signals) > 0:
            weeks_with_p1 += 1

            filtered_10 = strategy.filter_safe_entries(df_signals, max_distance=10)
            if len(filtered_10) > 0:
                weeks_with_filtered_10 += 1

print(f"Total weeks: {len(fridays)}")
print(f"Weeks with P1 signals: {weeks_with_p1} ({weeks_with_p1/len(fridays)*100:.1f}%)")
print(
    f"Weeks with P1 signals passing 10% filter: {weeks_with_filtered_10} ({weeks_with_filtered_10/len(fridays)*100:.1f}%)"
)
print(
    f"\nExpected trades (assuming buy 1/week when signals available): {weeks_with_filtered_10}"
)

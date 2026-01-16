"""
Compare trade selection between base engine and scanner engine
"""

import pandas as pd
import sys
import os

# Add backtest to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backtest.strategy_signals import GHBStrategy
from backtest.data_loader import DataLoader
import json


def main():
    # Initialize
    loader = DataLoader("backtest/config.json")
    strategy = GHBStrategy()

    # Load data
    print("Loading data...")
    tickers = loader.get_universe()
    data_dict = loader.download_historical_data(tickers, force_refresh=False)

    # Get Fridays
    start = pd.Timestamp("2021-07-16")  # First Friday in backtest
    end = pd.Timestamp("2025-12-26")
    fridays = pd.date_range(start=start, end=end, freq="W-FRI")

    # Compare first 5 weeks
    print("\n" + "=" * 80)
    print("COMPARING TRADE SELECTION: Base vs Scanner")
    print("=" * 80)

    for i, friday in enumerate(fridays[:5]):
        print(f"\nWeek {i+1}: {friday.date()}")
        print("-" * 40)

        # Get signals for this date
        df_signals = strategy.scan_universe(data_dict, target_date=friday)

        if df_signals.empty:
            print("   No signals")
            continue

        # Base method: get_buy_candidates (takes top 20 of pre-sorted)
        base_candidates = strategy.get_buy_candidates(df_signals, max_candidates=20)

        # Scanner method: filter_safe_entries (filters then re-sorts)
        scanner_candidates = strategy.filter_safe_entries(df_signals, max_distance=999)

        print(f"   Base picks (top 5):")
        if not base_candidates.empty:
            for idx, row in base_candidates.head(5).iterrows():
                print(
                    f"      {row['Ticker']:6s} ROC={row['ROC_4W_%']:6.2f}%  Distance={row['To_Support_%']:6.2f}%"
                )

        print(f"\n   Scanner picks (top 5):")
        if not scanner_candidates.empty:
            for idx, row in scanner_candidates.head(5).iterrows():
                print(
                    f"      {row['Ticker']:6s} ROC={row['ROC_4W_%']:6.2f}%  Distance={row['To_Support_%']:6.2f}%"
                )

        # Check if they match
        if not base_candidates.empty and not scanner_candidates.empty:
            base_tickers = set(base_candidates["Ticker"].tolist())
            scanner_tickers = set(scanner_candidates["Ticker"].tolist())

            if base_tickers == scanner_tickers:
                print("\n   ✅ MATCH: Same stocks selected")
            else:
                print("\n   ❌ MISMATCH:")
                print(f"      Base only: {base_tickers - scanner_tickers}")
                print(f"      Scanner only: {scanner_tickers - base_tickers}")


if __name__ == "__main__":
    main()

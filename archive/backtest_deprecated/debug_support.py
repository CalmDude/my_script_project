"""
Debug support calculation to see what's happening
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import DataLoader
from strategy_signals import GHBStrategy

# Load data
loader = DataLoader("backtest/config.json")
data_dict = loader.download_historical_data(loader.get_universe(), force_refresh=False)

# Pick TSLA for testing
tsla_df = data_dict["TSLA"]

print("TSLA Data:")
print(f"  Total rows: {len(tsla_df)}")
print(f"  Date range: {tsla_df['Date'].min()} to {tsla_df['Date'].max()}")

# Test for 2021-01-01
test_date = pd.Timestamp("2021-01-01")
df_filtered = tsla_df[tsla_df["Date"] <= test_date].copy()

print(f"\nFiltered to {test_date}:")
print(f"  Rows: {len(df_filtered)}")
print(f"  Date range: {df_filtered['Date'].min()} to {df_filtered['Date'].max()}")

# Calculate support
if len(df_filtered) >= 252:
    week_52_low = df_filtered["Close"].iloc[-252:].min()
    print(f"  Using last 252 days")
else:
    week_52_low = df_filtered["Close"].min()
    print(f"  Using all available data ({len(df_filtered)} days)")

support = week_52_low * 1.10
current_price = df_filtered["Close"].iloc[-1]
distance = ((current_price - support) / support) * 100

print(f"\n52-week low: ${week_52_low:.2f}")
print(f"Support (52w low * 1.10): ${support:.2f}")
print(f"Current price: ${current_price:.2f}")
print(f"Distance from support: {distance:.2f}%")

# Show recent lows
print(f"\nLast 252 days price range:")
print(f"  Min: ${df_filtered['Close'].iloc[-252:].min():.2f}")
print(f"  Max: ${df_filtered['Close'].iloc[-252:].max():.2f}")
print(f"  Current: ${current_price:.2f}")

# Test with GHBStrategy
strategy = GHBStrategy()
signals = strategy.calculate_signals_for_date(tsla_df, test_date, "TSLA")

print(f"\nStrategy calculation:")
print(f"  State: {signals['State']}")
print(f"  Support: ${signals['Support']:.2f}")
print(f"  To_Support_%: {signals['To_Support_%']:.2f}%")

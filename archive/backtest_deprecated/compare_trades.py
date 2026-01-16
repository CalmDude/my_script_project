"""
Compare actual trades between base and scanner
"""

import pandas as pd

# Load trade files (most recent)
print("Loading trade history...")
base_trades = pd.read_csv(
    "backtest/results/trades_20260116_113016.csv"
)  # Base from just now
scanner_trades = pd.read_csv("backtest/results/trades_20260116_112854.csv")  # Scanner

print(f"\nBase trades: {len(base_trades)}")
print(f"Scanner trades: {len(scanner_trades)}")

# Compare first 10 BUY trades
print("\n" + "=" * 80)
print("FIRST 10 BUY TRADES COMPARISON")
print("=" * 80)

base_buys = base_trades[base_trades["Action"] == "BUY"].head(10)
scanner_buys = scanner_trades[scanner_trades["Action"] == "BUY"].head(10)

print("\nBASE ENGINE:")
for idx, row in base_buys.iterrows():
    print(
        f"  {row['Date'][:10]} {row['Ticker']:6s} {row['Shares']:4.0f} shares @ ${row['Price']:7.2f} = ${row['Value']:10,.0f}"
    )

print("\nSCANNER ENGINE:")
for idx, row in scanner_buys.iterrows():
    print(
        f"  {row['Date'][:10]} {row['Ticker']:6s} {row['Shares']:4.0f} shares @ ${row['Price']:7.2f} = ${row['Value']:10,.0f}"
    )

# Check if tickers match
base_tickers = set(base_buys["Ticker"].tolist())
scanner_tickers = set(scanner_buys["Ticker"].tolist())

if base_tickers == scanner_tickers:
    print("\n✅ Same stocks traded")
else:
    print(f"\n❌ MISMATCH:")
    print(f"  Base only: {base_tickers - scanner_tickers}")
    print(f"  Scanner only: {scanner_tickers - base_tickers}")

# Compare position sizes
print("\n" + "=" * 80)
print("POSITION SIZE COMPARISON (First 5 buys)")
print("=" * 80)
for i in range(min(5, len(base_buys), len(scanner_buys))):
    base_row = base_buys.iloc[i]
    scanner_row = scanner_buys.iloc[i]

    if base_row["Ticker"] == scanner_row["Ticker"]:
        base_val = base_row["Value"]
        scanner_val = scanner_row["Value"]
        diff_pct = ((scanner_val / base_val) - 1) * 100

        print(
            f"{base_row['Ticker']:6s}: Base ${base_val:10,.0f}  Scanner ${scanner_val:10,.0f}  ({diff_pct:+.1f}%)"
        )

# Compare SELL trades
print("\n" + "=" * 80)
print("FIRST 10 SELL TRADES COMPARISON")
print("=" * 80)

base_sells = base_trades[base_trades["Action"] == "SELL"].head(10)
scanner_sells = scanner_trades[scanner_trades["Action"] == "SELL"].head(10)

print("\nBASE ENGINE:")
for idx, row in base_sells.iterrows():
    print(
        f"  {row['Date'][:10]} {row['Ticker']:6s} {row['Shares']:4.0f} shares @ ${row['Price']:7.2f} = ${row['Value']:10,.0f}"
    )

print("\nSCANNER ENGINE:")
for idx, row in scanner_sells.iterrows():
    print(
        f"  {row['Date'][:10]} {row['Ticker']:6s} {row['Shares']:4.0f} shares @ ${row['Price']:7.2f} = ${row['Value']:10,.0f}"
    )

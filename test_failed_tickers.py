"""Test downloading the failed tickers"""

import yfinance as yf
import pandas as pd

tickers = ["ALAB", "ARM", "ASML", "BKNG", "CRWD", "DASH", "MDB", "PLTR", "TSM"]

print("Testing downloads for failed tickers:")
print("=" * 80)

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start="2020-01-01", end="2025-12-31")

        if df.empty:
            print(f"{ticker:6s}: EMPTY - No data returned")
        else:
            print(
                f"{ticker:6s}: {len(df):4d} days - {df.index.min().date()} to {df.index.max().date()}"
            )

    except Exception as e:
        print(f"{ticker:6s}: ERROR - {str(e)}")

print("=" * 80)

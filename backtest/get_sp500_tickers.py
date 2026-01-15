"""
Fetch current S&P 500 ticker list from Wikipedia
"""

import pandas as pd


def get_sp500_tickers():
    """Get list of S&P 500 tickers from Wikipedia"""
    # Wikipedia maintains the official S&P 500 list
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    # Read the first table which contains current constituents
    tables = pd.read_html(url)
    sp500_table = tables[0]

    # Get ticker symbols
    tickers = sp500_table["Symbol"].tolist()

    # Clean up tickers (some have . instead of -, fix for Yahoo Finance)
    tickers = [ticker.replace(".", "-") for ticker in tickers]

    return sorted(tickers)


if __name__ == "__main__":
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} S&P 500 tickers")
    print("\nTickers:")

    # Format as Python list for easy copy-paste
    print("[")
    for i, ticker in enumerate(tickers):
        if i % 10 == 0:
            print("   ", end="")
        print(f'"{ticker}"', end="")
        if i < len(tickers) - 1:
            print(", ", end="")
        if (i + 1) % 10 == 0:
            print()
    print("\n]")

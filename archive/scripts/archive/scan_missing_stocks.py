import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Stocks not in NASDAQ 100 list
missing_tickers = ["ARM", "PLTR", "ALAB", "TSM", "MRVL"]

print("=" * 100)
print("SCANNING NON-NASDAQ 100 STOCKS FROM YOUR WATCHLIST")
print("=" * 100)

results = []

for ticker in missing_tickers:
    try:
        # Download data
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")

        if df.empty:
            print(f"\n❌ {ticker}: No data available")
            continue

        # Get latest data
        latest = df.iloc[-1]
        close = latest["Close"]

        # Calculate 200-day SMA
        d200 = df["Close"].rolling(window=200).mean().iloc[-1]

        # Calculate 4-week ROC (20 trading days)
        if len(df) >= 20:
            price_4w_ago = df["Close"].iloc[-20]
            roc_4w = ((close - price_4w_ago) / price_4w_ago) * 100
        else:
            roc_4w = 0

        # Calculate distance from D200
        distance_pct = ((close - d200) / d200) * 100

        # Determine Weekly Larsson state
        if close > d200:
            if roc_4w > 5 or distance_pct > 10:
                state = "P1"
            else:
                state = "P2"
        else:
            if distance_pct > -5:
                state = "N1"
            else:
                state = "N2"

        results.append(
            {
                "Ticker": ticker,
                "Close": close,
                "D200": d200,
                "Distance": distance_pct,
                "ROC_4W": roc_4w,
                "State": state,
            }
        )

    except Exception as e:
        print(f"\n❌ {ticker}: Error - {str(e)}")

if results:
    df_results = pd.DataFrame(results)

    # Separate by state
    p1 = df_results[df_results["State"] == "P1"]
    p2 = df_results[df_results["State"] == "P2"]
    n1 = df_results[df_results["State"] == "N1"]
    n2 = df_results[df_results["State"] == "N2"]

    print(f"\n🟡 P1 (GOLD - STRONG BUY): {len(p1)} stocks")
    if len(p1) > 0:
        print("-" * 100)
        print(
            f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Distance':<12} {'ROC 4W':<10} {'Signal':<20}"
        )
        print("-" * 100)
        for _, row in p1.iterrows():
            print(
                f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {row['Distance']:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'>>> BUY (GHB Strategy)':<20}"
            )

    print(f"\n⚪ P2 (GRAY - HOLD/CONSOLIDATION): {len(p2)} stocks")
    if len(p2) > 0:
        print("-" * 100)
        print(
            f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Distance':<12} {'ROC 4W':<10} {'Signal':<20}"
        )
        print("-" * 100)
        for _, row in p2.iterrows():
            print(
                f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {row['Distance']:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'HOLD if in position':<20}"
            )

    print(f"\n⚪ N1 (GRAY - WEAK/HOLD): {len(n1)} stocks")
    if len(n1) > 0:
        print("-" * 100)
        print(
            f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Distance':<12} {'ROC 4W':<10} {'Signal':<20}"
        )
        print("-" * 100)
        for _, row in n1.iterrows():
            print(
                f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {row['Distance']:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'HOLD if in position':<20}"
            )

    print(f"\n🔵 N2 (BLUE - SELL ZONE): {len(n2)} stocks")
    if len(n2) > 0:
        print("-" * 100)
        print(
            f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Distance':<12} {'ROC 4W':<10} {'Signal':<20}"
        )
        print("-" * 100)
        for _, row in n2.iterrows():
            print(
                f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {row['Distance']:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'>>> SELL (Exit)':<20}"
            )

print("\n" + "=" * 100)
print("COMPLETE WATCHLIST SUMMARY (12 STOCKS)")
print("=" * 100)
print("\nFrom NASDAQ 100 Report:")
print("  P1 (BUY): MU, ASML, GOOG, AMD, TSLA, AVGO, NVDA (8 stocks)")
print("\nFrom Manual Scan:")
if results:
    p1_count = len([r for r in results if r["State"] == "P1"])
    p2_count = len([r for r in results if r["State"] == "P2"])
    n1_count = len([r for r in results if r["State"] == "N1"])
    n2_count = len([r for r in results if r["State"] == "N2"])
    print(f"  P1 (BUY): {p1_count} stocks")
    print(f"  P2 (HOLD): {p2_count} stocks")
    print(f"  N1 (HOLD): {n1_count} stocks")
    print(f"  N2 (SELL): {n2_count} stocks")

    total_buy = 8 + p1_count
    print(f"\nTOTAL BUY SIGNALS: {total_buy}/12 stocks ({total_buy/12*100:.0f}%)")
print("=" * 100)

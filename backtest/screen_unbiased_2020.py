"""
Unbiased Stock Screening Using 2020 Data Only
Selects stocks based on 2020 fundamentals, then tests on 2021-2025

This avoids optimization bias by NOT looking at 2021-2025 performance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

from get_historical_sp500 import get_sp500_as_of_2021


def calculate_2020_metrics(ticker):
    """
    Calculate stock metrics using ONLY 2020 data
    Returns: dict with 2020 fundamentals or None
    """
    try:
        stock = yf.Ticker(ticker)

        # Download 2019-2020 data only (need some history for calculations)
        df = stock.history(start="2019-01-01", end="2020-12-31", interval="1d")

        if df.empty or len(df) < 200:
            return None

        # Get 2020 data only for metrics
        df_2020 = df[df.index.year == 2020]

        if df_2020.empty:
            return None

        # Calculate 2020 metrics
        close_2020_end = df_2020["Close"].iloc[-1]

        # Volatility (annualized standard deviation of 2020 returns)
        returns_2020 = df_2020["Close"].pct_change().dropna()
        volatility_pct = returns_2020.std() * np.sqrt(252) * 100

        # Average volume in 2020
        avg_volume = df_2020["Volume"].mean()

        # 2020 return
        close_2020_start = df_2020["Close"].iloc[0]
        return_2020_pct = ((close_2020_end - close_2020_start) / close_2020_start) * 100

        # Get market cap (approximate from 2020 end price)
        try:
            info = stock.info
            shares_outstanding = info.get("sharesOutstanding", 0)
            market_cap = (
                (close_2020_end * shares_outstanding) if shares_outstanding else 0
            )
        except:
            market_cap = 0

        return {
            "Ticker": ticker,
            "Close_2020": close_2020_end,
            "Volatility_2020_%": volatility_pct,
            "Avg_Volume_2020": avg_volume,
            "Return_2020_%": return_2020_pct,
            "Market_Cap_2020": market_cap,
        }

    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return None


def screen_stocks_2020_only():
    """
    Screen S&P 500 (as of Jan 2021) using only 2020 data

    Criteria (based on 2020 data):
    - Volatility >= 25% (moderate to high)
    - Average volume >= 2M shares/day (liquid)
    - Market cap >= $5B (substantial company)
    - Member of S&P 500 as of Jan 1, 2021
    """
    print("=" * 80)
    print("UNBIASED STOCK SCREENING - Using 2020 Data Only")
    print("=" * 80)

    # Get historical S&P 500 members (Jan 1, 2021)
    tickers = get_sp500_as_of_2021()
    print(f"\n📊 Screening {len(tickers)} S&P 500 stocks (as of Jan 1, 2021)")
    print(f"📅 Using 2020 data ONLY (no peeking at 2021-2025)")
    print(f"⏰ This will take 15-20 minutes...\n")

    results = []

    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i:3d}/{len(tickers)}] Processing {ticker:6s}...", end="\r")

        metrics = calculate_2020_metrics(ticker)
        if metrics:
            results.append(metrics)

    print(f"\n\n✅ Screening complete: {len(results)}/{len(tickers)} stocks analyzed")

    # Create DataFrame
    df = pd.DataFrame(results)

    # Apply qualification criteria (based on 2020 data only)
    df["Qualifies"] = (
        (df["Volatility_2020_%"] >= 25)
        & (df["Avg_Volume_2020"] >= 2_000_000)
        & (df["Market_Cap_2020"] >= 5_000_000_000)
    )

    # Separate qualified and non-qualified
    df_qualified = df[df["Qualifies"]].copy()
    df_not_qualified = df[~df["Qualifies"]].copy()

    # Sort qualified by volatility (higher = more momentum potential)
    df_qualified = df_qualified.sort_values("Volatility_2020_%", ascending=False)

    print("\n" + "=" * 80)
    print("SCREENING RESULTS")
    print("=" * 80)
    print(
        f"\n✅ Qualified: {len(df_qualified)} stocks ({len(df_qualified)/len(df)*100:.1f}%)"
    )
    print(
        f"❌ Not Qualified: {len(df_not_qualified)} stocks ({len(df_not_qualified)/len(df)*100:.1f}%)"
    )

    print("\n📊 Qualification Criteria (based on 2020):")
    print("   - Volatility >= 25%")
    print("   - Average volume >= 2M shares/day")
    print("   - Market cap >= $5B")

    print("\n🔝 Top 25 Qualified Stocks (by 2020 volatility):")
    print("=" * 80)
    top_25 = df_qualified.head(25)
    print(
        f"{'Ticker':<8} {'2020 Close':<12} {'Volatility':<12} {'Avg Volume':<15} {'2020 Return':<12}"
    )
    print("-" * 80)
    for _, row in top_25.iterrows():
        print(
            f"{row['Ticker']:<8} ${row['Close_2020']:<11.2f} {row['Volatility_2020_%']:<11.1f}% "
            f"{row['Avg_Volume_2020']/1e6:<14.1f}M {row['Return_2020_%']:<11.1f}%"
        )

    # Save results
    output_dir = Path("backtest/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save all results
    all_results_file = output_dir / f"screening_2020_all_{timestamp}.csv"
    df.to_csv(all_results_file, index=False)
    print(f"\n✅ All results saved: {all_results_file.name}")

    # Save qualified stocks
    qualified_file = output_dir / f"screening_2020_qualified_{timestamp}.csv"
    df_qualified.to_csv(qualified_file, index=False)
    print(f"✅ Qualified stocks saved: {qualified_file.name}")

    # Save top 25 as universe
    universe_file = Path("backtest/data/sp500_unbiased_2020.txt")
    universe_file.parent.mkdir(parents=True, exist_ok=True)

    with open(universe_file, "w") as f:
        for ticker in top_25["Ticker"]:
            f.write(f"{ticker}\n")

    print(f"✅ Universe file saved: {universe_file.name}")

    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS:")
    print("=" * 80)
    print("1. Review the top 25 stocks selected using 2020 data")
    print("2. Run backtest on 2021-2025 period with this universe")
    print("3. Compare results with biased backtest (46.80% CAGR)")
    print("4. The new CAGR will be more realistic for forward testing")

    print(f"\n📝 Universe: backtest/data/sp500_unbiased_2020.txt")
    print(f"📊 Results: {output_dir}/screening_2020_*.csv")

    return df_qualified


if __name__ == "__main__":
    df_qualified = screen_stocks_2020_only()

    print("\n" + "=" * 80)
    print("✅ UNBIASED SCREENING COMPLETE")
    print("=" * 80)
    print("\nReady to run unbiased backtest on 2021-2025 period")

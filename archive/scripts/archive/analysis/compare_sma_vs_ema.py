"""
Compare GHB Strategy: 200-Day SMA vs 200-Day EMA

Tests whether using EMA instead of SMA for the 200-day moving average
improves GHB Strategy performance.
"""

import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import yfinance as yf

# Add src to path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


def download_and_calculate_ema(
    ticker: str, start_date: str, end_date: str
) -> pd.DataFrame:
    """
    Download daily data and calculate 200-day EMA
    Returns DataFrame with date and d200_ema
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, interval="1d")

        if df.empty:
            return pd.DataFrame()

        # Calculate 200-day EMA
        df["d200_ema"] = df["Close"].ewm(span=200, adjust=False).mean()

        # Create weekly data (Friday closes)
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"])
        df["weekday"] = df["Date"].dt.dayofweek

        # Get Friday data (weekday 4 = Friday)
        weekly = df[df["weekday"] == 4].copy()

        # If no Fridays, get last day of each week
        if weekly.empty:
            df["week"] = df["Date"].dt.isocalendar().week
            weekly = df.groupby("week").last().reset_index()

        return weekly[["Date", "d200_ema"]].rename(columns={"Date": "date"})

    except Exception as e:
        print(f"  Error downloading {ticker}: {e}")
        return pd.DataFrame()


def parse_weekly_reports_with_ema(reports_dir: Path) -> tuple:
    """
    Parse weekly reports and augment with EMA data

    Returns two DataFrames:
    - df_sma: Original data with SMA
    - df_ema: Same data but with EMA instead of SMA
    """
    all_data = []
    excel_files = sorted(reports_dir.glob("nasdaq100_weekly_*.xlsx"))

    print(f"📊 Parsing {len(excel_files)} weekly reports...")

    for file_path in excel_files:
        try:
            filename = file_path.stem
            date_str = filename.split("_")[2]
            report_date = datetime.strptime(date_str, "%Y%m%d").date()

            df = pd.read_excel(file_path, sheet_name="Weekly Data")
            df = df.dropna(subset=["Ticker"])

            for _, row in df.iterrows():
                try:
                    ticker = str(row.get("Ticker", "")).strip()
                    weekly = str(row.get("Weekly_Larsson", "")).strip()
                    price = (
                        float(row.get("Close", 0)) if pd.notna(row.get("Close")) else 0
                    )
                    d200_sma = (
                        float(row.get("D200", 0)) if pd.notna(row.get("D200")) else 0
                    )

                    if ticker and weekly and price > 0 and d200_sma > 0:
                        all_data.append(
                            {
                                "report_date": report_date,
                                "ticker": ticker,
                                "weekly_state": weekly,
                                "current_price": price,
                                "d200_sma": d200_sma,
                            }
                        )
                except:
                    continue
        except:
            continue

    df_sma = pd.DataFrame(all_data)
    df_sma = df_sma.sort_values(["ticker", "report_date"]).reset_index(drop=True)

    print(
        f"✅ Parsed {len(df_sma)} observations from {df_sma['ticker'].nunique()} tickers"
    )

    # Now download EMA data for all tickers
    print(f"\n📥 Downloading EMA data for {df_sma['ticker'].nunique()} tickers...")

    tickers = df_sma["ticker"].unique()
    ema_data = {}

    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i:3d}/{len(tickers)}] {ticker:6s}", end="\r")
        weekly_ema = download_and_calculate_ema(ticker, "2020-01-01", "2025-12-31")
        if not weekly_ema.empty:
            weekly_ema["date"] = pd.to_datetime(weekly_ema["date"]).dt.date
            ema_data[ticker] = weekly_ema

    print(f"\n✅ Downloaded EMA data for {len(ema_data)} tickers")

    # Create df_ema by merging EMA values
    df_ema = df_sma.copy()
    df_ema["d200_ema"] = 0.0

    print(f"\n🔄 Merging EMA data with weekly reports...")

    for idx, row in df_ema.iterrows():
        ticker = row["ticker"]
        report_date = row["report_date"]

        if ticker in ema_data:
            ticker_ema = ema_data[ticker]
            # Find closest EMA value for this date
            matching = ticker_ema[ticker_ema["date"] == report_date]
            if not matching.empty:
                df_ema.at[idx, "d200_ema"] = matching.iloc[0]["d200_ema"]
            else:
                # Find nearest date
                ticker_ema_copy = ticker_ema.copy()
                ticker_ema_copy["date_diff"] = ticker_ema_copy["date"].apply(
                    lambda x: abs((x - report_date).days)
                )
                nearest = ticker_ema_copy.nsmallest(1, "date_diff")
                if not nearest.empty and nearest.iloc[0]["date_diff"] <= 7:
                    df_ema.at[idx, "d200_ema"] = nearest.iloc[0]["d200_ema"]

    # Filter out rows where we couldn't get EMA
    df_ema = df_ema[df_ema["d200_ema"] > 0].copy()
    df_ema = df_ema.rename(columns={"d200_sma": "d200"})
    df_ema["d200"] = df_ema["d200_ema"]
    df_ema = df_ema.drop("d200_ema", axis=1)

    # Prepare SMA dataframe
    df_sma = df_sma.rename(columns={"d200_sma": "d200"})

    print(f"✅ Merged successfully")
    print(f"   SMA dataset: {len(df_sma)} observations")
    print(f"   EMA dataset: {len(df_ema)} observations")

    return df_sma, df_ema


def backtest_ghb_strategy(df: pd.DataFrame, ma_type: str) -> pd.DataFrame:
    """
    GHB Strategy backtest
    """
    trades = []
    tickers = df["ticker"].unique()

    for ticker in tickers:
        ticker_data = df[df["ticker"] == ticker].copy()
        ticker_data = ticker_data.sort_values("report_date").reset_index(drop=True)

        in_trade = False
        entry_date = None
        entry_price = None
        prev_weekly_state = None

        for i in range(len(ticker_data)):
            row = ticker_data.iloc[i]
            weekly_state = row["weekly_state"]
            price = row["current_price"]
            d200 = row["d200"]

            if not weekly_state or price == 0 or d200 == 0:
                prev_weekly_state = weekly_state
                continue

            # Entry: transition TO P1 AND price > D200
            if not in_trade:
                if weekly_state == "P1" and prev_weekly_state != "P1" and price > d200:
                    in_trade = True
                    entry_date = row["report_date"]
                    entry_price = price

            # Exit: transition TO N2 AND price < D200
            else:
                should_exit = False
                exit_reason = ""

                if weekly_state == "N2" and prev_weekly_state != "N2" and price < d200:
                    should_exit = True
                    exit_reason = f"N2 + Price < D200 ({ma_type})"

                if should_exit:
                    exit_date = row["report_date"]
                    exit_price = price
                    hold_weeks = (exit_date - entry_date).days / 7
                    return_pct = ((exit_price - entry_price) / entry_price) * 100

                    trades.append(
                        {
                            "ticker": ticker,
                            "entry_date": entry_date,
                            "exit_date": exit_date,
                            "entry_price": entry_price,
                            "exit_price": exit_price,
                            "return_pct": return_pct,
                            "hold_weeks": hold_weeks,
                            "exit_reason": exit_reason,
                            "ma_type": ma_type,
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None

            prev_weekly_state = weekly_state

    return pd.DataFrame(trades)


def analyze_results(trades: pd.DataFrame, strategy_name: str) -> dict:
    """Analyze backtest results"""

    if trades.empty:
        return {
            "strategy": strategy_name,
            "total_trades": 0,
            "win_rate": 0,
            "avg_return": 0,
            "avg_win": 0,
            "avg_loss": 0,
        }

    wins = trades[trades["return_pct"] > 0]
    losses = trades[trades["return_pct"] <= 0]

    return {
        "strategy": strategy_name,
        "total_trades": len(trades),
        "win_rate": len(wins) / len(trades) * 100,
        "avg_return": trades["return_pct"].mean(),
        "total_return": trades["return_pct"].sum(),
        "avg_win": wins["return_pct"].mean() if len(wins) > 0 else 0,
        "avg_loss": losses["return_pct"].mean() if len(losses) > 0 else 0,
        "median_return": trades["return_pct"].median(),
        "std_dev": trades["return_pct"].std(),
        "avg_hold_weeks": trades["hold_weeks"].mean(),
    }


def main():
    print("=" * 100)
    print("GHB STRATEGY: 200-DAY SMA vs 200-DAY EMA COMPARISON")
    print("=" * 100)
    print("\nTesting whether EMA improves GHB Strategy performance over SMA")
    print("Backtesting period: 2021-2025 (5 years)")
    print("Universe: NASDAQ 100 stocks")

    # Load weekly reports
    reports_dir = ROOT / "scanner_results" / "weekly_larsson"

    if not reports_dir.exists():
        print(f"\n❌ Error: Weekly reports directory not found")
        print(f"   Expected: {reports_dir}")
        return

    # Parse and augment with EMA
    print("\n" + "=" * 100)
    print("STEP 1: LOAD AND PREPARE DATA")
    print("=" * 100)

    df_sma, df_ema = parse_weekly_reports_with_ema(reports_dir)

    if df_sma.empty or df_ema.empty:
        print("\n❌ Error: No data loaded")
        return

    # Backtest with SMA
    print("\n" + "=" * 100)
    print("STEP 2: BACKTEST WITH 200-DAY SMA (ORIGINAL)")
    print("=" * 100)

    trades_sma = backtest_ghb_strategy(df_sma, "SMA")
    metrics_sma = analyze_results(trades_sma, "GHB Strategy (SMA)")

    print(f"\n✅ SMA Backtest Complete: {len(trades_sma)} trades")

    # Backtest with EMA
    print("\n" + "=" * 100)
    print("STEP 3: BACKTEST WITH 200-DAY EMA (ALTERNATIVE)")
    print("=" * 100)

    trades_ema = backtest_ghb_strategy(df_ema, "EMA")
    metrics_ema = analyze_results(trades_ema, "GHB Strategy (EMA)")

    print(f"\n✅ EMA Backtest Complete: {len(trades_ema)} trades")

    # Compare results
    print("\n" + "=" * 100)
    print("STEP 4: PERFORMANCE COMPARISON")
    print("=" * 100)

    comparison = pd.DataFrame([metrics_sma, metrics_ema])

    print(
        f"\n{'Metric':<25} {'SMA (Original)':<20} {'EMA (Alternative)':<20} {'Difference':<15}"
    )
    print("-" * 100)

    metrics_to_compare = [
        ("Total Trades", "total_trades", ""),
        ("Win Rate %", "win_rate", "%"),
        ("Avg Return %", "avg_return", "%"),
        ("Total Return %", "total_return", "%"),
        ("Avg Win %", "avg_win", "%"),
        ("Avg Loss %", "avg_loss", "%"),
        ("Median Return %", "median_return", "%"),
        ("Std Deviation %", "std_dev", "%"),
        ("Avg Hold Weeks", "avg_hold_weeks", ""),
    ]

    for label, metric, suffix in metrics_to_compare:
        sma_val = metrics_sma[metric]
        ema_val = metrics_ema[metric]
        diff = ema_val - sma_val

        if suffix == "%":
            diff_str = f"{diff:+.2f}%"
            sma_str = f"{sma_val:.2f}%"
            ema_str = f"{ema_val:.2f}%"
        else:
            diff_str = f"{diff:+.2f}"
            sma_str = f"{sma_val:.2f}"
            ema_str = f"{ema_val:.2f}"

        print(f"{label:<25} {sma_str:<20} {ema_str:<20} {diff_str:<15}")

    # Calculate annual returns
    years = 5
    sma_annual = metrics_sma["total_return"] / years
    ema_annual = metrics_ema["total_return"] / years

    print("\n" + "-" * 100)
    print(
        f"{'Annual Return (5yr avg)':<25} {sma_annual:+.2f}%{'':<13} {ema_annual:+.2f}%{'':<13} {(ema_annual - sma_annual):+.2f}%"
    )
    print("=" * 100)

    # Determine winner
    print("\n📊 VERDICT:")
    print("-" * 100)

    if ema_annual > sma_annual:
        improvement = ((ema_annual - sma_annual) / abs(sma_annual)) * 100
        print(f"✅ EMA WINS! Annual return improved by {improvement:+.1f}%")
        print(f"   SMA: {sma_annual:+.2f}% per year")
        print(f"   EMA: {ema_annual:+.2f}% per year")
        print(f"\n💡 RECOMMENDATION: Switch to 200-day EMA for GHB Strategy")
    elif sma_annual > ema_annual:
        degradation = ((sma_annual - ema_annual) / abs(sma_annual)) * 100
        print(f"✅ SMA WINS! EMA decreased returns by {degradation:.1f}%")
        print(f"   SMA: {sma_annual:+.2f}% per year")
        print(f"   EMA: {ema_annual:+.2f}% per year")
        print(f"\n💡 RECOMMENDATION: Keep using 200-day SMA (current)")
    else:
        print(f"🟰 TIE! Both perform identically")
        print(f"   Both: {sma_annual:+.2f}% per year")
        print(f"\n💡 RECOMMENDATION: No change needed, SMA is simpler")

    print("=" * 100)

    # Save results
    output_dir = ROOT / "backtest_results"
    output_dir.mkdir(exist_ok=True)

    trades_sma.to_csv(output_dir / "ghb_sma_trades.csv", index=False)
    trades_ema.to_csv(output_dir / "ghb_ema_trades.csv", index=False)
    comparison.to_csv(output_dir / "sma_vs_ema_comparison.csv", index=False)

    print(f"\n💾 Results saved to backtest_results/")
    print(f"   - ghb_sma_trades.csv ({len(trades_sma)} trades)")
    print(f"   - ghb_ema_trades.csv ({len(trades_ema)} trades)")
    print(f"   - sma_vs_ema_comparison.csv")
    print("=" * 100)


if __name__ == "__main__":
    main()

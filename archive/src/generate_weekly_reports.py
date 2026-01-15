"""
Generate Weekly Larsson Scanner Reports

Scans NASDAQ 100 tickers on weekly timeframe and calculates:
- Weekly Larsson state (P1, P2, N1, N2)
- Price vs 200 Day SMA
- Weekly closes and trends

Saves reports to scanner_results/weekly_larsson/
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")


def calculate_weekly_larsson(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate weekly Larsson states from daily price data.

    States:
    - P1 (GOLD): Strong bullish - Price > D200 and rising
    - P2 (GRAY): Consolidation above - Price > D200 but weak/sideways
    - N1 (GRAY): Weak bearish - Price < D200 recent
    - N2 (BLUE): Strong bearish - Price < D200 extended
    """
    # Calculate 200-day SMA
    df["D200"] = df["Close"].rolling(window=200).mean()

    # Resample to weekly (using Friday close or last available)
    weekly = (
        df.resample("W-FRI")
        .agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
                "D200": "last",
            }
        )
        .dropna(subset=["Close", "D200"])
    )

    # Calculate weekly momentum (4-week rate of change)
    weekly["ROC_4W"] = weekly["Close"].pct_change(4) * 100

    # Calculate distance from D200
    weekly["Distance_D200_Pct"] = (
        (weekly["Close"] - weekly["D200"]) / weekly["D200"]
    ) * 100

    # Determine weekly Larsson state
    def get_weekly_state(row):
        price = row["Close"]
        d200 = row["D200"]
        roc = row["ROC_4W"]
        distance_pct = row["Distance_D200_Pct"]

        if price > d200:
            # Above D200
            if roc > 5 or distance_pct > 10:
                return "P1"  # Strong bullish - momentum or extended above
            else:
                return "P2"  # Consolidation - above but weak
        else:
            # Below D200
            if distance_pct > -5:
                return "N1"  # Weak bearish - just below
            else:
                return "N2"  # Strong bearish - extended below

    weekly["Weekly_Larsson"] = weekly.apply(get_weekly_state, axis=1)

    return weekly


def scan_nasdaq100_weekly(
    tickers: list, reference_date: datetime = None
) -> pd.DataFrame:
    """
    Scan NASDAQ 100 tickers and generate weekly report.

    Args:
        tickers: List of ticker symbols
        reference_date: Date for the report (defaults to last Friday)

    Returns:
        DataFrame with weekly states for all tickers
    """
    if reference_date is None:
        # Get last Friday
        today = datetime.now()
        days_since_friday = (today.weekday() - 4) % 7
        reference_date = today - timedelta(days=days_since_friday)

    print(f"Scanning for week ending: {reference_date.strftime('%Y-%m-%d')}")

    results = []

    for i, ticker in enumerate(tickers, 1):
        try:
            print(f"  [{i}/{len(tickers)}] Processing {ticker}...", end="\r")

            # Download 2 years of daily data (need 200+ days for D200)
            stock = yf.Ticker(ticker)
            start_date = reference_date - timedelta(days=730)
            df = stock.history(start=start_date, end=reference_date)

            if len(df) < 200:
                continue  # Not enough data for D200

            # Calculate weekly states
            weekly_df = calculate_weekly_larsson(df)

            if len(weekly_df) == 0:
                continue

            # Get the most recent weekly state
            latest = weekly_df.iloc[-1]

            results.append(
                {
                    "Ticker": ticker,
                    "Week_End": latest.name.strftime("%Y-%m-%d"),
                    "Close": round(latest["Close"], 2),
                    "D200": round(latest["D200"], 2),
                    "Distance_D200_Pct": round(latest["Distance_D200_Pct"], 2),
                    "Weekly_Larsson": latest["Weekly_Larsson"],
                    "ROC_4W": round(latest["ROC_4W"], 2),
                    "Volume": int(latest["Volume"]),
                }
            )

        except Exception as e:
            print(f"  Error processing {ticker}: {e}")
            continue

    print(f"\nScanned {len(results)} tickers successfully")

    return pd.DataFrame(results)


def save_weekly_report(df: pd.DataFrame, output_dir: Path, report_date: datetime):
    """Save weekly report to Excel"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Format filename
    date_str = report_date.strftime("%Y%m%d")
    filename = f"nasdaq100_weekly_{date_str}.xlsx"
    filepath = output_dir / filename

    # Sort by weekly state priority (P1 > P2 > N1 > N2)
    state_order = {"P1": 1, "P2": 2, "N1": 3, "N2": 4}
    df["_sort"] = df["Weekly_Larsson"].map(state_order)
    df = df.sort_values(["_sort", "Distance_D200_Pct"], ascending=[True, False])
    df = df.drop(columns=["_sort"])

    # Create Excel writer
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # Summary sheet
        summary_df = pd.DataFrame(
            {
                "Metric": [
                    "Report Date",
                    "Total Tickers",
                    "P1 (Strong Bull)",
                    "P2 (Consolidation)",
                    "N1 (Weak Bear)",
                    "N2 (Strong Bear)",
                    "Avg Distance D200 (%)",
                ],
                "Value": [
                    report_date.strftime("%Y-%m-%d"),
                    len(df),
                    len(df[df["Weekly_Larsson"] == "P1"]),
                    len(df[df["Weekly_Larsson"] == "P2"]),
                    len(df[df["Weekly_Larsson"] == "N1"]),
                    len(df[df["Weekly_Larsson"] == "N2"]),
                    f"{df['Distance_D200_Pct'].mean():.2f}",
                ],
            }
        )
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # Full data sheet
        df.to_excel(writer, sheet_name="Weekly Data", index=False)

        # Separate sheets by state
        for state in ["P1", "P2", "N1", "N2"]:
            state_df = df[df["Weekly_Larsson"] == state]
            if len(state_df) > 0:
                state_df.to_excel(writer, sheet_name=f"State_{state}", index=False)

    print(f"Saved report: {filepath}")
    return filepath


def load_nasdaq100_tickers() -> list:
    """Load NASDAQ 100 tickers from data/weekly_stocks.txt or use default list"""
    stocks_file = Path("data/weekly_stocks.txt")

    if stocks_file.exists():
        with open(stocks_file, "r") as f:
            tickers = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
        print(f"Loaded {len(tickers)} tickers from {stocks_file}")
        return tickers

    # Default NASDAQ 100 top holdings if file doesn't exist
    print("Using default NASDAQ 100 tickers")
    return [
        "AAPL",
        "MSFT",
        "AMZN",
        "NVDA",
        "GOOGL",
        "META",
        "GOOG",
        "TSLA",
        "AVGO",
        "COST",
        "NFLX",
        "ASML",
        "AMD",
        "PEP",
        "ADBE",
        "CSCO",
        "TMUS",
        "LIN",
        "CMCSA",
        "TXN",
        "QCOM",
        "INTU",
        "AMAT",
        "HON",
        "AMGN",
        "ISRG",
        "BKNG",
        "ADP",
        "VRTX",
        "SBUX",
        "GILD",
        "PANW",
        "ADI",
        "MU",
        "LRCX",
        "REGN",
        "MDLZ",
        "PYPL",
        "KLAC",
        "SNPS",
        "CDNS",
        "MAR",
        "MELI",
        "CTAS",
        "CRWD",
        "ORLY",
        "FTNT",
        "ABNB",
        "CSX",
        "ADSK",
    ]


def generate_historical_weekly_reports(start_date: str, end_date: str = None):
    """
    Generate historical weekly reports for backtesting.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD), defaults to today
    """
    tickers = load_nasdaq100_tickers()
    output_dir = Path("scanner_results/weekly_larsson")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()

    print(f"\n{'='*70}")
    print(f"GENERATING WEEKLY REPORTS: {start_date} to {end.strftime('%Y-%m-%d')}")
    print(f"{'='*70}\n")

    # Generate weekly reports (every Friday)
    current_date = start
    while current_date <= end:
        # Move to next Friday
        days_until_friday = (4 - current_date.weekday()) % 7
        if days_until_friday == 0 and current_date > start:
            days_until_friday = 7
        current_date += timedelta(days=days_until_friday)

        if current_date > end:
            break

        print(f"\n{'='*70}")
        print(f"Week ending: {current_date.strftime('%Y-%m-%d')}")
        print(f"{'='*70}")

        # Scan tickers
        weekly_df = scan_nasdaq100_weekly(tickers, current_date)

        if len(weekly_df) > 0:
            # Save report
            save_weekly_report(weekly_df, output_dir, current_date)

        # Move to next week
        current_date += timedelta(days=7)

    print(f"\n{'='*70}")
    print("COMPLETE - All weekly reports generated")
    print(f"{'='*70}\n")


def main():
    """Generate current week's report"""
    print(f"\n{'='*70}")
    print("NASDAQ 100 WEEKLY LARSSON SCANNER")
    print(f"{'='*70}\n")

    # Load tickers
    tickers = load_nasdaq100_tickers()

    # Scan current week
    weekly_df = scan_nasdaq100_weekly(tickers)

    # Save report
    output_dir = Path("scanner_results/weekly_larsson")
    save_weekly_report(weekly_df, output_dir, datetime.now())

    # Print summary
    print(f"\n{'='*70}")
    print("WEEKLY STATE SUMMARY")
    print(f"{'='*70}")
    state_counts = weekly_df["Weekly_Larsson"].value_counts()
    for state, count in state_counts.items():
        print(f"  {state}: {count} tickers ({count/len(weekly_df)*100:.1f}%)")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Generate historical reports
        start_date = sys.argv[1]
        end_date = sys.argv[2] if len(sys.argv) > 2 else None
        generate_historical_weekly_reports(start_date, end_date)
    else:
        # Generate current week only
        main()

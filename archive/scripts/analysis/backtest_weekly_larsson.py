"""
Backtest Weekly Larsson Strategies on NASDAQ 100 (2021-2025)

Tests 3 weekly-only strategies:
- Strategy A: Pure P1 Trend (enter P1, exit N1/N2)
- Strategy B: Strict P1 Only (enter P1, exit P2)
- Strategy C: Breakout Confirmation (enter P2→P1, exit N1/N2)

All strategies require: Price > D200 SMA for entry
All strategies exit if: Price < D200 SMA (hard stop)
"""

import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import yfinance as yf

# Add src to path (script is in scripts/analysis/)
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


def parse_weekly_reports(reports_dir: Path) -> pd.DataFrame:
    """
    Parse all weekly watchlist reports and extract key data

    Returns DataFrame with columns:
    - report_date
    - ticker
    - weekly_state (P1, P2, N1, N2)
    - current_price
    - d200 (200-day SMA)
    """
    all_data = []

    excel_files = sorted(reports_dir.glob("nasdaq100_weekly_*.xlsx"))

    print(f"Found {len(excel_files)} weekly reports")
    print("Parsing reports...")

    parsed_count = 0
    for file_path in excel_files:
        # Extract date from filename
        try:
            filename = file_path.stem
            date_str = filename.split("_")[2]  # nasdaq100_weekly_YYYYMMDD
            report_date = datetime.strptime(date_str, "%Y%m%d").date()
        except:
            continue

        # Read Excel file
        try:
            # Read Excel - Weekly Data sheet with headers in row 0
            df = pd.read_excel(file_path, sheet_name="Weekly Data")

            # Skip empty rows and filter for valid ticker entries
            df = df.dropna(subset=["Ticker"])

            # Extract needed columns
            for _, row in df.iterrows():
                try:
                    ticker = str(row.get("Ticker", "")).strip()
                    weekly = str(row.get("Weekly_Larsson", "")).strip()
                    price = (
                        float(row.get("Close", 0)) if pd.notna(row.get("Close")) else 0
                    )
                    d200_val = (
                        float(row.get("D200", 0)) if pd.notna(row.get("D200")) else 0
                    )

                    if ticker and weekly:  # Only include valid rows
                        all_data.append(
                            {
                                "report_date": report_date,
                                "ticker": ticker,
                                "weekly_state": weekly,
                                "current_price": price,
                                "d200": d200_val,
                            }
                        )
                except Exception as row_e:
                    continue  # Skip problematic rows

            parsed_count += 1
            if parsed_count % 50 == 0:
                print(
                    f"  Parsed {parsed_count} files, collected {len(all_data)} rows..."
                )

        except Exception as e:
            # Skip files with errors (old format, missing sheets, etc.)
            continue

    print(f"Successfully parsed {parsed_count} files")
    print(f"Collected {len(all_data)} total rows before DataFrame creation")

    df = pd.DataFrame(all_data)
    df = df.sort_values(["ticker", "report_date"]).reset_index(drop=True)

    print(f"Parsed {len(df)} ticker-week combinations")
    print(f"Date range: {df['report_date'].min()} to {df['report_date'].max()}")
    print(f"Unique tickers: {df['ticker'].nunique()}")

    return df


def get_future_price(ticker: str, entry_date: datetime, exit_date: datetime) -> float:
    """Get actual price at exit date for return calculation"""
    try:
        data = yf.download(
            ticker,
            start=exit_date,
            end=exit_date + pd.Timedelta(days=7),  # Get week of data
            progress=False,
        )
        if not data.empty:
            return data["Close"].iloc[0]
    except:
        pass
    return None


def backtest_strategy_a(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy A: Pure P1 Trend
    Entry: Weekly = P1 AND Price > D200
    Exit: Weekly goes N1/N2 OR Price < D200
    """
    trades = []

    tickers = df["ticker"].unique()

    for ticker in tickers:
        ticker_data = df[df["ticker"] == ticker].copy()
        ticker_data = ticker_data.sort_values("report_date").reset_index(drop=True)

        in_trade = False
        entry_date = None
        entry_price = None

        for i in range(len(ticker_data)):
            row = ticker_data.iloc[i]
            weekly_state = row["weekly_state"]
            price = row["current_price"]
            d200 = row["d200"]

            # Skip if missing data
            if not weekly_state or price == 0 or d200 == 0:
                continue

            # Entry logic
            if not in_trade:
                if weekly_state == "P1" and price > d200:
                    in_trade = True
                    entry_date = row["report_date"]
                    entry_price = price

            # Exit logic
            else:
                should_exit = False
                exit_reason = ""

                # Exit on N1/N2
                if weekly_state in ["N1", "N2"]:
                    should_exit = True
                    exit_reason = f"Weekly {weekly_state}"

                # Exit on price < D200
                elif price < d200:
                    should_exit = True
                    exit_reason = "Price < D200"

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
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None

    return pd.DataFrame(trades)


def backtest_strategy_b(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy B: Strict P1 Only
    Entry: Weekly = P1 AND Price > D200
    Exit: Weekly goes P2/N1/N2 OR Price < D200
    """
    trades = []

    tickers = df["ticker"].unique()

    for ticker in tickers:
        ticker_data = df[df["ticker"] == ticker].copy()
        ticker_data = ticker_data.sort_values("report_date").reset_index(drop=True)

        in_trade = False
        entry_date = None
        entry_price = None

        for i in range(len(ticker_data)):
            row = ticker_data.iloc[i]
            weekly_state = row["weekly_state"]
            price = row["current_price"]
            d200 = row["d200"]

            if not weekly_state or price == 0 or d200 == 0:
                continue

            # Entry logic
            if not in_trade:
                if weekly_state == "P1" and price > d200:
                    in_trade = True
                    entry_date = row["report_date"]
                    entry_price = price

            # Exit logic - exits on ANY non-P1 state
            else:
                should_exit = False
                exit_reason = ""

                # Exit on any state change from P1
                if weekly_state != "P1":
                    should_exit = True
                    exit_reason = f"Weekly {weekly_state}"

                # Exit on price < D200
                elif price < d200:
                    should_exit = True
                    exit_reason = "Price < D200"

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
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None

    return pd.DataFrame(trades)


def backtest_strategy_c(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy C: Breakout Confirmation
    Entry: Weekly P2 → P1 transition AND Price > D200
    Exit: Weekly goes N1/N2 OR Price < D200
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

            # Entry logic - only on P2 → P1 transition
            if not in_trade:
                if prev_weekly_state == "P2" and weekly_state == "P1" and price > d200:
                    in_trade = True
                    entry_date = row["report_date"]
                    entry_price = price

            # Exit logic
            else:
                should_exit = False
                exit_reason = ""

                # Exit on N1/N2
                if weekly_state in ["N1", "N2"]:
                    should_exit = True
                    exit_reason = f"Weekly {weekly_state}"

                # Exit on price < D200
                elif price < d200:
                    should_exit = True
                    exit_reason = "Price < D200"

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
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None

            prev_weekly_state = weekly_state

    return pd.DataFrame(trades)


def backtest_ghb_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    GHB Strategy: Gold-Gray-Blue
    Entry: Weekly transitions TO P1 (Gold) AND Price > D200
    Hold: Weekly is P2 or N1 (Gray) - ride through consolidation
    Exit: Weekly transitions TO N2 (Blue) AND Price < D200
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

            # Entry logic - transition TO P1 (Gold) AND price > D200
            if not in_trade:
                if weekly_state == "P1" and prev_weekly_state != "P1" and price > d200:
                    in_trade = True
                    entry_date = row["report_date"]
                    entry_price = price

            # Exit logic
            else:
                should_exit = False
                exit_reason = ""

                # Exit on transition TO N2 (Blue) AND price < D200
                if weekly_state == "N2" and prev_weekly_state != "N2" and price < d200:
                    should_exit = True
                    exit_reason = "Transition to N2 (Blue) + Price < D200"

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
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None

            prev_weekly_state = weekly_state

    return pd.DataFrame(trades)


def backtest_strategy_e(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy E: State Transition Trading
    Entry: Weekly state improves (N2→N1, N2→P2, N1→P2, N1→P1, P2→P1) AND Price > D200
    Exit: Weekly state deteriorates (P1→P2, P1→N1, P2→N1, P2→N2, N1→N2) AND Price < D200
    """
    trades = []

    # Define state hierarchy (lower number = stronger bearish, higher = stronger bullish)
    state_rank = {"N2": 1, "N1": 2, "P2": 3, "P1": 4}

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

            # Entry logic - state improves (rank increases) AND price > D200
            if not in_trade:
                if (
                    prev_weekly_state
                    and weekly_state in state_rank
                    and prev_weekly_state in state_rank
                ):
                    # Check if state improved
                    if (
                        state_rank[weekly_state] > state_rank[prev_weekly_state]
                        and price > d200
                    ):
                        in_trade = True
                        entry_date = row["report_date"]
                        entry_price = price

            # Exit logic - state deteriorates (rank decreases) AND price < D200
            else:
                should_exit = False
                exit_reason = ""

                if (
                    prev_weekly_state
                    and weekly_state in state_rank
                    and prev_weekly_state in state_rank
                ):
                    # Check if state deteriorated
                    if (
                        state_rank[weekly_state] < state_rank[prev_weekly_state]
                        and price < d200
                    ):
                        should_exit = True
                        exit_reason = f"State deteriorated {prev_weekly_state}→{weekly_state} + Price < D200"

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
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None

            prev_weekly_state = weekly_state

    return pd.DataFrame(trades)


def backtest_strategy_f(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy F: Gold-Gray-Blue with 20% Trailing Stop
    Entry: Weekly state is P1 (Gold)
    Hold: Continue holding in P2 (Gray) or N1 (Gray)
    Exit: Whichever comes first:
      1. Price drops 20% from highest close since entry, OR
      2. Weekly state is N2 (Blue) AND Price < D200 SMA
    """
    trades = []
    trailing_stop_pct = 0.20  # 20% trailing stop

    tickers = df["ticker"].unique()

    for ticker in tickers:
        ticker_data = df[df["ticker"] == ticker].copy()
        ticker_data = ticker_data.sort_values("report_date").reset_index(drop=True)

        in_trade = False
        entry_date = None
        entry_price = None
        peak_price = None
        prev_weekly_state = None

        for i in range(len(ticker_data)):
            row = ticker_data.iloc[i]
            weekly_state = row["weekly_state"]
            price = row["current_price"]
            d200 = row["d200"]

            if not weekly_state or price == 0 or d200 == 0:
                prev_weekly_state = weekly_state
                continue

            # Entry logic - state is P1
            if not in_trade:
                if weekly_state == "P1":
                    in_trade = True
                    entry_date = row["report_date"]
                    entry_price = price
                    peak_price = price  # Initialize peak

            # Hold and exit logic
            else:
                # Update peak price
                if price > peak_price:
                    peak_price = price

                should_exit = False
                exit_reason = ""

                # Check trailing stop (20% drop from peak)
                drawdown_from_peak = (peak_price - price) / peak_price
                if drawdown_from_peak >= trailing_stop_pct:
                    should_exit = True
                    exit_reason = f"20% Trailing Stop (Peak: ${peak_price:.2f})"

                # Check N2 + below D200 exit
                elif (
                    weekly_state == "N2" and prev_weekly_state != "N2" and price < d200
                ):
                    should_exit = True
                    exit_reason = "Transition to N2 (Blue) + Price < D200"

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
                        }
                    )

                    in_trade = False
                    entry_date = None
                    entry_price = None
                    peak_price = None

            prev_weekly_state = weekly_state

    return pd.DataFrame(trades)


def analyze_results(trades_df: pd.DataFrame, strategy_name: str) -> dict:
    """Calculate comprehensive metrics for a strategy"""

    if trades_df.empty:
        return {
            "strategy": strategy_name,
            "total_trades": 0,
            "winners": 0,
            "losers": 0,
            "win_rate": 0,
            "avg_return": 0,
            "median_return": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "max_win": 0,
            "max_loss": 0,
            "avg_hold_weeks": 0,
            "median_hold_weeks": 0,
            "std_dev": 0,
        }

    returns = trades_df["return_pct"]
    winners = returns[returns > 0]
    losers = returns[returns <= 0]

    metrics = {
        "strategy": strategy_name,
        "total_trades": len(trades_df),
        "winners": len(winners),
        "losers": len(losers),
        "win_rate": (len(winners) / len(trades_df) * 100) if len(trades_df) > 0 else 0,
        "avg_return": returns.mean(),
        "median_return": returns.median(),
        "avg_win": winners.mean() if len(winners) > 0 else 0,
        "avg_loss": losers.mean() if len(losers) > 0 else 0,
        "max_win": returns.max(),
        "max_loss": returns.min(),
        "avg_hold_weeks": trades_df["hold_weeks"].mean(),
        "median_hold_weeks": trades_df["hold_weeks"].median(),
        "std_dev": returns.std(),
    }

    return metrics


def print_comparison_report(metrics_list: list):
    """Print side-by-side comparison of all strategies"""

    print("\n" + "=" * 175)
    print("WEEKLY LARSSON STRATEGY COMPARISON (2021-2025)")
    print("=" * 175)

    # Header
    print(
        f"\n{'Metric':<25} {'Strategy A':<18} {'Strategy B':<18} {'Strategy C':<18} {'GHB Strategy':<18} {'Strategy E':<18} {'Strategy F':<18}"
    )
    print(
        f"{'':25} {'Pure P1 Trend':<18} {'Strict P1 Only':<18} {'P2→P1 Breakout':<18} {'Gold-Gray-Blue':<18} {'State Transition':<18} {'D + 20% Stop':<18}"
    )
    print("-" * 175)

    # Extract metrics
    m_a = metrics_list[0]
    m_b = metrics_list[1]
    m_c = metrics_list[2]
    m_d = (
        metrics_list[3]
        if len(metrics_list) > 3
        else {
            "total_trades": 0,
            "winners": 0,
            "losers": 0,
            "win_rate": 0,
            "avg_return": 0,
            "median_return": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "max_win": 0,
            "max_loss": 0,
            "avg_hold_weeks": 0,
            "median_hold_weeks": 0,
        }
    )
    m_e = (
        metrics_list[4]
        if len(metrics_list) > 4
        else {
            "total_trades": 0,
            "winners": 0,
            "losers": 0,
            "win_rate": 0,
            "avg_return": 0,
            "median_return": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "max_win": 0,
            "max_loss": 0,
            "avg_hold_weeks": 0,
            "median_hold_weeks": 0,
        }
    )
    m_f = (
        metrics_list[5]
        if len(metrics_list) > 5
        else {
            "total_trades": 0,
            "winners": 0,
            "losers": 0,
            "win_rate": 0,
            "avg_return": 0,
            "median_return": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "max_win": 0,
            "max_loss": 0,
            "avg_hold_weeks": 0,
            "median_hold_weeks": 0,
        }
    )

    # Trades
    print(
        f"{'Total Trades':<25} {m_a['total_trades']:<18} {m_b['total_trades']:<18} {m_c['total_trades']:<18} {m_d['total_trades']:<18} {m_e['total_trades']:<18} {m_f['total_trades']:<18}"
    )
    print(
        f"{'Winners':<25} {m_a['winners']:<18} {m_b['winners']:<18} {m_c['winners']:<18} {m_d['winners']:<18} {m_e['winners']:<18} {m_f['winners']:<18}"
    )
    print(
        f"{'Losers':<25} {m_a['losers']:<18} {m_b['losers']:<18} {m_c['losers']:<18} {m_d['losers']:<18} {m_e['losers']:<18} {m_f['losers']:<18}"
    )

    # Win Rate
    print(
        f"\n{'Win Rate':<25} {m_a['win_rate']:.1f}%{' ':<13} {m_b['win_rate']:.1f}%{' ':<13} {m_c['win_rate']:.1f}%{' ':<13} {m_d['win_rate']:.1f}%{' ':<13} {m_e['win_rate']:.1f}%{' ':<13} {m_f['win_rate']:.1f}%"
    )

    # Returns
    print(
        f"\n{'Avg Return':<25} {m_a['avg_return']:+.2f}%{' ':<12} {m_b['avg_return']:+.2f}%{' ':<12} {m_c['avg_return']:+.2f}%{' ':<12} {m_d['avg_return']:+.2f}%{' ':<12} {m_e['avg_return']:+.2f}%{' ':<12} {m_f['avg_return']:+.2f}%"
    )
    print(
        f"{'Median Return':<25} {m_a['median_return']:+.2f}%{' ':<12} {m_b['median_return']:+.2f}%{' ':<12} {m_c['median_return']:+.2f}%{' ':<12} {m_d['median_return']:+.2f}%{' ':<12} {m_e['median_return']:+.2f}%{' ':<12} {m_f['median_return']:+.2f}%"
    )
    print(
        f"{'Avg Win':<25} {m_a['avg_win']:+.2f}%{' ':<12} {m_b['avg_win']:+.2f}%{' ':<12} {m_c['avg_win']:+.2f}%{' ':<12} {m_d['avg_win']:+.2f}%{' ':<12} {m_e['avg_win']:+.2f}%{' ':<12} {m_f['avg_win']:+.2f}%"
    )
    print(
        f"{'Avg Loss':<25} {m_a['avg_loss']:+.2f}%{' ':<12} {m_b['avg_loss']:+.2f}%{' ':<12} {m_c['avg_loss']:+.2f}%{' ':<12} {m_d['avg_loss']:+.2f}%{' ':<12} {m_e['avg_loss']:+.2f}%{' ':<12} {m_f['avg_loss']:+.2f}%"
    )

    # Extremes
    print(
        f"\n{'Max Win':<25} {m_a['max_win']:+.2f}%{' ':<12} {m_b['max_win']:+.2f}%{' ':<12} {m_c['max_win']:+.2f}%{' ':<12} {m_d['max_win']:+.2f}%{' ':<12} {m_e['max_win']:+.2f}%{' ':<12} {m_f['max_win']:+.2f}%"
    )
    print(
        f"{'Max Loss':<25} {m_a['max_loss']:+.2f}%{' ':<12} {m_b['max_loss']:+.2f}%{' ':<12} {m_c['max_loss']:+.2f}%{' ':<12} {m_d['max_loss']:+.2f}%{' ':<12} {m_e['max_loss']:+.2f}%{' ':<12} {m_f['max_loss']:+.2f}%"
    )

    # Hold Period
    print(
        f"\n{'Avg Hold (weeks)':<25} {m_a['avg_hold_weeks']:.1f}{' ':<14} {m_b['avg_hold_weeks']:.1f}{' ':<14} {m_c['avg_hold_weeks']:.1f}{' ':<14} {m_d['avg_hold_weeks']:.1f}{' ':<14} {m_e['avg_hold_weeks']:.1f}{' ':<14} {m_f['avg_hold_weeks']:.1f}"
    )
    print(
        f"{'Median Hold (weeks)':<25} {m_a['median_hold_weeks']:.1f}{' ':<14} {m_b['median_hold_weeks']:.1f}{' ':<14} {m_c['median_hold_weeks']:.1f}{' ':<14} {m_d['median_hold_weeks']:.1f}{' ':<14} {m_e['median_hold_weeks']:.1f}{' ':<14} {m_f['median_hold_weeks']:.1f}"
    )

    print("\n" + "=" * 175)

    # Determine winner
    best_win_rate = max(
        m_a["win_rate"],
        m_b["win_rate"],
        m_c["win_rate"],
        m_d["win_rate"],
        m_e["win_rate"],
    )
    best_avg_return = max(
        m_a["avg_return"],
        m_b["avg_return"],
        m_c["avg_return"],
        m_d["avg_return"],
        m_e["avg_return"],
    )

    print("\nRECOMMENDATION:")
    if m_a["win_rate"] == best_win_rate and m_a["avg_return"] == best_avg_return:
        print("  [WINNER] Strategy A: Pure P1 Trend - Best win rate and returns")
    elif m_b["win_rate"] == best_win_rate and m_b["avg_return"] == best_avg_return:
        print("  [WINNER] Strategy B: Strict P1 Only - Best win rate and returns")
    elif m_c["win_rate"] == best_win_rate and m_c["avg_return"] == best_avg_return:
        print("  [WINNER] Strategy C: P2→P1 Breakout - Best win rate and returns")
    else:
        print(
            "  [MIXED] No clear winner - consider trade frequency vs holding period preference"
        )

    print("\n" + "=" * 100)


def main():
    """Run backtest on all 3 strategies"""

    print("=" * 100)
    print("WEEKLY LARSSON STRATEGY BACKTEST - NASDAQ 100 (2021-2025)")
    print("=" * 100)

    # Load historical weekly reports
    reports_dir = ROOT / "scanner_results" / "weekly_larsson"

    if not reports_dir.exists():
        print(f"\n[ERROR] Directory not found: {reports_dir}")
        return

    # Parse all weekly reports
    df = parse_weekly_reports(reports_dir)

    if df.empty:
        print("\n[ERROR] No data parsed from reports!")
        return

    print(f"\n[OK] Loaded {len(df)} weekly observations")

    # Test Strategy A: Pure P1 Trend
    print("\nTesting Strategy A: Pure P1 Trend (enter P1, exit N1/N2)...")
    trades_a = backtest_strategy_a(df)
    metrics_a = analyze_results(trades_a, "Strategy A")
    print(f"  Generated {len(trades_a)} trades")

    # Test Strategy B: Strict P1 Only
    print("\nTesting Strategy B: Strict P1 Only (enter P1, exit P2)...")
    trades_b = backtest_strategy_b(df)
    metrics_b = analyze_results(trades_b, "Strategy B")
    print(f"  Generated {len(trades_b)} trades")

    # Test Strategy C: Breakout Confirmation
    print("\nTesting Strategy C: P2→P1 Breakout (enter P2→P1, exit N1/N2)...")
    trades_c = backtest_strategy_c(df)
    metrics_c = analyze_results(trades_c, "Strategy C")
    print(f"  Generated {len(trades_c)} trades")

    # Test GHB Strategy: Gold-Gray-Blue
    print("\nTesting GHB Strategy: Gold-Gray-Blue (enter P1, hold P2/N1, exit N2)...")
    trades_d = backtest_ghb_strategy(df)
    metrics_d = analyze_results(trades_d, "GHB Strategy")
    print(f"  Generated {len(trades_d)} trades")

    # Test Strategy E: State Transition Trading
    print(
        "\nTesting Strategy E: State Transition (enter on improvement, exit on deterioration)..."
    )
    trades_e = backtest_strategy_e(df)
    metrics_e = analyze_results(trades_e, "Strategy E")
    print(f"  Generated {len(trades_e)} trades")

    # Test Strategy F: GHB Strategy + 20% Trailing Stop
    print("\nTesting Strategy F: Gold-Gray-Blue + 20% Trailing Stop...")
    trades_f = backtest_strategy_f(df)
    metrics_f = analyze_results(trades_f, "Strategy F")
    print(f"  Generated {len(trades_f)} trades")

    # Print comparison
    print_comparison_report(
        [metrics_a, metrics_b, metrics_c, metrics_d, metrics_e, metrics_f]
    )

    # Save detailed results
    output_dir = ROOT / "backtest_results"
    output_dir.mkdir(exist_ok=True)

    trades_a.to_csv(output_dir / "weekly_strategy_a_trades.csv", index=False)
    trades_b.to_csv(output_dir / "weekly_strategy_b_trades.csv", index=False)
    trades_c.to_csv(output_dir / "weekly_strategy_c_trades.csv", index=False)
    trades_d.to_csv(output_dir / "weekly_ghb_strategy_trades.csv", index=False)
    trades_e.to_csv(output_dir / "weekly_strategy_e_trades.csv", index=False)
    trades_f.to_csv(output_dir / "weekly_strategy_f_trades.csv", index=False)

    # Save summary
    summary_df = pd.DataFrame(
        [metrics_a, metrics_b, metrics_c, metrics_d, metrics_e, metrics_f]
    )
    summary_df.to_csv(output_dir / "weekly_strategies_summary.csv", index=False)

    print(f"\n[OK] Detailed results saved to backtest_results/")
    print(f"  - weekly_strategy_a_trades.csv ({len(trades_a)} trades)")
    print(f"  - weekly_strategy_b_trades.csv ({len(trades_b)} trades)")
    print(f"  - weekly_strategy_c_trades.csv ({len(trades_c)} trades)")
    print(f"  - weekly_ghb_strategy_trades.csv ({len(trades_d)} trades)")
    print(f"  - weekly_strategy_e_trades.csv ({len(trades_e)} trades)")
    print(f"  - weekly_strategy_f_trades.csv ({len(trades_f)} trades)")
    print(f"  - weekly_strategies_summary.csv")
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()

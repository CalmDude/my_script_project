"""
Signal Performance Tracker - Track Larsson signals and their outcomes

Logs every signal trigger and calculates returns 30/60/90 days later.
Helps build confidence in the trading system by showing historical win rates.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf
import logging

logger = logging.getLogger(__name__)


def log_signal(
    ticker: str,
    signal: str,
    price: float,
    buy_quality: str = None,
    history_file: Path = None,
):
    """
    Log a new signal trigger to signal_history.csv

    Args:
        ticker: Stock symbol
        signal: Larsson signal (e.g., "FULL HOLD + ADD")
        price: Current price when signal triggered
        buy_quality: Quality rating (EXCELLENT/GOOD/OK/EXTENDED/WEAK)
        history_file: Path to signal_history.csv
    """
    if history_file is None:
        history_file = Path("data/signal_history.csv")

    # Create file if it doesn't exist
    if not history_file.exists():
        history_file.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(
            columns=[
                "date",
                "ticker",
                "signal",
                "trigger_price",
                "buy_quality",
                "return_30d",
                "return_60d",
                "return_90d",
                "price_30d",
                "price_60d",
                "price_90d",
            ]
        )
        df.to_csv(history_file, index=False)

    # Read existing history
    history = pd.read_csv(history_file)

    # Check if this signal already logged today
    today = datetime.now().strftime("%Y-%m-%d")
    existing = history[
        (history["ticker"] == ticker)
        & (history["date"] == today)
        & (history["signal"] == signal)
    ]

    if not existing.empty:
        logger.info(f"Signal already logged today: {ticker} {signal}")
        return

    # Add new signal
    new_row = {
        "date": today,
        "ticker": ticker,
        "signal": signal,
        "trigger_price": price,
        "buy_quality": buy_quality if buy_quality else "",
        "return_30d": None,
        "return_60d": None,
        "return_90d": None,
        "price_30d": None,
        "price_60d": None,
        "price_90d": None,
    }

    history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)
    history.to_csv(history_file, index=False)
    logger.info(f"Logged signal: {ticker} {signal} @ ${price:.2f}")


def update_returns(history_file: Path = None, lookback_days: int = 120):
    """
    Update returns for signals that are 30/60/90 days old

    Args:
        history_file: Path to signal_history.csv
        lookback_days: Only check signals from last N days (performance optimization)
    """
    if history_file is None:
        history_file = Path("data/signal_history.csv")

    if not history_file.exists():
        logger.warning(f"Signal history file not found: {history_file}")
        return

    history = pd.read_csv(history_file)
    history["date"] = pd.to_datetime(history["date"])

    # Only update recent signals (older ones already have returns)
    cutoff = datetime.now() - timedelta(days=lookback_days)
    recent_signals = history[history["date"] >= cutoff].copy()

    if recent_signals.empty:
        return

    today = datetime.now()
    updated_count = 0

    for idx, row in recent_signals.iterrows():
        signal_date = row["date"]
        ticker = row["ticker"]
        trigger_price = row["trigger_price"]

        # Calculate target dates
        date_30 = signal_date + timedelta(days=30)
        date_60 = signal_date + timedelta(days=60)
        date_90 = signal_date + timedelta(days=90)

        # Check which returns need updating
        needs_update = False
        if pd.isna(row["return_30d"]) and today >= date_30:
            needs_update = True
        if pd.isna(row["return_60d"]) and today >= date_60:
            needs_update = True
        if pd.isna(row["return_90d"]) and today >= date_90:
            needs_update = True

        if not needs_update:
            continue

        try:
            # Fetch historical data
            stock = yf.Ticker(ticker)
            start_date = signal_date.strftime("%Y-%m-%d")
            end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                logger.warning(f"No price data for {ticker} from {start_date}")
                continue

            # Update 30-day return
            if pd.isna(row["return_30d"]) and today >= date_30:
                price_30 = (
                    hist[hist.index >= date_30]["Close"].iloc[0]
                    if len(hist[hist.index >= date_30]) > 0
                    else None
                )
                if price_30:
                    history.at[idx, "price_30d"] = price_30
                    history.at[idx, "return_30d"] = (
                        (price_30 - trigger_price) / trigger_price
                    ) * 100
                    updated_count += 1

            # Update 60-day return
            if pd.isna(row["return_60d"]) and today >= date_60:
                price_60 = (
                    hist[hist.index >= date_60]["Close"].iloc[0]
                    if len(hist[hist.index >= date_60]) > 0
                    else None
                )
                if price_60:
                    history.at[idx, "price_60d"] = price_60
                    history.at[idx, "return_60d"] = (
                        (price_60 - trigger_price) / trigger_price
                    ) * 100
                    updated_count += 1

            # Update 90-day return
            if pd.isna(row["return_90d"]) and today >= date_90:
                price_90 = (
                    hist[hist.index >= date_90]["Close"].iloc[0]
                    if len(hist[hist.index >= date_90]) > 0
                    else None
                )
                if price_90:
                    history.at[idx, "price_90d"] = price_90
                    history.at[idx, "return_90d"] = (
                        (price_90 - trigger_price) / trigger_price
                    ) * 100
                    updated_count += 1

        except Exception as e:
            logger.error(f"Error updating returns for {ticker}: {e}")

    # Save updated history
    if updated_count > 0:
        history.to_csv(history_file, index=False)
        logger.info(f"Updated {updated_count} return values")


def get_signal_performance(
    signal_type: str = None, history_file: Path = None, min_quality: str = None
):
    """
    Calculate performance statistics for signals

    Args:
        signal_type: Filter by signal type (e.g., "FULL HOLD + ADD")
        history_file: Path to signal_history.csv
        min_quality: Only include signals with this quality or better

    Returns:
        dict with performance stats (win_rate, avg_return, etc.)
    """
    if history_file is None:
        history_file = Path("data/signal_history.csv")

    if not history_file.exists():
        return {
            "total_signals": 0,
            "win_rate_30d": 0,
            "win_rate_60d": 0,
            "win_rate_90d": 0,
            "avg_return_30d": 0,
            "avg_return_60d": 0,
            "avg_return_90d": 0,
        }

    history = pd.read_csv(history_file)

    # Apply filters
    if signal_type:
        history = history[history["signal"] == signal_type]

    if min_quality:
        quality_order = ["EXCELLENT", "GOOD", "OK", "EXTENDED", "WEAK"]
        min_idx = (
            quality_order.index(min_quality)
            if min_quality in quality_order
            else len(quality_order)
        )
        valid_qualities = quality_order[: min_idx + 1]
        history = history[history["buy_quality"].isin(valid_qualities)]

    # Calculate stats
    stats = {
        "total_signals": len(history),
    }

    for period in [30, 60, 90]:
        col = f"return_{period}d"
        returns = history[col].dropna()

        if len(returns) > 0:
            wins = (returns > 0).sum()
            stats[f"win_rate_{period}d"] = (wins / len(returns)) * 100
            stats[f"avg_return_{period}d"] = returns.mean()
            stats[f"median_return_{period}d"] = returns.median()
            stats[f"best_return_{period}d"] = returns.max()
            stats[f"worst_return_{period}d"] = returns.min()
            stats[f"signals_with_data_{period}d"] = len(returns)
        else:
            stats[f"win_rate_{period}d"] = 0
            stats[f"avg_return_{period}d"] = 0
            stats[f"median_return_{period}d"] = 0
            stats[f"best_return_{period}d"] = 0
            stats[f"worst_return_{period}d"] = 0
            stats[f"signals_with_data_{period}d"] = 0

    return stats

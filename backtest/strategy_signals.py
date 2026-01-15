"""
Strategy Signals Calculator for GHB Strategy Backtest
Implements the GHB (Gold-Gray-Blue) weekly momentum strategy
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class GHBStrategy:
    """
    GHB Strategy Signal Calculator

    States:
    - P1 (Gold): Strong uptrend - BUY signal
    - P2 (Gray): Consolidation above D200 - HOLD signal
    - N1 (Gray): Shallow pullback below D200 - HOLD signal
    - N2 (Blue): Downtrend - SELL signal
    """

    def __init__(self):
        """Initialize GHB Strategy calculator"""
        self.name = "GHB Strategy (Gold-Gray-Blue)"
        self.required_history = 200  # Need 200 days for D200

    def calculate_d200(self, df: pd.DataFrame) -> float:
        """Calculate 200-day Simple Moving Average"""
        if len(df) < 200:
            return np.nan
        return df["Close"].iloc[-200:].mean()

    def calculate_roc_4w(self, df: pd.DataFrame) -> float:
        """Calculate 4-week (20 trading days) Rate of Change"""
        if len(df) < 20:
            return 0.0

        close_now = df["Close"].iloc[-1]
        close_4w_ago = df["Close"].iloc[-20]

        roc = ((close_now - close_4w_ago) / close_4w_ago) * 100
        return roc

    def calculate_distance_from_d200(self, close: float, d200: float) -> float:
        """Calculate percentage distance from D200"""
        if pd.isna(d200) or d200 == 0:
            return 0.0
        return ((close - d200) / d200) * 100

    def determine_state(
        self, close: float, d200: float, roc_4w: float, distance_pct: float
    ) -> str:
        """
        Determine GHB state based on Strategy D rules

        Rules:
        - P1: Price > D200 AND (ROC > 5% OR Distance > 10%)
        - P2: Price > D200 AND NOT P1 conditions
        - N1: Price < D200 AND Distance > -5%
        - N2: Price < D200 AND Distance <= -5%
        """
        if pd.isna(d200):
            return "UNKNOWN"

        if close > d200:
            # Above D200
            if roc_4w > 5 or distance_pct > 10:
                return "P1"  # Strong bullish
            else:
                return "P2"  # Consolidation
        else:
            # Below D200
            if distance_pct > -5:
                return "N1"  # Shallow pullback
            else:
                return "N2"  # Downtrend

    def calculate_signals(self, df: pd.DataFrame, ticker: str = None) -> Dict:
        """
        Calculate GHB signals for a single stock's price history

        Args:
            df: DataFrame with columns [Date, Open, High, Low, Close, Volume]
            ticker: Optional ticker symbol for labeling

        Returns:
            Dictionary with signal data
        """
        if df.empty or len(df) < self.required_history:
            return None

        # Get latest close
        close = df["Close"].iloc[-1]

        # Calculate D200
        d200 = self.calculate_d200(df)

        # Calculate 4-week ROC
        roc_4w = self.calculate_roc_4w(df)

        # Calculate distance from D200
        distance_pct = self.calculate_distance_from_d200(close, d200)

        # Determine state
        state = self.determine_state(close, d200, roc_4w, distance_pct)

        # Map state to signal
        signal_map = {
            "P1": "BUY",
            "P2": "HOLD",
            "N1": "HOLD",
            "N2": "SELL",
            "UNKNOWN": "SKIP",
        }

        signal = signal_map.get(state, "SKIP")

        return {
            "Ticker": ticker if ticker else "UNKNOWN",
            "Date": df["Date"].iloc[-1] if "Date" in df.columns else pd.Timestamp.now(),
            "Close": close,
            "D200": d200,
            "Distance_%": distance_pct,
            "ROC_4W_%": roc_4w,
            "State": state,
            "Signal": signal,
        }

    def calculate_signals_for_date(
        self, df: pd.DataFrame, target_date: pd.Timestamp, ticker: str = None
    ) -> Dict:
        """
        Calculate GHB signals as of a specific historical date

        This is used in backtesting to simulate what signals would have been on a past Friday

        Args:
            df: Full price history DataFrame
            target_date: The date to calculate signals for (should be a Friday)
            ticker: Optional ticker symbol

        Returns:
            Dictionary with signal data as of that date
        """
        # Filter data up to and including target_date
        df_historical = df[df["Date"] <= target_date].copy()

        if len(df_historical) < self.required_history:
            return None

        # Calculate signals using only historical data
        signals = self.calculate_signals(df_historical, ticker)

        # Ensure the date in result is the target_date
        if signals:
            signals["Date"] = target_date

        return signals

    def scan_universe(
        self, data_dict: Dict[str, pd.DataFrame], target_date: pd.Timestamp = None
    ) -> pd.DataFrame:
        """
        Scan entire universe of stocks and calculate signals

        Args:
            data_dict: Dictionary of {ticker: DataFrame}
            target_date: Optional specific date to calculate for (for backtesting)

        Returns:
            DataFrame with signals for all stocks
        """
        results = []

        for ticker, df in data_dict.items():
            if target_date:
                signals = self.calculate_signals_for_date(df, target_date, ticker)
            else:
                signals = self.calculate_signals(df, ticker)

            if signals:
                results.append(signals)

        if not results:
            return pd.DataFrame()

        df_results = pd.DataFrame(results)

        # Sort by ROC (best opportunities first)
        df_results = df_results.sort_values("ROC_4W_%", ascending=False)

        return df_results

    def get_buy_candidates(
        self, df_signals: pd.DataFrame, max_candidates: int = 20
    ) -> pd.DataFrame:
        """Get top buy candidates (P1 stocks)"""
        buy_signals = df_signals[df_signals["State"] == "P1"].copy()
        return buy_signals.head(max_candidates)

    def get_sell_signals(self, df_signals: pd.DataFrame) -> pd.DataFrame:
        """Get sell signals (N2 stocks)"""
        return df_signals[df_signals["State"] == "N2"].copy()

    def get_hold_signals(self, df_signals: pd.DataFrame) -> pd.DataFrame:
        """Get hold signals (P2 and N1 stocks)"""
        return df_signals[df_signals["State"].isin(["P2", "N1"])].copy()


if __name__ == "__main__":
    # Test the strategy calculator
    import yfinance as yf
    from datetime import datetime, timedelta

    print("=" * 80)
    print("Testing GHB Strategy Calculator")
    print("=" * 80)

    strategy = GHBStrategy()

    # Test with a single stock
    ticker = "NVDA"
    print(f"\n📊 Testing with {ticker}...")

    stock = yf.Ticker(ticker)
    df = stock.history(period="1y", interval="1d")
    df = df.reset_index()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Calculate current signals
    signals = strategy.calculate_signals(df, ticker)

    print(f"\n✅ Current Signals for {ticker}:")
    for key, value in signals.items():
        if key != "Date":
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")

    # Test historical signal (30 days ago)
    historical_date = df["Date"].iloc[-30]
    historical_signals = strategy.calculate_signals_for_date(
        df, historical_date, ticker
    )

    print(f"\n📅 Historical Signals for {ticker} on {historical_date.date()}:")
    print(f"   State: {historical_signals['State']}")
    print(f"   Signal: {historical_signals['Signal']}")
    print(f"   ROC 4W: {historical_signals['ROC_4W_%']:.2f}%")

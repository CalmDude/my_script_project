"""
Phase 2 Enhanced Strategy with ATR Stop Losses and Momentum Entry Filters
Keep unbiased universe, enhance trading logic
"""

import pandas as pd
import numpy as np
from typing import Dict

from strategy_signals import GHBStrategy


class GHBStrategyPhase2(GHBStrategy):
    """
    Phase 2 Enhancements to GHB Strategy:
    1. ATR-based stop losses (-2×ATR exit)
    2. Momentum entry filters (RSI >50, Price >50-day MA, 4-week ROC >10%)
    3. Keep all original logic, add protective layers
    """

    def __init__(self, use_stop_losses=True, use_entry_filters=True):
        super().__init__()
        self.name = "GHB Strategy Phase 2 (Enhanced)"
        self.use_stop_losses = use_stop_losses
        self.use_entry_filters = use_entry_filters

    def calculate_atr(self, df: pd.DataFrame, period=14) -> float:
        """Calculate Average True Range"""
        if len(df) < period + 1:
            return np.nan

        df_calc = df.iloc[-(period + 1) :].copy()

        high = df_calc["High"]
        low = df_calc["Low"]
        close_prev = df_calc["Close"].shift(1)

        tr1 = high - low
        tr2 = abs(high - close_prev)
        tr3 = abs(low - close_prev)

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.iloc[1:].mean()  # Skip first NaN

        return atr

    def calculate_rsi(self, df: pd.DataFrame, period=14) -> float:
        """Calculate RSI indicator"""
        if len(df) < period + 1:
            return np.nan

        closes = df["Close"].iloc[-(period + 1) :]
        delta = closes.diff()

        gain = (delta.where(delta > 0, 0)).mean()
        loss = (-delta.where(delta < 0, 0)).mean()

        if loss == 0:
            return 100.0

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_sma_50(self, df: pd.DataFrame) -> float:
        """Calculate 50-day Simple Moving Average"""
        if len(df) < 50:
            return np.nan
        return df["Close"].iloc[-50:].mean()

    def check_entry_filters(
        self, df: pd.DataFrame, close: float, roc_4w: float
    ) -> Dict:
        """
        Phase 2 Entry Filters - Only enter if momentum is strong

        Filters:
        1. RSI > 50 (trending up)
        2. Price > 50-day MA (intermediate uptrend)
        3. 4-week ROC > 10% (strong momentum already confirmed)

        Returns: {
            'passed': bool,
            'rsi': float,
            'sma_50': float,
            'distance_from_sma': float,
            'reason': str if failed
        }
        """
        if not self.use_entry_filters:
            return {"passed": True, "reason": "Entry filters disabled"}

        # Calculate indicators
        rsi = self.calculate_rsi(df)
        sma_50 = self.calculate_sma_50(df)

        # Check filters
        filters_passed = True
        reason = ""

        if pd.isna(rsi) or rsi < 50:
            filters_passed = False
            reason = (
                f"RSI too low ({rsi:.1f} < 50)"
                if not pd.isna(rsi)
                else "RSI unavailable"
            )
        elif pd.notna(sma_50) and close < sma_50:
            filters_passed = False
            distance_pct = ((close - sma_50) / sma_50) * 100
            reason = f"Below 50-day MA ({distance_pct:.1f}%)"
        elif roc_4w < 10:
            filters_passed = False
            reason = f"ROC too weak ({roc_4w:.1f}% < 10%)"

        distance_from_sma = ((close - sma_50) / sma_50) * 100 if pd.notna(sma_50) else 0

        return {
            "passed": filters_passed,
            "rsi": rsi,
            "sma_50": sma_50,
            "distance_from_sma_%": distance_from_sma,
            "reason": reason if not filters_passed else "All filters passed",
        }

    def check_stop_loss(
        self, entry_price: float, current_price: float, atr: float
    ) -> Dict:
        """
        Phase 2 Stop Loss - Exit if loss exceeds 2×ATR from entry

        Returns: {
            'hit': bool,
            'stop_price': float,
            'current_loss_pct': float,
            'atr': float
        }
        """
        if not self.use_stop_losses or pd.isna(atr):
            return {"hit": False, "stop_price": None, "atr": atr}

        # Stop loss at entry - 2×ATR
        stop_price = entry_price - (2 * atr)

        # Check if stopped out
        hit = current_price <= stop_price

        current_loss_pct = ((current_price - entry_price) / entry_price) * 100

        return {
            "hit": hit,
            "stop_price": stop_price,
            "current_loss_pct": current_loss_pct,
            "atr": atr,
        }

    def calculate_signals(self, df: pd.DataFrame, ticker: str = None) -> Dict:
        """
        Enhanced GHB signals with Phase 2 improvements
        """
        # Get base GHB signals
        base_signals = super().calculate_signals(df, ticker)

        if not base_signals:
            return None

        close = base_signals["Close"]
        roc_4w = base_signals["ROC_4W_%"]

        # Add Phase 2 metrics
        atr = self.calculate_atr(df)
        rsi = self.calculate_rsi(df)
        sma_50 = self.calculate_sma_50(df)

        # Check entry filters (only for BUY signals)
        entry_check = {"passed": True, "reason": "N/A"}
        if base_signals["Signal"] == "BUY":
            entry_check = self.check_entry_filters(df, close, roc_4w)

            # Override BUY signal if filters fail
            if not entry_check["passed"]:
                base_signals["Signal"] = "SKIP"
                base_signals["State"] = "P1_FILTERED"

        # Add enhanced metrics to signals
        base_signals.update(
            {
                "ATR": atr,
                "RSI": rsi,
                "SMA_50": sma_50,
                "Entry_Filter_Passed": entry_check["passed"],
                "Entry_Filter_Reason": entry_check["reason"],
            }
        )

        return base_signals

    def calculate_signals_for_date(
        self, df: pd.DataFrame, target_date: pd.Timestamp, ticker: str = None
    ) -> Dict:
        """Calculate enhanced signals as of specific date"""
        # Filter data up to target_date
        df_historical = df[df["Date"] <= target_date].copy()

        if len(df_historical) < self.required_history:
            return None

        # Calculate enhanced signals
        signals = self.calculate_signals(df_historical, ticker)

        if signals:
            signals["Date"] = target_date

        return signals


if __name__ == "__main__":
    import yfinance as yf

    print("=" * 80)
    print("Testing GHB Strategy Phase 2 Enhancements")
    print("=" * 80)

    # Test with energy winner
    ticker = "DVN"
    print(f"\n📊 Testing with {ticker} (energy winner)...")

    stock = yf.Ticker(ticker)
    df = stock.history(start="2021-01-01", end="2021-12-31", interval="1d")
    df = df.reset_index()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Test original vs Phase 2
    strategy_original = GHBStrategy()
    strategy_phase2 = GHBStrategyPhase2(use_stop_losses=True, use_entry_filters=True)

    # Get signals from mid-2021
    test_date = pd.Timestamp("2021-06-01")
    df_test = df[df["Date"] <= test_date].copy()

    if len(df_test) >= 200:
        print(f"\n🔍 Signals as of {test_date.date()}:")

        signals_orig = strategy_original.calculate_signals(df_test, ticker)
        signals_phase2 = strategy_phase2.calculate_signals(df_test, ticker)

        print(f"\n  Original GHB:")
        print(f"    State: {signals_orig['State']}")
        print(f"    Signal: {signals_orig['Signal']}")
        print(f"    ROC 4W: {signals_orig['ROC_4W_%']:.1f}%")

        print(f"\n  Phase 2 Enhanced:")
        print(f"    State: {signals_phase2['State']}")
        print(f"    Signal: {signals_phase2['Signal']}")
        print(f"    ROC 4W: {signals_phase2['ROC_4W_%']:.1f}%")
        print(f"    RSI: {signals_phase2['RSI']:.1f}")
        print(f"    ATR: ${signals_phase2['ATR']:.2f}")
        print(f"    Entry Filter: {signals_phase2['Entry_Filter_Passed']}")
        print(f"    Filter Reason: {signals_phase2['Entry_Filter_Reason']}")

    print("\n" + "=" * 80)
    print("✅ Phase 2 Strategy Test Complete")
    print("=" * 80)

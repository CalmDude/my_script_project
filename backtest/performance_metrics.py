"""
Performance Metrics Calculator for GHB Strategy Backtest
Calculates advanced performance statistics
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime


class PerformanceMetrics:
    """Calculate comprehensive performance metrics"""

    @staticmethod
    def calculate_returns(df_equity: pd.DataFrame) -> Dict:
        """Calculate various return metrics"""
        if df_equity.empty:
            return {}

        starting_value = df_equity["Portfolio_Value"].iloc[0]
        final_value = df_equity["Portfolio_Value"].iloc[-1]

        total_return_pct = ((final_value - starting_value) / starting_value) * 100

        # Calculate period length in years
        days = (df_equity["Date"].iloc[-1] - df_equity["Date"].iloc[0]).days
        years = days / 365.25

        # CAGR
        if years > 0:
            cagr = (((final_value / starting_value) ** (1 / years)) - 1) * 100
        else:
            cagr = 0

        return {
            "Total_Return_%": total_return_pct,
            "CAGR_%": cagr,
            "Starting_Value": starting_value,
            "Final_Value": final_value,
            "Period_Years": years,
        }

    @staticmethod
    def calculate_drawdown(df_equity: pd.DataFrame) -> Dict:
        """Calculate drawdown metrics"""
        if df_equity.empty:
            return {}

        # Calculate running maximum
        running_max = df_equity["Portfolio_Value"].expanding().max()

        # Calculate drawdown
        drawdown = (df_equity["Portfolio_Value"] - running_max) / running_max * 100

        # Max drawdown
        max_drawdown = drawdown.min()
        max_dd_date = df_equity.loc[drawdown.idxmin(), "Date"]

        # Average drawdown (only negative values)
        avg_drawdown = drawdown[drawdown < 0].mean() if any(drawdown < 0) else 0

        # Drawdown duration (longest period underwater)
        underwater = (df_equity["Portfolio_Value"] < running_max).astype(int)
        underwater_periods = underwater.groupby(
            (underwater != underwater.shift()).cumsum()
        ).cumsum()
        max_duration = underwater_periods.max() if len(underwater_periods) > 0 else 0

        return {
            "Max_Drawdown_%": max_drawdown,
            "Max_Drawdown_Date": max_dd_date,
            "Avg_Drawdown_%": avg_drawdown,
            "Max_Underwater_Periods": max_duration,
        }

    @staticmethod
    def calculate_sharpe_ratio(
        df_equity: pd.DataFrame, risk_free_rate: float = 0.0
    ) -> float:
        """
        Calculate Sharpe Ratio

        Args:
            df_equity: Equity curve dataframe
            risk_free_rate: Annual risk-free rate (default 0%)

        Returns:
            Sharpe ratio
        """
        if df_equity.empty or len(df_equity) < 2:
            return 0.0

        # Calculate weekly returns
        df_equity = df_equity.sort_values("Date")
        returns = df_equity["Portfolio_Value"].pct_change().dropna()

        if len(returns) == 0:
            return 0.0

        # Annualize (assuming weekly returns, ~52 weeks per year)
        avg_return = returns.mean() * 52
        std_return = returns.std() * np.sqrt(52)

        if std_return == 0:
            return 0.0

        sharpe = (avg_return - risk_free_rate) / std_return

        return sharpe

    @staticmethod
    def calculate_sortino_ratio(
        df_equity: pd.DataFrame, risk_free_rate: float = 0.0
    ) -> float:
        """
        Calculate Sortino Ratio (only penalizes downside volatility)

        Args:
            df_equity: Equity curve dataframe
            risk_free_rate: Annual risk-free rate (default 0%)

        Returns:
            Sortino ratio
        """
        if df_equity.empty or len(df_equity) < 2:
            return 0.0

        # Calculate weekly returns
        df_equity = df_equity.sort_values("Date")
        returns = df_equity["Portfolio_Value"].pct_change().dropna()

        if len(returns) == 0:
            return 0.0

        # Annualize
        avg_return = returns.mean() * 52

        # Downside deviation (only negative returns)
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return np.inf  # Perfect - no negative returns

        downside_std = negative_returns.std() * np.sqrt(52)

        if downside_std == 0:
            return 0.0

        sortino = (avg_return - risk_free_rate) / downside_std

        return sortino

    @staticmethod
    def calculate_trade_metrics(df_trades: pd.DataFrame) -> Dict:
        """Calculate detailed trade statistics"""
        if df_trades.empty:
            return {}

        # Filter to closed trades only
        closed_trades = df_trades[df_trades["Action"] == "SELL"].copy()

        if closed_trades.empty:
            return {"Total_Trades": 0}

        total_trades = len(closed_trades)

        # Winners and losers
        winners = closed_trades[closed_trades["PnL_%"] > 0]
        losers = closed_trades[closed_trades["PnL_%"] < 0]
        breakeven = closed_trades[closed_trades["PnL_%"] == 0]

        # Win rate
        win_rate = (len(winners) / total_trades) * 100 if total_trades > 0 else 0

        # Average returns
        avg_win_pct = winners["PnL_%"].mean() if len(winners) > 0 else 0
        avg_loss_pct = losers["PnL_%"].mean() if len(losers) > 0 else 0
        avg_trade_pct = closed_trades["PnL_%"].mean()

        # Best/worst
        best_trade_pct = closed_trades["PnL_%"].max()
        worst_trade_pct = closed_trades["PnL_%"].min()
        best_ticker = closed_trades.loc[closed_trades["PnL_%"].idxmax(), "Ticker"]
        worst_ticker = closed_trades.loc[closed_trades["PnL_%"].idxmin(), "Ticker"]

        # Profit factor
        total_wins = winners["PnL_$"].sum() if len(winners) > 0 else 0
        total_losses = abs(losers["PnL_$"].sum()) if len(losers) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else np.inf

        # Expectancy (average $ per trade)
        expectancy = closed_trades["PnL_$"].mean()

        # Hold time
        avg_hold_days = closed_trades["Hold_Days"].mean()
        max_hold_days = closed_trades["Hold_Days"].max()
        min_hold_days = closed_trades["Hold_Days"].min()

        # Consecutive wins/losses
        win_loss = (closed_trades["PnL_%"] > 0).astype(int)
        consecutive = win_loss.groupby((win_loss != win_loss.shift()).cumsum()).cumsum()
        max_consecutive_wins = (
            consecutive[win_loss == 1].max() if any(win_loss == 1) else 0
        )

        lose_streak = (closed_trades["PnL_%"] < 0).astype(int)
        consecutive_losses = lose_streak.groupby(
            (lose_streak != lose_streak.shift()).cumsum()
        ).cumsum()
        max_consecutive_losses = (
            consecutive_losses[lose_streak == 1].max() if any(lose_streak == 1) else 0
        )

        return {
            "Total_Trades": total_trades,
            "Winners": len(winners),
            "Losers": len(losers),
            "Breakeven": len(breakeven),
            "Win_Rate_%": win_rate,
            "Avg_Win_%": avg_win_pct,
            "Avg_Loss_%": avg_loss_pct,
            "Avg_Trade_%": avg_trade_pct,
            "Best_Trade_%": best_trade_pct,
            "Best_Ticker": best_ticker,
            "Worst_Trade_%": worst_trade_pct,
            "Worst_Ticker": worst_ticker,
            "Profit_Factor": profit_factor,
            "Expectancy_$": expectancy,
            "Avg_Hold_Days": avg_hold_days,
            "Max_Hold_Days": max_hold_days,
            "Min_Hold_Days": min_hold_days,
            "Max_Consecutive_Wins": max_consecutive_wins,
            "Max_Consecutive_Losses": max_consecutive_losses,
        }

    @staticmethod
    def calculate_monthly_returns(df_equity: pd.DataFrame) -> pd.DataFrame:
        """Calculate monthly returns"""
        if df_equity.empty:
            return pd.DataFrame()

        df = df_equity.copy()
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        # Get month-end values
        monthly = df.groupby(["Year", "Month"]).last().reset_index()
        monthly["Monthly_Return_%"] = monthly["Portfolio_Value"].pct_change() * 100

        return monthly[["Year", "Month", "Portfolio_Value", "Monthly_Return_%"]]

    @staticmethod
    def calculate_all_metrics(df_equity: pd.DataFrame, df_trades: pd.DataFrame) -> Dict:
        """Calculate all performance metrics"""
        metrics = {}

        # Returns
        metrics["Returns"] = PerformanceMetrics.calculate_returns(df_equity)

        # Drawdown
        metrics["Drawdown"] = PerformanceMetrics.calculate_drawdown(df_equity)

        # Risk-adjusted
        metrics["Sharpe_Ratio"] = PerformanceMetrics.calculate_sharpe_ratio(df_equity)
        metrics["Sortino_Ratio"] = PerformanceMetrics.calculate_sortino_ratio(df_equity)

        # Trade metrics
        metrics["Trade_Stats"] = PerformanceMetrics.calculate_trade_metrics(df_trades)

        return metrics

    @staticmethod
    def print_comprehensive_report(df_equity: pd.DataFrame, df_trades: pd.DataFrame):
        """Print comprehensive performance report"""
        metrics = PerformanceMetrics.calculate_all_metrics(df_equity, df_trades)

        print(f"\n{'='*80}")
        print("COMPREHENSIVE PERFORMANCE REPORT")
        print(f"{'='*80}")

        # Returns
        print(f"\n📈 RETURNS:")
        returns = metrics["Returns"]
        print(f"   Total Return:    {returns.get('Total_Return_%', 0):>10.2f}%")
        print(f"   CAGR:            {returns.get('CAGR_%', 0):>10.2f}%")
        print(f"   Period:          {returns.get('Period_Years', 0):>10.2f} years")

        # Drawdown
        print(f"\n📉 DRAWDOWN:")
        dd = metrics["Drawdown"]
        print(f"   Max Drawdown:    {dd.get('Max_Drawdown_%', 0):>10.2f}%")
        print(f"   Avg Drawdown:    {dd.get('Avg_Drawdown_%', 0):>10.2f}%")

        # Risk-adjusted
        print(f"\n⚖️  RISK-ADJUSTED:")
        print(f"   Sharpe Ratio:    {metrics.get('Sharpe_Ratio', 0):>10.2f}")
        print(f"   Sortino Ratio:   {metrics.get('Sortino_Ratio', 0):>10.2f}")

        # Trading
        print(f"\n📊 TRADING:")
        trade_stats = metrics["Trade_Stats"]
        print(f"   Total Trades:    {trade_stats.get('Total_Trades', 0):>10.0f}")
        print(f"   Win Rate:        {trade_stats.get('Win_Rate_%', 0):>10.2f}%")
        print(f"   Profit Factor:   {trade_stats.get('Profit_Factor', 0):>10.2f}")
        print(f"   Expectancy:      ${trade_stats.get('Expectancy_$', 0):>9.2f}")
        print(f"   Avg Hold:        {trade_stats.get('Avg_Hold_Days', 0):>10.1f} days")

        print(f"\n{'='*80}")


if __name__ == "__main__":
    # Test with sample data
    print("=" * 80)
    print("Testing Performance Metrics")
    print("=" * 80)

    # Create sample equity curve
    dates = pd.date_range("2024-01-01", "2024-12-31", freq="W-MON")
    values = [
        110000 * (1 + 0.01 * i + np.random.normal(0, 0.02)) for i in range(len(dates))
    ]

    df_equity = pd.DataFrame({"Date": dates, "Portfolio_Value": values})

    # Create sample trades
    df_trades = pd.DataFrame(
        {
            "Date": dates[:10],
            "Ticker": [
                "NVDA",
                "MSFT",
                "AAPL",
                "GOOGL",
                "TSLA",
                "AMD",
                "META",
                "NFLX",
                "COST",
                "MU",
            ],
            "Action": ["SELL"] * 10,
            "PnL_%": [15, -8, 25, -5, 30, 10, -12, 18, -6, 22],
            "PnL_$": [1000, -600, 2000, -400, 2500, 800, -900, 1400, -500, 1800],
            "Hold_Days": [14, 7, 21, 10, 28, 14, 12, 16, 8, 19],
        }
    )

    # Calculate metrics
    PerformanceMetrics.print_comprehensive_report(df_equity, df_trades)

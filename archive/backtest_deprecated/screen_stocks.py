"""
Stock Screening Module for GHB Strategy
Backtests individual stocks to identify optimal universe based on volatility criteria
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

from data_loader import DataLoader
from strategy_signals import GHBStrategy
from portfolio_manager import PortfolioManager


class StockScreener:
    """Screen stocks individually to find best performers for GHB strategy"""

    def __init__(self, config_path: str = "backtest/config.json"):
        """Initialize stock screener"""
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.data_loader = DataLoader(config_path)
        self.strategy = GHBStrategy()

        print("✅ Stock Screener initialized")

    def backtest_single_stock(
        self, ticker: str, df: pd.DataFrame, fridays: List[pd.Timestamp]
    ) -> Dict:
        """
        Backtest GHB strategy on a single stock

        Returns metrics including:
        - Total return, CAGR
        - Win rate, avg win, avg loss, max win
        - Standard deviation
        - Trade count
        """
        # Initialize single-stock portfolio
        portfolio = PortfolioManager(
            starting_cash=10000,  # Use fixed starting capital for comparison
            position_size_pct=100,  # All-in for single stock test
            max_positions=1,
        )

        buy_slippage = self.config["execution_settings"]["buy_slippage"]
        sell_slippage = self.config["execution_settings"]["sell_slippage"]

        trades_executed = 0
        current_position = None

        for friday in fridays:
            monday = friday + pd.Timedelta(days=3)

            # Calculate signals for this Friday
            signals = self.strategy.calculate_signals_for_date(df, friday, ticker)

            if not signals:
                continue

            state = signals["State"]
            close_price = signals["Close"]

            # Check if we have a position
            if portfolio.has_position(ticker):
                # Update position price
                position = portfolio.positions[ticker]
                position.update_price(close_price, state)

                # Check for exit signal (N2)
                if state == "N2":
                    portfolio.close_position(
                        ticker, monday, close_price, state, sell_slippage
                    )
                    current_position = None
                    trades_executed += 1
            else:
                # Check for entry signal (P1)
                if state == "P1":
                    success = portfolio.open_position(
                        ticker, monday, close_price, state, buy_slippage
                    )
                    if success:
                        current_position = ticker

        # Calculate metrics
        df_trades = portfolio.get_trades_dataframe()
        closed_trades = (
            df_trades[df_trades["Action"] == "SELL"]
            if not df_trades.empty
            else pd.DataFrame()
        )

        if closed_trades.empty:
            return {
                "Ticker": ticker,
                "Total_Trades": 0,
                "CAGR_%": 0,
                "Total_Return_%": 0,
                "Win_Rate_%": 0,
                "Avg_Win_%": 0,
                "Avg_Loss_%": 0,
                "Max_Win_%": 0,
                "Std_Dev_%": 0,
                "Qualified": False,
                "Reason": "No trades",
            }

        # Calculate returns
        total_return_pct = portfolio.total_return_pct
        years = len(fridays) / 52
        cagr = (
            (((1 + total_return_pct / 100) ** (1 / years)) - 1) * 100
            if years > 0
            else 0
        )

        # Trading stats
        winners = closed_trades[closed_trades["PnL_%"] > 0]
        losers = closed_trades[closed_trades["PnL_%"] < 0]

        win_rate = (len(winners) / len(closed_trades)) * 100
        avg_win = winners["PnL_%"].mean() if len(winners) > 0 else 0
        avg_loss = losers["PnL_%"].mean() if len(losers) > 0 else 0
        max_win = closed_trades["PnL_%"].max()

        # Standard deviation of returns
        std_dev = closed_trades["PnL_%"].std()

        # Check qualification criteria (from GHB_STRATEGY_GUIDE.md)
        qualifies = (
            std_dev >= 30  # Std Dev ≥ 30%
            or max_win >= 150  # Max Win ≥ 150%
            or avg_win >= 40  # Avg Win ≥ 40%
        )

        # Determine qualification reason
        reasons = []
        if std_dev >= 30:
            reasons.append(f"Std Dev {std_dev:.1f}% ≥30%")
        if max_win >= 150:
            reasons.append(f"Max Win {max_win:.1f}% ≥150%")
        if avg_win >= 40:
            reasons.append(f"Avg Win {avg_win:.1f}% ≥40%")

        qualification_reason = (
            ", ".join(reasons) if reasons else "Does not meet criteria"
        )

        return {
            "Ticker": ticker,
            "Total_Trades": len(closed_trades),
            "CAGR_%": cagr,
            "Total_Return_%": total_return_pct,
            "Win_Rate_%": win_rate,
            "Avg_Win_%": avg_win,
            "Avg_Loss_%": avg_loss,
            "Max_Win_%": max_win,
            "Std_Dev_%": std_dev,
            "Qualified": qualifies,
            "Qualification_Reason": qualification_reason,
        }

    def screen_universe(
        self, universe: str = "sp100", force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Screen entire universe and return ranked results

        Args:
            universe: 'sp100' or 'sp500'
            force_refresh: Force re-download of data

        Returns:
            DataFrame with all stocks ranked by CAGR
        """
        print(f"\n{'='*80}")
        print(f"SCREENING {universe.upper()} UNIVERSE FOR GHB STRATEGY")
        print(f"{'='*80}")

        # Load data - temporarily override config universe
        print("\n📥 Loading historical data...")
        original_universe = self.data_loader.backtest_settings["universe"]
        self.data_loader.backtest_settings["universe"] = universe
        tickers = self.data_loader.get_universe()
        data_dict = self.data_loader.download_historical_data(tickers, force_refresh)
        self.data_loader.backtest_settings["universe"] = original_universe

        # Generate Friday schedule
        print("\n📅 Generating Friday schedule...")
        start_date = pd.to_datetime(self.config["backtest_settings"]["start_date"])
        end_date = pd.to_datetime(self.config["backtest_settings"]["end_date"])
        all_dates = pd.date_range(start=start_date, end=end_date, freq="D", tz=None)
        fridays = [d for d in all_dates if d.weekday() == 4]

        # Filter to valid Fridays (where we have enough data)
        valid_fridays = []
        for friday in fridays:
            stocks_with_data = sum(
                1 for df in data_dict.values() if len(df[df["Date"] <= friday]) >= 200
            )
            if stocks_with_data / len(data_dict) >= 0.8:
                valid_fridays.append(friday)

        print(f"   Found {len(valid_fridays)} valid trading Fridays")

        # Backtest each stock individually
        print(f"\n🔄 Backtesting {len(data_dict)} stocks individually...")
        print("   This will take 10-15 minutes...\n")

        results = []
        for i, (ticker, df) in enumerate(data_dict.items(), 1):
            print(f"  [{i:3d}/{len(data_dict)}] Testing {ticker:6s}...", end="\r")

            try:
                metrics = self.backtest_single_stock(ticker, df, valid_fridays)
                results.append(metrics)
            except Exception as e:
                print(f"\n❌ Error testing {ticker}: {str(e)}")
                continue

        print(f"\n✅ Screening complete!")

        # Create results dataframe
        df_results = pd.DataFrame(results)

        # Sort by CAGR (best performers first)
        df_results = df_results.sort_values("CAGR_%", ascending=False)

        return df_results

    def generate_report(
        self, df_results: pd.DataFrame, output_dir: str = "backtest/results"
    ):
        """Generate screening report with qualified stocks"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\n{'='*80}")
        print("SCREENING REPORT")
        print(f"{'='*80}")

        # Overall stats
        total_stocks = len(df_results)
        qualified_stocks = len(df_results[df_results["Qualified"] == True])

        print(f"\n📊 UNIVERSE ANALYSIS:")
        print(f"   Total Stocks Tested: {total_stocks}")
        print(
            f"   Qualified Stocks: {qualified_stocks} ({qualified_stocks/total_stocks*100:.1f}%)"
        )
        print(
            f"   Non-Qualified: {total_stocks - qualified_stocks} ({(total_stocks-qualified_stocks)/total_stocks*100:.1f}%)"
        )

        # Qualified stocks summary
        df_qualified = df_results[df_results["Qualified"] == True]

        if len(df_qualified) > 0:
            print(f"\n🏆 TOP 25 QUALIFIED STOCKS (By CAGR):")
            print(
                f"\n{'Rank':<6} {'Ticker':<8} {'CAGR':<10} {'Win Rate':<10} {'Avg Win':<10} {'Max Win':<10} {'Qualification':<40}"
            )
            print("-" * 100)

            for i, (_, row) in enumerate(df_qualified.head(25).iterrows(), 1):
                print(
                    f"{i:<6} {row['Ticker']:<8} {row['CAGR_%']:>8.2f}% {row['Win_Rate_%']:>8.2f}% "
                    f"{row['Avg_Win_%']:>8.2f}% {row['Max_Win_%']:>8.2f}% {row['Qualification_Reason']:<40}"
                )

            # Save full results
            csv_file = output_path / f"stock_screening_{timestamp}.csv"
            df_results.to_csv(csv_file, index=False)
            print(f"\n✅ Full results saved: {csv_file}")

            # Save qualified stocks list
            qualified_tickers = df_qualified.head(30)["Ticker"].tolist()
            qualified_file = output_path / f"qualified_stocks_{timestamp}.json"

            report = {
                "screening_date": timestamp,
                "total_stocks_tested": total_stocks,
                "qualified_stocks": qualified_stocks,
                "qualification_criteria": {
                    "std_dev_pct": 30,
                    "max_win_pct": 150,
                    "avg_win_pct": 40,
                },
                "top_30_tickers": qualified_tickers,
                "recommended_universe": qualified_tickers[:25],
            }

            with open(qualified_file, "w") as f:
                json.dump(report, f, indent=2)

            print(f"✅ Qualified stocks saved: {qualified_file}")

            # Print recommended universe for config
            print(f"\n💡 RECOMMENDED UNIVERSE (Top 25):")
            print(f"   {', '.join(qualified_tickers[:25])}")

        else:
            print("\n⚠️  No stocks met qualification criteria!")

        print(f"\n{'='*80}")

        return df_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Screen stocks for GHB Strategy")
    parser.add_argument(
        "--universe",
        choices=["sp100", "sp500", "nasdaq25", "nasdaq39"],
        default="sp100",
        help="Universe to screen (default: sp100)",
    )
    parser.add_argument(
        "--refresh-data", action="store_true", help="Force refresh historical data"
    )
    parser.add_argument(
        "--config", default="backtest/config.json", help="Path to config file"
    )

    args = parser.parse_args()

    # Run screening
    screener = StockScreener(config_path=args.config)
    df_results = screener.screen_universe(
        universe=args.universe, force_refresh=args.refresh_data
    )
    screener.generate_report(df_results)

    print("\n✅ Stock screening complete!")
    print("\n💡 Next steps:")
    print("   1. Review qualified stocks in CSV file")
    print("   2. Update config.json with recommended universe")
    print("   3. Run portfolio backtest with optimized universe")

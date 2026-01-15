"""
Backtest Engine for GHB Strategy
Simulates week-by-week trading from historical data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List
import warnings

warnings.filterwarnings("ignore")

from data_loader import DataLoader
from strategy_signals import GHBStrategy
from portfolio_manager import PortfolioManager


class BacktestEngine:
    """Main backtest simulation engine"""

    def __init__(self, config_path: str = "backtest/config.json"):
        """Initialize backtest engine"""
        # Load configuration
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.backtest_settings = self.config["backtest_settings"]
        self.portfolio_settings = self.config["portfolio_settings"]
        self.execution_settings = self.config["execution_settings"]
        self.strategy_settings = self.config["strategy_settings"]
        self.output_settings = self.config["output_settings"]

        # Initialize components
        self.data_loader = DataLoader(config_path)
        self.strategy = GHBStrategy()
        self.portfolio = PortfolioManager(
            starting_cash=self.portfolio_settings["starting_cash"],
            position_size_pct=self.portfolio_settings["position_size_pct"],
            max_positions=self.portfolio_settings["max_positions"],
        )

        # State
        self.data_dict = {}
        self.fridays = []

        print(f"\n✅ Backtest Engine initialized")
        print(
            f"   Period: {self.backtest_settings['start_date']} to {self.backtest_settings['end_date']}"
        )
        print(f"   Strategy: {self.strategy.name}")

    def load_data(self, force_refresh: bool = False):
        """Load historical data for all tickers"""
        print(f"\n{'='*80}")
        print("STEP 1: Loading Historical Data")
        print(f"{'='*80}")

        tickers = self.data_loader.get_universe()
        self.data_dict = self.data_loader.download_historical_data(
            tickers, force_refresh
        )

        print(f"\n✅ Data loaded for {len(self.data_dict)} stocks")

    def generate_fridays(self):
        """Generate list of all Fridays in backtest period"""
        print(f"\n{'='*80}")
        print("STEP 2: Generating Friday Schedule")
        print(f"{'='*80}")

        start_date = pd.to_datetime(self.backtest_settings["start_date"])
        end_date = pd.to_datetime(self.backtest_settings["end_date"])

        # Generate all dates in range (tz-naive to match data)
        all_dates = pd.date_range(start=start_date, end=end_date, freq="D", tz=None)

        # Filter to Fridays (weekday 4)
        fridays = [d for d in all_dates if d.weekday() == 4]

        # Filter to dates where we have data for most stocks
        valid_fridays = []
        for friday in fridays:
            # Check if we have data for at least 80% of stocks on this date
            stocks_with_data = 0
            for ticker, df in self.data_dict.items():
                if not df[df["Date"] <= friday].empty:
                    if len(df[df["Date"] <= friday]) >= 200:  # Need 200 days of history
                        stocks_with_data += 1

            coverage = stocks_with_data / len(self.data_dict)
            if coverage >= 0.8:
                valid_fridays.append(friday)

        self.fridays = valid_fridays

        print(f"\n✅ Found {len(self.fridays)} trading Fridays")
        print(f"   First: {self.fridays[0].date()}")
        print(f"   Last: {self.fridays[-1].date()}")
        print(f"   Expected trades per year: ~14")
        print(f"   Total period: {len(self.fridays) / 52:.1f} years")

    def run_backtest(self):
        """Run the main backtest simulation"""
        print(f"\n{'='*80}")
        print("STEP 3: Running Backtest Simulation")
        print(f"{'='*80}")

        buy_slippage = self.execution_settings["buy_slippage"]
        sell_slippage = self.execution_settings["sell_slippage"]

        total_weeks = len(self.fridays)

        for week_num, friday in enumerate(self.fridays, 1):
            # Monday execution date (3 days after Friday)
            monday = friday + timedelta(days=3)

            # Progress indicator
            if week_num % 10 == 0 or week_num == 1:
                progress_pct = (week_num / total_weeks) * 100
                print(
                    f"  Week {week_num:3d}/{total_weeks} ({progress_pct:5.1f}%) - {friday.date()} | "
                    + f"Portfolio: ${self.portfolio.portfolio_value:>10,.0f} | "
                    + f"Positions: {self.portfolio.position_count}/{self.portfolio.max_positions}"
                )

            # Calculate signals for this Friday
            df_signals = self.strategy.scan_universe(self.data_dict, friday)

            if df_signals.empty:
                continue

            # Update existing positions with current prices/states
            self.portfolio.update_positions(df_signals)

            # STEP 1: Process SELL signals (exit N2 positions)
            sell_signals = self.strategy.get_sell_signals(df_signals)

            for _, signal in sell_signals.iterrows():
                ticker = signal["Ticker"]
                if self.portfolio.has_position(ticker):
                    # Exit position on Monday at Friday close with slippage
                    self.portfolio.close_position(
                        ticker=ticker,
                        exit_date=monday,
                        exit_price=signal["Close"],
                        exit_state=signal["State"],
                        slippage=sell_slippage,
                    )

            # STEP 2: Process BUY signals (enter new P1 positions)
            buy_candidates = self.strategy.get_buy_candidates(
                df_signals, max_candidates=20
            )

            for _, signal in buy_candidates.iterrows():
                ticker = signal["Ticker"]

                # Skip if already have position
                if self.portfolio.has_position(ticker):
                    continue

                # Skip if portfolio full
                if not self.portfolio.can_open_position():
                    break

                # Enter position on Monday at Friday close with slippage
                self.portfolio.open_position(
                    ticker=ticker,
                    entry_date=monday,
                    entry_price=signal["Close"],
                    entry_state=signal["State"],
                    slippage=buy_slippage,
                )

            # Record equity for this week
            self.portfolio.record_equity(monday)

        print(f"\n✅ Backtest complete!")
        print(f"   Total weeks simulated: {total_weeks}")
        print(f"   Final portfolio value: ${self.portfolio.portfolio_value:,.2f}")
        print(f"   Total return: {self.portfolio.total_return_pct:.2f}%")

    def save_results(self):
        """Save backtest results to files"""
        print(f"\n{'='*80}")
        print("STEP 4: Saving Results")
        print(f"{'='*80}")

        # Create results directory
        results_path = Path(self.output_settings["results_path"])
        results_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save trades
        if self.output_settings["save_trades"]:
            df_trades = self.portfolio.get_trades_dataframe()
            if not df_trades.empty:
                trades_file = results_path / f"trades_{timestamp}.csv"
                df_trades.to_csv(trades_file, index=False)
                print(f"✅ Trades saved: {trades_file}")

        # Save equity curve
        if self.output_settings["save_equity_curve"]:
            df_equity = self.portfolio.get_equity_curve_dataframe()
            if not df_equity.empty:
                equity_file = results_path / f"equity_curve_{timestamp}.csv"
                df_equity.to_csv(equity_file, index=False)
                print(f"✅ Equity curve saved: {equity_file}")

        # Save summary
        if self.output_settings["save_summary"]:
            summary = self.get_summary()
            summary_file = results_path / f"summary_{timestamp}.json"
            with open(summary_file, "w") as f:
                json.dump(summary, f, indent=2, default=str)
            print(f"✅ Summary saved: {summary_file}")

        print(f"\n📁 All results saved to: {results_path}")

        return {
            "trades_file": trades_file if self.output_settings["save_trades"] else None,
            "equity_file": (
                equity_file if self.output_settings["save_equity_curve"] else None
            ),
            "summary_file": (
                summary_file if self.output_settings["save_summary"] else None
            ),
        }

    def get_summary(self) -> Dict:
        """Generate summary statistics"""
        portfolio_stats = self.portfolio.get_summary_stats()

        # Calculate additional metrics
        df_equity = self.portfolio.get_equity_curve_dataframe()

        if not df_equity.empty:
            # Calculate max drawdown
            running_max = df_equity["Portfolio_Value"].expanding().max()
            drawdown = (df_equity["Portfolio_Value"] - running_max) / running_max * 100
            max_drawdown = drawdown.min()

            # Calculate annual return
            years = len(self.fridays) / 52
            total_return = portfolio_stats["Total_Return_%"] / 100
            cagr = (((1 + total_return) ** (1 / years)) - 1) * 100 if years > 0 else 0
        else:
            max_drawdown = 0
            cagr = 0

        summary = {
            "Backtest_Period": {
                "Start_Date": self.backtest_settings["start_date"],
                "End_Date": self.backtest_settings["end_date"],
                "Total_Weeks": len(self.fridays),
                "Years": len(self.fridays) / 52,
            },
            "Portfolio_Settings": self.portfolio_settings,
            "Performance": {
                "Starting_Value": self.portfolio_settings["starting_cash"],
                "Final_Value": portfolio_stats["Final_Value"],
                "Total_Return_%": portfolio_stats["Total_Return_%"],
                "CAGR_%": cagr,
                "Max_Drawdown_%": max_drawdown,
            },
            "Trading_Stats": {
                "Total_Trades": portfolio_stats["Total_Trades"],
                "Win_Rate_%": portfolio_stats["Win_Rate_%"],
                "Avg_Win_%": portfolio_stats["Avg_Win_%"],
                "Avg_Loss_%": portfolio_stats["Avg_Loss_%"],
                "Avg_Trade_%": portfolio_stats["Avg_Trade_%"],
                "Best_Trade_%": portfolio_stats["Best_Trade_%"],
                "Best_Trade_Ticker": portfolio_stats["Best_Trade_Ticker"],
                "Worst_Trade_%": portfolio_stats["Worst_Trade_%"],
                "Worst_Trade_Ticker": portfolio_stats["Worst_Trade_Ticker"],
            },
            "Strategy": {
                "Name": self.strategy.name,
                "Entry_States": self.strategy_settings["entry_states"],
                "Exit_States": self.strategy_settings["exit_states"],
                "Buy_Slippage": self.execution_settings["buy_slippage"],
                "Sell_Slippage": self.execution_settings["sell_slippage"],
            },
        }

        return summary

    def print_summary(self):
        """Print summary to console"""
        summary = self.get_summary()

        print(f"\n{'='*80}")
        print("BACKTEST RESULTS SUMMARY")
        print(f"{'='*80}")

        print(f"\n📅 PERIOD:")
        print(
            f"   {summary['Backtest_Period']['Start_Date']} to {summary['Backtest_Period']['End_Date']}"
        )
        print(
            f"   {summary['Backtest_Period']['Total_Weeks']} weeks ({summary['Backtest_Period']['Years']:.1f} years)"
        )

        print(f"\n💰 PERFORMANCE:")
        print(
            f"   Starting Value:  ${summary['Performance']['Starting_Value']:>12,.0f}"
        )
        print(f"   Final Value:     ${summary['Performance']['Final_Value']:>12,.0f}")
        print(f"   Total Return:    {summary['Performance']['Total_Return_%']:>12.2f}%")
        print(f"   CAGR:            {summary['Performance']['CAGR_%']:>12.2f}%")
        print(f"   Max Drawdown:    {summary['Performance']['Max_Drawdown_%']:>12.2f}%")

        print(f"\n📊 TRADING STATS:")
        print(f"   Total Trades:    {summary['Trading_Stats']['Total_Trades']:>12.0f}")
        print(f"   Win Rate:        {summary['Trading_Stats']['Win_Rate_%']:>12.2f}%")
        print(f"   Avg Win:         {summary['Trading_Stats']['Avg_Win_%']:>12.2f}%")
        print(f"   Avg Loss:        {summary['Trading_Stats']['Avg_Loss_%']:>12.2f}%")
        print(f"   Avg Trade:       {summary['Trading_Stats']['Avg_Trade_%']:>12.2f}%")

        print(f"\n🏆 BEST/WORST:")
        print(
            f"   Best Trade:      {summary['Trading_Stats']['Best_Trade_%']:>12.2f}% ({summary['Trading_Stats']['Best_Trade_Ticker']})"
        )
        print(
            f"   Worst Trade:     {summary['Trading_Stats']['Worst_Trade_%']:>12.2f}% ({summary['Trading_Stats']['Worst_Trade_Ticker']})"
        )

        print(f"\n{'='*80}")

    def run(self, force_refresh_data: bool = False):
        """Run complete backtest from start to finish"""
        print(f"\n{'#'*80}")
        print(f"# GHB STRATEGY BACKTEST")
        print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}")

        # Load data
        self.load_data(force_refresh=force_refresh_data)

        # Generate Friday schedule
        self.generate_fridays()

        # Run simulation
        self.run_backtest()

        # Print results
        self.print_summary()

        # Save results
        files = self.save_results()

        print(f"\n{'#'*80}")
        print(f"# BACKTEST COMPLETE")
        print(f"{'#'*80}\n")

        return files


if __name__ == "__main__":
    # Run backtest
    engine = BacktestEngine()
    engine.run()

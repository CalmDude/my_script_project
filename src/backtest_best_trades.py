"""
Watchlist Backtest Engine

Analyzes historical watchlist recommendations to:
1. Measure win rate and average returns
2. Identify which quality ratings/flags have the strongest edge
3. Test Vol R:R prediction accuracy
4. Optimize entry/exit strategies

Usage:
    python backtest_best_trades.py --period 30 --category sp500
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings("ignore")


class WatchlistBacktest:
    """
    Backtest historical Watchlist recommendations
    """

    def __init__(self, results_dir: Path = None):
        """
        Initialize backtester

        Args:
            results_dir: Path to scanner_results directory
        """
        if results_dir is None:
            results_dir = Path("scanner_results")

        self.results_dir = results_dir
        self.backtest_results = []

    def find_watchlist_files(self, category: str = None) -> List[Path]:
        """
        Find all watchlist Excel files

        Args:
            category: Filter by category (sp500, nasdaq100, portfolio) or None for all

        Returns:
            List of Excel file paths
        """
        files = []

        # Search in main results_dir and archive
        search_paths = [self.results_dir, self.results_dir / "archive"]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # Search in category subfolders
            if category:
                category_dir = search_path / category
                if category_dir.exists():
                    files.extend(category_dir.glob("*_watchlist_*.xlsx"))
            else:
                # Search all subfolders
                for subfolder in ["sp500", "nasdaq100", "portfolio"]:
                    subfolder_path = search_path / subfolder
                    if subfolder_path.exists():
                        files.extend(subfolder_path.glob("*_watchlist_*.xlsx"))

        # Sort by date (newest first)
        files.sort(reverse=True)
        return files

    def extract_date_from_filename(self, file_path: Path) -> datetime:
        """
        Extract date from filename (e.g., sp500_watchlist_20260111_1525.xlsx)

        Args:
            file_path: Path to file

        Returns:
            datetime object
        """
        try:
            # Extract timestamp from filename
            filename = file_path.stem
            parts = filename.split("_")

            # Find date part (YYYYMMDD format)
            for part in parts:
                if len(part) == 8 and part.isdigit():
                    date_str = part
                    return datetime.strptime(date_str, "%Y%m%d")
        except:
            # Fallback to file modification time
            return datetime.fromtimestamp(file_path.stat().st_mtime)

        return datetime.now()

    def parse_watchlist_excel(self, file_path: Path) -> pd.DataFrame:
        """
        Parse watchlist Excel file

        Args:
            file_path: Path to Excel file

        Returns:
            DataFrame with recommendations
        """
        try:
            # Read Top Buy Setups sheet
            df = pd.read_excel(file_path, sheet_name="Top Buy Setups", skiprows=3)

            # Extract report date from filename
            report_date = self.extract_date_from_filename(file_path)
            df["report_date"] = report_date
            df["report_file"] = file_path.name

            return df
        except Exception as e:
            print(f"Error parsing {file_path.name}: {e}")
            return pd.DataFrame()

    def fetch_price_history(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical price data for backtesting

        Args:
            ticker: Stock symbol
            start_date: Start date for price data
            end_date: End date for price data

        Returns:
            DataFrame with OHLCV data
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()

    def calculate_performance(
        self,
        entry_price: float,
        price_history: pd.DataFrame,
        vol_stop_pct: float = 5.0,
        target_r1: float = None,
    ) -> Dict:
        """
        Calculate trade performance metrics

        Args:
            entry_price: Entry price from recommendation
            price_history: Historical price data after entry
            vol_stop_pct: Volatility stop loss percentage
            target_r1: Target R1 price

        Returns:
            Dictionary with performance metrics
        """
        if price_history.empty or entry_price <= 0:
            return {}

        stop_price = entry_price * (1 - vol_stop_pct / 100)

        # Calculate returns at various intervals
        results = {
            "entry_price": entry_price,
            "vol_stop_price": stop_price,
            "target_r1": target_r1,
        }

        # Check each period
        for days in [7, 14, 30, 60, 90]:
            if len(price_history) >= days:
                period_data = price_history.iloc[:days]

                # Check if stop was hit and when
                stop_hit_mask = period_data["Low"] <= stop_price
                stop_hit = stop_hit_mask.any()
                stop_hit_day = stop_hit_mask.idxmax() if stop_hit else None

                # Check if R1 target was hit and when
                r1_hit = False
                r1_hit_day = None
                if target_r1 and target_r1 > 0:
                    r1_hit_mask = period_data["High"] >= target_r1
                    r1_hit = r1_hit_mask.any()
                    r1_hit_day = r1_hit_mask.idxmax() if r1_hit else None

                # Determine exit: stop first, then R1 target, then hold to end
                exit_price = period_data.iloc[-1]["Close"]  # Default: hold to end
                exit_reason = "hold"

                if stop_hit and r1_hit:
                    # Both hit - exit at whichever came first
                    if stop_hit_day < r1_hit_day:
                        exit_price = stop_price
                        exit_reason = "stop"
                    else:
                        exit_price = target_r1
                        exit_reason = "target"
                elif stop_hit:
                    # Only stop hit
                    exit_price = stop_price
                    exit_reason = "stop"
                elif r1_hit:
                    # Only R1 target hit - EXIT HERE (this is the key fix!)
                    exit_price = target_r1
                    exit_reason = "target"

                # Calculate return based on actual exit
                return_pct = (exit_price - entry_price) / entry_price * 100

                # Max favorable excursion (highest gain reached)
                max_price = period_data["High"].max()
                mfe = (max_price - entry_price) / entry_price * 100

                # Max adverse excursion (worst drawdown)
                min_price = period_data["Low"].min()
                mae = (min_price - entry_price) / entry_price * 100

                results[f"return_{days}d"] = return_pct
                results[f"mfe_{days}d"] = mfe
                results[f"mae_{days}d"] = mae
                results[f"stop_hit_{days}d"] = stop_hit
                results[f"r1_hit_{days}d"] = r1_hit
                results[f"exit_reason_{days}d"] = exit_reason

        return results

    def backtest_report(
        self, file_path: Path, holding_period: int = 30
    ) -> pd.DataFrame:
        """
        Backtest a single watchlist report

        Args:
            file_path: Path to watchlist Excel file
            holding_period: Days to hold for performance measurement

        Returns:
            DataFrame with backtest results
        """
        print(f"\nBacktesting: {file_path.name}")

        # Parse the report
        df = self.parse_watchlist_excel(file_path)

        if df.empty:
            return pd.DataFrame()

        report_date = df["report_date"].iloc[0]
        results = []

        for idx, row in df.iterrows():
            ticker = row.get("Ticker", "")
            rank = row.get("Rank", 0)
            quality = row.get("Quality", "")
            quality_flag = row.get("Quality Flag", "")
            entry_price = row.get("Current Price", 0)
            vol_rr = row.get("Vol R:R", "")
            vol_stop_loss_pct = (
                row.get("Vol Stop Loss %", "").replace("-", "").replace("%", "")
            )
            target_r1 = row.get("Target R1", 0)

            if not ticker or entry_price <= 0:
                continue

            # Parse vol_rr (format: "1:3.5" -> 3.5)
            try:
                if isinstance(vol_rr, str) and ":" in vol_rr:
                    vol_rr_value = float(vol_rr.split(":")[1])
                else:
                    vol_rr_value = float(vol_rr) if vol_rr else 0
            except:
                vol_rr_value = 0

            # Parse stop loss %
            try:
                stop_pct = float(vol_stop_loss_pct) if vol_stop_loss_pct else 5.0
            except:
                stop_pct = 5.0

            # Fetch price data
            start_date = report_date + timedelta(days=1)
            end_date = report_date + timedelta(days=max(holding_period, 90) + 10)

            # Don't try to fetch future data
            today = datetime.now()
            if end_date > today:
                end_date = today

            price_data = self.fetch_price_history(ticker, start_date, end_date)

            if not price_data.empty:
                perf = self.calculate_performance(
                    entry_price, price_data, stop_pct, target_r1
                )

                # Compile results
                result = {
                    "report_date": report_date,
                    "report_file": file_path.name,
                    "rank": rank,
                    "ticker": ticker,
                    "quality": quality,
                    "quality_flag": quality_flag,
                    "vol_rr": vol_rr_value,
                    **perf,
                }

                results.append(result)
                print(
                    f"  {ticker:6s} Rank #{rank:2d} | {quality:10s} | {holding_period}d return: {perf.get(f'return_{holding_period}d', 0):+6.1f}%"
                )

        return pd.DataFrame(results)

    def run_backtest(
        self, category: str = None, max_reports: int = 10, holding_period: int = 30
    ) -> pd.DataFrame:
        """
        Run backtest across multiple reports

        Args:
            category: Category to backtest (sp500, nasdaq100, portfolio) or None for all
            max_reports: Maximum number of reports to backtest
            holding_period: Primary holding period for analysis

        Returns:
            Combined DataFrame with all backtest results
        """
        print(f"=" * 80)
        print(f"WATCHLIST BACKTEST")
        print(f"=" * 80)
        print(f"Category: {category or 'ALL'}")
        print(f"Holding Period: {holding_period} days")
        print(f"Max Reports: {max_reports}")

        # Find files
        files = self.find_watchlist_files(category)

        if not files:
            print("\n[ERROR] No watchlist files found!")
            return pd.DataFrame()

        print(f"\nFound {len(files)} watchlist reports")

        # Filter out reports that are too recent (need holding_period + buffer days)
        today = datetime.now()
        cutoff_date = today - timedelta(days=holding_period + 5)

        valid_files = []
        for file_path in files[:max_reports]:
            report_date = self.extract_date_from_filename(file_path)
            if report_date <= cutoff_date:
                valid_files.append(file_path)

        if not valid_files:
            print(
                f"\n[WARNING] No reports old enough to backtest with {holding_period}-day holding period"
            )
            print(f"Reports must be from before {cutoff_date.strftime('%Y-%m-%d')}")
            return pd.DataFrame()

        if len(valid_files) < len(files[:max_reports]):
            print(
                f"Filtered to {len(valid_files)} reports (excluded {len(files[:max_reports]) - len(valid_files)} too recent)"
            )

        files = valid_files

        # Backtest each report
        all_results = []
        for file_path in files:
            results_df = self.backtest_report(file_path, holding_period)
            if not results_df.empty:
                all_results.append(results_df)

        if not all_results:
            print("\n[ERROR] No backtest results generated!")
            return pd.DataFrame()

        # Combine all results
        combined = pd.concat(all_results, ignore_index=True)

        print(f"\n[OK] Backtest complete: {len(combined)} trades analyzed")

        return combined

    def generate_edge_analysis(
        self, results_df: pd.DataFrame, holding_period: int = 30
    ) -> Dict:
        """
        Analyze results to identify edge

        Args:
            results_df: Backtest results DataFrame
            holding_period: Primary holding period

        Returns:
            Dictionary with edge analysis
        """
        if results_df.empty:
            return {}

        return_col = f"return_{holding_period}d"

        analysis = {
            "overall": self._analyze_segment(results_df, return_col),
            "by_quality": {},
            "by_quality_flag": {},
            "by_vol_rr_tier": {},
            "by_rank_tier": {},
        }

        # By Quality
        for quality in results_df["quality"].unique():
            segment = results_df[results_df["quality"] == quality]
            analysis["by_quality"][quality] = self._analyze_segment(segment, return_col)

        # By Quality Flag
        for flag in results_df["quality_flag"].unique():
            if pd.notna(flag) and flag:
                segment = results_df[results_df["quality_flag"] == flag]
                analysis["by_quality_flag"][flag] = self._analyze_segment(
                    segment, return_col
                )

        # By Vol R:R tier
        results_df["vol_rr_tier"] = pd.cut(
            results_df["vol_rr"], bins=[0, 2, 3, 100], labels=["<2:1", "2-3:1", "3+:1"]
        )
        for tier in ["<2:1", "2-3:1", "3+:1"]:
            segment = results_df[results_df["vol_rr_tier"] == tier]
            analysis["by_vol_rr_tier"][tier] = self._analyze_segment(
                segment, return_col
            )

        # By Rank tier
        results_df["rank_tier"] = pd.cut(
            results_df["rank"], bins=[0, 5, 10, 100], labels=["Top 5", "6-10", "11+"]
        )
        for tier in ["Top 5", "6-10", "11+"]:
            segment = results_df[results_df["rank_tier"] == tier]
            analysis["by_rank_tier"][tier] = self._analyze_segment(segment, return_col)

        return analysis

    def _analyze_segment(self, df: pd.DataFrame, return_col: str) -> Dict:
        """
        Analyze a segment of trades

        Args:
            df: DataFrame segment
            return_col: Column name for returns

        Returns:
            Dictionary with statistics
        """
        if df.empty or return_col not in df.columns:
            return {}

        returns = df[return_col].dropna()

        if len(returns) == 0:
            return {}

        winners = returns[returns > 0]
        losers = returns[returns < 0]

        return {
            "count": len(returns),
            "win_rate": len(winners) / len(returns) * 100 if len(returns) > 0 else 0,
            "avg_return": returns.mean(),
            "median_return": returns.median(),
            "avg_win": winners.mean() if len(winners) > 0 else 0,
            "avg_loss": losers.mean() if len(losers) > 0 else 0,
            "best_trade": returns.max(),
            "worst_trade": returns.min(),
            "win_loss_ratio": (
                abs(winners.mean() / losers.mean())
                if len(losers) > 0 and len(winners) > 0
                else 0
            ),
        }

    def print_edge_report(self, analysis: Dict):
        """
        Print formatted edge analysis report

        Args:
            analysis: Edge analysis dictionary
        """
        print("\n" + "=" * 80)
        print("EDGE ANALYSIS REPORT")
        print("=" * 80)

        # Overall
        overall = analysis.get("overall", {})
        if overall:
            print(f"\n{'OVERALL PERFORMANCE':^80}")
            print("-" * 80)
            self._print_stats(overall)

        # By Quality
        print(f"\n{'BREAKDOWN BY QUALITY RATING':^80}")
        print("-" * 80)
        for quality, stats in sorted(analysis.get("by_quality", {}).items()):
            if stats:
                print(f"\n{quality}:")
                self._print_stats(stats, indent=2)

        # By Quality Flag
        print(f"\n{'BREAKDOWN BY QUALITY FLAG':^80}")
        print("-" * 80)
        for flag, stats in sorted(analysis.get("by_quality_flag", {}).items()):
            if stats:
                print(f"\n{flag}:")
                self._print_stats(stats, indent=2)

        # By Vol R:R Tier
        print(f"\n{'BREAKDOWN BY VOL R:R TIER':^80}")
        print("-" * 80)
        for tier, stats in analysis.get("by_vol_rr_tier", {}).items():
            if stats:
                print(f"\n{tier}:")
                self._print_stats(stats, indent=2)

        # By Rank Tier
        print(f"\n{'BREAKDOWN BY RANK POSITION':^80}")
        print("-" * 80)
        for tier, stats in analysis.get("by_rank_tier", {}).items():
            if stats:
                print(f"\n{tier}:")
                self._print_stats(stats, indent=2)

        print("\n" + "=" * 80)

    def _print_stats(self, stats: Dict, indent: int = 0):
        """
        Print statistics in formatted way

        Args:
            stats: Statistics dictionary
            indent: Indentation level
        """
        prefix = " " * indent
        print(f"{prefix}Trades: {stats.get('count', 0)}")
        print(f"{prefix}Win Rate: {stats.get('win_rate', 0):.1f}%")
        print(f"{prefix}Avg Return: {stats.get('avg_return', 0):+.2f}%")
        print(f"{prefix}Median Return: {stats.get('median_return', 0):+.2f}%")
        print(f"{prefix}Avg Winner: {stats.get('avg_win', 0):+.2f}%")
        print(f"{prefix}Avg Loser: {stats.get('avg_loss', 0):+.2f}%")
        print(f"{prefix}Win/Loss Ratio: {stats.get('win_loss_ratio', 0):.2f}x")
        print(f"{prefix}Best Trade: {stats.get('best_trade', 0):+.2f}%")
        print(f"{prefix}Worst Trade: {stats.get('worst_trade', 0):+.2f}%")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backtest Watchlist Reports")
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Category: sp500, nasdaq100, or portfolio (default: all)",
    )
    parser.add_argument(
        "--period", type=int, default=30, help="Holding period in days (default: 30)"
    )
    parser.add_argument(
        "--max-reports",
        type=int,
        default=10,
        help="Maximum reports to backtest (default: 10)",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="scanner_results",
        help="Path to scanner results directory",
    )

    args = parser.parse_args()

    # Run backtest
    backtester = WatchlistBacktest(Path(args.results_dir))
    results = backtester.run_backtest(
        category=args.category, max_reports=args.max_reports, holding_period=args.period
    )

    if not results.empty:
        # Analyze edge
        analysis = backtester.generate_edge_analysis(results, args.period)
        backtester.print_edge_report(analysis)

        # Save results to backtest_results/ directory
        backtest_dir = Path("backtest_results")
        backtest_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = backtest_dir / f"backtest_results_{timestamp}.csv"
        results.to_csv(output_file, index=False)
        print(f"\n[OK] Detailed results saved to: {output_file}")

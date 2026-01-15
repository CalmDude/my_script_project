"""
Backtest Strategy 1 on Historical Data (2021-2025)

Strategy 1 Filters:
- Quality: EXCELLENT
- Rank: 6-15
- Entry Flag: SAFE ENTRY
- Vol R:R: >= 2.0

This script analyzes 5 years of historical watchlist data to validate:
- Win rate (target: 80%)
- Average return (target: +8%)
- Trade frequency (target: ~1.7 trades/month)
- Drawdowns and consecutive losses
"""

import pandas as pd
from pathlib import Path
import sys

# Add src to path (script is in scripts/analysis/)
ROOT = Path(__file__).parent.parent.parent
src_path = ROOT / "src"
sys.path.insert(0, str(src_path))

from backtest_watchlist import WatchlistBacktest

# Configuration
CATEGORY = "nasdaq100"
HOLDING_PERIOD = 30  # Days
MAX_REPORTS = 260  # ~5 years of weekly reports (52 weeks/year × 5)

# Strategy 1 Filters
STRATEGY_1_FILTERS = {
    "quality": "EXCELLENT",
    "rank_min": 6,
    "rank_max": 15,
    "quality_flag": "SAFE ENTRY",
    "vol_rr_min": 2.0,
}


def apply_strategy1_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply Strategy 1 filters to backtest results

    Args:
        df: Backtest results DataFrame

    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()

    # Filter by quality
    if "quality" in filtered.columns:
        filtered = filtered[filtered["quality"] == STRATEGY_1_FILTERS["quality"]]

    # Filter by rank (6-15)
    if "rank" in filtered.columns:
        filtered = filtered[
            (filtered["rank"] >= STRATEGY_1_FILTERS["rank_min"])
            & (filtered["rank"] <= STRATEGY_1_FILTERS["rank_max"])
        ]

    # Filter by quality flag (SAFE ENTRY) - handle checkmark symbol
    if "quality_flag" in filtered.columns:
        # Handle both "SAFE ENTRY" and "✓ SAFE ENTRY"
        filtered = filtered[
            filtered["quality_flag"].str.contains("SAFE ENTRY", na=False)
        ]

    # Filter by Vol R:R >= 2.0
    if "vol_rr" in filtered.columns:
        filtered = filtered[filtered["vol_rr"] >= STRATEGY_1_FILTERS["vol_rr_min"]]

    return filtered


def calculate_strategy_metrics(df: pd.DataFrame, holding_period: int) -> dict:
    """
    Calculate comprehensive strategy metrics

    Args:
        df: Filtered backtest results
        holding_period: Holding period in days

    Returns:
        Dictionary with metrics
    """
    if df.empty:
        return {"error": "No trades match Strategy 1 filters"}

    return_col = f"return_{holding_period}d"

    if return_col not in df.columns:
        return {"error": f"Column {return_col} not found"}

    returns = df[return_col].dropna()

    if len(returns) == 0:
        return {"error": "No valid returns data"}

    # Win/Loss counts
    winners = returns[returns > 0]
    losers = returns[returns <= 0]

    # Calculate metrics
    metrics = {
        # Basic stats
        "total_trades": len(returns),
        "winners": len(winners),
        "losers": len(losers),
        "win_rate": (len(winners) / len(returns) * 100) if len(returns) > 0 else 0,
        # Returns
        "avg_return": returns.mean(),
        "median_return": returns.median(),
        "avg_win": winners.mean() if len(winners) > 0 else 0,
        "avg_loss": losers.mean() if len(losers) > 0 else 0,
        # Extremes
        "max_win": returns.max(),
        "max_loss": returns.min(),
        # Distribution
        "std_dev": returns.std(),
        # Expectancy
        "expectancy": returns.mean(),
    }

    # Calculate consecutive losses
    consecutive_losses = []
    current_streak = 0

    for ret in returns:
        if ret <= 0:
            current_streak += 1
        else:
            if current_streak > 0:
                consecutive_losses.append(current_streak)
            current_streak = 0

    if current_streak > 0:
        consecutive_losses.append(current_streak)

    metrics["max_consecutive_losses"] = (
        max(consecutive_losses) if consecutive_losses else 0
    )

    # Time-based metrics
    if "report_date" in df.columns:
        df_sorted = df.sort_values("report_date")
        date_range = df_sorted["report_date"].max() - df_sorted["report_date"].min()
        months = date_range.days / 30.44  # Average days per month

        metrics["date_range_days"] = date_range.days
        metrics["date_range_months"] = months
        metrics["trades_per_month"] = len(returns) / months if months > 0 else 0

    return metrics


def print_strategy_report(metrics: dict, filters: dict):
    """
    Print formatted strategy report

    Args:
        metrics: Strategy metrics dictionary
        filters: Strategy filter criteria
    """
    print("=" * 80)
    print("STRATEGY 1 BACKTEST RESULTS")
    print("=" * 80)

    # Print filters
    print("\nSTRATEGY FILTERS:")
    print(f"  Quality: {filters['quality']}")
    print(f"  Rank: {filters['rank_min']}-{filters['rank_max']}")
    print(f"  Entry Flag: {filters['quality_flag']}")
    print(f"  Vol R:R: >= {filters['vol_rr_min']}")

    if "error" in metrics:
        print(f"\n[ERROR] {metrics['error']}")
        return

    print("\n" + "=" * 80)
    print("PERFORMANCE METRICS")
    print("=" * 80)

    # Trade count
    print(f"\nTOTAL TRADES: {metrics['total_trades']}")

    # Time range
    if "date_range_months" in metrics:
        print(f"TIME PERIOD: {metrics['date_range_months']:.1f} months")
        print(f"TRADE FREQUENCY: {metrics['trades_per_month']:.2f} trades/month")

    # Win rate
    print(f"\nWIN RATE: {metrics['win_rate']:.1f}%")
    print(f"  Winners: {metrics['winners']}")
    print(f"  Losers: {metrics['losers']}")

    # Returns
    print(f"\nRETURNS:")
    print(f"  Average: {metrics['avg_return']:+.2f}%")
    print(f"  Median: {metrics['median_return']:+.2f}%")
    print(f"  Std Dev: {metrics['std_dev']:.2f}%")

    print(f"\n  Avg Win: {metrics['avg_win']:+.2f}%")
    print(f"  Avg Loss: {metrics['avg_loss']:+.2f}%")

    print(f"\n  Max Win: {metrics['max_win']:+.2f}%")
    print(f"  Max Loss: {metrics['max_loss']:+.2f}%")

    # Risk metrics
    print(f"\nRISK METRICS:")
    print(
        f"  Max Consecutive Losses: {metrics['max_consecutive_losses']} trades in a row"
    )

    # Expectancy
    print(f"\nEXPECTANCY: {metrics['expectancy']:+.2f}% per trade")

    # Comparison to target
    print("\n" + "=" * 80)
    print("COMPARISON TO TARGET METRICS")
    print("=" * 80)

    target_win_rate = 80.0
    target_avg_return = 8.14
    target_trades_per_month = 1.7

    print(f"\nWin Rate: {metrics['win_rate']:.1f}% vs Target {target_win_rate}%")
    if metrics["win_rate"] >= target_win_rate:
        print("  [OK] MEETS TARGET")
    else:
        print(f"  [X] Below target by {target_win_rate - metrics['win_rate']:.1f}%")

    print(
        f"\nAvg Return: {metrics['avg_return']:+.2f}% vs Target +{target_avg_return}%"
    )
    if metrics["avg_return"] >= target_avg_return:
        print("  [OK] MEETS TARGET")
    else:
        print(f"  [X] Below target by {target_avg_return - metrics['avg_return']:.2f}%")

    if "trades_per_month" in metrics:
        print(
            f"\nTrade Frequency: {metrics['trades_per_month']:.2f} vs Target {target_trades_per_month}"
        )
        if abs(metrics["trades_per_month"] - target_trades_per_month) < 0.5:
            print("  [OK] CLOSE TO TARGET")
        else:
            print(
                f"  [!] Different by {abs(metrics['trades_per_month'] - target_trades_per_month):.2f} trades/month"
            )

    print("\n" + "=" * 80)


def main():
    """
    Run Strategy 1 backtest on historical data
    """
    print("=" * 80)
    print("STRATEGY 1 BACKTEST - 5 YEARS OF DATA")
    print("=" * 80)
    print(f"\nCategory: {CATEGORY}")
    print(f"Holding Period: {HOLDING_PERIOD} days")
    print(f"Max Reports: {MAX_REPORTS}")

    # Initialize backtester
    results_dir = ROOT / "scanner_results" / "historical_simulation"
    backtester = WatchlistBacktest(results_dir)

    print(f"\nResults directory: {results_dir}")

    # Find available reports
    files = backtester.find_watchlist_files(CATEGORY)
    print(f"Found {len(files)} watchlist reports")

    if not files:
        print("\n[ERROR] No watchlist files found!")
        return

    # Show date range
    oldest_date = backtester.extract_date_from_filename(files[-1])
    newest_date = backtester.extract_date_from_filename(files[0])
    print(
        f"Date range: {oldest_date.strftime('%Y-%m-%d')} to {newest_date.strftime('%Y-%m-%d')}"
    )

    # Run backtest
    print(f"\nRunning backtest on up to {MAX_REPORTS} reports...")
    results = backtester.run_backtest(
        category=CATEGORY, max_reports=MAX_REPORTS, holding_period=HOLDING_PERIOD
    )

    if results.empty:
        print("\n[ERROR] No backtest results generated!")
        return

    print(f"\n[OK] Backtest complete: {len(results)} total trades")

    # Apply Strategy 1 filters
    print("\nApplying Strategy 1 filters...")
    filtered_results = apply_strategy1_filters(results)

    print(
        f"[OK] Strategy 1 trades: {len(filtered_results)} (filtered from {len(results)})"
    )

    # Calculate metrics
    metrics = calculate_strategy_metrics(filtered_results, HOLDING_PERIOD)

    # Print report
    print_strategy_report(metrics, STRATEGY_1_FILTERS)

    # Save results
    output_dir = ROOT / "backtest_results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "backtest_strategy1_results.csv"
    filtered_results.to_csv(output_file, index=False)
    print(f"\n[OK] Detailed results saved to: backtest_results/{output_file.name}")

    # Save summary
    summary_file = output_dir / "backtest_strategy1_summary.csv"
    summary_df = pd.DataFrame([metrics])
    summary_df.to_csv(summary_file, index=False)
    print(f"[OK] Summary saved to: backtest_results/{summary_file.name}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

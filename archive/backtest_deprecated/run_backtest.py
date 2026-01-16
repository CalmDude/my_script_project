"""
Run GHB Strategy Backtest
Entry point for running historical backtests
"""

import sys
from pathlib import Path

# Add backtest directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backtest_engine import BacktestEngine
from performance_metrics import PerformanceMetrics
import argparse


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run GHB Strategy Backtest")
    parser.add_argument(
        "--config", default="backtest/config.json", help="Path to config file"
    )
    parser.add_argument(
        "--refresh-data",
        action="store_true",
        help="Force refresh historical data (ignore cache)",
    )
    parser.add_argument(
        "--detailed-report",
        action="store_true",
        help="Print detailed performance report",
    )

    args = parser.parse_args()

    # Create and run backtest
    print("\n" + "=" * 80)
    print("GHB STRATEGY BACKTEST")
    print("=" * 80)

    engine = BacktestEngine(config_path=args.config)
    files = engine.run(force_refresh_data=args.refresh_data)

    # Print detailed report if requested
    if args.detailed_report:
        df_equity = engine.portfolio.get_equity_curve_dataframe()
        df_trades = engine.portfolio.get_trades_dataframe()
        PerformanceMetrics.print_comprehensive_report(df_equity, df_trades)

    print("\n✅ Backtest complete!")
    print(f"   Results saved to: {files.get('summary_file')}")
    print(f"\n💡 Next steps:")
    print(f"   1. Review trades: {files.get('trades_file')}")
    print(f"   2. Analyze equity curve: {files.get('equity_file')}")
    print(f"   3. Check summary: {files.get('summary_file')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

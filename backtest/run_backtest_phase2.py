"""
Run Phase 2 Backtest with Enhanced Trading Logic
Uses unbiased universe with stop losses and entry filters
"""

import sys
import argparse
from datetime import datetime
from backtest_engine_phase2 import BacktestEnginePhase2


def print_header():
    """Print header"""
    print("\n" + "=" * 80)
    print("GHB STRATEGY PHASE 2 BACKTEST")
    print("=" * 80)
    print("\nPhase 2 Enhancements:")
    print("  ✅ ATR-based stop losses (-2×ATR exit)")
    print("  ✅ Momentum entry filters (RSI >50, Price >50-day MA, ROC >10%)")
    print("  ✅ Keep unbiased universe (same 25 stocks)")
    print("=" * 80)


def main():
    """Main backtest execution"""
    parser = argparse.ArgumentParser(description="Run Phase 2 GHB Strategy Backtest")
    parser.add_argument(
        "--config", type=str, default="backtest/config.json", help="Path to config file"
    )
    parser.add_argument(
        "--refresh-data",
        action="store_true",
        help="Force refresh of historical data",
    )
    parser.add_argument(
        "--no-stop-loss",
        action="store_true",
        help="Disable stop losses (test baseline)",
    )
    parser.add_argument(
        "--no-entry-filter",
        action="store_true",
        help="Disable entry filters (test baseline)",
    )

    args = parser.parse_args()

    print_header()

    print(f"\n{'#'*80}")
    print(f"# GHB STRATEGY PHASE 2 BACKTEST")
    print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}")

    # Initialize Phase 2 engine
    engine = BacktestEnginePhase2(
        config_path=args.config,
        use_stop_losses=not args.no_stop_loss,
        use_entry_filters=not args.no_entry_filter,
    )

    # Load data
    engine.load_data(force_refresh=args.refresh_data)

    # Generate Friday schedule
    engine.generate_fridays()

    # Run backtest
    engine.run_backtest()

    # Save results
    files = engine.save_results()

    # Print summary
    summary = engine.get_summary()

    print("\n" + "=" * 80)
    print("PHASE 2 BACKTEST RESULTS SUMMARY")
    print("=" * 80)

    print(f"\n📅 PERIOD:")
    print(
        f"   {summary['Backtest_Period']['Start_Date']} to {summary['Backtest_Period']['End_Date']}"
    )
    print(
        f"   {summary['Backtest_Period']['Total_Weeks']} weeks ({summary['Backtest_Period']['Years']:.1f} years)"
    )

    print(f"\n💰 PERFORMANCE:")
    print(f"   Starting Value:  ${summary['Performance']['Starting_Value']:12,.0f}")
    print(f"   Final Value:     ${summary['Performance']['Final_Value']:12,.0f}")
    print(f"   Total Return:     {summary['Performance']['Total_Return_%']:10.2f}%")
    print(f"   CAGR:             {summary['Performance']['CAGR_%']:10.2f}%")
    print(f"   Max Drawdown:     {summary['Performance']['Max_Drawdown_%']:10.2f}%")

    print(f"\n📊 TRADING STATS:")
    print(f"   Total Trades:       {summary['Trading_Stats']['Total_Trades']:10}")
    print(f"   Win Rate:           {summary['Trading_Stats']['Win_Rate_%']:10.2f}%")
    print(f"   Avg Win:            {summary['Trading_Stats']['Avg_Win_%']:10.2f}%")
    print(f"   Avg Loss:           {summary['Trading_Stats']['Avg_Loss_%']:10.2f}%")
    print(f"   Avg Trade:          {summary['Trading_Stats']['Avg_Trade_%']:10.2f}%")

    print(f"\n🏆 BEST/WORST:")
    print(
        f"   Best Trade:      {summary['Trading_Stats']['Best_Trade_%']:10.2f}% ({summary['Trading_Stats']['Best_Trade_Ticker']})"
    )
    print(
        f"   Worst Trade:     {summary['Trading_Stats']['Worst_Trade_%']:10.2f}% ({summary['Trading_Stats']['Worst_Trade_Ticker']})"
    )

    print("\n" + "=" * 80)

    print(f"\n{'#'*80}")
    print(f"# BACKTEST COMPLETE")
    print(f"{'#'*80}")

    print(f"\n✅ Backtest complete!")
    print(f"   Results saved to: {files['summary_file']}")

    print(f"\n💡 Next steps:")
    print(f"   1. Review trades: {files['trades_file']}")
    print(f"   2. Analyze equity curve: {files['equity_file']}")
    print(f"   3. Check summary: {files['summary_file']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

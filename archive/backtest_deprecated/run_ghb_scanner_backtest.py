"""
Run GHB Portfolio Scanner Backtest
Uses exact scanner logic: variable allocation, entry filtering, risk-adjusted sizing
"""

import sys
from pathlib import Path
import json

# Add backtest directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backtest_engine import BacktestEngine
from performance_metrics import PerformanceMetrics
import pandas as pd


def main():
    """Main entry point for scanner backtest"""
    print("\n" + "=" * 80)
    print("GHB PORTFOLIO SCANNER BACKTEST")
    print("=" * 80)
    print("Testing with:")
    print("  ✓ Variable allocation (TSLA 50%, NVDA 20%, others 3.75%)")
    print("  ✓ Entry filter (< 10% from support)")
    print("  ✓ Risk-adjusted sizing (100%/75%/50% tiers)")
    print("=" * 80)

    # Load config
    config_path = "backtest/config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    # Create custom backtest engine with scanner logic
    engine = ScannerBacktestEngine(config_path=config_path)

    # Run backtest with scanner settings
    results = engine.run(force_refresh_data=False)

    # Print detailed report
    df_equity = engine.portfolio.get_equity_curve_dataframe()
    df_trades = engine.portfolio.get_trades_dataframe()

    if not df_equity.empty and not df_trades.empty:
        PerformanceMetrics.print_comprehensive_report(df_equity, df_trades)

    print("\n✅ Scanner backtest complete!")
    print(f"   Results saved to: {results.get('summary_file')}")

    # Validate scanner claims
    validate_scanner_claims(results, df_trades)

    return 0


class ScannerBacktestEngine(BacktestEngine):
    """Extended backtest engine with scanner-specific logic"""

    def __init__(self, config_path: str = "backtest/config.json"):
        """Initialize with scanner configuration"""
        super().__init__(config_path)

        # Override portfolio manager with variable allocations
        position_allocations = self.portfolio_settings.get("position_allocations", {})

        from portfolio_manager import PortfolioManager

        self.portfolio = PortfolioManager(
            starting_cash=self.portfolio_settings["starting_cash"],
            position_size_pct=self.portfolio_settings["position_size_pct"],
            max_positions=self.portfolio_settings["max_positions"],
            position_allocations=position_allocations,
        )

        # Get scanner-specific settings
        self.use_entry_filter = (
            self.strategy_settings.get("max_support_distance") is not None
        )
        self.max_support_distance = self.strategy_settings.get(
            "max_support_distance", 10
        )
        self.use_risk_adjustment = self.strategy_settings.get(
            "use_risk_adjusted_sizing", True
        )

        print(f"\n📊 Scanner Settings:")
        print(
            f"   Entry Filter: {'ON' if self.use_entry_filter else 'OFF'} (max distance: {self.max_support_distance}%)"
        )
        print(f"   Risk Adjustment: {'ON' if self.use_risk_adjustment else 'OFF'}")

    def run_backtest(self):
        """
        Run backtest simulation with scanner logic (OVERRIDE parent method)

        Changes from base engine:
        1. Apply entry filter (configurable threshold from support)
        2. Use variable position allocation
        3. Use risk-adjusted sizing
        """
        print(f"\n{'='*80}")
        print("STEP 3: Simulating Weekly Trading (Scanner Logic)")
        print(f"{'='*80}")

        buy_slippage = self.execution_settings["buy_slippage"]
        sell_slippage = self.execution_settings["sell_slippage"]

        total_weeks = len(self.fridays)

        for week_idx, friday in enumerate(self.fridays):
            if week_idx % 10 == 0:
                print(f"   Week {week_idx+1}/{total_weeks}: {friday.date()}")

            # Calculate signals for this Friday
            df_signals = self.strategy.scan_universe(self.data_dict, target_date=friday)

            if df_signals.empty:
                continue

            # Update all position prices with current signals
            self.portfolio.update_positions(df_signals)

            # Monday after Friday (execution day)
            monday = friday + pd.Timedelta(days=3)

            # STEP 1: Process SELL signals (exit N2 positions)
            sell_signals = self.strategy.get_sell_signals(df_signals)

            for _, signal in sell_signals.iterrows():
                ticker = signal["Ticker"]

                if self.portfolio.has_position(ticker):
                    self.portfolio.close_position(
                        ticker=ticker,
                        exit_date=monday,
                        exit_price=signal["Close"],
                        exit_state=signal["State"],
                        slippage=sell_slippage,
                    )

            # STEP 2: Process BUY signals with scanner logic
            # Apply entry filter if enabled
            if self.use_entry_filter:
                buy_candidates = self.strategy.filter_safe_entries(
                    df_signals, max_distance=self.max_support_distance
                )
                # Debug: print filter results
                if week_idx == 0:  # First week only
                    all_p1 = df_signals[df_signals["State"] == "P1"]
                    print(
                        f"\n   DEBUG: Entry filter active (max={self.max_support_distance}%)"
                    )
                    print(f"   P1 signals before filter: {len(all_p1)}")
                    print(f"   P1 signals after filter: {len(buy_candidates)}")
                    if len(buy_candidates) > 0:
                        print(
                            f"   Sample distances: {buy_candidates['To_Support_%'].head(3).tolist()}"
                        )
            else:
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

                # Get distance from support for risk adjustment
                distance_from_support = signal.get("To_Support_%", 0)

                # Enter position with variable allocation and risk adjustment
                self.portfolio.open_position(
                    ticker=ticker,
                    entry_date=monday,
                    entry_price=signal["Close"],
                    entry_state=signal["State"],
                    slippage=buy_slippage,
                    distance_from_support=distance_from_support,
                    use_risk_adjustment=self.use_risk_adjustment,
                )

            # Record equity for this week
            self.portfolio.record_equity(monday)

        print(f"\n✅ Trading simulation complete!")
        print(f"   Total weeks: {total_weeks}")
        print(f"   Final value: ${self.portfolio.portfolio_value:,.2f}")
        print(f"   Total return: {self.portfolio.total_return_pct:.2f}%")


def validate_scanner_claims(results, df_trades):
    """Validate scanner performance claims"""
    print("\n" + "=" * 80)
    print("SCANNER CLAIMS VALIDATION")
    print("=" * 80)

    # Load summary from results
    if results.get("summary_file"):
        with open(results["summary_file"], "r") as f:
            summary = json.load(f)

        cagr = summary["Performance"]["CAGR_%"]
        total_return = summary["Performance"]["Total_Return_%"]
        win_rate = summary["Trading_Stats"]["Win_Rate_%"]

        # Claim 1: CAGR = 56.51%
        claim_cagr = 56.51
        print(f"\n1. CAGR Claim: {claim_cagr}%")
        print(f"   Actual: {cagr:.2f}%")
        if cagr >= claim_cagr * 0.9:  # Within 10% of claim
            print(f"   ✅ VALIDATED (within 10%)")
        else:
            print(f"   ⚠️  NEEDS REVIEW (difference: {cagr - claim_cagr:.2f}%)")

        # Claim 2: Total Return = 332% over 3.3 years
        claim_return = 332
        years = summary["Backtest_Period"]["Years"]
        print(f"\n2. Total Return Claim: {claim_return}% over ~3.3 years")
        print(f"   Actual: {total_return:.2f}% over {years:.1f} years")
        if total_return >= claim_return * 0.9:
            print(f"   ✅ VALIDATED")
        else:
            print(f"   ⚠️  NEEDS REVIEW")

        # Claim 3: Win Rate = 40%
        claim_win_rate = 40
        print(f"\n3. Win Rate Claim: {claim_win_rate}%")
        print(f"   Actual: {win_rate:.2f}%")
        if abs(win_rate - claim_win_rate) <= 5:  # Within 5%
            print(f"   ✅ VALIDATED")
        else:
            print(f"   ⚠️  NEEDS REVIEW")

        # Claim 4: Best Trade = NVDA +516%
        if not df_trades.empty:
            sell_trades = df_trades[df_trades["Action"] == "SELL"]
            if not sell_trades.empty:
                best_trade = sell_trades.nlargest(1, "PnL_%").iloc[0]
                print(f"\n4. Best Trade Claim: NVDA +516%")
                print(
                    f"   Actual Best: {best_trade['Ticker']} +{best_trade['PnL_%']:.1f}%"
                )
                if best_trade["PnL_%"] >= 400:  # Close to 516%
                    print(f"   ✅ MEGA-WINNER ACHIEVED")
                else:
                    print(f"   ⚠️  NO MEGA-WINNER (>400%)")

        # Claim 5: ~14 trades per year
        total_trades = summary["Trading_Stats"]["Total_Trades"]
        trades_per_year = total_trades / years if years > 0 else 0
        print(f"\n5. Trade Frequency Claim: ~14 trades/year")
        print(f"   Actual: {trades_per_year:.1f} trades/year")
        if abs(trades_per_year - 14) <= 5:
            print(f"   ✅ VALIDATED")
        else:
            print(f"   ⚠️  DIFFERENT FREQUENCY")


if __name__ == "__main__":
    sys.exit(main())

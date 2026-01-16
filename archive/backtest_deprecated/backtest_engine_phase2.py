"""
Phase 2 Backtest Engine with Stop Loss Logic
Enhanced version of BacktestEngine that checks stop losses on every position
"""

from backtest_engine import BacktestEngine
from strategy_signals_phase2 import GHBStrategyPhase2
import pandas as pd


class BacktestEnginePhase2(BacktestEngine):
    """Phase 2 backtest engine with stop loss checks"""

    def __init__(
        self,
        config_path: str = "backtest/config.json",
        use_stop_losses=True,
        use_entry_filters=True,
    ):
        """Initialize Phase 2 backtest engine"""
        # Call parent init
        super().__init__(config_path)

        # Replace strategy with Phase 2 version
        self.strategy = GHBStrategyPhase2(
            use_stop_losses=use_stop_losses, use_entry_filters=use_entry_filters
        )

        self.use_stop_losses = use_stop_losses

        print(f"\n✅ Phase 2 Enhancements:")
        print(f"   Stop Losses: {'ENABLED' if use_stop_losses else 'DISABLED'}")
        print(f"   Entry Filters: {'ENABLED' if use_entry_filters else 'DISABLED'}")

    def check_stop_losses(self, friday: pd.Timestamp):
        """
        Check all open positions for stop loss hits
        This is called BEFORE processing signals
        """
        if not self.use_stop_losses:
            return

        # Get slippage
        sell_slippage = self.execution_settings["sell_slippage"]

        # Check each position
        positions_to_close = []

        for ticker, position in list(self.portfolio.positions.items()):
            # Get current data for this stock
            if ticker not in self.data_dict:
                continue

            df = self.data_dict[ticker]
            df_current = df[df["Date"] <= friday].copy()

            if df_current.empty:
                continue

            # Get current price and ATR
            current_price = df_current["Close"].iloc[-1]
            atr = self.strategy.calculate_atr(df_current)

            # Check stop loss
            stop_check = self.strategy.check_stop_loss(
                entry_price=position.entry_price, current_price=current_price, atr=atr
            )

            if stop_check["hit"]:
                positions_to_close.append(
                    {
                        "ticker": ticker,
                        "current_price": current_price,
                        "stop_price": stop_check["stop_price"],
                        "loss_pct": stop_check["current_loss_pct"],
                        "atr": atr,
                    }
                )

        # Close stopped-out positions
        monday = friday + pd.Timedelta(days=3)

        for stop_info in positions_to_close:
            self.portfolio.close_position(
                ticker=stop_info["ticker"],
                exit_date=monday,
                exit_price=stop_info["current_price"],
                exit_state="STOP_LOSS",
                slippage=sell_slippage,
            )

    def run_backtest(self):
        """Run backtest simulation with Phase 2 enhancements"""
        print(f"\n{'='*80}")
        print("STEP 3: Running Phase 2 Backtest Simulation")
        print(f"{'='*80}")

        buy_slippage = self.execution_settings["buy_slippage"]
        sell_slippage = self.execution_settings["sell_slippage"]

        total_weeks = len(self.fridays)

        for week_idx, friday in enumerate(self.fridays, 1):
            # Monday execution date (3 days after Friday)
            monday = friday + pd.Timedelta(days=3)

            # Progress indicator
            if week_idx % 10 == 0 or week_idx == 1 or week_idx == total_weeks:
                print(
                    f"  Week {week_idx:3d}/{total_weeks} ({week_idx/total_weeks*100:5.1f}%) - {friday.date()} | "
                    f"Portfolio: ${self.portfolio.portfolio_value:12,.0f} | "
                    f"Positions: {len(self.portfolio.positions)}/{self.portfolio.max_positions}"
                )

            # PHASE 2 ENHANCEMENT: Check stop losses FIRST
            self.check_stop_losses(friday)

            # Generate signals for all stocks as of this Friday
            df_signals = self.strategy.scan_universe(self.data_dict, friday)

            if df_signals.empty:
                self.portfolio.record_equity(monday)
                continue

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

            # STEP 2: Process BUY signals (enter new P1 positions)
            # NOTE: Phase 2 strategy already filtered P1 signals by entry criteria
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

        print(f"\n✅ Phase 2 Backtest complete!")
        print(f"   Total weeks simulated: {total_weeks}")
        print(f"   Final portfolio value: ${self.portfolio.portfolio_value:,.2f}")
        print(f"   Total return: {self.portfolio.total_return_pct:.2f}%")


if __name__ == "__main__":
    print("=" * 80)
    print("Testing Phase 2 Backtest Engine")
    print("=" * 80)

    engine = BacktestEnginePhase2(
        config_path="backtest/config.json", use_stop_losses=True, use_entry_filters=True
    )

    print("\n✅ Phase 2 engine initialized successfully")
    print("\nTo run full backtest, use: python backtest/run_backtest_phase2.py")

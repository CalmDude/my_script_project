"""
Portfolio Manager for GHB Strategy Backtest
Handles position tracking, cash management, and P&L calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class Position:
    """Represents a single stock position"""

    def __init__(
        self,
        ticker: str,
        entry_date: pd.Timestamp,
        entry_price: float,
        shares: int,
        entry_state: str,
    ):
        self.ticker = ticker
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.entry_state = entry_state
        self.current_state = entry_state
        self.current_price = entry_price

    @property
    def cost_basis(self) -> float:
        """Total cost of position"""
        return self.entry_price * self.shares

    @property
    def current_value(self) -> float:
        """Current market value"""
        return self.current_price * self.shares

    @property
    def pnl_dollars(self) -> float:
        """Profit/Loss in dollars"""
        return self.current_value - self.cost_basis

    @property
    def pnl_percent(self) -> float:
        """Profit/Loss in percent"""
        return (
            (self.pnl_dollars / self.cost_basis) * 100 if self.cost_basis > 0 else 0.0
        )

    def update_price(self, price: float, state: str):
        """Update current price and state"""
        self.current_price = price
        self.current_state = state

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "Ticker": self.ticker,
            "Entry_Date": self.entry_date,
            "Entry_Price": self.entry_price,
            "Shares": self.shares,
            "Entry_State": self.entry_state,
            "Current_State": self.current_state,
            "Current_Price": self.current_price,
            "Cost_Basis": self.cost_basis,
            "Current_Value": self.current_value,
            "PnL_$": self.pnl_dollars,
            "PnL_%": self.pnl_percent,
        }


class PortfolioManager:
    """Manages portfolio state throughout backtest"""

    def __init__(
        self,
        starting_cash: float,
        position_size_pct: float,
        max_positions: int,
        position_allocations: Dict[str, float] = None,
    ):
        """
        Initialize portfolio manager

        Args:
            starting_cash: Initial capital
            position_size_pct: Default size of each position as % of portfolio (e.g., 7 for 7%)
            max_positions: Maximum number of concurrent positions
            position_allocations: Optional dict of custom allocations per ticker {ticker: pct}
        """
        self.starting_cash = starting_cash
        self.position_size_pct = position_size_pct
        self.max_positions = max_positions
        self.position_allocations = position_allocations or {}

        # Portfolio state
        self.cash = starting_cash
        self.positions: Dict[str, Position] = {}  # {ticker: Position}
        self.trade_history: List[Dict] = []

        # Performance tracking
        self.equity_curve: List[Dict] = []

        print(f"✅ Portfolio initialized:")
        print(f"   Starting Cash: ${starting_cash:,.0f}")
        print(
            f"   Default Position Size: {position_size_pct}% (${starting_cash * position_size_pct / 100:,.0f} per position)"
        )
        print(f"   Max Positions: {max_positions}")
        if self.position_allocations:
            print(f"   Custom Allocations:")
            for ticker, pct in self.position_allocations.items():
                print(f"      {ticker}: {pct}% (${starting_cash * pct / 100:,.0f})")

    @property
    def portfolio_value(self) -> float:
        """Total portfolio value (cash + positions)"""
        positions_value = sum(pos.current_value for pos in self.positions.values())
        return self.cash + positions_value

    @property
    def positions_value(self) -> float:
        """Total value of all open positions"""
        return sum(pos.current_value for pos in self.positions.values())

    @property
    def position_count(self) -> int:
        """Number of open positions"""
        return len(self.positions)

    @property
    def total_return_pct(self) -> float:
        """Total return since inception"""
        return ((self.portfolio_value - self.starting_cash) / self.starting_cash) * 100

    def get_position_allocation_pct(self, ticker: str) -> float:
        """
        Get position allocation percentage for a ticker

        If ticker has custom allocation, return it.
        Otherwise, calculate dynamic allocation from remaining percentage.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Allocation percentage for this ticker
        """
        # Check if ticker has custom allocation
        if ticker in self.position_allocations:
            return self.position_allocations[ticker]

        # Calculate remaining allocation for non-custom stocks
        total_custom_alloc = sum(self.position_allocations.values())
        remaining_alloc = 100 - total_custom_alloc

        # Split remaining among (max_positions - custom_count) stocks
        num_non_custom_slots = self.max_positions - len(self.position_allocations)

        if num_non_custom_slots > 0:
            return remaining_alloc / num_non_custom_slots
        else:
            # Fallback if all positions are custom
            return self.position_size_pct

    def adjust_position_for_risk(
        self, base_position_value: float, distance_from_support: float
    ) -> float:
        """
        Adjust position size based on distance from support (entry risk)

        Risk tiers based on distance from support:
        - < 3%: LOW risk → 100% of allocation
        - 3-5%: LOW-MOD risk → 75% of allocation
        - 5-10%: MOD risk → 50% of allocation
        - 10-15%: HIGH risk → 30% of allocation (should be filtered out)
        - > 15%: WAIT → 0% (should be filtered out)

        Args:
            base_position_value: Base position value based on allocation %
            distance_from_support: Percentage distance from support level

        Returns:
            Risk-adjusted position value
        """
        if distance_from_support < 3:
            multiplier = 1.0  # LOW risk - full position
        elif distance_from_support < 5:
            multiplier = 0.75  # LOW-MOD risk - 75% position
        elif distance_from_support < 10:
            multiplier = 0.50  # MOD risk - 50% position
        elif distance_from_support < 15:
            multiplier = 0.30  # HIGH risk - 30% position (should be filtered out)
        else:
            multiplier = 0.0  # WAIT - no position (should be filtered out)

        return base_position_value * multiplier

    def calculate_position_size(
        self,
        price: float,
        ticker: str = None,
        distance_from_support: float = None,
        use_risk_adjustment: bool = False,
    ) -> int:
        """
        Calculate number of shares for a new position

        Now supports:
        1. Variable allocation per ticker (TSLA 50%, NVDA 20%, etc.)
        2. Risk-adjusted sizing based on distance from support

        Args:
            price: Stock price
            ticker: Stock ticker (required for variable allocation)
            distance_from_support: Distance from support % (for risk adjustment)
            use_risk_adjustment: Whether to apply risk-based sizing

        Returns:
            Number of shares to buy
        """
        # Get allocation percentage for this ticker
        if ticker:
            alloc_pct = self.get_position_allocation_pct(ticker)
        else:
            alloc_pct = self.position_size_pct

        # Calculate base position value based on starting cash (not current portfolio value)
        # This ensures consistent allocations throughout backtest
        base_position_value = self.starting_cash * (alloc_pct / 100)

        # Apply risk adjustment if enabled
        if use_risk_adjustment and distance_from_support is not None:
            position_value = self.adjust_position_for_risk(
                base_position_value, distance_from_support
            )
        else:
            position_value = base_position_value

        # Calculate shares
        shares = int(position_value / price)

        return shares

    def can_open_position(self) -> bool:
        """Check if we can open a new position"""
        return self.position_count < self.max_positions

    def has_position(self, ticker: str) -> bool:
        """Check if we currently hold a position in ticker"""
        return ticker in self.positions

    def open_position(
        self,
        ticker: str,
        entry_date: pd.Timestamp,
        entry_price: float,
        entry_state: str,
        slippage: float = 1.0,
        distance_from_support: float = None,
        use_risk_adjustment: bool = False,
    ) -> bool:
        """
        Open a new position

        Args:
            ticker: Stock ticker
            entry_date: Date of entry (Monday after Friday signal)
            entry_price: Friday close price
            entry_state: Signal state (usually P1)
            slippage: Execution slippage multiplier (e.g., 1.015 for +1.5%)
            distance_from_support: Distance from support % (for risk adjustment)
            use_risk_adjustment: Whether to apply risk-based sizing

        Returns:
            True if position opened successfully, False otherwise
        """
        if not self.can_open_position():
            return False

        if self.has_position(ticker):
            return False

        # Calculate shares using new method with variable allocation and risk adjustment
        shares = self.calculate_position_size(
            entry_price,
            ticker=ticker,
            distance_from_support=distance_from_support,
            use_risk_adjustment=use_risk_adjustment,
        )

        if shares == 0:
            return False

        # Apply slippage to get actual execution price
        execution_price = entry_price * slippage
        total_cost = execution_price * shares

        if total_cost > self.cash:
            # Not enough cash - reduce shares
            shares = int(self.cash / execution_price)
            if shares == 0:
                return False
            total_cost = execution_price * shares

        # Create position
        position = Position(ticker, entry_date, execution_price, shares, entry_state)
        self.positions[ticker] = position

        # Update cash
        self.cash -= total_cost

        # Record trade
        trade = {
            "Date": entry_date,
            "Ticker": ticker,
            "Action": "BUY",
            "Shares": shares,
            "Price": execution_price,
            "Value": total_cost,
            "State": entry_state,
            "Portfolio_Value": self.portfolio_value,
            "Distance_From_Support": distance_from_support,
        }
        self.trade_history.append(trade)

        return True

    def close_position(
        self,
        ticker: str,
        exit_date: pd.Timestamp,
        exit_price: float,
        exit_state: str,
        slippage: float = 1.0,
    ) -> bool:
        """
        Close an existing position

        Args:
            ticker: Stock ticker
            exit_date: Date of exit (Monday after Friday signal)
            exit_price: Friday close price
            exit_state: Signal state (usually N2)
            slippage: Execution slippage multiplier (e.g., 0.99 for -1%)

        Returns:
            True if position closed successfully, False otherwise
        """
        if not self.has_position(ticker):
            return False

        position = self.positions[ticker]

        # Apply slippage to get actual execution price
        execution_price = exit_price * slippage
        total_proceeds = execution_price * position.shares

        # Calculate P&L
        pnl_dollars = total_proceeds - position.cost_basis
        pnl_percent = (pnl_dollars / position.cost_basis) * 100

        # Update cash
        self.cash += total_proceeds

        # Record trade
        trade = {
            "Date": exit_date,
            "Ticker": ticker,
            "Action": "SELL",
            "Shares": position.shares,
            "Price": execution_price,
            "Value": total_proceeds,
            "State": exit_state,
            "Entry_Date": position.entry_date,
            "Entry_Price": position.entry_price,
            "Entry_State": position.entry_state,
            "Hold_Days": (exit_date - position.entry_date).days,
            "PnL_$": pnl_dollars,
            "PnL_%": pnl_percent,
            "Portfolio_Value": self.portfolio_value,
        }
        self.trade_history.append(trade)

        # Remove position
        del self.positions[ticker]

        return True

    def update_positions(self, df_signals: pd.DataFrame):
        """
        Update all positions with current prices and states

        Args:
            df_signals: DataFrame with current signals for all stocks
        """
        for ticker, position in self.positions.items():
            # Find this ticker in signals
            ticker_signals = df_signals[df_signals["Ticker"] == ticker]

            if not ticker_signals.empty:
                current_price = ticker_signals.iloc[0]["Close"]
                current_state = ticker_signals.iloc[0]["State"]
                position.update_price(current_price, current_state)

    def record_equity(self, date: pd.Timestamp):
        """Record current portfolio value for equity curve"""
        equity_point = {
            "Date": date,
            "Cash": self.cash,
            "Positions_Value": self.positions_value,
            "Portfolio_Value": self.portfolio_value,
            "Return_%": self.total_return_pct,
            "Position_Count": self.position_count,
        }
        self.equity_curve.append(equity_point)

    def get_positions_dataframe(self) -> pd.DataFrame:
        """Get current positions as DataFrame"""
        if not self.positions:
            return pd.DataFrame()

        positions_data = [pos.to_dict() for pos in self.positions.values()]
        return pd.DataFrame(positions_data)

    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trade history as DataFrame"""
        if not self.trade_history:
            return pd.DataFrame()

        return pd.DataFrame(self.trade_history)

    def get_equity_curve_dataframe(self) -> pd.DataFrame:
        """Get equity curve as DataFrame"""
        if not self.equity_curve:
            return pd.DataFrame()

        return pd.DataFrame(self.equity_curve)

    def get_summary_stats(self) -> Dict:
        """Calculate portfolio summary statistics"""
        df_trades = self.get_trades_dataframe()

        if df_trades.empty:
            return {
                "Total_Trades": 0,
                "Final_Value": self.portfolio_value,
                "Total_Return_%": self.total_return_pct,
            }

        # Filter to closed trades only (have PnL)
        closed_trades = df_trades[df_trades["Action"] == "SELL"].copy()

        if closed_trades.empty:
            return {
                "Total_Trades": 0,
                "Final_Value": self.portfolio_value,
                "Total_Return_%": self.total_return_pct,
            }

        # Calculate statistics
        total_trades = len(closed_trades)
        winners = closed_trades[closed_trades["PnL_%"] > 0]
        losers = closed_trades[closed_trades["PnL_%"] < 0]

        win_rate = (len(winners) / total_trades) * 100 if total_trades > 0 else 0
        avg_win = winners["PnL_%"].mean() if len(winners) > 0 else 0
        avg_loss = losers["PnL_%"].mean() if len(losers) > 0 else 0
        avg_trade = closed_trades["PnL_%"].mean()

        best_trade = (
            closed_trades.loc[closed_trades["PnL_%"].idxmax()]
            if total_trades > 0
            else None
        )
        worst_trade = (
            closed_trades.loc[closed_trades["PnL_%"].idxmin()]
            if total_trades > 0
            else None
        )

        return {
            "Total_Trades": total_trades,
            "Win_Rate_%": win_rate,
            "Avg_Win_%": avg_win,
            "Avg_Loss_%": avg_loss,
            "Avg_Trade_%": avg_trade,
            "Best_Trade_%": best_trade["PnL_%"] if best_trade is not None else 0,
            "Best_Trade_Ticker": (
                best_trade["Ticker"] if best_trade is not None else "N/A"
            ),
            "Worst_Trade_%": worst_trade["PnL_%"] if worst_trade is not None else 0,
            "Worst_Trade_Ticker": (
                worst_trade["Ticker"] if worst_trade is not None else "N/A"
            ),
            "Final_Value": self.portfolio_value,
            "Total_Return_%": self.total_return_pct,
        }


if __name__ == "__main__":
    # Test portfolio manager
    print("=" * 80)
    print("Testing Portfolio Manager")
    print("=" * 80)

    # Create portfolio
    portfolio = PortfolioManager(
        starting_cash=110000, position_size_pct=7, max_positions=7
    )

    # Simulate some trades
    test_date = pd.Timestamp("2024-01-15")

    # Open positions
    portfolio.open_position("NVDA", test_date, 100.0, "P1", slippage=1.015)
    portfolio.open_position("MSFT", test_date, 350.0, "P1", slippage=1.015)

    print(f"\n📊 Portfolio after opening 2 positions:")
    print(f"   Cash: ${portfolio.cash:,.2f}")
    print(f"   Positions Value: ${portfolio.positions_value:,.2f}")
    print(f"   Total Value: ${portfolio.portfolio_value:,.2f}")
    print(f"   Position Count: {portfolio.position_count}")

    # Close a position
    portfolio.close_position(
        "NVDA", test_date + pd.Timedelta(days=14), 110.0, "P1", slippage=0.99
    )

    print(f"\n📊 Portfolio after closing NVDA:")
    print(f"   Cash: ${portfolio.cash:,.2f}")
    print(f"   Total Value: ${portfolio.portfolio_value:,.2f}")
    print(f"   Return: {portfolio.total_return_pct:.2f}%")

    # Show summary
    stats = portfolio.get_summary_stats()
    print(f"\n📈 Summary Stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

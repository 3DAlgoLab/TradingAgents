"""
Portfolio tracking module for backtesting.

Tracks positions, cash, and portfolio value over time.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


@dataclass
class Position:
    """Represents a single position in a stock."""

    ticker: str
    shares: float = 0.0
    avg_price: float = 0.0

    def market_value(self, current_price: float) -> float:
        """Calculate market value at current price."""
        return self.shares * current_price

    @property
    def cost_basis(self) -> float:
        """Calculate total cost basis."""
        return self.shares * self.avg_price

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss."""
        return self.market_value(current_price) - self.cost_basis

    def buy(self, shares: float, price: float):
        """Add shares to position."""
        total_cost = self.cost_basis + (shares * price)
        self.shares += shares
        if self.shares > 0:
            self.avg_price = total_cost / self.shares

    def sell(self, shares: float, price: float) -> float:
        """Remove shares from position and return realized P&L."""
        if shares > self.shares:
            shares = self.shares  # Can't sell more than we have

        realized_pnl = shares * (price - self.avg_price)
        self.shares -= shares

        if self.shares == 0:
            self.avg_price = 0.0

        return realized_pnl


@dataclass
class PortfolioSnapshot:
    """Snapshot of portfolio state at a specific date."""

    date: datetime
    cash: float
    positions: Dict[str, Position]
    prices: Dict[str, float]

    def total_value(self) -> float:
        """Calculate total portfolio value."""
        positions_value = sum(
            pos.market_value(self.prices.get(ticker, 0))
            for ticker, pos in self.positions.items()
        )
        return self.cash + positions_value

    def total_return(self, initial_value: float) -> float:
        """Calculate total return since inception."""
        if initial_value == 0:
            return 0.0
        total_val = self.total_value()
        return (total_val - initial_value) / initial_value


class Portfolio:
    """
    Portfolio tracker for backtesting.

    Tracks cash, positions, and portfolio value over time.
    Maintains a history of daily snapshots for analysis.
    """

    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize portfolio with initial capital.

        Args:
            initial_capital: Starting cash amount (default: $100,000)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.history: List[PortfolioSnapshot] = []
        self.trades: List[Dict] = []

    def get_position(self, ticker: str) -> Position:
        """Get or create position for ticker."""
        if ticker not in self.positions:
            self.positions[ticker] = Position(ticker)
        return self.positions[ticker]

    def buy(self, ticker: str, shares: float, price: float, date: datetime) -> bool:
        """
        Execute buy order.

        Args:
            ticker: Stock symbol
            shares: Number of shares to buy
            price: Price per share
            date: Trade date

        Returns:
            True if trade executed successfully
        """
        cost = shares * price
        # Use small tolerance for floating point comparison
        if cost > self.cash + 0.01:
            return False  # Insufficient funds

        self.cash -= cost
        position = self.get_position(ticker)
        position.buy(shares, price)

        self.trades.append(
            {
                "date": date,
                "ticker": ticker,
                "action": "BUY",
                "shares": shares,
                "price": price,
                "value": cost,
            }
        )

        return True

    def sell(self, ticker: str, shares: float, price: float, date: datetime) -> bool:
        """
        Execute sell order.

        Args:
            ticker: Stock symbol
            shares: Number of shares to sell
            price: Price per share
            date: Trade date

        Returns:
            True if trade executed successfully
        """
        position = self.get_position(ticker)
        if position.shares < shares:
            return False  # Insufficient shares

        proceeds = shares * price
        realized_pnl = position.sell(shares, price)

        self.cash += proceeds

        self.trades.append(
            {
                "date": date,
                "ticker": ticker,
                "action": "SELL",
                "shares": shares,
                "price": price,
                "value": proceeds,
                "realized_pnl": realized_pnl,
            }
        )

        return True

    def get_total_value(self, prices: Dict[str, float]) -> float:
        """Calculate total portfolio value with given prices."""
        positions_value = sum(
            pos.market_value(prices.get(ticker, 0))
            for ticker, pos in self.positions.items()
        )
        return self.cash + positions_value

    def record_snapshot(self, date: datetime, prices: Dict[str, float]):
        """Record daily portfolio snapshot."""
        snapshot = PortfolioSnapshot(
            date=date,
            cash=self.cash,
            positions={
                ticker: Position(ticker, pos.shares, pos.avg_price)
                for ticker, pos in self.positions.items()
            },
            prices=prices.copy(),
        )
        self.history.append(snapshot)

    def get_history_df(self) -> pd.DataFrame:
        """Get portfolio history as DataFrame."""
        if not self.history:
            return pd.DataFrame()

        data = []
        for snapshot in self.history:
            data.append(
                {
                    "date": snapshot.date,
                    "cash": snapshot.cash,
                    "total_value": snapshot.total_value(),
                    "total_return": snapshot.total_return(self.initial_capital),
                }
            )

        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        return df

    def get_trades_df(self) -> pd.DataFrame:
        """Get trades as DataFrame."""
        if not self.trades:
            return pd.DataFrame()

        df = pd.DataFrame(self.trades)
        if not df.empty:
            df.set_index("date", inplace=True)
        return df

    def get_current_allocation(self, prices: Dict[str, float]) -> Dict[str, float]:
        """Get current portfolio allocation by ticker."""
        total = self.get_total_value(prices)
        if total == 0:
            return {}

        allocation = {"CASH": self.cash / total}
        for ticker, pos in self.positions.items():
            allocation[ticker] = pos.market_value(prices.get(ticker, 0)) / total

        return allocation

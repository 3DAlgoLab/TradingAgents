"""
Performance metrics calculation module.

Calculates key trading performance metrics:
- CR%: Cumulative Returns
- ARR%: Annualized Rate of Return
- SR: Sharpe Ratio
- MDD%: Maximum Drawdown
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    cumulative_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    volatility_pct: float
    num_trades: int
    win_rate_pct: Optional[float] = None
    profit_factor: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "CR%": round(self.cumulative_return_pct, 2),
            "ARR%": round(self.annualized_return_pct, 2),
            "Sharpe": round(self.sharpe_ratio, 2),
            "MDD%": round(self.max_drawdown_pct, 2),
            "Volatility%": round(self.volatility_pct, 2),
            "Num Trades": self.num_trades,
            "Win Rate%": round(self.win_rate_pct, 2) if self.win_rate_pct else None,
            "Profit Factor": round(self.profit_factor, 2)
            if self.profit_factor
            else None,
        }


class MetricsCalculator:
    """
    Calculate trading performance metrics.

    Implements the metrics used in the TradingAgents paper:
    - Cumulative Returns (CR%)
    - Annualized Rate of Return (ARR%)
    - Sharpe Ratio (SR)
    - Maximum Drawdown (MDD%)
    """

    RISK_FREE_RATE = 0.02  # 2% annual risk-free rate

    @classmethod
    def calculate_all_metrics(
        cls,
        portfolio_values: pd.Series,
        trades_df: Optional[pd.DataFrame] = None,
    ) -> PerformanceMetrics:
        """
        Calculate all performance metrics from portfolio history.

        Args:
            portfolio_values: Series of portfolio values indexed by date
            trades_df: DataFrame of trades (optional, for win rate, profit factor)

        Returns:
            PerformanceMetrics object with all calculated metrics
        """
        if len(portfolio_values) < 2:
            return PerformanceMetrics(
                cumulative_return_pct=0.0,
                annualized_return_pct=0.0,
                sharpe_ratio=0.0,
                max_drawdown_pct=0.0,
                volatility_pct=0.0,
                num_trades=0,
            )

        # Calculate daily returns
        daily_returns = portfolio_values.pct_change().dropna()

        # Cumulative Return
        cr = cls.calculate_cumulative_return(portfolio_values)

        # Annualized Return
        arr = cls.calculate_annualized_return(portfolio_values)

        # Sharpe Ratio
        sharpe = cls.calculate_sharpe_ratio(daily_returns)

        # Maximum Drawdown
        mdd = cls.calculate_max_drawdown(portfolio_values)

        # Volatility (annualized)
        vol = cls.calculate_volatility(daily_returns)

        # Trade statistics
        num_trades = len(trades_df) if trades_df is not None else 0
        win_rate = cls.calculate_win_rate(trades_df) if trades_df is not None else None
        pf = cls.calculate_profit_factor(trades_df) if trades_df is not None else None

        return PerformanceMetrics(
            cumulative_return_pct=cr,
            annualized_return_pct=arr,
            sharpe_ratio=sharpe,
            max_drawdown_pct=mdd,
            volatility_pct=vol,
            num_trades=num_trades,
            win_rate_pct=win_rate,
            profit_factor=pf,
        )

    @classmethod
    def calculate_cumulative_return(cls, portfolio_values: pd.Series) -> float:
        """
        Calculate Cumulative Return (CR%).

        Formula: (Final Value / Initial Value - 1) * 100
        """
        initial_value = portfolio_values.iloc[0]
        final_value = portfolio_values.iloc[-1]

        if initial_value == 0:
            return 0.0

        return ((final_value / initial_value) - 1) * 100

    @classmethod
    def calculate_annualized_return(cls, portfolio_values: pd.Series) -> float:
        """
        Calculate Annualized Rate of Return (ARR%).

        Formula: ((Final Value / Initial Value) ^ (252 / n_days) - 1) * 100
        """
        initial_value = portfolio_values.iloc[0]
        final_value = portfolio_values.iloc[-1]
        n_days = len(portfolio_values)

        if initial_value == 0 or n_days < 2:
            return 0.0

        # Calculate total return
        total_return = final_value / initial_value

        # Annualize (assuming 252 trading days per year)
        years = n_days / 252
        if years == 0:
            return 0.0

        annualized = (total_return ** (1 / years) - 1) * 100
        return annualized

    @classmethod
    def calculate_sharpe_ratio(
        cls, daily_returns: pd.Series, risk_free_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Sharpe Ratio (SR).

        Formula: (Mean Return - Risk Free Rate) / Standard Deviation of Returns
        Annualized by multiplying by sqrt(252)
        """
        if len(daily_returns) < 2:
            return 0.0

        rf = risk_free_rate if risk_free_rate is not None else cls.RISK_FREE_RATE

        # Daily risk-free rate
        daily_rf = rf / 252

        # Excess return
        excess_return = daily_returns.mean() - daily_rf

        # Standard deviation
        std = daily_returns.std()

        if std == 0:
            return 0.0

        # Daily Sharpe
        daily_sharpe = excess_return / std

        # Annualize
        annualized_sharpe = daily_sharpe * np.sqrt(252)

        return annualized_sharpe

    @classmethod
    def calculate_max_drawdown(cls, portfolio_values: pd.Series) -> float:
        """
        Calculate Maximum Drawdown (MDD%).

        Formula: Maximum peak-to-trough decline as percentage
        """
        if len(portfolio_values) < 2:
            return 0.0

        # Calculate running maximum
        running_max = portfolio_values.cummax()

        # Calculate drawdown
        drawdown = (portfolio_values - running_max) / running_max

        # Get maximum drawdown (most negative)
        max_dd = drawdown.min()

        # Return as positive percentage
        return abs(max_dd) * 100

    @classmethod
    def calculate_volatility(cls, daily_returns: pd.Series) -> float:
        """
        Calculate annualized volatility.

        Formula: Standard Deviation of Daily Returns * sqrt(252) * 100
        """
        if len(daily_returns) < 2:
            return 0.0

        return daily_returns.std() * np.sqrt(252) * 100

    @classmethod
    def calculate_win_rate(cls, trades_df: pd.DataFrame) -> Optional[float]:
        """
        Calculate win rate percentage from trades.

        Only considers closed positions (SELL trades with realized P&L).
        """
        if trades_df is None or trades_df.empty:
            return None

        # Filter sell trades with realized P&L
        sell_trades = trades_df[trades_df["action"] == "SELL"]

        if "realized_pnl" not in sell_trades.columns or sell_trades.empty:
            return None

        winning_trades = (sell_trades["realized_pnl"] > 0).sum()
        total_trades = len(sell_trades)

        if total_trades == 0:
            return None

        return (winning_trades / total_trades) * 100

    @classmethod
    def calculate_profit_factor(cls, trades_df: pd.DataFrame) -> Optional[float]:
        """
        Calculate Profit Factor.

        Formula: Gross Profit / Gross Loss
        """
        if trades_df is None or trades_df.empty:
            return None

        # Filter sell trades with realized P&L
        sell_trades = trades_df[trades_df["action"] == "SELL"]

        if "realized_pnl" not in sell_trades.columns or sell_trades.empty:
            return None

        gross_profit = sell_trades[sell_trades["realized_pnl"] > 0][
            "realized_pnl"
        ].sum()
        gross_loss = abs(
            sell_trades[sell_trades["realized_pnl"] < 0]["realized_pnl"].sum()
        )

        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    @staticmethod
    def format_metrics_table(metrics_list: List[Dict], names: List[str]) -> str:
        """
        Format multiple metrics as a comparison table.

        Args:
            metrics_list: List of metric dictionaries
            names: List of strategy names

        Returns:
            Formatted string table
        """
        if not metrics_list or not names or len(metrics_list) != len(names):
            return "Invalid metrics data"

        # Get all metric keys
        all_keys = set()
        for m in metrics_list:
            all_keys.update(m.keys())

        # Define key order (prioritize important metrics)
        priority_keys = ["CR%", "ARR%", "Sharpe", "MDD%", "Volatility%", "Num Trades"]
        other_keys = sorted([k for k in all_keys if k not in priority_keys])
        key_order = [k for k in priority_keys if k in all_keys] + other_keys

        # Build table
        lines = []

        # Header
        header = f"{'Metric':<20}"
        for name in names:
            header += f"{name:>15}"
        lines.append(header)
        lines.append("-" * (20 + 15 * len(names)))

        # Data rows
        for key in key_order:
            row = f"{key:<20}"
            for m in metrics_list:
                value = m.get(key)
                if value is None:
                    row += f"{'N/A':>15}"
                elif isinstance(value, float):
                    row += (
                        f"{value:>14.2f}%"
                        if "Rate" in key
                        or "Return" in key
                        or "MDD" in key
                        or "Volatility" in key
                        else f"{value:>15.2f}"
                    )
                else:
                    row += f"{value:>15}"
            lines.append(row)

        return "\n".join(lines)

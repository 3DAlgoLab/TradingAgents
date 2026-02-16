"""DSPy portfolio manager module.

This module implements the Portfolio Manager who makes the final trading
decision based on all analysis and risk evaluations.
"""

import dspy
from typing import Optional

from tradingagents_dspy.signatures import PortfolioManagerSignature


class PortfolioManager(dspy.Module):
    """Portfolio Manager that makes the final trading decision.

    The Portfolio Manager synthesizes the investment plan from the research team
    and the risk evaluation from the risk management team to make the ultimate
    BUY, SELL, or HOLD decision.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> pm = PortfolioManager()
        >>> decision = pm(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     trader_investment_plan="...",
        ...     risk_evaluation="..."
        ... )
    """

    def __init__(self):
        """Initialize the portfolio manager."""
        super().__init__()
        self.decide = dspy.ChainOfThought(PortfolioManagerSignature)

    def forward(
        self,
        company: str,
        date: str,
        trader_investment_plan: str,
        risk_evaluation: str,
        past_memories: str = "",
    ) -> str:
        """Make final trading decision.

        Args:
            company: Stock ticker symbol
            date: Trading date in YYYY-MM-DD format
            trader_investment_plan: Trading plan from Trader agent
            risk_evaluation: Risk evaluation from Risk Manager
            past_memories: Previous trading memories and lessons learned

        Returns:
            Final trading decision in format: 'ACTION - RATIONALE'
            where ACTION is BUY, SELL, or HOLD
        """
        result = self.decide(
            company=company,
            date=date,
            trader_investment_plan=trader_investment_plan,
            risk_evaluation=risk_evaluation,
            past_memories=past_memories,
        )
        return result.final_trade_decision


__all__ = [
    "PortfolioManager",
]

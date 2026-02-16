"""DSPy trader agent module.

This module implements the trader agent that creates a detailed investment
plan based on the research team's analysis.
"""

import dspy
from typing import Optional

from tradingagents_dspy.signatures import TraderSignature


class Trader(dspy.Module):
    """Trader agent that creates a detailed investment plan.

    The Trader takes the research manager's decision and creates a specific,
    actionable trading plan with entry/exit points and position sizing.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> trader = Trader()
        >>> plan = trader(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     investment_decision="..."
        ... )
    """

    def __init__(self):
        """Initialize the trader agent."""
        super().__init__()
        self.trade = dspy.ChainOfThought(TraderSignature)

    def forward(
        self,
        company: str,
        date: str,
        investment_decision: str,
        past_memories: str = "",
    ) -> str:
        """Generate a detailed trading plan.

        Args:
            company: Stock ticker symbol
            date: Trading date in YYYY-MM-DD format
            investment_decision: Investment decision from Research Manager
            past_memories: Previous trading memories and lessons learned

        Returns:
            Detailed trading plan including action, targets, and position size
        """
        result = self.trade(
            company=company,
            date=date,
            investment_decision=investment_decision,
            past_memories=past_memories,
        )
        return result.trader_investment_plan


__all__ = [
    "Trader",
]

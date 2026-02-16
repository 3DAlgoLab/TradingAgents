"""DSPy researcher agent modules.

This module implements the bull/bear researcher debate system and the
research manager who synthesizes the debate into an investment decision.
"""

import dspy
from typing import Optional, List

from tradingagents_dspy.signatures import (
    BullResearcherSignature,
    BearResearcherSignature,
    ResearchManagerSignature,
)


class BullResearcher(dspy.Module):
    """Bull researcher agent that argues for buying a stock.

    This agent analyzes all available research data and presents compelling
    arguments for why the stock is a good investment opportunity. It can
    engage in iterative debate rounds with the Bear Researcher.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> researcher = BullResearcher()
        >>> argument = researcher(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     market_report="...",
        ...     sentiment_report="...",
        ...     news_report="...",
        ...     fundamentals_report="..."
        ... )
    """

    def __init__(self):
        """Initialize the bull researcher."""
        super().__init__()
        self.debate = dspy.ChainOfThought(BullResearcherSignature)

    def forward(
        self,
        company: str,
        date: str,
        market_report: str,
        sentiment_report: str,
        news_report: str,
        fundamentals_report: str,
        bear_argument: str = "",
        past_memories: str = "",
    ) -> str:
        """Generate bullish argument for a company.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            market_report: Technical analysis report from Market Analyst
            sentiment_report: Social media sentiment analysis
            news_report: News and current affairs analysis
            fundamentals_report: Company fundamentals analysis
            bear_argument: Previous bearish argument (empty for first round)
            past_memories: Previous trading memories and lessons learned

        Returns:
            Bullish investment thesis as a string
        """
        result = self.debate(
            company=company,
            date=date,
            market_report=market_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            bear_argument=bear_argument,
            past_memories=past_memories,
        )
        return result.bull_argument


class BearResearcher(dspy.Module):
    """Bear researcher agent that argues against buying a stock.

    This agent critically analyzes all available research data and presents
    compelling arguments for why the stock may be risky or overvalued.
    It can engage in iterative debate rounds with the Bull Researcher.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> researcher = BearResearcher()
        >>> argument = researcher(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     market_report="...",
        ...     sentiment_report="...",
        ...     news_report="...",
        ...     fundamentals_report="..."
        ... )
    """

    def __init__(self):
        """Initialize the bear researcher."""
        super().__init__()
        self.debate = dspy.ChainOfThought(BearResearcherSignature)

    def forward(
        self,
        company: str,
        date: str,
        market_report: str,
        sentiment_report: str,
        news_report: str,
        fundamentals_report: str,
        bull_argument: str = "",
        past_memories: str = "",
    ) -> str:
        """Generate bearish argument for a company.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            market_report: Technical analysis report from Market Analyst
            sentiment_report: Social media sentiment analysis
            news_report: News and current affairs analysis
            fundamentals_report: Company fundamentals analysis
            bull_argument: Previous bullish argument
            past_memories: Previous trading memories and lessons learned

        Returns:
            Bearish investment thesis as a string
        """
        result = self.debate(
            company=company,
            date=date,
            market_report=market_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            bull_argument=bull_argument,
            past_memories=past_memories,
        )
        return result.bear_argument


class ResearchManager(dspy.Module):
    """Research manager agent that synthesizes bull/bear debate into a decision.

    The Research Manager acts as a judge, weighing the arguments from both
    the Bull and Bear researchers to make an investment decision.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> manager = ResearchManager()
        >>> decision = manager(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     market_report="...",
        ...     sentiment_report="...",
        ...     news_report="...",
        ...     fundamentals_report="...",
        ...     bull_argument="...",
        ...     bear_argument="..."
        ... )
    """

    def __init__(self):
        """Initialize the research manager."""
        super().__init__()
        self.evaluate = dspy.ChainOfThought(ResearchManagerSignature)

    def forward(
        self,
        company: str,
        date: str,
        market_report: str,
        sentiment_report: str,
        news_report: str,
        fundamentals_report: str,
        bull_argument: str,
        bear_argument: str,
        debate_history: str = "",
    ) -> str:
        """Synthesize bull and bear arguments into an investment decision.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            market_report: Technical analysis report from Market Analyst
            sentiment_report: Social media sentiment analysis
            news_report: News and current affairs analysis
            fundamentals_report: Company fundamentals analysis
            bull_argument: Bullish argument from Bull Researcher
            bear_argument: Bearish argument from Bear Researcher
            debate_history: Complete history of bull/bear debate rounds

        Returns:
            Investment plan including direction, sizing, targets, and rationale
        """
        result = self.evaluate(
            company=company,
            date=date,
            market_report=market_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            bull_argument=bull_argument,
            bear_argument=bear_argument,
            debate_history=debate_history,
        )
        return result.investment_plan


class DebateRunner(dspy.Module):
    """Helper module to run iterative bull/bear debate rounds.

    This module orchestrates multiple rounds of debate between Bull and Bear
    researchers before the Research Manager makes a final decision.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> runner = DebateRunner(num_rounds=2)
        >>> bull_arg, bear_arg, history = runner(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     market_report="...",
        ...     sentiment_report="...",
        ...     news_report="...",
        ...     fundamentals_report="...",
        ...     past_memories="..."
        ... )
    """

    def __init__(self, num_rounds: int = 2):
        """Initialize the debate runner.

        Args:
            num_rounds: Number of debate rounds (default 2)
        """
        super().__init__()
        self.num_rounds = num_rounds
        self.bull_researcher = BullResearcher()
        self.bear_researcher = BearResearcher()

    def forward(
        self,
        company: str,
        date: str,
        market_report: str,
        sentiment_report: str,
        news_report: str,
        fundamentals_report: str,
        past_memories: str = "",
    ) -> tuple[str, str, str]:
        """Run iterative bull/bear debate.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            market_report: Technical analysis report
            sentiment_report: Sentiment analysis
            news_report: News analysis
            fundamentals_report: Fundamentals analysis
            past_memories: Previous trading memories

        Returns:
            Tuple of (final_bull_argument, final_bear_argument, debate_history)
        """
        history = ""
        bull_arg = ""
        bear_arg = ""

        for round_num in range(self.num_rounds):
            bull_arg = self.bull_researcher(
                company=company,
                date=date,
                market_report=market_report,
                sentiment_report=sentiment_report,
                news_report=news_report,
                fundamentals_report=fundamentals_report,
                bear_argument=bear_arg,
                past_memories=past_memories,
            )

            bear_arg = self.bear_researcher(
                company=company,
                date=date,
                market_report=market_report,
                sentiment_report=sentiment_report,
                news_report=news_report,
                fundamentals_report=fundamentals_report,
                bull_argument=bull_arg,
                past_memories=past_memories,
            )

            history += f"\n--- Round {round_num + 1} ---\n"
            history += f"BULL: {bull_arg}\n\n"
            history += f"BEAR: {bear_arg}\n"

        return bull_arg, bear_arg, history


__all__ = [
    "BullResearcher",
    "BearResearcher",
    "ResearchManager",
    "DebateRunner",
]

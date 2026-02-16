"""DSPy analyst agent modules.

This module implements the analyst agents using DSPy's ReAct pattern.
Each analyst can use tools to fetch market data and produce analysis reports.
"""

import dspy
from typing import Optional, List, Callable

from tradingagents_dspy.signatures import (
    MarketAnalysisSignature,
    SentimentAnalysisSignature,
    NewsAnalysisSignature,
    FundamentalsAnalysisSignature,
)

from .tools import (
    MARKET_TOOLS,
    SOCIAL_TOOLS,
    NEWS_TOOLS,
    FUNDAMENTALS_TOOLS,
)


class MarketAnalyst(dspy.Module):
    """Market analyst agent that analyzes stock price data and technical indicators.

    This agent fetches stock price history and technical indicators using tools,
    then produces a comprehensive market analysis report.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> analyst = MarketAnalyst()
        >>> report = analyst(company="AAPL", date="2024-06-19")
        >>> print(report)
    """

    def __init__(self, tools: Optional[List[Callable]] = None):
        """Initialize the market analyst.

        Args:
            tools: List of tool functions. If None, uses default MARKET_TOOLS.
        """
        super().__init__()
        self.tools = tools or MARKET_TOOLS
        # Use ReAct to allow the agent to call tools
        self.analyze = dspy.ReAct(
            MarketAnalysisSignature,
            tools=self.tools,
        )

    def forward(self, company: str, date: str) -> str:
        """Analyze market data for a company.

        Args:
            company: Stock ticker symbol (e.g., AAPL, NVDA)
            date: Analysis date in YYYY-MM-DD format

        Returns:
            Comprehensive market analysis report as a string
        """
        # The ReAct agent will use tools to fetch data and then generate the report
        result = self.analyze(company=company, date=date)
        return result.market_report


class SentimentAnalyst(dspy.Module):
    """Social media sentiment analyst agent.

    This agent fetches and analyzes social media sentiment, forum discussions,
    and public opinion about a company.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> analyst = SentimentAnalyst()
        >>> report = analyst(company="AAPL", date="2024-06-19")
        >>> print(report)
    """

    def __init__(self, tools: Optional[List[Callable]] = None):
        """Initialize the sentiment analyst.

        Args:
            tools: List of tool functions. If None, uses default SOCIAL_TOOLS.
        """
        super().__init__()
        self.tools = tools or SOCIAL_TOOLS
        self.analyze = dspy.ReAct(
            SentimentAnalysisSignature,
            tools=self.tools,
        )

    def forward(self, company: str, date: str) -> str:
        """Analyze social media sentiment for a company.

        Args:
            company: Stock ticker symbol (e.g., AAPL, NVDA)
            date: Analysis date in YYYY-MM-DD format

        Returns:
            Sentiment analysis report as a string
        """
        result = self.analyze(company=company, date=date)
        return result.sentiment_report


class NewsAnalyst(dspy.Module):
    """News analyst agent that examines current affairs and news impact.

    This agent fetches company-specific news, insider transactions, and global
    market news to assess potential impact on stock price.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> analyst = NewsAnalyst()
        >>> report = analyst(company="AAPL", date="2024-06-19")
        >>> print(report)
    """

    def __init__(self, tools: Optional[List[Callable]] = None):
        """Initialize the news analyst.

        Args:
            tools: List of tool functions. If None, uses default NEWS_TOOLS.
        """
        super().__init__()
        self.tools = tools or NEWS_TOOLS
        self.analyze = dspy.ReAct(
            NewsAnalysisSignature,
            tools=self.tools,
        )

    def forward(self, company: str, date: str) -> str:
        """Analyze news and current affairs for a company.

        Args:
            company: Stock ticker symbol (e.g., AAPL, NVDA)
            date: Analysis date in YYYY-MM-DD format

        Returns:
            News analysis report as a string
        """
        result = self.analyze(company=company, date=date)
        return result.news_report


class FundamentalsAnalyst(dspy.Module):
    """Fundamentals analyst agent that analyzes financial health.

    This agent fetches and analyzes financial statements, balance sheets,
    income statements, and key financial ratios to assess company fundamentals.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> analyst = FundamentalsAnalyst()
        >>> report = analyst(company="AAPL", date="2024-06-19")
        >>> print(report)
    """

    def __init__(self, tools: Optional[List[Callable]] = None):
        """Initialize the fundamentals analyst.

        Args:
            tools: List of tool functions. If None, uses default FUNDAMENTALS_TOOLS.
        """
        super().__init__()
        self.tools = tools or FUNDAMENTALS_TOOLS
        self.analyze = dspy.ReAct(
            FundamentalsAnalysisSignature,
            tools=self.tools,
        )

    def forward(self, company: str, date: str) -> str:
        """Analyze company fundamentals.

        Args:
            company: Stock ticker symbol (e.g., AAPL, NVDA)
            date: Analysis date in YYYY-MM-DD format

        Returns:
            Fundamentals analysis report as a string
        """
        result = self.analyze(company=company, date=date)
        return result.fundamentals_report


__all__ = [
    "MarketAnalyst",
    "SentimentAnalyst",
    "NewsAnalyst",
    "FundamentalsAnalyst",
]

"""DSPy agent modules for TradingAgents.

This package contains the DSPy-based agent implementations including:
- Analyst agents (Market, Sentiment, News, Fundamentals)
- Researcher agents (Bull, Bear, ResearchManager)
- Trader and Risk agents
- Tool wrappers for data fetching

Example:
    >>> from tradingagents_dspy.agents import MarketAnalyst, SentimentAnalyst
    >>> from tradingagents_dspy.config import configure_dspy
    >>>
    >>> configure_dspy()
    >>> market_analyst = MarketAnalyst()
    >>> report = market_analyst(company="AAPL", date="2024-06-19")
"""

from .analysts import (
    MarketAnalyst,
    SentimentAnalyst,
    NewsAnalyst,
    FundamentalsAnalyst,
)

from .tools import (
    get_stock_data,
    get_indicators,
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_news,
    get_insider_transactions,
    get_global_news,
    MARKET_TOOLS,
    SOCIAL_TOOLS,
    NEWS_TOOLS,
    FUNDAMENTALS_TOOLS,
)

__all__ = [
    # Analyst agents
    "MarketAnalyst",
    "SentimentAnalyst",
    "NewsAnalyst",
    "FundamentalsAnalyst",
    # Tools
    "get_stock_data",
    "get_indicators",
    "get_fundamentals",
    "get_balance_sheet",
    "get_cashflow",
    "get_income_statement",
    "get_news",
    "get_insider_transactions",
    "get_global_news",
    # Tool sets
    "MARKET_TOOLS",
    "SOCIAL_TOOLS",
    "NEWS_TOOLS",
    "FUNDAMENTALS_TOOLS",
]

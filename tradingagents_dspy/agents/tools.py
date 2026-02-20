"""DSPy-compatible tool wrappers for TradingAgents.

This module wraps the standalone data fetching functions for use with
DSPy's ReAct pattern. Tools are functions that agents can call
to fetch real-time market data.
"""

from typing import Any, Dict, List, Callable

# Import standalone data fetching functions
from tradingagents_dspy.data import (
    get_stock_data as _get_stock_data,
    get_indicators as _get_indicators,
    get_fundamentals as _get_fundamentals,
    get_balance_sheet as _get_balance_sheet,
    get_cashflow as _get_cashflow,
    get_income_statement as _get_income_statement,
    get_news as _get_news,
    get_insider_transactions as _get_insider_transactions,
    get_global_news as _get_global_news,
)


def get_stock_data(ticker: str) -> str:
    """Fetch stock price and volume data for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing recent OHLCV (Open, High, Low, Close, Volume) data
    """
    return _get_stock_data(ticker)


def get_indicators(ticker: str) -> str:
    """Fetch technical indicators for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing technical indicators (MACD, RSI, moving averages, etc.)
    """
    return _get_indicators(ticker)


def get_fundamentals(ticker: str) -> str:
    """Fetch company fundamentals and profile information.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing company profile, key metrics, and financial ratios
    """
    return _get_fundamentals(ticker)


def get_balance_sheet(ticker: str) -> str:
    """Fetch balance sheet data.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing balance sheet data
    """
    return _get_balance_sheet(ticker)


def get_cashflow(ticker: str) -> str:
    """Fetch cash flow data.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing cash flow data
    """
    return _get_cashflow(ticker)


def get_income_statement(ticker: str) -> str:
    """Fetch income statement data.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing income statement data
    """
    return _get_income_statement(ticker)


def get_news(ticker: str) -> str:
    """Fetch recent news for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing recent news headlines
    """
    return _get_news(ticker)


def get_insider_transactions(ticker: str) -> str:
    """Fetch insider transaction data.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing insider transaction data
    """
    return _get_insider_transactions(ticker)


def get_global_news() -> str:
    """Fetch recent global market news.

    Returns:
        String containing global market news
    """
    return _get_global_news()


# Define tool sets for different analyst types
MARKET_TOOLS = [get_stock_data, get_indicators]
SOCIAL_TOOLS = []
NEWS_TOOLS = [get_news, get_global_news, get_insider_transactions]
FUNDAMENTALS_TOOLS = [
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
]


__all__ = [
    "get_stock_data",
    "get_indicators",
    "get_fundamentals",
    "get_balance_sheet",
    "get_cashflow",
    "get_income_statement",
    "get_news",
    "get_insider_transactions",
    "get_global_news",
    "MARKET_TOOLS",
    "SOCIAL_TOOLS",
    "NEWS_TOOLS",
    "FUNDAMENTALS_TOOLS",
]

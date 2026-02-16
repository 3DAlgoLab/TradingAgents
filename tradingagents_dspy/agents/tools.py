"""DSPy-compatible tool wrappers for TradingAgents.

This module wraps the existing tool functions from tradingagents to make them
compatible with DSPy's ReAct pattern. Tools are functions that agents can call
to fetch real-time market data.
"""

from typing import Any, Dict
from datetime import datetime, date

# Import existing tool functions from tradingagents
from tradingagents.agents.utils.agent_utils import (
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
    try:
        result = _get_stock_data(ticker)
        if isinstance(result, dict):
            # Format as readable string
            lines = [f"Stock Data for {ticker}:"]
            for key, value in result.items():
                lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"


def get_indicators(ticker: str) -> str:
    """Fetch technical indicators for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing technical indicators (MACD, RSI, moving averages, etc.)
    """
    try:
        result = _get_indicators(ticker)
        if isinstance(result, dict):
            lines = [f"Technical Indicators for {ticker}:"]
            for key, value in result.items():
                lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching indicators for {ticker}: {str(e)}"


def get_fundamentals(ticker: str) -> str:
    """Fetch company fundamentals and profile information.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing company profile, key metrics, and financial ratios
    """
    try:
        result = _get_fundamentals(ticker)
        if isinstance(result, dict):
            lines = [f"Fundamentals for {ticker}:"]
            for key, value in result.items():
                lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"


def get_balance_sheet(ticker: str) -> str:
    """Fetch balance sheet data for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing balance sheet information (assets, liabilities, equity)
    """
    try:
        result = _get_balance_sheet(ticker)
        if isinstance(result, dict):
            lines = [f"Balance Sheet for {ticker}:"]
            for key, value in result.items():
                lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching balance sheet for {ticker}: {str(e)}"


def get_cashflow(ticker: str) -> str:
    """Fetch cash flow statement for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing cash flow data (operating, investing, financing)
    """
    try:
        result = _get_cashflow(ticker)
        if isinstance(result, dict):
            lines = [f"Cash Flow for {ticker}:"]
            for key, value in result.items():
                lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching cash flow for {ticker}: {str(e)}"


def get_income_statement(ticker: str) -> str:
    """Fetch income statement for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing income statement data (revenue, expenses, profit)
    """
    try:
        result = _get_income_statement(ticker)
        if isinstance(result, dict):
            lines = [f"Income Statement for {ticker}:"]
            for key, value in result.items():
                lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching income statement for {ticker}: {str(e)}"


def get_news(ticker: str) -> str:
    """Fetch recent news articles for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing recent news headlines and summaries
    """
    try:
        result = _get_news(ticker)
        if isinstance(result, list):
            lines = [f"Recent News for {ticker}:"]
            for item in result:
                if isinstance(item, dict):
                    title = item.get("title", "No title")
                    lines.append(f"  - {title}")
                else:
                    lines.append(f"  - {item}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"


def get_insider_transactions(ticker: str) -> str:
    """Fetch insider trading transactions for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)

    Returns:
        String containing recent insider buying/selling activity
    """
    try:
        result = _get_insider_transactions(ticker)
        if isinstance(result, list):
            lines = [f"Insider Transactions for {ticker}:"]
            for item in result:
                if isinstance(item, dict):
                    lines.append(f"  {item}")
                else:
                    lines.append(f"  - {item}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching insider transactions for {ticker}: {str(e)}"


def get_global_news() -> str:
    """Fetch global market news and current affairs.

    Returns:
        String containing global market news that may impact stocks
    """
    try:
        result = _get_global_news()
        if isinstance(result, list):
            lines = ["Global Market News:"]
            for item in result:
                if isinstance(item, dict):
                    title = item.get("title", "No title")
                    lines.append(f"  - {title}")
                else:
                    lines.append(f"  - {item}")
            return "\n".join(lines)
        return str(result)
    except Exception as e:
        return f"Error fetching global news: {str(e)}"


# Tool sets organized by analyst type
MARKET_TOOLS = [get_stock_data, get_indicators]
SOCIAL_TOOLS = [get_news]
NEWS_TOOLS = [get_news, get_global_news, get_insider_transactions]
FUNDAMENTALS_TOOLS = [
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
]

__all__ = [
    # Individual tools
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

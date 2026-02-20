"""Standalone data fetching tools for TradingAgents DSPy.

This module provides independent data fetching functions using yfinance,
without depending on the main tradingagents package.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def get_stock_data(ticker: str, period: str = "1y") -> str:
    """Fetch stock price and volume data for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA)
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        String containing recent OHLCV (Open, High, Low, Close, Volume) data
    """
    try:
        stock = yf.Ticker(ticker.upper())
        df = stock.history(period=period)

        if df.empty:
            return f"No data found for {ticker}"

        # Format the data
        lines = [f"Stock Data for {ticker.upper()} (last {period}):"]
        lines.append("-" * 50)

        # Show last 30 days
        recent = df.tail(30)
        for idx, row in recent.iterrows():
            date_str = idx.strftime("%Y-%m-%d")
            lines.append(
                f"{date_str}: O:{row['Open']:.2f} H:{row['High']:.2f} "
                f"L:{row['Low']:.2f} C:{row['Close']:.2f} V:{int(row['Volume']):,}"
            )

        # Add current price info
        if len(df) > 0:
            latest = df.iloc[-1]
            lines.append("-" * 50)
            lines.append(
                f"Latest: ${latest['Close']:.2f} (Volume: {int(latest['Volume']):,})"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"


def get_indicators(ticker: str, period: str = "6mo") -> str:
    """Fetch technical indicators for a company.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA)
        period: Data period for calculation

    Returns:
        String containing technical indicators
    """
    try:
        stock = yf.Ticker(ticker.upper())
        df = stock.history(period=period)

        if df.empty or len(df) < 50:
            return f"Insufficient data for {ticker} to calculate indicators"

        lines = [f"Technical Indicators for {ticker.upper()}:"]
        lines.append("-" * 50)

        close = df["Close"]

        # Simple Moving Averages
        sma_20 = close.rolling(window=20).mean().iloc[-1]
        sma_50 = close.rolling(window=50).mean().iloc[-1]
        sma_200 = (
            close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
        )

        lines.append(f"SMA 20: ${sma_20:.2f}")
        lines.append(f"SMA 50: ${sma_50:.2f}")
        if sma_200:
            lines.append(f"SMA 200: ${sma_200:.2f}")

        # Exponential Moving Averages
        ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        lines.append(f"EMA 12: ${ema_12:.2f}")
        lines.append(f"EMA 26: ${ema_26:.2f}")

        # MACD
        macd_line = ema_12 - ema_26
        signal_line = macd_line  # Simplified
        lines.append(f"MACD: {macd_line:.2f}")

        # RSI (14 periods)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        lines.append(f"RSI(14): {rsi.iloc[-1]:.1f}")

        # Current price
        lines.append("-" * 50)
        lines.append(f"Current Price: ${close.iloc[-1]:.2f}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching indicators for {ticker}: {str(e)}"


def get_fundamentals(ticker: str) -> str:
    """Fetch company fundamentals and profile information.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA)

    Returns:
        String containing company profile and key metrics
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        lines = [f"Fundamentals for {ticker.upper()}:"]
        lines.append("-" * 50)

        # Company info
        if "longName" in info:
            lines.append(f"Company: {info.get('longName', 'N/A')}")
        if "sector" in info:
            lines.append(f"Sector: {info.get('sector', 'N/A')}")
        if "industry" in info:
            lines.append(f"Industry: {info.get('industry', 'N/A')}")

        lines.append("-" * 50)

        # Key metrics
        metrics = [
            ("currentPrice", "Current Price"),
            ("marketCap", "Market Cap"),
            ("peRatio", "P/E Ratio"),
            ("forwardPE", "Forward P/E"),
            ("dividendYield", "Dividend Yield"),
            ("beta", "Beta"),
            ("52WeekChange", "52W Change"),
            ("targetMeanPrice", "Target Price"),
            ("recommendationKey", "Recommendation"),
        ]

        for key, label in metrics:
            if key in info and info[key] is not None:
                value = info[key]
                if key == "marketCap":
                    value = (
                        f"${value / 1e9:.2f}B"
                        if value > 1e9
                        else f"${value / 1e6:.2f}M"
                    )
                elif key == "dividendYield":
                    value = f"{value * 100:.2f}%"
                elif key == "52WeekChange":
                    value = f"{value * 100:.2f}%"
                else:
                    value = str(value)
                lines.append(f"{label}: {value}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"


def get_balance_sheet(ticker: str) -> str:
    """Fetch balance sheet data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        String containing balance sheet data
    """
    try:
        stock = yf.Ticker(ticker.upper())
        bs = stock.balance_sheet

        if bs.empty:
            return f"No balance sheet data for {ticker}"

        lines = [f"Balance Sheet for {ticker.upper()}:"]
        lines.append("-" * 50)

        # Get latest quarter
        latest_date = bs.columns[0]
        latest = bs[latest_date]

        items = [
            ("Total Assets", "totalAssets"),
            ("Total Liabilities", "totalLiab"),
            ("Total Debt", "totalDebt"),
            ("Cash", "cash"),
            ("Stockholders Equity", "stockholdersEquity"),
        ]

        for label, key in items:
            if key in latest.index and pd.notna(latest[key]):
                value = latest[key]
                lines.append(f"{label}: ${value / 1e9:.2f}B")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching balance sheet for {ticker}: {str(e)}"


def get_cashflow(ticker: str) -> str:
    """Fetch cash flow data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        String containing cash flow data
    """
    try:
        stock = yf.Ticker(ticker.upper())
        cf = stock.cashflow

        if cf.empty:
            return f"No cash flow data for {ticker}"

        lines = [f"Cash Flow for {ticker.upper()}:"]
        lines.append("-" * 50)

        latest_date = cf.columns[0]
        latest = cf[latest_date]

        items = [
            ("Operating Cash Flow", "operatingCashflow"),
            ("Free Cash Flow", "freeCashflow"),
            ("Capital Expenditures", "capex"),
        ]

        for label, key in items:
            if key in latest.index and pd.notna(latest[key]):
                value = latest[key]
                lines.append(f"{label}: ${value / 1e9:.2f}B")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching cash flow for {ticker}: {str(e)}"


def get_income_statement(ticker: str) -> str:
    """Fetch income statement data.

    Args:
        ticker: Stock ticker symbol

    Returns:
        String containing income statement data
    """
    try:
        stock = yf.Ticker(ticker.upper())
        is_df = stock.income_statement

        if is_df.empty:
            return f"No income statement data for {ticker}"

        lines = [f"Income Statement for {ticker.upper()}:"]
        lines.append("-" * 50)

        latest_date = is_df.columns[0]
        latest = is_df[latest_date]

        items = [
            ("Total Revenue", "totalRevenue"),
            ("Operating Income", "operatingIncome"),
            ("Net Income", "netIncome"),
            ("EPS", "epsdiluted"),
        ]

        for label, key in items:
            if key in latest.index and pd.notna(latest[key]):
                value = latest[key]
                if key == "epsdiluted":
                    lines.append(f"{label}: ${value:.2f}")
                else:
                    lines.append(f"{label}: ${value / 1e9:.2f}B")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching income statement for {ticker}: {str(e)}"


def get_news(ticker: str, limit: int = 5) -> str:
    """Fetch recent news for a company.

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of news items

    Returns:
        String containing recent news headlines
    """
    try:
        stock = yf.Ticker(ticker.upper())
        news = stock.news

        if not news:
            return f"No recent news for {ticker}"

        lines = [f"Recent News for {ticker.upper()}:"]
        lines.append("-" * 50)

        for i, item in enumerate(news[:limit]):
            title = item.get("title", "N/A")
            publisher = item.get("publisher", "N/A")
            lines.append(f"{i + 1}. {title}")
            lines.append(f"   Source: {publisher}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"


def get_insider_transactions(ticker: str) -> str:
    """Fetch insider transactions.

    Args:
        ticker: Stock ticker symbol

    Returns:
        String containing insider transaction data
    """
    try:
        stock = yf.Ticker(ticker.upper())
        insider = stock.insider_transactions

        if insider is None or insider.empty:
            return f"No insider transaction data for {ticker}"

        lines = [f"Insider Transactions for {ticker.upper()}:"]
        lines.append("-" * 50)

        recent = insider.tail(5)
        for _, row in recent.iterrows():
            date = row.get("Date", "N/A")
            insider = row.get("Insider", "N/A")
            transaction = row.get("Transaction", "N/A")
            shares = row.get("Shares", 0)
            lines.append(f"{date}: {insider} - {transaction} ({int(shares):,} shares)")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching insider transactions for {ticker}: {str(e)}"


def get_global_news() -> str:
    """Fetch recent global market news.

    Returns:
        String containing global market news
    """
    try:
        # Get market indices news
        indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, Nasdaq
        lines = ["Global Market News:"]
        lines.append("-" * 50)

        for idx in indices:
            ticker = yf.Ticker(idx)
            info = ticker.info
            name = info.get("shortName", idx)
            price = info.get("currentPrice", 0)
            change = info.get("regularMarketChange", 0)
            pct_change = info.get("regularMarketChangePercent", 0)

            lines.append(f"{name}: ${price:.2f} ({change:+.2f} {pct_change:+.2f}%)")

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching global news: {str(e)}"


# Import pandas for data handling
import pandas as pd

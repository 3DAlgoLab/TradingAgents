"""DSPy signatures for TradingAgents.

This module defines all the input/output signatures used by the DSPy-based
TradingAgents implementation. Signatures declaratively specify what each
agent expects as input and produces as output.
"""

import dspy


class MarketAnalysisSignature(dspy.Signature):
    """Analyze market data and technical indicators for a company.

    This signature is used by the Market Analyst to examine stock price data,
    trading volume, and technical indicators (MACD, RSI, moving averages, etc.)
    to produce a comprehensive market analysis report.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol (e.g., AAPL, NVDA, TSLA)")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    market_report: str = dspy.OutputField(
        desc="Comprehensive market analysis including price trends, volume analysis, "
        "technical indicators (MACD, RSI, moving averages), support/resistance levels, "
        "and short-term price outlook"
    )


class SentimentAnalysisSignature(dspy.Signature):
    """Analyze social media sentiment for a company.

    This signature is used by the Social Media Analyst to examine sentiment
    from social media platforms, forums, and public discussions about a company.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol (e.g., AAPL, NVDA, TSLA)")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    sentiment_report: str = dspy.OutputField(
        desc="Social media sentiment analysis including overall sentiment score, "
        "key topics discussed, influencer opinions, retail investor sentiment, "
        "and potential sentiment-driven price impacts"
    )


class NewsAnalysisSignature(dspy.Signature):
    """Analyze news and current affairs for a company.

    This signature is used by the News Analyst to examine recent news articles,
    press releases, insider transactions, and global market news that may impact
    the company's stock price.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol (e.g., AAPL, NVDA, TSLA)")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    news_report: str = dspy.OutputField(
        desc="News analysis including recent company-specific news, insider transactions, "
        "global market news impact, earnings announcements, product launches, "
        "regulatory changes, and analyst rating updates"
    )


class FundamentalsAnalysisSignature(dspy.Signature):
    """Analyze company fundamentals and financial statements.

    This signature is used by the Fundamentals Analyst to examine financial
    statements, balance sheets, income statements, cash flow, and key financial
    ratios to assess the company's financial health.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol (e.g., AAPL, NVDA, TSLA)")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    fundamentals_report: str = dspy.OutputField(
        desc="Fundamental analysis including revenue growth, profit margins, "
        "balance sheet strength, cash flow health, P/E ratio, debt levels, "
        "competitive position, and intrinsic value assessment"
    )


__all__ = [
    "MarketAnalysisSignature",
    "SentimentAnalysisSignature",
    "NewsAnalysisSignature",
    "FundamentalsAnalysisSignature",
]

"""DSPy signatures for TradingAgents.

This package contains all the signature definitions used by the DSPy-based
TradingAgents implementation. Signatures declaratively specify the input/output
contracts for each agent in the trading workflow.

The signatures are organized into three categories:
- Analyst Signatures: Market, sentiment, news, and fundamentals analysis
- Researcher Signatures: Bull/bear debate and investment decisions
- Trader Signatures: Trading plans, risk assessment, and final decisions

Example:
    >>> from tradingagents_dspy.signatures import MarketAnalysisSignature
    >>> from tradingagents_dspy.config import configure_dspy
    >>> import dspy
    >>>
    >>> configure_dspy()
    >>> predictor = dspy.Predict(MarketAnalysisSignature)
    >>> result = predictor(company="AAPL", date="2024-06-19")
    >>> print(result.market_report)
"""

from .analyst_signatures import (
    MarketAnalysisSignature,
    SentimentAnalysisSignature,
    NewsAnalysisSignature,
    FundamentalsAnalysisSignature,
)

from .researcher_signatures import (
    BullResearcherSignature,
    BearResearcherSignature,
    ResearchManagerSignature,
)

from .trader_signatures import (
    TraderSignature,
    AggressiveRiskSignature,
    ConservativeRiskSignature,
    NeutralRiskSignature,
    RiskManagerSignature,
    PortfolioManagerSignature,
)

__all__ = [
    # Analyst signatures
    "MarketAnalysisSignature",
    "SentimentAnalysisSignature",
    "NewsAnalysisSignature",
    "FundamentalsAnalysisSignature",
    # Researcher signatures
    "BullResearcherSignature",
    "BearResearcherSignature",
    "ResearchManagerSignature",
    # Trader signatures
    "TraderSignature",
    "AggressiveRiskSignature",
    "ConservativeRiskSignature",
    "NeutralRiskSignature",
    "RiskManagerSignature",
    "PortfolioManagerSignature",
]

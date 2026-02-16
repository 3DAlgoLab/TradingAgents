"""DSPy signatures for researcher agents.

This module defines signatures for the bull/bear researcher debate system
and the research manager who makes investment decisions based on the debate.
"""

import dspy


class BullResearcherSignature(dspy.Signature):
    """Generate bullish arguments for investing in a company.

    The Bull Researcher analyzes all available research data and presents
    compelling arguments for why the stock is a good investment opportunity.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    market_report: str = dspy.InputField(
        desc="Technical analysis report from Market Analyst"
    )
    sentiment_report: str = dspy.InputField(
        desc="Social media sentiment analysis report"
    )
    news_report: str = dspy.InputField(desc="News and current affairs analysis report")
    fundamentals_report: str = dspy.InputField(
        desc="Company fundamentals and financial analysis report"
    )
    bear_argument: str = dspy.InputField(
        desc="Previous bearish argument from Bear Researcher (empty string for first round)",
        default="",
    )
    past_memories: str = dspy.InputField(
        desc="Previous trading memories and lessons learned (optional)", default=""
    )
    bull_argument: str = dspy.OutputField(
        desc="Bullish investment thesis including growth catalysts, competitive advantages, "
        "undervaluation evidence, and rebuttals to bearish concerns"
    )


class BearResearcherSignature(dspy.Signature):
    """Generate bearish arguments against investing in a company.

    The Bear Researcher critically analyzes all available research data and
    presents compelling arguments for why the stock may be risky or overvalued.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    market_report: str = dspy.InputField(
        desc="Technical analysis report from Market Analyst"
    )
    sentiment_report: str = dspy.InputField(
        desc="Social media sentiment analysis report"
    )
    news_report: str = dspy.InputField(desc="News and current affairs analysis report")
    fundamentals_report: str = dspy.InputField(
        desc="Company fundamentals and financial analysis report"
    )
    bull_argument: str = dspy.InputField(
        desc="Previous bullish argument from Bull Researcher"
    )
    past_memories: str = dspy.InputField(
        desc="Previous trading memories and lessons learned (optional)", default=""
    )
    bear_argument: str = dspy.OutputField(
        desc="Bearish investment thesis including risk factors, overvaluation evidence, "
        "competitive threats, and counter-arguments to bullish claims"
    )


class ResearchManagerSignature(dspy.Signature):
    """Synthesize bull and bear arguments into an investment decision.

    The Research Manager acts as a judge, weighing the arguments from both
    the Bull and Bear researchers to make a final investment decision.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    market_report: str = dspy.InputField(
        desc="Technical analysis report from Market Analyst"
    )
    sentiment_report: str = dspy.InputField(
        desc="Social media sentiment analysis report"
    )
    news_report: str = dspy.InputField(desc="News and current affairs analysis report")
    fundamentals_report: str = dspy.InputField(
        desc="Company fundamentals and financial analysis report"
    )
    bull_argument: str = dspy.InputField(
        desc="Complete bullish argument from Bull Researcher"
    )
    bear_argument: str = dspy.InputField(
        desc="Complete bearish argument from Bear Researcher"
    )
    debate_history: str = dspy.InputField(
        desc="Complete history of the bull/bear debate rounds", default=""
    )
    investment_plan: str = dspy.OutputField(
        desc="Comprehensive investment decision including position direction (BUY/SELL/HOLD), "
        "position sizing rationale, entry/exit price targets, time horizon, "
        "key catalysts to watch, and risk factors"
    )


__all__ = [
    "BullResearcherSignature",
    "BearResearcherSignature",
    "ResearchManagerSignature",
]

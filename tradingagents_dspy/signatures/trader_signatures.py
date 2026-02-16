"""DSPy signatures for trader and risk management agents.

This module defines signatures for the trader agent, risk management debate,
and the final portfolio manager who makes the ultimate trading decision.
"""

import dspy


class TraderSignature(dspy.Signature):
    """Generate a detailed investment plan based on research analysis.

    The Trader takes the research manager's decision and creates a specific,
    actionable trading plan with entry/exit points and position sizing.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Trading date in YYYY-MM-DD format")
    investment_decision: str = dspy.InputField(
        desc="Investment decision from Research Manager including bull/bear analysis"
    )
    past_memories: str = dspy.InputField(
        desc="Previous trading memories and lessons learned (optional)", default=""
    )
    trader_investment_plan: str = dspy.OutputField(
        desc="Detailed trading plan including specific action (BUY/SELL/HOLD), "
        "target entry price, stop-loss level, take-profit targets, "
        "position size recommendation, and expected holding period"
    )


class AggressiveRiskSignature(dspy.Signature):
    """Assess risks from an aggressive/agrowth-oriented perspective.

    The Aggressive Risk Analyst focuses on growth opportunities and is willing
    to accept higher risk for potentially higher returns.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    trader_investment_plan: str = dspy.InputField(
        desc="Trading plan from the Trader agent"
    )
    previous_conservative_argument: str = dspy.InputField(
        desc="Previous argument from Conservative Risk Analyst (empty for first round)",
        default="",
    )
    previous_neutral_argument: str = dspy.InputField(
        desc="Previous argument from Neutral Risk Analyst (empty for first round)",
        default="",
    )
    aggressive_assessment: str = dspy.OutputField(
        desc="Aggressive risk assessment focusing on growth potential, "
        "opportunity cost of not taking the trade, upside scenarios, "
        "and justification for higher risk tolerance"
    )


class ConservativeRiskSignature(dspy.Signature):
    """Assess risks from a conservative/capital-preservation perspective.

    The Conservative Risk Analyst prioritizes capital preservation and focuses
    on downside risks and worst-case scenarios.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    trader_investment_plan: str = dspy.InputField(
        desc="Trading plan from the Trader agent"
    )
    previous_aggressive_argument: str = dspy.InputField(
        desc="Previous argument from Aggressive Risk Analyst"
    )
    previous_neutral_argument: str = dspy.InputField(
        desc="Previous argument from Neutral Risk Analyst (empty for first round)",
        default="",
    )
    conservative_assessment: str = dspy.OutputField(
        desc="Conservative risk assessment focusing on downside protection, "
        "maximum loss scenarios, market volatility concerns, liquidity risks, "
        "and arguments for caution or position size reduction"
    )


class NeutralRiskSignature(dspy.Signature):
    """Assess risks from a balanced, neutral perspective.

    The Neutral Risk Analyst provides a balanced view, weighing both upside
    potential and downside risks to find the optimal risk/reward balance.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    trader_investment_plan: str = dspy.InputField(
        desc="Trading plan from the Trader agent"
    )
    previous_aggressive_argument: str = dspy.InputField(
        desc="Previous argument from Aggressive Risk Analyst"
    )
    previous_conservative_argument: str = dspy.InputField(
        desc="Previous argument from Conservative Risk Analyst"
    )
    neutral_assessment: str = dspy.OutputField(
        desc="Balanced risk assessment synthesizing both aggressive and conservative views, "
        "identifying key risk factors to monitor, suggesting risk mitigation strategies, "
        "and proposing optimal position sizing based on risk/reward ratio"
    )


class RiskManagerSignature(dspy.Signature):
    """Synthesize risk assessments into a final risk evaluation.

    The Risk Manager acts as a judge over the risk debate, weighing arguments
    from aggressive, conservative, and neutral analysts to make a final
    risk assessment.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Analysis date in YYYY-MM-DD format")
    trader_investment_plan: str = dspy.InputField(
        desc="Trading plan from the Trader agent"
    )
    aggressive_assessment: str = dspy.InputField(
        desc="Risk assessment from Aggressive Risk Analyst"
    )
    conservative_assessment: str = dspy.InputField(
        desc="Risk assessment from Conservative Risk Analyst"
    )
    neutral_assessment: str = dspy.InputField(
        desc="Risk assessment from Neutral Risk Analyst"
    )
    risk_debate_history: str = dspy.InputField(
        desc="Complete history of the risk debate rounds", default=""
    )
    risk_evaluation: str = dspy.OutputField(
        desc="Comprehensive risk evaluation including overall risk level (LOW/MEDIUM/HIGH), "
        "recommended position size adjustment, maximum acceptable loss, "
        "key risk monitoring points, and conditions for trade modification or exit"
    )


class PortfolioManagerSignature(dspy.Signature):
    """Make the final trading decision based on all analysis.

    The Portfolio Manager synthesizes the investment plan from the research team
    and the risk evaluation from the risk management team to make the ultimate
    BUY, SELL, or HOLD decision.
    """

    company: str = dspy.InputField(desc="Stock ticker symbol being analyzed")
    date: str = dspy.InputField(desc="Trading date in YYYY-MM-DD format")
    trader_investment_plan: str = dspy.InputField(
        desc="Trading plan from the Trader agent"
    )
    risk_evaluation: str = dspy.InputField(desc="Risk evaluation from Risk Manager")
    past_memories: str = dspy.InputField(
        desc="Previous trading memories and lessons learned (optional)", default=""
    )
    final_trade_decision: str = dspy.OutputField(
        desc="Final trading decision in format: 'ACTION - RATIONALE' where ACTION is "
        "BUY, SELL, or HOLD. Include position sizing, specific price levels, "
        "stop-loss, take-profit targets, and brief justification for the decision."
    )


__all__ = [
    "TraderSignature",
    "AggressiveRiskSignature",
    "ConservativeRiskSignature",
    "NeutralRiskSignature",
    "RiskManagerSignature",
    "PortfolioManagerSignature",
]

"""DSPy risk management agent modules.

This module implements the risk debate system with aggressive, conservative,
and neutral perspectives, along with the Risk Manager who synthesizes
the risk debate into a final evaluation.
"""

import dspy

from tradingagents_dspy.signatures import (
    AggressiveRiskSignature,
    ConservativeRiskSignature,
    NeutralRiskSignature,
    RiskManagerSignature,
)


class AggressiveRisk(dspy.Module):
    """Aggressive risk analyst focused on growth opportunities.

    This agent assesses risks from an aggressive growth-oriented perspective,
    willing to accept higher risk for potentially higher returns.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> risk = AggressiveRisk()
        >>> assessment = risk(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     trader_investment_plan="..."
        ... )
    """

    def __init__(self):
        """Initialize the aggressive risk analyst."""
        super().__init__()
        self.assess = dspy.ChainOfThought(AggressiveRiskSignature)

    def forward(
        self,
        company: str,
        date: str,
        trader_investment_plan: str,
        previous_conservative_argument: str = "",
        previous_neutral_argument: str = "",
    ) -> str:
        """Generate aggressive risk assessment.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            trader_investment_plan: Trading plan from Trader agent
            previous_conservative_argument: Previous argument from Conservative Risk
            previous_neutral_argument: Previous argument from Neutral Risk

        Returns:
            Aggressive risk assessment focusing on growth potential
        """
        result = self.assess(
            company=company,
            date=date,
            trader_investment_plan=trader_investment_plan,
            previous_conservative_argument=previous_conservative_argument,
            previous_neutral_argument=previous_neutral_argument,
        )
        return result.aggressive_assessment


class ConservativeRisk(dspy.Module):
    """Conservative risk analyst focused on capital preservation.

    This agent assesses risks from a conservative perspective, prioritizing
    downside protection and capital preservation.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> risk = ConservativeRisk()
        >>> assessment = risk(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     trader_investment_plan="..."
        ... )
    """

    def __init__(self):
        """Initialize the conservative risk analyst."""
        super().__init__()
        self.assess = dspy.ChainOfThought(ConservativeRiskSignature)

    def forward(
        self,
        company: str,
        date: str,
        trader_investment_plan: str,
        previous_aggressive_argument: str = "",
        previous_neutral_argument: str = "",
    ) -> str:
        """Generate conservative risk assessment.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            trader_investment_plan: Trading plan from Trader agent
            previous_aggressive_argument: Previous argument from Aggressive Risk
            previous_neutral_argument: Previous argument from Neutral Risk

        Returns:
            Conservative risk assessment focusing on downside protection
        """
        result = self.assess(
            company=company,
            date=date,
            trader_investment_plan=trader_investment_plan,
            previous_aggressive_argument=previous_aggressive_argument,
            previous_neutral_argument=previous_neutral_argument,
        )
        return result.conservative_assessment


class NeutralRisk(dspy.Module):
    """Neutral risk analyst providing balanced perspective.

    This agent provides a balanced view, weighing both upside potential
    and downside risks to find the optimal risk/reward balance.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> risk = NeutralRisk()
        >>> assessment = risk(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     trader_investment_plan="..."
        ... )
    """

    def __init__(self):
        """Initialize the neutral risk analyst."""
        super().__init__()
        self.assess = dspy.ChainOfThought(NeutralRiskSignature)

    def forward(
        self,
        company: str,
        date: str,
        trader_investment_plan: str,
        previous_aggressive_argument: str = "",
        previous_conservative_argument: str = "",
    ) -> str:
        """Generate neutral risk assessment.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            trader_investment_plan: Trading plan from Trader agent
            previous_aggressive_argument: Previous argument from Aggressive Risk
            previous_conservative_argument: Previous argument from Conservative Risk

        Returns:
            Balanced risk assessment with optimal risk/reward analysis
        """
        result = self.assess(
            company=company,
            date=date,
            trader_investment_plan=trader_investment_plan,
            previous_aggressive_argument=previous_aggressive_argument,
            previous_conservative_argument=previous_conservative_argument,
        )
        return result.neutral_assessment


class RiskManager(dspy.Module):
    """Risk manager that synthesizes risk assessments into final evaluation.

    The Risk Manager acts as a judge over the risk debate, weighing arguments
    from aggressive, conservative, and neutral analysts to make a final
    risk assessment.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> manager = RiskManager()
        >>> evaluation = manager(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     trader_investment_plan="...",
        ...     aggressive_assessment="...",
        ...     conservative_assessment="...",
        ...     neutral_assessment="..."
        ... )
    """

    def __init__(self):
        """Initialize the risk manager."""
        super().__init__()
        self.evaluate = dspy.ChainOfThought(RiskManagerSignature)

    def forward(
        self,
        company: str,
        date: str,
        trader_investment_plan: str,
        aggressive_assessment: str,
        conservative_assessment: str,
        neutral_assessment: str,
        risk_debate_history: str = "",
    ) -> str:
        """Synthesize risk assessments into final evaluation.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            trader_investment_plan: Trading plan from Trader agent
            aggressive_assessment: Risk assessment from Aggressive Risk Analyst
            conservative_assessment: Risk assessment from Conservative Risk Analyst
            neutral_assessment: Risk assessment from Neutral Risk Analyst
            risk_debate_history: Complete history of risk debate rounds

        Returns:
            Comprehensive risk evaluation with position adjustments and monitoring points
        """
        result = self.evaluate(
            company=company,
            date=date,
            trader_investment_plan=trader_investment_plan,
            aggressive_assessment=aggressive_assessment,
            conservative_assessment=conservative_assessment,
            neutral_assessment=neutral_assessment,
            risk_debate_history=risk_debate_history,
        )
        return result.risk_evaluation


class RiskDebateRunner(dspy.Module):
    """Helper module to run iterative risk debate rounds.

    This module orchestrates multiple rounds of debate between aggressive,
    conservative, and neutral risk analysts before the Risk Manager
    makes a final evaluation.

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> configure_dspy()
        >>> runner = RiskDebateRunner(num_rounds=2)
        >>> agg, cons, neut, history = runner(
        ...     company="AAPL",
        ...     date="2024-06-19",
        ...     trader_investment_plan="..."
        ... )
    """

    def __init__(self, num_rounds: int = 2):
        """Initialize the risk debate runner.

        Args:
            num_rounds: Number of debate rounds (default 2)
        """
        super().__init__()
        self.num_rounds = num_rounds
        self.aggressive_risk = AggressiveRisk()
        self.conservative_risk = ConservativeRisk()
        self.neutral_risk = NeutralRisk()

    def forward(
        self,
        company: str,
        date: str,
        trader_investment_plan: str,
    ) -> tuple[str, str, str, str]:
        """Run iterative risk debate.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            trader_investment_plan: Trading plan from Trader agent

        Returns:
            Tuple of (aggressive_assessment, conservative_assessment,
                     neutral_assessment, debate_history)
        """
        history = ""
        agg_arg = ""
        cons_arg = ""
        neut_arg = ""

        for round_num in range(self.num_rounds):
            agg_arg = self.aggressive_risk(
                company=company,
                date=date,
                trader_investment_plan=trader_investment_plan,
                previous_conservative_argument=cons_arg,
                previous_neutral_argument=neut_arg,
            )

            cons_arg = self.conservative_risk(
                company=company,
                date=date,
                trader_investment_plan=trader_investment_plan,
                previous_aggressive_argument=agg_arg,
                previous_neutral_argument=neut_arg,
            )

            neut_arg = self.neutral_risk(
                company=company,
                date=date,
                trader_investment_plan=trader_investment_plan,
                previous_aggressive_argument=agg_arg,
                previous_conservative_argument=cons_arg,
            )

            history += f"\n--- Round {round_num + 1} ---\n"
            history += f"AGGRESSIVE: {agg_arg}\n\n"
            history += f"CONSERVATIVE: {cons_arg}\n\n"
            history += f"NEUTRAL: {neut_arg}\n"

        return agg_arg, cons_arg, neut_arg, history


__all__ = [
    "AggressiveRisk",
    "ConservativeRisk",
    "NeutralRisk",
    "RiskManager",
    "RiskDebateRunner",
]

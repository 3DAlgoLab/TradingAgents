"""Main DSPy TradingAgentsProgram module.

This module implements the main orchestration program that wires together
all DSPy agents into a cohesive trading decision system.
"""

import dspy
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents_dspy.agents import (
    MarketAnalyst,
    SentimentAnalyst,
    NewsAnalyst,
    FundamentalsAnalyst,
    BullResearcher,
    BearResearcher,
    ResearchManager,
    DebateRunner,
    Trader,
    AggressiveRisk,
    ConservativeRisk,
    NeutralRisk,
    RiskManager,
    RiskDebateRunner,
    PortfolioManager,
    MemoryWrapper,
)


@dataclass
class TradingResult:
    """Structured result from TradingAgentsProgram."""

    final_decision: str
    market_report: str
    sentiment_report: str
    news_report: str
    fundamentals_report: str
    bull_argument: str
    bear_argument: str
    investment_decision: str
    trader_plan: str
    risk_evaluation: str
    debate_history: str
    risk_debate_history: str


class TradingAgentsProgram(dspy.Module):
    """Main DSPy program that orchestrates all trading agents.

    This program implements the full TradingAgents workflow:
    1. Phase 1: Run all analysts (Market, Sentiment, News, Fundamentals)
    2. Phase 2: Run bull/bear debate (iterative rounds)
    3. Phase 3: Research manager makes investment decision
    4. Phase 4: Trader creates trading plan
    5. Phase 5: Risk debate (aggressive/conservative/neutral)
    6. Phase 6: Risk manager evaluates
    7. Phase 7: Portfolio manager makes final decision

    Example:
        >>> from tradingagents_dspy.config import configure_dspy
        >>> from tradingagents_dspy.program import TradingAgentsProgram
        >>>
        >>> configure_dspy()
        >>> program = TradingAgentsProgram(config=DEFAULT_CONFIG)
        >>> result = program(company="AAPL", date="2024-06-19")
        >>> print(result.final_decision)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the TradingAgentsProgram.

        Args:
            config: Configuration dictionary. If None, uses DEFAULT_CONFIG
        """
        super().__init__()
        self.config = config or DEFAULT_CONFIG.copy()

        self.num_debate_rounds = self.config.get("num_debate_rounds", 2)
        self.enable_memory = self.config.get("enable_memory", False)
        self.parallel_analysts = self.config.get("parallel_analysts", False)

        self.market_analyst = MarketAnalyst()
        self.sentiment_analyst = SentimentAnalyst()
        self.news_analyst = NewsAnalyst()
        self.fundamentals_analyst = FundamentalsAnalyst()

        self.debate_runner = DebateRunner(num_rounds=self.num_debate_rounds)
        self.research_manager = ResearchManager()

        self.trader = Trader()

        self.risk_debate_runner = RiskDebateRunner(num_rounds=self.num_debate_rounds)
        self.risk_manager = RiskManager()

        self.portfolio_manager = PortfolioManager()

        if self.enable_memory:
            self.memory = MemoryWrapper(config=self.config)

    def forward(
        self,
        company: str,
        date: str,
        verbose: bool = False,
    ) -> TradingResult:
        """Run the full TradingAgents pipeline.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            verbose: Whether to print progress updates

        Returns:
            TradingResult with all intermediate and final outputs
        """
        past_memories = ""
        if self.enable_memory and hasattr(self, "memory"):
            situation = f"Analyze {company} on {date}"
            past_memories = self.memory.get_memories(situation, n_matches=2)

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"TradingAgents DSPy - {company} on {date}")
            print(f"{'=' * 60}\n")

        if verbose:
            print("Phase 1: Running Analysts...")

        market_report = self.market_analyst(company=company, date=date)
        sentiment_report = self.sentiment_analyst(company=company, date=date)
        news_report = self.news_analyst(company=company, date=date)
        fundamentals_report = self.fundamentals_analyst(company=company, date=date)

        if verbose:
            print(f"  - Market Analyst: Done")
            print(f"  - Sentiment Analyst: Done")
            print(f"  - News Analyst: Done")
            print(f"  - Fundamentals Analyst: Done")

        if verbose:
            print(
                f"\nPhase 2: Running Bull/Bear Debate ({self.num_debate_rounds} rounds)..."
            )

        bull_argument, bear_argument, debate_history = self.debate_runner(
            company=company,
            date=date,
            market_report=market_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            past_memories=past_memories,
        )

        if verbose:
            print(f"  - Debate complete")

        if verbose:
            print("\nPhase 3: Research Manager Decision...")

        investment_decision = self.research_manager(
            company=company,
            date=date,
            market_report=market_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            bull_argument=bull_argument,
            bear_argument=bear_argument,
            debate_history=debate_history,
        )

        if verbose:
            print(f"  - Investment Decision: {investment_decision[:100]}...")

        if verbose:
            print("\nPhase 4: Trader Creates Plan...")

        trader_plan = self.trader(
            company=company,
            date=date,
            investment_decision=investment_decision,
            past_memories=past_memories,
        )

        if verbose:
            print(f"  - Trading Plan: {trader_plan[:100]}...")

        if verbose:
            print(f"\nPhase 5: Risk Debate ({self.num_debate_rounds} rounds)...")

        (
            aggressive_assessment,
            conservative_assessment,
            neutral_assessment,
            risk_debate_history,
        ) = self.risk_debate_runner(
            company=company,
            date=date,
            trader_investment_plan=trader_plan,
        )

        if verbose:
            print(f"  - Risk Debate complete")

        if verbose:
            print("\nPhase 6: Risk Manager Evaluation...")

        risk_evaluation = self.risk_manager(
            company=company,
            date=date,
            trader_investment_plan=trader_plan,
            aggressive_assessment=aggressive_assessment,
            conservative_assessment=conservative_assessment,
            neutral_assessment=neutral_assessment,
            risk_debate_history=risk_debate_history,
        )

        if verbose:
            print(f"  - Risk Evaluation: {risk_evaluation[:100]}...")

        if verbose:
            print("\nPhase 7: Portfolio Manager Final Decision...")

        final_decision = self.portfolio_manager(
            company=company,
            date=date,
            trader_investment_plan=trader_plan,
            risk_evaluation=risk_evaluation,
            past_memories=past_memories,
        )

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"FINAL DECISION: {final_decision}")
            print(f"{'=' * 60}\n")

        return TradingResult(
            final_decision=final_decision,
            market_report=market_report,
            sentiment_report=sentiment_report,
            news_report=news_report,
            fundamentals_report=fundamentals_report,
            bull_argument=bull_argument,
            bear_argument=bear_argument,
            investment_decision=investment_decision,
            trader_plan=trader_plan,
            risk_evaluation=risk_evaluation,
            debate_history=debate_history,
            risk_debate_history=risk_debate_history,
        )

    def add_memory(
        self,
        market_analysis: str,
        sentiment_analysis: str,
        news_analysis: str,
        fundamentals_analysis: str,
        trade_decision: str,
        outcome: str,
    ) -> None:
        """Add a trade result to memory for future learning.

        Args:
            market_analysis: Market analysis at time of trade
            sentiment_analysis: Sentiment analysis at time of trade
            news_analysis: News analysis at time of trade
            fundamentals_analysis: Fundamentals analysis at time of trade
            trade_decision: The trade decision made (BUY/SELL/HOLD)
            outcome: The outcome/result of the trade
        """
        if hasattr(self, "memory"):
            self.memory.add_trade_result(
                market_analysis=market_analysis,
                sentiment_analysis=sentiment_analysis,
                news_analysis=news_analysis,
                fundamentals_analysis=fundamentals_analysis,
                trade_decision=trade_decision,
                outcome=outcome,
            )

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Dictionary with memory stats
        """
        if hasattr(self, "memory"):
            return self.memory.get_stats()
        return {"memory_enabled": False}

    def propagate(
        self,
        company: str,
        date: str,
        verbose: bool = True,
    ) -> tuple:
        """Run the trading analysis (API-compatible with LangGraph version).

        This method provides API compatibility with the original TradingAgentsGraph.

        Args:
            company: Stock ticker symbol
            date: Analysis date in YYYY-MM-DD format
            verbose: Whether to print progress updates (default: True)

        Returns:
            Tuple of (state_dict, decision_string)
        """
        result = self.forward(company=company, date=date, verbose=verbose)
        state_dict = {
            "company": company,
            "date": date,
            "final_decision": result.final_decision,
            "market_report": result.market_report,
            "sentiment_report": result.sentiment_report,
            "news_report": result.news_report,
            "fundamentals_report": result.fundamentals_report,
            "bull_argument": result.bull_argument,
            "bear_argument": result.bear_argument,
            "investment_decision": result.investment_decision,
            "trader_plan": result.trader_plan,
            "risk_evaluation": result.risk_evaluation,
        }
        decision = result.final_decision
        return state_dict, decision


__all__ = [
    "TradingAgentsProgram",
    "TradingResult",
]

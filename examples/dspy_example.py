"""Example usage of DSPy TradingAgentsProgram.

This script demonstrates how to use the DSPy-based TradingAgents
to make trading decisions.
"""

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents_dspy.config import configure_dspy
from tradingagents_dspy.program import TradingAgentsProgram


def main():
    """Run a simple example of TradingAgents DSPy."""

    print("Configuring DSPy...")
    configure_dspy()

    config = DEFAULT_CONFIG.copy()
    config["num_debate_rounds"] = 1
    config["enable_memory"] = False

    print("Creating TradingAgentsProgram...")
    program = TradingAgentsProgram(config=config)

    print("\nRunning TradingAgents for AAPL on 2024-06-19...")
    print("(This will make LLM calls - may take a minute)\n")

    result = program(
        company="AAPL",
        date="2024-06-19",
        verbose=True,
    )

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Final Decision: {result.final_decision}")

    print("\n--- Intermediate Results ---")
    print(f"Investment Decision: {result.investment_decision[:200]}...")
    print(f"Trading Plan: {result.trader_plan[:200]}...")
    print(f"Risk Evaluation: {result.risk_evaluation[:200]}...")

    return result


if __name__ == "__main__":
    main()

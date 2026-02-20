"""Test script for DSPy TradingAgentsProgram.

This script verifies that the main TradingAgentsProgram can be instantiated
and has proper structure.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents_dspy.config import DEFAULT_CONFIG
from tradingagents_dspy.program import TradingAgentsProgram, TradingResult


def test_program_instantiation():
    """Test that TradingAgentsProgram can be instantiated."""
    print("=" * 60)
    print("Test: Program Instantiation")
    print("=" * 60)

    try:
        program = TradingAgentsProgram(config=DEFAULT_CONFIG.copy())
        print(f"✓ TradingAgentsProgram instantiated")

        if hasattr(program, "market_analyst"):
            print(f"  - Has market_analyst")
        if hasattr(program, "sentiment_analyst"):
            print(f"  - Has sentiment_analyst")
        if hasattr(program, "news_analyst"):
            print(f"  - Has news_analyst")
        if hasattr(program, "fundamentals_analyst"):
            print(f"  - Has fundamentals_analyst")
        if hasattr(program, "debate_runner"):
            print(f"  - Has debate_runner")
        if hasattr(program, "research_manager"):
            print(f"  - Has research_manager")
        if hasattr(program, "trader"):
            print(f"  - Has trader")
        if hasattr(program, "risk_debate_runner"):
            print(f"  - Has risk_debate_runner")
        if hasattr(program, "risk_manager"):
            print(f"  - Has risk_manager")
        if hasattr(program, "portfolio_manager"):
            print(f"  - Has portfolio_manager")
        if hasattr(program, "forward"):
            print(f"  - Has forward method")

    except Exception as e:
        print(f"✗ TradingAgentsProgram: {e}")
        return False

    print()
    return True


def test_program_api():
    """Test that program has the expected API."""
    print("=" * 60)
    print("Test: Program API")
    print("=" * 60)

    import inspect

    program = TradingAgentsProgram(config=DEFAULT_CONFIG.copy())
    sig = inspect.signature(program.forward)
    params = list(sig.parameters.keys())

    has_company = "company" in params
    has_date = "date" in params
    has_verbose = "verbose" in params

    if has_company:
        print(f"✓ forward() has 'company' parameter")
    else:
        print(f"✗ forward() missing 'company' parameter")

    if has_date:
        print(f"✓ forward() has 'date' parameter")
    else:
        print(f"✗ forward() missing 'date' parameter")

    if has_verbose:
        print(f"✓ forward() has 'verbose' parameter")
    else:
        print(f"✗ forward() missing 'verbose' parameter")

    print()
    return has_company and has_date


def test_trading_result():
    """Test TradingResult dataclass."""
    print("=" * 60)
    print("Test: TradingResult Dataclass")
    print("=" * 60)

    try:
        result = TradingResult(
            final_decision="BUY - Good opportunity",
            market_report="Market report content",
            sentiment_report="Sentiment report content",
            news_report="News report content",
            fundamentals_report="Fundamentals report content",
            bull_argument="Bull argument",
            bear_argument="Bear argument",
            investment_decision="Investment decision",
            trader_plan="Trading plan",
            risk_evaluation="Risk evaluation",
            debate_history="Debate history",
            risk_debate_history="Risk debate history",
        )

        print(f"✓ TradingResult created")

        assert result.final_decision == "BUY - Good opportunity"
        print(f"  - final_decision accessible")

        assert result.market_report == "Market report content"
        print(f"  - market_report accessible")

        assert result.debate_history == "Debate history"
        print(f"  - debate_history accessible")

    except Exception as e:
        print(f"✗ TradingResult: {e}")
        return False

    print()
    return True


def test_config_options():
    """Test configuration options."""
    print("=" * 60)
    print("Test: Configuration Options")
    print("=" * 60)

    try:
        config1 = DEFAULT_CONFIG.copy()
        config1["num_debate_rounds"] = 1
        program1 = TradingAgentsProgram(config=config1)
        assert program1.num_debate_rounds == 1
        print(f"✓ num_debate_rounds = 1 works")

        config2 = DEFAULT_CONFIG.copy()
        config2["num_debate_rounds"] = 3
        program2 = TradingAgentsProgram(config=config2)
        assert program2.num_debate_rounds == 3
        print(f"✓ num_debate_rounds = 3 works")

        config3 = DEFAULT_CONFIG.copy()
        config3["enable_memory"] = True
        program3 = TradingAgentsProgram(config=config3)
        assert program3.enable_memory == True
        print(f"✓ enable_memory = True works")

    except Exception as e:
        print(f"✗ Configuration: {e}")
        return False

    print()
    return True


def test_memory_methods():
    """Test memory-related methods."""
    print("=" * 60)
    print("Test: Memory Methods")
    print("=" * 60)

    try:
        config = DEFAULT_CONFIG.copy()
        config["enable_memory"] = False
        program = TradingAgentsProgram(config=config)

        assert hasattr(program, "add_memory")
        print(f"✓ Has add_memory method")

        assert hasattr(program, "get_memory_stats")
        print(f"✓ Has get_memory_stats method")

        stats = program.get_memory_stats()
        assert stats.get("memory_enabled") == False
        print(f"✓ get_memory_stats works when memory disabled")

    except Exception as e:
        print(f"✗ Memory methods: {e}")
        return False

    print()
    return True


def test_program_docstrings():
    """Test that program has proper docstrings."""
    print("=" * 60)
    print("Test: Program Docstrings")
    print("=" * 60)

    try:
        if TradingAgentsProgram.__doc__ and len(TradingAgentsProgram.__doc__) > 10:
            print(f"✓ TradingAgentsProgram has class docstring")
        else:
            print(f"✗ TradingAgentsProgram missing class docstring")
            return False

        if (
            TradingAgentsProgram.forward.__doc__
            and len(TradingAgentsProgram.forward.__doc__) > 10
        ):
            print(f"✓ TradingAgentsProgram.forward() has docstring")
        else:
            print(f"✗ TradingAgentsProgram.forward() missing docstring")
            return False

        if TradingResult.__doc__ and len(TradingResult.__doc__) > 10:
            print(f"✓ TradingResult has docstring")
        else:
            print(f"✗ TradingResult missing docstring")
            return False

    except Exception as e:
        print(f"✗ Docstrings: {e}")
        return False

    print()
    return True


def main():
    """Run all tests."""
    print("\nDSPy TradingAgentsProgram Tests")
    print("=" * 60)
    print()

    results = []

    results.append(("Program Instantiation", test_program_instantiation()))
    results.append(("Program API", test_program_api()))
    results.append(("TradingResult Dataclass", test_trading_result()))
    results.append(("Configuration Options", test_config_options()))
    results.append(("Memory Methods", test_memory_methods()))
    results.append(("Program Docstrings", test_program_docstrings()))

    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

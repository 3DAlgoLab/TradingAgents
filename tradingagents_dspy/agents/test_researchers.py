"""Test script for DSPy researcher, trader, risk, and portfolio agents.

This script verifies that all non-analyst agents can be instantiated and have
proper structure.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents_dspy.agents import (
    BullResearcher,
    BearResearcher,
    ResearchManager,
    DebateRunner,
    Trader,
    AggressiveRisk,
    ConservativeRisk,
    NeutralRisk,
    RiskManager as RiskMgr,
    RiskDebateRunner,
    PortfolioManager,
)


def test_researcher_instantiation():
    """Test that all researcher agents can be instantiated."""
    print("=" * 60)
    print("Test: Researcher Instantiation")
    print("=" * 60)

    agents = {
        "BullResearcher": BullResearcher,
        "BearResearcher": BearResearcher,
        "ResearchManager": ResearchManager,
        "DebateRunner": DebateRunner,
    }

    all_passed = True
    for name, agent_class in agents.items():
        try:
            agent = agent_class()
            print(f"✓ {name} instantiated")

            if hasattr(agent, "debate"):
                print(f"  - Has debate module")
            if hasattr(agent, "evaluate"):
                print(f"  - Has evaluate module")
            if hasattr(agent, "forward"):
                print(f"  - Has forward method")

        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False

    print()
    return all_passed


def test_trader_instantiation():
    """Test that trader agent can be instantiated."""
    print("=" * 60)
    print("Test: Trader Instantiation")
    print("=" * 60)

    try:
        trader = Trader()
        print(f"✓ Trader instantiated")

        if hasattr(trader, "trade"):
            print(f"  - Has trade module")
        if hasattr(trader, "forward"):
            print(f"  - Has forward method")

    except Exception as e:
        print(f"✗ Trader: {e}")
        return False

    print()
    return True


def test_risk_instantiation():
    """Test that all risk agents can be instantiated."""
    print("=" * 60)
    print("Test: Risk Agent Instantiation")
    print("=" * 60)

    agents = {
        "AggressiveRisk": AggressiveRisk,
        "ConservativeRisk": ConservativeRisk,
        "NeutralRisk": NeutralRisk,
        "RiskManager": RiskMgr,
        "RiskDebateRunner": RiskDebateRunner,
    }

    all_passed = True
    for name, agent_class in agents.items():
        try:
            agent = agent_class()
            print(f"✓ {name} instantiated")

            if hasattr(agent, "assess"):
                print(f"  - Has assess module")
            if hasattr(agent, "evaluate"):
                print(f"  - Has evaluate module")
            if hasattr(agent, "forward"):
                print(f"  - Has forward method")

        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False

    print()
    return all_passed


def test_portfolio_instantiation():
    """Test that portfolio manager can be instantiated."""
    print("=" * 60)
    print("Test: Portfolio Manager Instantiation")
    print("=" * 60)

    try:
        pm = PortfolioManager()
        print(f"✓ PortfolioManager instantiated")

        if hasattr(pm, "decide"):
            print(f"  - Has decide module")
        if hasattr(pm, "forward"):
            print(f"  - Has forward method")

    except Exception as e:
        print(f"✗ PortfolioManager: {e}")
        return False

    print()
    return True


def test_agent_api():
    """Test that agents have the expected API."""
    print("=" * 60)
    print("Test: Agent API")
    print("=" * 60)

    import inspect

    tests_passed = True

    # Test BullResearcher
    bull = BullResearcher()
    sig = inspect.signature(bull.forward)
    params = list(sig.parameters.keys())
    assert "company" in params, "BullResearcher missing 'company'"
    assert "date" in params, "BullResearcher missing 'date'"
    assert "market_report" in params, "BullResearcher missing 'market_report'"
    print(f"✓ BullResearcher.forward() has correct parameters: {params}")

    # Test ResearchManager
    rm = ResearchManager()
    sig = inspect.signature(rm.forward)
    params = list(sig.parameters.keys())
    assert "bull_argument" in params, "ResearchManager missing 'bull_argument'"
    assert "bear_argument" in params, "ResearchManager missing 'bear_argument'"
    print(f"✓ ResearchManager.forward() has correct parameters: {params}")

    # Test Trader
    trader = Trader()
    sig = inspect.signature(trader.forward)
    params = list(sig.parameters.keys())
    assert "company" in params, "Trader missing 'company'"
    assert "date" in params, "Trader missing 'date'"
    assert "investment_decision" in params, "Trader missing 'investment_decision'"
    print(f"✓ Trader.forward() has correct parameters: {params}")

    # Test RiskManager
    risk_mgr = RiskMgr()
    sig = inspect.signature(risk_mgr.forward)
    params = list(sig.parameters.keys())
    assert "company" in params, "RiskManager missing 'company'"
    assert "trader_investment_plan" in params, (
        "RiskManager missing 'trader_investment_plan'"
    )
    assert "aggressive_assessment" in params, (
        "RiskManager missing 'aggressive_assessment'"
    )
    print(f"✓ RiskManager.forward() has correct parameters: {params}")

    # Test PortfolioManager
    pm = PortfolioManager()
    sig = inspect.signature(pm.forward)
    params = list(sig.parameters.keys())
    assert "company" in params, "PortfolioManager missing 'company'"
    assert "risk_evaluation" in params, "PortfolioManager missing 'risk_evaluation'"
    print(f"✓ PortfolioManager.forward() has correct parameters: {params}")

    print()
    return tests_passed


def test_agent_docstrings():
    """Test that agents have docstrings."""
    print("=" * 60)
    print("Test: Agent Docstrings")
    print("=" * 60)

    agents = [
        BullResearcher,
        BearResearcher,
        ResearchManager,
        DebateRunner,
        Trader,
        AggressiveRisk,
        ConservativeRisk,
        NeutralRisk,
        RiskMgr,
        RiskDebateRunner,
        PortfolioManager,
    ]

    all_passed = True
    for agent_class in agents:
        if agent_class.__doc__ and len(agent_class.__doc__) > 10:
            print(f"✓ {agent_class.__name__} has class docstring")
        else:
            print(f"✗ {agent_class.__name__} missing or short class docstring")
            all_passed = False

        if agent_class.forward.__doc__ and len(agent_class.forward.__doc__) > 10:
            print(f"✓ {agent_class.__name__}.forward() has docstring")
        else:
            print(f"✗ {agent_class.__name__}.forward() missing docstring")
            all_passed = False

    print()
    return all_passed


def test_debate_runner():
    """Test DebateRunner with configurable rounds."""
    print("=" * 60)
    print("Test: Debate Runner Configuration")
    print("=" * 60)

    try:
        # Test with different round counts
        runner1 = DebateRunner(num_rounds=1)
        runner2 = DebateRunner(num_rounds=3)

        assert runner1.num_rounds == 1, "DebateRunner round config failed"
        assert runner2.num_rounds == 3, "DebateRunner round config failed"

        print(f"✓ DebateRunner with 1 round: {runner1.num_rounds}")
        print(f"✓ DebateRunner with 3 rounds: {runner2.num_rounds}")

    except Exception as e:
        print(f"✗ DebateRunner configuration: {e}")
        return False

    print()
    return True


def main():
    """Run all tests."""
    print("\nDSPy Researcher, Trader, Risk & Portfolio Agents Tests")
    print("=" * 60)
    print()

    results = []

    results.append(("Researcher Instantiation", test_researcher_instantiation()))
    results.append(("Trader Instantiation", test_trader_instantiation()))
    results.append(("Risk Agent Instantiation", test_risk_instantiation()))
    results.append(("Portfolio Manager Instantiation", test_portfolio_instantiation()))
    results.append(("Agent API", test_agent_api()))
    results.append(("Agent Docstrings", test_agent_docstrings()))
    results.append(("Debate Runner Configuration", test_debate_runner()))

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

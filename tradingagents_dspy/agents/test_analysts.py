"""Test script for DSPy analyst agents.

This script verifies that all analyst agents can be instantiated and have
proper structure.
"""

import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents_dspy.agents import (
    MarketAnalyst,
    SentimentAnalyst,
    NewsAnalyst,
    FundamentalsAnalyst,
)

from tradingagents_dspy.agents.tools import (
    MARKET_TOOLS,
    SOCIAL_TOOLS,
    NEWS_TOOLS,
    FUNDAMENTALS_TOOLS,
)


def test_tool_sets():
    """Test that tool sets are properly defined."""
    print("=" * 60)
    print("Test: Tool Sets")
    print("=" * 60)

    print(f"✓ MARKET_TOOLS: {len(MARKET_TOOLS)} tools")
    for tool in MARKET_TOOLS:
        print(f"  - {tool.__name__}")

    print(f"✓ SOCIAL_TOOLS: {len(SOCIAL_TOOLS)} tools")
    for tool in SOCIAL_TOOLS:
        print(f"  - {tool.__name__}")

    print(f"✓ NEWS_TOOLS: {len(NEWS_TOOLS)} tools")
    for tool in NEWS_TOOLS:
        print(f"  - {tool.__name__}")

    print(f"✓ FUNDAMENTALS_TOOLS: {len(FUNDAMENTALS_TOOLS)} tools")
    for tool in FUNDAMENTALS_TOOLS:
        print(f"  - {tool.__name__}")

    print()
    return True


def test_analyst_instantiation():
    """Test that all analysts can be instantiated."""
    print("=" * 60)
    print("Test: Analyst Instantiation")
    print("=" * 60)

    analysts = {
        "MarketAnalyst": MarketAnalyst,
        "SentimentAnalyst": SentimentAnalyst,
        "NewsAnalyst": NewsAnalyst,
        "FundamentalsAnalyst": FundamentalsAnalyst,
    }

    all_passed = True
    for name, analyst_class in analysts.items():
        try:
            analyst = analyst_class()
            print(f"✓ {name} instantiated")

            # Check required attributes
            if hasattr(analyst, "analyze"):
                print(f"  - Has analyze module")
            if hasattr(analyst, "tools"):
                print(f"  - Has {len(analyst.tools)} tools")
            if hasattr(analyst, "forward"):
                print(f"  - Has forward method")

        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False

    print()
    return all_passed


def test_analyst_with_custom_tools():
    """Test that analysts can accept custom tools."""
    print("=" * 60)
    print("Test: Custom Tool Configuration")
    print("=" * 60)

    try:
        # Create analyst with subset of tools
        custom_tools = [MARKET_TOOLS[0]] if MARKET_TOOLS else []
        analyst = MarketAnalyst(tools=custom_tools)
        print(f"✓ MarketAnalyst with custom tools ({len(custom_tools)} tools)")

        # Verify tools were set
        assert analyst.tools == custom_tools, "Custom tools not set correctly"
        print(f"  - Custom tools correctly assigned")

    except Exception as e:
        print(f"✗ Custom tool test failed: {e}")
        return False

    print()
    return True


def test_analyst_api():
    """Test that analysts have the expected API."""
    print("=" * 60)
    print("Test: Analyst API")
    print("=" * 60)

    analyst = MarketAnalyst()

    # Test forward method signature
    import inspect

    sig = inspect.signature(analyst.forward)
    params = list(sig.parameters.keys())

    assert "company" in params, "Missing 'company' parameter"
    assert "date" in params, "Missing 'date' parameter"
    print("✓ MarketAnalyst.forward() has correct parameters")
    print(f"  - Parameters: {params}")

    # Test return type annotation if available
    if sig.return_annotation != inspect.Signature.empty:
        print(f"  - Return type: {sig.return_annotation}")

    print()
    return True


def test_analyst_docstrings():
    """Test that analysts have docstrings."""
    print("=" * 60)
    print("Test: Analyst Docstrings")
    print("=" * 60)

    analysts = [
        MarketAnalyst,
        SentimentAnalyst,
        NewsAnalyst,
        FundamentalsAnalyst,
    ]

    all_passed = True
    for analyst_class in analysts:
        if analyst_class.__doc__ and len(analyst_class.__doc__) > 10:
            print(f"✓ {analyst_class.__name__} has class docstring")
        else:
            print(f"✗ {analyst_class.__name__} missing or short class docstring")
            all_passed = False

        # Check forward method docstring
        if analyst_class.forward.__doc__ and len(analyst_class.forward.__doc__) > 10:
            print(f"✓ {analyst_class.__name__}.forward() has docstring")
        else:
            print(f"✗ {analyst_class.__name__}.forward() missing docstring")
            all_passed = False

    print()
    return all_passed


def main():
    """Run all tests."""
    print("\nDSPy Analyst Agents Tests")
    print("=" * 60)
    print()

    results = []

    results.append(("Tool Sets", test_tool_sets()))
    results.append(("Analyst Instantiation", test_analyst_instantiation()))
    results.append(("Custom Tool Configuration", test_analyst_with_custom_tools()))
    results.append(("Analyst API", test_analyst_api()))
    results.append(("Analyst Docstrings", test_analyst_docstrings()))

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

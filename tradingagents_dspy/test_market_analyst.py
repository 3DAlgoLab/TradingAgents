"""Test script for MarketAnalyst module.

This script tests the MarketAnalyst DSPy module with actual LLM calls.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents_dspy.config import configure_dspy
from tradingagents_dspy.agents import MarketAnalyst



def test_market_analyst_execution():
    """Test that MarketAnalyst can execute and produce output."""
    print("=" * 60)
    print("Test: MarketAnalyst Execution")
    print("=" * 60)    

    print("Configuring DSPy...")
    configure_dspy()

    print("Creating MarketAnalyst...")
    analyst = MarketAnalyst()

    print("Running MarketAnalyst for AAPL on 2024-06-19...")
    print("(This will make LLM calls - may take a minute)\n")

    result = analyst(company="AAPL", date="2024-06-19")

    print("\n--- Result ---")
    print(f"Type: {type(result)}")
    print(f"Length: {len(result)} characters")
    print(f"Content: {result[:500]}...")

    print()
    return True


def test_market_analyst_with_different_ticker():
    """Test MarketAnalyst with different stock tickers."""
    print("=" * 60)
    print("Test: MarketAnalyst Different Tickers")
    print("=" * 60)

    analyst = MarketAnalyst()

    tickers = ["NVDA", "GOOGL"]
    for ticker in tickers:
        print(f"\nTesting {ticker}...")
        result = analyst(company=ticker, date="2024-06-19")
        print(f"  Result length: {len(result)} chars")
        print(f"  First 200 chars: {result[:200]}...")

    print()
    return True


def test_market_analyst_api():
    """Test MarketAnalyst API compatibility."""
    print("=" * 60)
    print("Test: MarketAnalyst API")
    print("=" * 60)

    analyst = MarketAnalyst()

    import inspect

    sig = inspect.signature(analyst.forward)
    params = list(sig.parameters.keys())

    assert "company" in params, "Missing 'company' parameter"
    assert "date" in params, "Missing 'date' parameter"
    print("✓ Parameters: company, date")

    print()
    return True


def main():
    """Run all tests."""
    print("\nMarketAnalyst Module Tests")
    print("=" * 60)
    print()

    results = []

    results.append(("API Test", test_market_analyst_api()))
    results.append(("Execution Test", test_market_analyst_execution()))
    results.append(("Different Tickers", test_market_analyst_with_different_ticker()))

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

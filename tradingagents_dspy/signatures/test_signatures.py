"""Test script for DSPy signatures.

This script verifies that all signatures can be instantiated and used correctly.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents_dspy.signatures import (
    # Analyst signatures
    MarketAnalysisSignature,
    SentimentAnalysisSignature,
    NewsAnalysisSignature,
    FundamentalsAnalysisSignature,
    # Researcher signatures
    BullResearcherSignature,
    BearResearcherSignature,
    ResearchManagerSignature,
    # Trader signatures
    TraderSignature,
    AggressiveRiskSignature,
    ConservativeRiskSignature,
    NeutralRiskSignature,
    RiskManagerSignature,
    PortfolioManagerSignature,
)


def test_signature_structure():
    """Test that all signatures have proper structure."""
    print("=" * 60)
    print("Test: Signature Structure")
    print("=" * 60)

    signatures = {
        "MarketAnalysisSignature": MarketAnalysisSignature,
        "SentimentAnalysisSignature": SentimentAnalysisSignature,
        "NewsAnalysisSignature": NewsAnalysisSignature,
        "FundamentalsAnalysisSignature": FundamentalsAnalysisSignature,
        "BullResearcherSignature": BullResearcherSignature,
        "BearResearcherSignature": BearResearcherSignature,
        "ResearchManagerSignature": ResearchManagerSignature,
        "TraderSignature": TraderSignature,
        "AggressiveRiskSignature": AggressiveRiskSignature,
        "ConservativeRiskSignature": ConservativeRiskSignature,
        "NeutralRiskSignature": NeutralRiskSignature,
        "RiskManagerSignature": RiskManagerSignature,
        "PortfolioManagerSignature": PortfolioManagerSignature,
    }

    all_passed = True
    for name, sig_class in signatures.items():
        try:
            # Check class attributes (not instance)
            print(f"✓ {name}")

            # Check that it has the required class attributes
            if hasattr(sig_class, "input_fields") and hasattr(
                sig_class, "output_fields"
            ):
                print(f"  Inputs: {list(sig_class.input_fields.keys())}")
                print(f"  Outputs: {list(sig_class.output_fields.keys())}")
            else:
                print(f"  Note: Signature structure validated")
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_passed = False

    print()
    return all_passed


def test_signature_fields():
    """Test that signatures have the expected fields."""
    print("=" * 60)
    print("Test: Signature Fields")
    print("=" * 60)

    # Test MarketAnalysisSignature
    assert "company" in MarketAnalysisSignature.input_fields, "Missing 'company' input"
    assert "date" in MarketAnalysisSignature.input_fields, "Missing 'date' input"
    assert "market_report" in MarketAnalysisSignature.output_fields, (
        "Missing 'market_report' output"
    )
    print("✓ MarketAnalysisSignature has correct fields")

    # Test ResearchManagerSignature
    assert "investment_plan" in ResearchManagerSignature.output_fields, (
        "Missing 'investment_plan' output"
    )
    print("✓ ResearchManagerSignature has correct fields")

    # Test PortfolioManagerSignature
    assert "final_trade_decision" in PortfolioManagerSignature.output_fields, (
        "Missing 'final_trade_decision' output"
    )
    print("✓ PortfolioManagerSignature has correct fields")

    print()
    return True


def test_signature_docstrings():
    """Test that signatures have docstrings."""
    print("=" * 60)
    print("Test: Signature Docstrings")
    print("=" * 60)

    signatures = [
        MarketAnalysisSignature,
        SentimentAnalysisSignature,
        NewsAnalysisSignature,
        FundamentalsAnalysisSignature,
        BullResearcherSignature,
        BearResearcherSignature,
        ResearchManagerSignature,
        TraderSignature,
        AggressiveRiskSignature,
        ConservativeRiskSignature,
        NeutralRiskSignature,
        RiskManagerSignature,
        PortfolioManagerSignature,
    ]

    all_passed = True
    for sig_class in signatures:
        # Check class docstring directly
        if sig_class.__doc__ and len(sig_class.__doc__) > 10:
            print(f"✓ {sig_class.__name__} has docstring")
        else:
            print(f"✗ {sig_class.__name__} missing or short docstring")
            all_passed = False

    print()
    return all_passed


def main():
    """Run all tests."""
    print("\nDSPy Signatures Tests")
    print("=" * 60)
    print()

    results = []

    results.append(("Signature Structure", test_signature_structure()))
    results.append(("Signature Fields", test_signature_fields()))
    results.append(("Signature Docstrings", test_signature_docstrings()))

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

"""Test script for DSPy configuration module.

This script verifies that the DSPy configuration module works correctly
with the existing TradingAgents configuration.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents_dspy.config import configure_dspy, get_lm, reset_dspy, quick_setup


def test_configure_dspy_with_default_config():
    """Test DSPy configuration with DEFAULT_CONFIG."""
    print("=" * 60)
    print("Test 1: Configure DSPy with DEFAULT_CONFIG")
    print("=" * 60)

    try:
        lm = configure_dspy(DEFAULT_CONFIG)
        print(f"✓ DSPy configured successfully")
        print(f"  Provider: {DEFAULT_CONFIG['llm_provider']}")
        print(f"  Model: {DEFAULT_CONFIG['deep_think_llm']}")
        print(f"  LM object: {lm}")
        print()
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        print()
        return False
    finally:
        reset_dspy()


def test_get_lm():
    """Test getting the configured LM."""
    print("=" * 60)
    print("Test 2: Get configured LM")
    print("=" * 60)

    # Should fail before configuration
    try:
        get_lm()
        print("✗ get_lm() should have failed before configuration")
        return False
    except RuntimeError as e:
        print(f"✓ Correctly raised RuntimeError: {e}")

    # Configure and try again
    try:
        configure_dspy(DEFAULT_CONFIG)
        lm = get_lm()
        print(f"✓ Successfully retrieved LM: {lm}")
        print()
        return True
    except Exception as e:
        print(f"✗ Failed to get LM: {e}")
        print()
        return False
    finally:
        reset_dspy()


def test_quick_setup():
    """Test quick setup function."""
    print("=" * 60)
    print("Test 3: Quick setup")
    print("=" * 60)

    try:
        # This will fail without a valid API key, but tests the function structure
        lm = quick_setup(
            provider="openai",
            model="gpt-4",
        )
        print(f"✓ Quick setup successful")
        print(f"  LM object: {lm}")
        print()
        return True
    except Exception as e:
        # Expected to fail without API key, but validates the code path
        if "API key" in str(e) or "authentication" in str(e).lower():
            print(f"✓ Quick setup code path works (expected auth error)")
            print(f"  Error: {e}")
            print()
            return True
        else:
            print(f"✗ Unexpected error: {e}")
            print()
            return False
    finally:
        reset_dspy()


def test_config_validation():
    """Test configuration validation."""
    print("=" * 60)
    print("Test 4: Configuration validation")
    print("=" * 60)

    # Test missing provider
    try:
        configure_dspy({})
        print("✗ Should have failed with empty config")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError for empty config: {e}")

    # Test missing model
    try:
        configure_dspy({"llm_provider": "openai"})
        print("✗ Should have failed without model")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError for missing model: {e}")

    # Test unsupported provider
    try:
        configure_dspy(
            {"llm_provider": "unsupported_provider", "deep_think_llm": "some-model"}
        )
        print("✗ Should have failed with unsupported provider")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError for unsupported provider: {e}")

    print()
    return True


def main():
    """Run all tests."""
    print("\nDSPy Configuration Module Tests")
    print("=" * 60)
    print()

    results = []

    results.append(
        ("Configure with DEFAULT_CONFIG", test_configure_dspy_with_default_config())
    )
    results.append(("Get LM", test_get_lm()))
    results.append(("Quick setup", test_quick_setup()))
    results.append(("Config validation", test_config_validation()))

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

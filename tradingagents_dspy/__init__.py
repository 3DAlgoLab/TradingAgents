"""TradingAgents DSPy Implementation.

This package provides a DSPy-based implementation of the TradingAgents framework,
offering a more compact and optimizable alternative to the LangGraph version.
"""

from .config import configure_dspy, get_lm, reset_dspy, quick_setup
from . import signatures
from .program import TradingAgentsProgram, TradingResult

__version__ = "0.1.0"

__all__ = [
    "configure_dspy",
    "get_lm",
    "reset_dspy",
    "quick_setup",
    "signatures",
    "TradingAgentsProgram",
    "TradingResult",
]

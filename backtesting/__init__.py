"""
Backtesting Infrastructure for TradingAgents

This module provides comprehensive backtesting capabilities for the TradingAgents framework,
enabling performance validation and comparison between LangGraph and DSPy implementations.

Based on the TradingAgents paper (arXiv:2412.20138):
- Testing Period: June - November 2024 (5 months)
- Stocks: AAPL, GOOGL, AMZN
- Metrics: CR%, ARR%, Sharpe Ratio, MDD%
- Benchmarks: Buy & Hold, MACD, KDJ & RSI, ZMR, SMA
"""

from .portfolio import Portfolio, Position
from .metrics import MetricsCalculator
from .benchmarks import (
    BuyAndHoldStrategy,
    MACDStrategy,
    RSIStrategy,
    SMAStrategy,
    KDJStrategy,
    ZMRStrategy,
)
from .backtester import Backtester
from .data_loader import DataLoader

__all__ = [
    "Portfolio",
    "Position",
    "MetricsCalculator",
    "BuyAndHoldStrategy",
    "MACDStrategy",
    "RSIStrategy",
    "SMAStrategy",
    "KDJStrategy",
    "ZMRStrategy",
    "Backtester",
    "DataLoader",
]

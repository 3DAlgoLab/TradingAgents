"""
Benchmark trading strategies for comparison.

Implements baseline strategies from the TradingAgents paper:
- Buy & Hold (B&H)
- MACD
- RSI
- KDJ (to be implemented)
- ZMR - Zero Mean Reversion (to be implemented)
- SMA - Simple Moving Average
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        self.name = name
        self.signals: List[Dict] = []

    @abstractmethod
    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """
        Generate trading signal for given date.

        Args:
            ticker: Stock symbol
            date: Current date
            data: Historical price data up to current date

        Returns:
            Signal: 'BUY', 'SELL', or 'HOLD'
        """
        pass

    def record_signal(self, date: datetime, signal: str, price: float):
        """Record generated signal."""
        self.signals.append(
            {
                "date": date,
                "signal": signal,
                "price": price,
            }
        )


class BuyAndHoldStrategy(BaseStrategy):
    """
    Buy and Hold strategy.

    Buys at the start and holds until the end.
    Simple market benchmark.
    """

    def __init__(self):
        super().__init__("Buy & Hold")
        self.has_bought = False

    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """Buy on first day, hold forever."""
        if not self.has_bought and len(data) > 0:
            self.has_bought = True
            current_price = data["Close"].iloc[-1]
            self.record_signal(date, "BUY", current_price)
            return "BUY"

        return "HOLD"


class MACDStrategy(BaseStrategy):
    """
    MACD (Moving Average Convergence Divergence) strategy.

    Uses MACD line and Signal line crossovers:
    - BUY when MACD crosses above Signal
    - SELL when MACD crosses below Signal

    Default parameters: fast=12, slow=26, signal=9
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ):
        super().__init__(f"MACD({fast_period},{slow_period},{signal_period})")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.position = 0  # 0 = no position, 1 = long

    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """Generate MACD crossover signal."""
        if len(data) < self.slow_period + self.signal_period:
            return "HOLD"  # Not enough data

        # Calculate MACD
        exp1 = data["Close"].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = data["Close"].ewm(span=self.slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period, adjust=False).mean()

        # Get current and previous values
        macd_current = macd.iloc[-1]
        macd_prev = macd.iloc[-2]
        signal_current = signal.iloc[-1]
        signal_prev = signal.iloc[-2]

        current_price = data["Close"].iloc[-1]

        # Check for crossover
        # Buy: MACD crosses above Signal
        if macd_prev <= signal_prev and macd_current > signal_current:
            if self.position == 0:
                self.position = 1
                self.record_signal(date, "BUY", current_price)
                return "BUY"

        # Sell: MACD crosses below Signal
        elif macd_prev >= signal_prev and macd_current < signal_current:
            if self.position == 1:
                self.position = 0
                self.record_signal(date, "SELL", current_price)
                return "SELL"

        return "HOLD"


class RSIStrategy(BaseStrategy):
    """
    RSI (Relative Strength Index) strategy.

    Uses RSI overbought/oversold levels:
    - BUY when RSI < oversold_threshold (default 30)
    - SELL when RSI > overbought_threshold (default 70)

    Default period: 14
    """

    def __init__(
        self,
        period: int = 14,
        oversold: int = 30,
        overbought: int = 70,
    ):
        super().__init__(f"RSI({period})")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.position = 0

    def _calculate_rsi(self, prices: pd.Series) -> float:
        """Calculate RSI for price series."""
        deltas = prices.diff()

        # Separate gains and losses
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=self.period).mean()
        avg_losses = losses.rolling(window=self.period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """Generate RSI signal."""
        if len(data) < self.period + 1:
            return "HOLD"

        rsi = self._calculate_rsi(data["Close"])
        current_price = data["Close"].iloc[-1]

        # Buy signal: RSI below oversold threshold
        if rsi < self.oversold and self.position == 0:
            self.position = 1
            self.record_signal(date, "BUY", current_price)
            return "BUY"

        # Sell signal: RSI above overbought threshold
        elif rsi > self.overbought and self.position == 1:
            self.position = 0
            self.record_signal(date, "SELL", current_price)
            return "SELL"

        return "HOLD"


class SMAStrategy(BaseStrategy):
    """
    Simple Moving Average crossover strategy.

    Uses short and long SMA crossovers:
    - BUY when short SMA crosses above long SMA
    - SELL when short SMA crosses below long SMA

    Default: short=50, long=200 (Golden/Death Cross)
    """

    def __init__(
        self,
        short_period: int = 50,
        long_period: int = 200,
    ):
        super().__init__(f"SMA({short_period},{long_period})")
        self.short_period = short_period
        self.long_period = long_period
        self.position = 0

    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """Generate SMA crossover signal."""
        if len(data) < self.long_period:
            return "HOLD"

        # Calculate SMAs
        short_sma = data["Close"].rolling(window=self.short_period).mean()
        long_sma = data["Close"].rolling(window=self.long_period).mean()

        # Get current and previous values
        short_current = short_sma.iloc[-1]
        short_prev = short_sma.iloc[-2]
        long_current = long_sma.iloc[-1]
        long_prev = long_sma.iloc[-2]

        current_price = data["Close"].iloc[-1]

        # Buy: Short crosses above Long
        if short_prev <= long_prev and short_current > long_current:
            if self.position == 0:
                self.position = 1
                self.record_signal(date, "BUY", current_price)
                return "BUY"

        # Sell: Short crosses below Long
        elif short_prev >= long_prev and short_current < long_current:
            if self.position == 1:
                self.position = 0
                self.record_signal(date, "SELL", current_price)
                return "SELL"

        return "HOLD"


class KDJStrategy(BaseStrategy):
    """
    KDJ Indicator strategy (Stochastic Oscillator variant).

    Popular in Asian markets. Uses K, D, and J lines.
    - BUY when K crosses above D in oversold region
    - SELL when K crosses below D in overbought region

    Note: Simplified implementation. Full KDJ is more complex.
    """

    def __init__(
        self,
        period: int = 9,
        smooth_k: int = 3,
        smooth_d: int = 3,
    ):
        super().__init__(f"KDJ({period})")
        self.period = period
        self.smooth_k = smooth_k
        self.smooth_d = smooth_d
        self.position = 0

    def _calculate_kdj(self, data: pd.DataFrame) -> tuple:
        """Calculate K, D, J values."""
        # Calculate RSV (Raw Stochastic Value)
        low_min = data["Low"].rolling(window=self.period).min()
        high_max = data["High"].rolling(window=self.period).max()

        rsv = 100 * (data["Close"] - low_min) / (high_max - low_min)

        # Calculate K (fast %K)
        k = rsv.ewm(com=self.smooth_k - 1, adjust=False).mean()

        # Calculate D (slow %D)
        d = k.ewm(com=self.smooth_d - 1, adjust=False).mean()

        # Calculate J
        j = 3 * k - 2 * d

        return k.iloc[-1], d.iloc[-1], j.iloc[-1]

    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """Generate KDJ signal."""
        if len(data) < self.period + max(self.smooth_k, self.smooth_d):
            return "HOLD"

        k, d, j = self._calculate_kdj(data)
        current_price = data["Close"].iloc[-1]

        # Buy: K crosses above D in oversold region (< 20)
        if k > d and self.position == 0 and k < 20:
            self.position = 1
            self.record_signal(date, "BUY", current_price)
            return "BUY"

        # Sell: K crosses below D in overbought region (> 80)
        elif k < d and self.position == 1 and k > 80:
            self.position = 0
            self.record_signal(date, "SELL", current_price)
            return "SELL"

        return "HOLD"


class ZMRStrategy(BaseStrategy):
    """
    Zero Mean Reversion (ZMR) strategy.

    Mean reversion strategy based on price deviation from moving average.
    - BUY when price significantly below MA (oversold)
    - SELL when price significantly above MA (overbought)

    Uses Z-score to measure deviation.
    """

    def __init__(
        self,
        period: int = 20,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
    ):
        super().__init__(f"ZMR({period})")
        self.period = period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.position = 0

    def generate_signal(self, ticker: str, date: datetime, data: pd.DataFrame) -> str:
        """Generate ZMR signal."""
        if len(data) < self.period:
            return "HOLD"

        # Calculate Z-score
        prices = data["Close"]
        ma = prices.rolling(window=self.period).mean()
        std = prices.rolling(window=self.period).std()

        z_score = (prices.iloc[-1] - ma.iloc[-1]) / std.iloc[-1]
        current_price = prices.iloc[-1]

        # Buy: Price significantly below mean (oversold)
        if z_score < -self.entry_threshold and self.position == 0:
            self.position = 1
            self.record_signal(date, "BUY", current_price)
            return "BUY"

        # Sell: Price reverts to mean or goes significantly above
        elif self.position == 1:
            if z_score > -self.exit_threshold or z_score > self.entry_threshold:
                self.position = 0
                self.record_signal(date, "SELL", current_price)
                return "SELL"

        return "HOLD"

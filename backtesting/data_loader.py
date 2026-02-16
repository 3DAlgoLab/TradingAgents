"""
Data loading utilities for backtesting.

Handles downloading and caching of historical price data.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import pandas as pd
import yfinance as yf


class DataLoader:
    """
    Load and cache historical stock data for backtesting.

    Uses yfinance as the data source and caches data locally
    to avoid repeated API calls.
    """

    def __init__(self, cache_dir: str = "backtesting/data_cache"):
        """
        Initialize data loader.

        Args:
            cache_dir: Directory to cache downloaded data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self._data_cache: Dict[str, pd.DataFrame] = {}

    def load_data(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Load historical price data for a ticker.

        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            start_date: Start date for data
            end_date: End date for data
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with OHLCV data
        """
        cache_key = (
            f"{ticker}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        )

        # Check memory cache
        if use_cache and cache_key in self._data_cache:
            return self._data_cache[cache_key].copy()

        # Check file cache
        cache_file = os.path.join(
            self.cache_dir,
            f"{ticker}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
        )

        if use_cache and os.path.exists(cache_file):
            df = pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
            self._data_cache[cache_key] = df
            return df.copy()

        # Download from yfinance
        print(
            f"Downloading data for {ticker} from {start_date.date()} to {end_date.date()}..."
        )

        ticker_obj = yf.Ticker(ticker.upper())

        # Add buffer days for indicator calculation
        buffer_start = start_date - timedelta(days=365)  # 1 year buffer

        df = ticker_obj.history(
            start=buffer_start.strftime("%Y-%m-%d"),
            end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        )

        if df.empty:
            raise ValueError(f"No data found for {ticker}")

        # Clean up index
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        df.index.name = "Date"

        # Cache the data
        if use_cache:
            df.to_csv(cache_file)
            self._data_cache[cache_key] = df

        return df.copy()

    def get_price(self, ticker: str, date: datetime, data: pd.DataFrame) -> float:
        """
        Get price for a specific date.

        Uses Close price if available, otherwise tries to find nearest trading day.

        Args:
            ticker: Stock symbol
            date: Target date
            data: Price data DataFrame

        Returns:
            Closing price
        """
        date_key = pd.Timestamp(date)

        # Try exact date
        if date_key in data.index:
            return data.loc[date_key, "Close"]

        # Find nearest previous trading day
        valid_dates = data.index[data.index <= date_key]
        if len(valid_dates) == 0:
            raise ValueError(
                f"No price data available for {ticker} on or before {date}"
            )

        nearest_date = valid_dates[-1]
        return data.loc[nearest_date, "Close"]

    def get_data_up_to(self, data: pd.DataFrame, date: datetime) -> pd.DataFrame:
        """
        Get data up to and including a specific date.

        Args:
            data: Full price data DataFrame
            date: Cutoff date

        Returns:
            Filtered DataFrame
        """
        return data[data.index <= pd.Timestamp(date)]

    def get_trading_days(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list:
        """
        Get list of trading days for a ticker in date range.

        Args:
            ticker: Stock symbol
            start_date: Start date
            end_date: End date

        Returns:
            List of trading days (datetime objects)
        """
        data = self.load_data(ticker, start_date, end_date)

        # Filter to requested date range
        mask = (data.index >= start_date) & (data.index <= end_date)
        filtered = data[mask]

        return filtered.index.tolist()

    def clear_cache(self):
        """Clear all cached data."""
        self._data_cache.clear()

        # Clear file cache
        for file in os.listdir(self.cache_dir):
            if file.endswith(".csv"):
                os.remove(os.path.join(self.cache_dir, file))

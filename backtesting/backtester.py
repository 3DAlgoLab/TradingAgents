"""
Main backtesting engine.

Simulates trading over historical periods and calculates performance metrics.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, List, Any
import pandas as pd

from .portfolio import Portfolio
from .metrics import MetricsCalculator, PerformanceMetrics
from .data_loader import DataLoader
from .benchmarks import BaseStrategy


class Backtester:
    """
    Main backtesting engine for TradingAgents.

    Simulates trading over historical periods:
    1. Iterates through each trading day
    2. Generates trading signal (from strategy or TradingAgents)
    3. Executes trades
    4. Records portfolio snapshots
    5. Calculates performance metrics
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        data_loader: Optional[DataLoader] = None,
    ):
        """
        Initialize backtester.

        Args:
            initial_capital: Starting portfolio value
            data_loader: DataLoader instance (creates new one if None)
        """
        self.initial_capital = initial_capital
        self.data_loader = data_loader or DataLoader()
        self.results: Dict[str, Any] = {}

    def run_backtest(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        strategy: BaseStrategy,
    ) -> Dict[str, Any]:
        """
        Run backtest for a single ticker with a strategy.

        Args:
            ticker: Stock symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            strategy: Trading strategy to test

        Returns:
            Dictionary with backtest results
        """
        print(f"\n{'=' * 60}")
        print(f"Running Backtest: {ticker}")
        print(f"Strategy: {strategy.name}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"{'=' * 60}\n")

        # Load data
        data = self.data_loader.load_data(ticker, start_date, end_date)

        # Initialize portfolio
        portfolio = Portfolio(self.initial_capital)

        # Get trading days in range
        trading_days = self.data_loader.get_trading_days(ticker, start_date, end_date)

        if len(trading_days) == 0:
            raise ValueError(f"No trading days found for {ticker} in specified range")

        print(f"Total trading days: {len(trading_days)}")

        # Run simulation
        for i, date in enumerate(trading_days):
            # Get data up to current date
            current_data = self.data_loader.get_data_up_to(data, date)

            if len(current_data) < 2:
                continue

            # Get current price
            current_price = current_data["Close"].iloc[-1]
            prices = {ticker: current_price}

            # Generate trading signal
            signal = strategy.generate_signal(ticker, date, current_data)

            # Execute trades
            if signal == "BUY":
                # Calculate position size (invest all cash)
                cash = portfolio.cash
                if cash > 0:
                    shares = cash / current_price
                    if portfolio.buy(ticker, shares, current_price, date):
                        print(
                            f"[{date.date()}] BUY {shares:.2f} shares @ ${current_price:.2f}"
                        )

            elif signal == "SELL":
                # Sell all shares
                position = portfolio.get_position(ticker)
                shares_to_sell = position.shares
                if shares_to_sell > 0:
                    portfolio.sell(ticker, shares_to_sell, current_price, date)
                    print(
                        f"[{date.date()}] SELL {shares_to_sell:.2f} shares @ ${current_price:.2f}"
                    )

            # Record snapshot after trading
            portfolio.record_snapshot(date, prices)

            # Progress indicator
            if (i + 1) % 20 == 0 or i == len(trading_days) - 1:
                progress = (i + 1) / len(trading_days) * 100
                print(f"Progress: {progress:.1f}% ({i + 1}/{len(trading_days)} days)")

        # Get final portfolio value
        final_data = data[data.index <= end_date]
        if len(final_data) > 0:
            final_price = final_data["Close"].iloc[-1]
            final_value = portfolio.get_total_value({ticker: final_price})
        else:
            final_value = portfolio.cash

        # Calculate metrics
        portfolio_df = portfolio.get_history_df()
        trades_df = portfolio.get_trades_df()

        metrics = MetricsCalculator.calculate_all_metrics(
            portfolio_df["total_value"],
            trades_df,
        )

        # Compile results
        results = {
            "ticker": ticker,
            "strategy": strategy.name,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return_pct": ((final_value / self.initial_capital) - 1) * 100,
            "num_trades": len(trades_df),
            "metrics": metrics,
            "portfolio_history": portfolio_df,
            "trades": trades_df,
            "signals": pd.DataFrame(strategy.signals),
        }

        # Store results
        self.results[f"{ticker}_{strategy.name}"] = results

        # Print summary
        self._print_summary(results)

        return results

    def run_tradingagents_backtest(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        trading_graph: Any,  # TradingAgentsGraph instance
    ) -> Dict[str, Any]:
        """
        Run backtest using the TradingAgents framework.

        Args:
            ticker: Stock symbol
            start_date: Start date
            end_date: End date
            trading_graph: Initialized TradingAgentsGraph instance

        Returns:
            Dictionary with backtest results
        """
        print(f"\n{'=' * 60}")
        print(f"Running TradingAgents Backtest: {ticker}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"{'=' * 60}\n")

        # Load data
        data = self.data_loader.load_data(ticker, start_date, end_date)

        # Initialize portfolio
        portfolio = Portfolio(self.initial_capital)

        # Get trading days
        trading_days = self.data_loader.get_trading_days(ticker, start_date, end_date)

        print(f"Total trading days: {len(trading_days)}")

        signals = []

        # Run simulation
        for i, date in enumerate(trading_days):
            date_str = date.strftime("%Y-%m-%d")

            # Get current price
            current_price = self.data_loader.get_price(ticker, date, data)
            prices = {ticker: current_price}

            # Get TradingAgents decision
            try:
                final_state, decision = trading_graph.propagate(ticker, date_str)

                # Parse decision (expecting "BUY", "SELL", or "HOLD")
                signal = "HOLD"
                if "buy" in decision.lower():
                    signal = "BUY"
                elif "sell" in decision.lower():
                    signal = "SELL"

                signals.append(
                    {
                        "date": date,
                        "signal": signal,
                        "raw_decision": decision,
                        "price": current_price,
                    }
                )

                # Execute trade
                if signal == "BUY":
                    cash = portfolio.cash
                    if cash > 0:
                        shares = cash / current_price
                        if portfolio.buy(ticker, shares, current_price, date):
                            print(
                                f"[{date.date()}] BUY {shares:.2f} shares @ ${current_price:.2f}"
                            )

                elif signal == "SELL":
                    position = portfolio.get_position(ticker)
                    shares_to_sell = position.shares
                    if shares_to_sell > 0:
                        if portfolio.sell(ticker, shares_to_sell, current_price, date):
                            print(
                                f"[{date.date()}] SELL {shares_to_sell:.2f} shares @ ${current_price:.2f}"
                            )

            except Exception as e:
                print(f"Error on {date.date()}: {e}")
                signals.append(
                    {
                        "date": date,
                        "signal": "ERROR",
                        "error": str(e),
                        "price": current_price,
                    }
                )

            # Record snapshot after trading
            portfolio.record_snapshot(date, prices)

            # Progress indicator
            if (i + 1) % 5 == 0 or i == len(trading_days) - 1:
                progress = (i + 1) / len(trading_days) * 100
                print(f"Progress: {progress:.1f}% ({i + 1}/{len(trading_days)} days)")

        # Get final value
        final_data = data[data.index <= end_date]
        if len(final_data) > 0:
            final_price = final_data["Close"].iloc[-1]
            final_value = portfolio.get_total_value({ticker: final_price})
        else:
            final_value = portfolio.cash

        # Calculate metrics
        portfolio_df = portfolio.get_history_df()
        trades_df = portfolio.get_trades_df()

        metrics = MetricsCalculator.calculate_all_metrics(
            portfolio_df["total_value"],
            trades_df,
        )

        # Compile results
        results = {
            "ticker": ticker,
            "strategy": "TradingAgents",
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return_pct": ((final_value / self.initial_capital) - 1) * 100,
            "num_trades": len(trades_df),
            "metrics": metrics,
            "portfolio_history": portfolio_df,
            "trades": trades_df,
            "signals": pd.DataFrame(signals),
        }

        self.results[f"{ticker}_TradingAgents"] = results

        self._print_summary(results)

        return results

    def _print_summary(self, results: Dict[str, Any]):
        """Print backtest summary."""
        print(f"\n{'=' * 60}")
        print(f"BACKTEST SUMMARY: {results['ticker']} - {results['strategy']}")
        print(f"{'=' * 60}")
        print(f"Period: {results['start_date'].date()} to {results['end_date'].date()}")
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Value: ${results['final_value']:,.2f}")
        print(f"Total Return: {results['total_return_pct']:.2f}%")
        print(f"Number of Trades: {results['num_trades']}")
        print(f"\nPerformance Metrics:")
        print(
            f"  Cumulative Return (CR%): {results['metrics'].cumulative_return_pct:.2f}%"
        )
        print(
            f"  Annualized Return (ARR%): {results['metrics'].annualized_return_pct:.2f}%"
        )
        print(f"  Sharpe Ratio: {results['metrics'].sharpe_ratio:.2f}")
        print(f"  Max Drawdown (MDD%): {results['metrics'].max_drawdown_pct:.2f}%")
        print(f"  Volatility: {results['metrics'].volatility_pct:.2f}%")
        if results["metrics"].win_rate_pct:
            print(f"  Win Rate: {results['metrics'].win_rate_pct:.2f}%")
        print(f"{'=' * 60}\n")

    def compare_strategies(
        self,
        ticker: str,
        results_list: List[Dict[str, Any]],
    ) -> str:
        """
        Compare multiple strategies for a ticker.

        Args:
            ticker: Stock symbol
            results_list: List of backtest results

        Returns:
            Formatted comparison table
        """
        print(f"\n{'=' * 80}")
        print(f"STRATEGY COMPARISON: {ticker}")
        print(f"{'=' * 80}\n")

        metrics_list = [r["metrics"].to_dict() for r in results_list]
        names = [r["strategy"] for r in results_list]

        comparison = MetricsCalculator.format_metrics_table(metrics_list, names)
        print(comparison)

        return comparison

    def save_results(self, results: Dict[str, Any], filepath: str):
        """
        Save backtest results to files.

        Args:
            results: Backtest results dictionary
            filepath: Base filepath for saving
        """
        import json

        # Save metrics as JSON
        metrics_file = filepath.replace(".json", "_metrics.json")
        metrics_dict = {
            "ticker": results["ticker"],
            "strategy": results["strategy"],
            "start_date": results["start_date"].strftime("%Y-%m-%d"),
            "end_date": results["end_date"].strftime("%Y-%m-%d"),
            "initial_capital": results["initial_capital"],
            "final_value": results["final_value"],
            "total_return_pct": results["total_return_pct"],
            "num_trades": results["num_trades"],
            "metrics": results["metrics"].to_dict(),
        }

        with open(metrics_file, "w") as f:
            json.dump(metrics_dict, f, indent=2)

        # Save portfolio history
        history_file = filepath.replace(".json", "_history.csv")
        results["portfolio_history"].to_csv(history_file)

        # Save trades
        if not results["trades"].empty:
            trades_file = filepath.replace(".json", "_trades.csv")
            results["trades"].to_csv(trades_file)

        # Save signals
        if not results["signals"].empty:
            signals_file = filepath.replace(".json", "_signals.csv")
            results["signals"].to_csv(signals_file)

        print(f"Results saved to: {filepath.replace('.json', '*')}")

#!/usr/bin/env python3
"""
Backtest Runner for TradingAgents

This script runs backtests for the TradingAgents framework and benchmark strategies.
Based on the TradingAgents paper (arXiv:2412.20138):
- Testing Period: June - November 2024 (5 months)
- Stocks: AAPL, GOOGL, AMZN
- Metrics: CR%, ARR%, Sharpe Ratio, MDD%

Usage:
    python backtest_runner.py --ticker AAPL --strategy all
    python backtest_runner.py --ticker AAPL --strategy TradingAgents
    python backtest_runner.py --all --start-date 2024-06-01 --end-date 2024-11-30
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from tradingagents.default_config import DEFAULT_CONFIG

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backtesting import (
    Backtester,
    DataLoader,
    BuyAndHoldStrategy,
    MACDStrategy,
    RSIStrategy,
    SMAStrategy,
    KDJStrategy,
    ZMRStrategy,
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run backtests for TradingAgents and benchmark strategies"
    )

    parser.add_argument(
        "--ticker",
        type=str,
        default="AAPL",
        help="Stock ticker symbol (default: AAPL)",
    )

    parser.add_argument(
        "--strategy",
        type=str,
        default="all",
        choices=["all", "buyhold", "macd", "rsi", "sma", "kdj", "zmr", "TradingAgents"],
        help="Strategy to backtest (default: all)",
    )

    parser.add_argument(
        "--start-date",
        type=str,
        default="2024-06-01",
        help="Start date for backtest (YYYY-MM-DD, default: 2024-06-01)",
    )

    parser.add_argument(
        "--end-date",
        type=str,
        default="2024-11-30",
        help="End date for backtest (YYYY-MM-DD, default: 2024-11-30)",
    )

    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000.0,
        help="Initial capital (default: 100000)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run backtest on all paper tickers (AAPL, GOOGL, AMZN)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="backtesting/results",
        help="Output directory for results (default: backtesting/results)",
    )

    parser.add_argument(
        "--tradingagents",
        action="store_true",
        help="Include TradingAgents strategy (requires API keys)",
    )

    return parser.parse_args()


def run_benchmark_backtests(
    backtester: Backtester,
    ticker: str,
    start_date: datetime,
    end_date: datetime,
    strategies: list,
) -> list:
    """Run benchmark strategy backtests."""
    results = []

    strategy_map = {
        "buyhold": BuyAndHoldStrategy(),
        "macd": MACDStrategy(),
        "rsi": RSIStrategy(),
        "sma": SMAStrategy(),
        "kdj": KDJStrategy(),
        "zmr": ZMRStrategy(),
    }

    for strategy_name in strategies:
        if strategy_name in strategy_map:
            try:
                result = backtester.run_backtest(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    strategy=strategy_map[strategy_name],
                )
                results.append(result)
            except Exception as e:
                print(f"Error running {strategy_name} strategy: {e}")

    return results


def run_tradingagents_backtest(
    backtester: Backtester,
    ticker: str,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    """Run TradingAgents backtest."""
    load_dotenv()
    config = DEFAULT_CONFIG.copy()

    # Configure which LLM models to use for different thinking tasks:
    # - deep_think_llm: Used for complex reasoning (research debates, risk analysis)
    # - quick_think_llm: Used for simpler tasks (data fetching, basic analysis)
    config["deep_think_llm"] = (
        "qwen/qwen3-coder-next"  # Model for complex reasoning tasks
    )
    config["quick_think_llm"] = "qwen/qwen3-coder-next"  # Model for quick/simple tasks

    # Set the maximum number of debate rounds between bull/bear researchers
    # Higher values = more thorough analysis but slower execution and higher API costs
    config["max_debate_rounds"] = 1

    # Configure which data vendors to use for fetching market data
    # Options: "yfinance" (free, uses Yahoo Finance) or "alpha_vantage" (requires API key)
    # Default uses yfinance which requires no additional API keys
    config["data_vendors"] = {
        "core_stock_apis": "yfinance",  # For basic stock price/volume data
        "technical_indicators": "yfinance",  # For technical indicators (MACD, RSI, etc.)
        "fundamental_data": "yfinance",  # For financial statements, fundamentals
        "news_data": "yfinance",  # For news articles and sentiment data
    }

    try:
        # Import TradingAgents
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        print("\nInitializing TradingAgents...")
        trading_graph = TradingAgentsGraph(
            selected_analysts=["market", "social", "news", "fundamentals"],
            debug=False,
            config=config,
            recursion_limit=150,
        )

        result = backtester.run_tradingagents_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            trading_graph=trading_graph,
        )

        return result

    except ImportError as e:
        print(f"Error importing TradingAgents: {e}")
        print("Make sure you're running from the project root.")
        return None
    except Exception as e:
        print(f"Error running TradingAgents backtest: {e}")
        return None


def main():
    """Main entry point."""
    args = parse_args()

    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Determine tickers to test
    if args.all:
        tickers = ["AAPL", "GOOGL", "AMZN"]
    else:
        tickers = [args.ticker]

    # Determine strategies to test
    if args.strategy == "all":
        strategies = ["buyhold", "macd", "rsi", "sma"]
    else:
        strategies = [args.strategy]

    # Initialize backtester
    backtester = Backtester(initial_capital=args.initial_capital)

    print("=" * 80)
    print("TRADINGAGENTS BACKTESTING FRAMEWORK")
    print("=" * 80)
    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"Initial Capital: ${args.initial_capital:,.2f}")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Strategies: {', '.join(strategies)}")
    if args.tradingagents:
        print("Include TradingAgents: Yes")
    print("=" * 80)

    # Run backtests for each ticker
    all_results = {}

    for ticker in tickers:
        print(f"\n\n{'=' * 80}")
        print(f"BACKTESTING: {ticker}")
        print(f"{'=' * 80}\n")

        ticker_results = []

        # Run benchmark strategies
        if args.strategy in ["all", "buyhold", "macd", "rsi", "sma", "kdj", "zmr"]:
            benchmark_results = run_benchmark_backtests(
                backtester, ticker, start_date, end_date, strategies
            )
            ticker_results.extend(benchmark_results)

        # Run TradingAgents if requested
        if args.tradingagents or args.strategy == "TradingAgents":
            ta_result = run_tradingagents_backtest(
                backtester, ticker, start_date, end_date
            )
            if ta_result:
                ticker_results.append(ta_result)

        # Compare strategies
        if len(ticker_results) > 1:
            backtester.compare_strategies(ticker, ticker_results)

        # Save results
        for result in ticker_results:
            output_file = os.path.join(
                args.output_dir,
                f"{ticker}_{result['strategy']}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json",
            )
            backtester.save_results(result, output_file)

        all_results[ticker] = ticker_results

    # Final summary
    print(f"\n\n{'=' * 80}")
    print("BACKTEST COMPLETE")
    print(f"{'=' * 80}")
    print(f"Results saved to: {args.output_dir}")
    print(f"Total backtests run: {sum(len(r) for r in all_results.values())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

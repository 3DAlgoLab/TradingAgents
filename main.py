# Import the main TradingAgentsGraph class - this is the entry point to the framework
from tradingagents.graph.trading_graph import TradingAgentsGraph

# Import the default configuration dictionary with all preset values
from tradingagents.default_config import DEFAULT_CONFIG

# Import function to load environment variables from .env file
from dotenv import load_dotenv

# Load environment variables from .env file (contains API keys like OPENAI_API_KEY, GOOGLE_API_KEY, etc.)
# This must be called before creating LLM clients that need those API keys
load_dotenv()

# Create a custom configuration by copying the default config
# We use .copy() to avoid modifying the original DEFAULT_CONFIG
config = DEFAULT_CONFIG.copy()

# Configure which LLM models to use for different thinking tasks:
# - deep_think_llm: Used for complex reasoning (research debates, risk analysis)
# - quick_think_llm: Used for simpler tasks (data fetching, basic analysis)
config["deep_think_llm"] = "qwen/qwen3-coder-next"  # Model for complex reasoning tasks
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

# Create an instance of TradingAgentsGraph with our custom configuration
# debug=True: Enables verbose output showing each agent's progress
# config=config: Uses our customized configuration settings
ta = TradingAgentsGraph(debug=True, config=config)

# Execute the trading analysis workflow for NVIDIA (NVDA) on the specified date
# The propagate() method runs all agents in sequence:
# 1. Analysts gather market, news, sentiment, and fundamental data
# 2. Researchers debate bull vs bear cases
# 3. Trader creates an investment plan
# 4. Risk managers evaluate the plan
# 5. Portfolio manager makes final decision
# Returns: (final_state_dict, trade_decision)
_, decision = ta.propagate("NVDA", "2026-02-13")

# Print the final trading decision (BUY, SELL, or HOLD with reasoning)
print(decision)

# Optional: Reflection and learning feature (currently commented out)
# After executing trades in real markets, you can call reflect_and_remember()
# with the actual returns/losses to help agents learn from their decisions
# The parameter represents the dollar amount gained (+) or lost (-) from the trade
# ta.reflect_and_remember(1000)  # Example: trade made $1000 profit

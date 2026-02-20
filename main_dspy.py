"""DSPy-based TradingAgents main entry point.

This is the main entry point for the DSPy-based TradingAgents implementation.
It provides a simple API similar to the original LangGraph version.
"""

from dotenv import load_dotenv
from tradingagents_dspy.config import DEFAULT_CONFIG, configure_dspy
from tradingagents_dspy.program import TradingAgentsProgram

load_dotenv()

config = DEFAULT_CONFIG.copy()

config["deep_think_llm"] = "qwen/qwen3-coder-next"
config["quick_think_llm"] = "qwen/qwen3-coder-next"
config["num_debate_rounds"] = 1
config["enable_memory"] = False

print("Configuring DSPy...")
configure_dspy(config)

print("Creating TradingAgentsProgram...")
ta = TradingAgentsProgram(config=config)

print("\nRunning TradingAgents DSPy for NVDA on 2026-02-13...")
_, decision = ta.propagate("NVDA", "2026-02-13")

print(decision)

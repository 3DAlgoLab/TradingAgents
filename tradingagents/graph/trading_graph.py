# TradingAgents/graph/trading_graph.py
# This is the main orchestration module that sets up and runs the multi-agent trading workflow.
# It uses LangGraph to create a stateful graph where different AI agents collaborate to make trading decisions.

# Standard library imports for file operations, path handling, JSON serialization, dates, and type hints
import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

# LangGraph import for creating tool nodes - these are special nodes that can execute functions/tools
from langgraph.prebuilt import ToolNode

# Import the LLM client factory to create language model clients for different providers (OpenAI, Google, Anthropic, etc.)
from tradingagents.llm_clients import create_llm_client

# Import default configuration dictionary containing preset values for the framework
from tradingagents.default_config import DEFAULT_CONFIG

# Import memory management for storing agent context and financial situations
from tradingagents.agents.utils.memory import FinancialSituationMemory

# Import type definitions for the graph state - these define the structure of data flowing through the graph
from tradingagents.agents.utils.agent_states import (
    AgentState,  # Main state type for the entire graph
    InvestDebateState,  # State type for bull/bear researcher debates
    RiskDebateState,  # State type for risk management debates
)

# Import configuration setter for the data interface layer
from tradingagents.dataflows.config import set_config

# Import tool functions that agents can call to fetch market data
# These are the actual functions bound to LLMs as "tools" they can invoke
from tradingagents.agents.utils.agent_utils import (
    get_stock_data,  # Fetch stock price/volume data
    get_indicators,  # Fetch technical indicators (MACD, RSI, etc.)
    get_fundamentals,  # Fetch company fundamentals/profile
    get_balance_sheet,  # Fetch balance sheet data
    get_cashflow,  # Fetch cash flow statement
    get_income_statement,  # Fetch income statement
    get_news,  # Fetch news articles
    get_insider_transactions,  # Fetch insider trading data
    get_global_news,  # Fetch global market news
)

# Import modular components that handle different aspects of the graph:
from .conditional_logic import (
    ConditionalLogic,
)  # Logic for determining graph flow (which node to go to next)
from .setup import (
    GraphSetup,
)  # Sets up the LangGraph structure with all nodes and edges
from .propagation import Propagator  # Handles state initialization and graph execution
from .reflection import (
    Reflector,
)  # Handles post-trade reflection and learning from results
from .signal_processing import (
    SignalProcessor,
)  # Processes raw LLM outputs into actionable trading signals


class TradingAgentsGraph:
    """Main orchestrator class that manages the entire multi-agent trading workflow.

    This class:
    1. Initializes LLM clients for different thinking tasks (deep vs quick)
    2. Sets up memory systems for each agent type
    3. Creates tool nodes that agents can use to fetch data
    4. Builds the LangGraph with all agents and their connections
    5. Provides methods to run analysis and process results

    The workflow follows this sequence:
    Analysts → Researchers (Bull/Bear debate) → Trader → Risk Managers (debate) → Portfolio Manager
    """

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
        callbacks: Optional[List] = None,
    ):
        """Initialize the trading agents graph with all necessary components.

        Args:
            selected_analysts: List of analyst types to include in the analysis.
                              Options: "market", "social" (sentiment), "news", "fundamentals"
            debug: If True, enables verbose output showing each agent's progress
            config: Configuration dictionary. If None, uses DEFAULT_CONFIG
            callbacks: Optional list of callback handlers for tracking LLM calls,
                      token usage, tool executions (used by CLI for statistics)
        """
        # Store initialization parameters as instance attributes
        self.debug = debug
        # Use provided config or fall back to default, ensuring we have a valid config dict
        self.config = config or DEFAULT_CONFIG
        # Store callbacks for LLM/tool tracking (can be None)
        self.callbacks = callbacks or []

        # Update the data interface's configuration
        # This ensures data fetching tools use the same config (e.g., which data vendor to use)
        set_config(self.config)

        # Create the data cache directory if it doesn't exist
        # This is where downloaded stock data, news, etc. are stored locally
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,  # Don't raise error if directory already exists
        )

        # Get provider-specific configuration parameters
        # Different LLM providers have different settings (e.g., Google's thinking_level, OpenAI's reasoning_effort)
        llm_kwargs = self._get_provider_kwargs()

        # Add callbacks to the LLM kwargs if provided
        # These callbacks track metrics like token usage, API calls for the CLI display
        if self.callbacks:
            llm_kwargs["callbacks"] = self.callbacks

        # Create the "deep thinking" LLM client for complex reasoning tasks
        # This is used for: researcher debates, risk management debates, portfolio decisions
        deep_client = create_llm_client(
            provider=self.config[
                "llm_provider"
            ],  # e.g., "openai", "google", "anthropic"
            model=self.config["deep_think_llm"],  # e.g., "gpt-5.2", "claude-4"
            base_url=self.config.get("backend_url"),  # Optional custom API endpoint
            **llm_kwargs,  # Provider-specific settings
        )

        # Create the "quick thinking" LLM client for simpler tasks
        # This is used for: data fetching, basic analysis, formatting
        quick_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["quick_think_llm"],  # e.g., "gpt-5-mini" (cheaper/faster)
            base_url=self.config.get("backend_url"),
            **llm_kwargs,
        )

        # Extract the actual LLM objects from the clients
        # These are the objects passed to agents for generating responses
        self.deep_thinking_llm = deep_client.get_llm()
        self.quick_thinking_llm = quick_client.get_llm()

        # Initialize memory systems for each agent type
        # These memories store context about past decisions and market conditions
        # They enable agents to learn from previous trades and maintain context across runs
        self.bull_memory = FinancialSituationMemory(
            "bull_memory", self.config
        )  # Bull researcher memory
        self.bear_memory = FinancialSituationMemory(
            "bear_memory", self.config
        )  # Bear researcher memory
        self.trader_memory = FinancialSituationMemory(
            "trader_memory", self.config
        )  # Trader memory
        self.invest_judge_memory = FinancialSituationMemory(
            "invest_judge_memory", self.config
        )  # Research manager memory
        self.risk_manager_memory = FinancialSituationMemory(
            "risk_manager_memory", self.config
        )  # Risk team memory

        # Create tool nodes for each analyst type
        # Tool nodes are LangGraph components that wrap Python functions as callable tools
        # Agents can invoke these tools to fetch real-time market data
        self.tool_nodes = self._create_tool_nodes()

        # Initialize the graph setup component
        # This object builds the actual LangGraph with all nodes, edges, and conditional routing
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,  # LLM for quick tasks
            self.deep_thinking_llm,  # LLM for complex reasoning
            self.tool_nodes,  # Dictionary of tool nodes for data fetching
            self.bull_memory,  # Research team memories
            self.bear_memory,
            self.trader_memory,  # Trading team memory
            self.invest_judge_memory,  # Research manager memory
            self.risk_manager_memory,  # Risk team memory
            self.conditional_logic,  # Routing logic
        )

        # Initialize supporting components
        self.propagator = Propagator()  # Handles state initialization
        self.reflector = Reflector(self.quick_thinking_llm)  # Post-trade reflection
        self.signal_processor = SignalProcessor(
            self.quick_thinking_llm
        )  # Output processing

        # State tracking attributes
        self.curr_state = None  # Stores the final state after graph execution
        self.ticker = None  # Current ticker being analyzed
        self.log_states_dict = {}  # Dictionary mapping dates to state snapshots (for logging)

        # Build the LangGraph!
        # This creates the complete workflow graph with all agents connected
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _get_provider_kwargs(self) -> Dict[str, Any]:
        """Get provider-specific kwargs for LLM client creation.

        Different LLM providers have unique configuration options:
        - Google (Gemini): thinking_level ("high", "minimal", etc.)
        - OpenAI: reasoning_effort ("low", "medium", "high")

        Returns:
            Dictionary of provider-specific parameters to pass to the LLM client
        """
        kwargs = {}
        # Normalize provider name to lowercase for comparison
        provider = self.config.get("llm_provider", "").lower()

        # Google Gemini-specific: thinking configuration
        if provider == "google":
            thinking_level = self.config.get("google_thinking_level")
            if thinking_level:
                kwargs["thinking_level"] = thinking_level

        # OpenAI-specific: reasoning effort configuration
        elif provider == "openai":
            reasoning_effort = self.config.get("openai_reasoning_effort")
            if reasoning_effort:
                kwargs["reasoning_effort"] = reasoning_effort

        return kwargs

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different analyst types.

        Tool nodes bundle related data-fetching functions together.
        Each analyst type gets access to specific tools relevant to their role.

        Returns:
            Dictionary mapping analyst type to ToolNode containing relevant tools
        """
        return {
            # Market Analyst tools: stock data and technical indicators
            "market": ToolNode(
                [
                    get_stock_data,  # Fetch OHLCV price data
                    get_indicators,  # Calculate technical indicators
                ]
            ),
            # Social Media Analyst tools: news sentiment analysis
            "social": ToolNode(
                [
                    get_news,  # Fetch news for sentiment scoring
                ]
            ),
            # News Analyst tools: comprehensive news + insider data
            "news": ToolNode(
                [
                    get_news,  # Company-specific news
                    get_global_news,  # Broader market news
                    get_insider_transactions,  # Insider trading activity
                ]
            ),
            # Fundamentals Analyst tools: financial statement data
            "fundamentals": ToolNode(
                [
                    get_fundamentals,  # Company profile and key metrics
                    get_balance_sheet,  # Assets, liabilities, equity
                    get_cashflow,  # Operating, investing, financing cash flows
                    get_income_statement,  # Revenue, expenses, profit/loss
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Execute the trading analysis workflow for a specific company and date.

        This is the main entry point to run the complete multi-agent analysis.
        It runs the LangGraph and returns the final state and trading decision.

        Args:
            company_name: Stock ticker symbol (e.g., "AAPL", "NVDA")
            trade_date: Date string in format "YYYY-MM-DD" for historical analysis

        Returns:
            Tuple of (final_state_dict, trade_decision_string)
            - final_state_dict: Complete state containing all agent outputs
            - trade_decision: Processed BUY/SELL/HOLD decision with reasoning
        """
        # Store the current ticker for logging purposes
        self.ticker = company_name

        # Initialize the graph state with company and date information
        # This creates the initial state that flows through the graph
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        # Get graph execution arguments (can include callbacks for tracking)
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode: Stream the graph execution and print each message
            # This shows real-time progress as agents complete their tasks
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass  # Skip empty message chunks
                else:
                    # Pretty print the last message (agent output or tool result)
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            # Get final state from the last chunk
            final_state = trace[-1]
        else:
            # Standard mode: Run graph without streaming output
            # More efficient but doesn't show real-time progress
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store final state for potential reflection later
        self.curr_state = final_state

        # Log the complete state to a JSON file for record-keeping
        self._log_state(trade_date, final_state)

        # Return both the full state and the processed trading decision
        # process_signal extracts the actionable decision from the Portfolio Manager's output
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """Log the complete analysis state to a JSON file for record-keeping.

        This creates a detailed log of all agent outputs, debates, and decisions
        that can be reviewed later for debugging or performance analysis.

        Args:
            trade_date: The date of the analysis
            final_state: The complete final state dictionary from the graph
        """
        # Build the state dictionary to log
        # We extract specific fields to ensure consistent structure
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            # Analyst reports
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            # Research team debate state (bull vs bear)
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            # Trader's investment plan
            "trader_investment_decision": final_state["trader_investment_plan"],
            # Risk management debate state
            "risk_debate_state": {
                "aggressive_history": final_state["risk_debate_state"][
                    "aggressive_history"
                ],
                "conservative_history": final_state["risk_debate_state"][
                    "conservative_history"
                ],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            # Final outputs
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Create directory structure for logs: eval_results/{TICKER}/TradingAgentsStrategy_logs/
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        # Write the state log to a JSON file with timestamp in filename
        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            # Use indent=4 for pretty-printed JSON (human-readable)
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on trading decisions and update agent memories based on actual returns.

        This method enables learning from real trading outcomes. After executing a trade
        in the market and observing the returns (profit or loss), agents can reflect on
        their decisions and update their memories to improve future performance.

        Args:
            returns_losses: The actual dollar amount gained (positive) or lost (negative)
                          from the trading decision. This is the feedback signal for learning.

        Note: This should be called AFTER propagate() and AFTER the trade is executed
              in the real market and returns are known.
        """
        # Each reflector method analyzes what the agent decided vs. what actually happened
        # and updates the agent's memory with lessons learned

        # Bull researcher reflects on their bullish arguments
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        # Bear researcher reflects on their bearish arguments
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        # Trader reflects on their investment plan
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        # Research manager reflects on their final decision
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        # Risk manager reflects on risk assessment
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process the raw trading signal into an actionable decision.

        The Portfolio Manager outputs a detailed text response. This method
        extracts the core trading decision (BUY, SELL, or HOLD) and formats
        it for display or execution.

        Args:
            full_signal: The raw text output from the Portfolio Manager agent

        Returns:
            Processed signal string with the core decision and key reasoning
        """
        return self.signal_processor.process_signal(full_signal)

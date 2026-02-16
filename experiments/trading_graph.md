# `tradingagents/graph/trading_graph.py`

## Key sections explained:
1. Imports & Dependencies
    - Standard library (os, json, Path)
    - LangGraph's ToolNode for binding functions as LLM tools
    - LLM client factory for multi-provider support
    - All agent types, memory systems, and state types
    - Data fetching tools (stock data, news, fundamentals)

2. TradingAgentsGraph Class
    - Purpose: Main orchestrator managing the 5-step workflow
    - init: Sets up dual LLM clients (deep/quick thinking), memory systems, tool nodes, and builds the graph
    - Dual LLM Strategy: Deep model for debates/complex reasoning, quick model for data fetching/basic analysis

3. Core Methods
    - `propagate()`: Main execution entry point - runs the complete workflow and returns final state + decision
    - `_create_tool_nodes()`: Groups data-fetching tools by analyst type (market → indicators, fundamentals → financials)
    - `_get_provider_kwargs()`: Provider-specific config (Google's thinking_level, OpenAI's reasoning_effort)
    - `_log_state()`: Persists complete analysis to JSON for record-keeping
    - `reflect_and_remember()`: Learning method - agents reflect on decisions vs actual returns
    - `process_signal()`: Extracts `BUY/SELL/HOLD` from raw Portfolio Manager output

### Architecture Highlights:
- Memory systems enable agents to learn across runs
- Tool nodes give LLMs access to real-time market data
- State flows through: Analysts → Researchers → Trader → Risk → Portfolio Manager
- Callbacks support real-time tracking (used by CLI for token usage stats)

# TradingAgents Coding Guidelines

This file provides guidelines for AI coding agents working on the TradingAgents repository.

## Project Overview

TradingAgents is a multi-agent LLM financial trading framework built with LangGraph. It uses specialized agents (analysts, researchers, traders, risk managers) that collaborate to make trading decisions.

- **Language**: Python 3.11+
- **Package Manager**: `uv` (preferred) or `pip`
- **Framework**: LangGraph, LangChain

## Build/Test/Lint Commands

### Installation
```bash
# Using uv (preferred)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Running the Application
```bash
# CLI mode
python -m cli.main

# Programmatic usage (LangGraph version)
python main.py

# DSPy version (alternative implementation)
python main_dspy.py

# As installed package
tradingagents
```

### Testing
```bash
# Run all tests (if pytest is configured)
uv run pytest

# Run a single test file
uv run pytest test.py

# Run with verbose output
uv run pytest -v

# Run a specific test function
uv run pytest test.py::test_function_name -v

# Run test script directly (project uses test.py for ad-hoc testing)
uv run python test.py
```

### Code Quality
```bash
# Format code with ruff (if installed)
uv run ruff format .

# Lint with ruff (if installed)
uv run ruff check .

# Type checking with mypy (if installed)
uv run mypy tradingagents
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Required API keys (set one or more)
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export ANTHROPIC_API_KEY=...
export XAI_API_KEY=...
export OPENROUTER_API_KEY=...
```

## Code Style Guidelines

### Imports
- **Standard library imports first** (e.g., `import json`, `from datetime import date`)
- **Third-party imports second** (e.g., `from langchain_core.prompts import ChatPromptTemplate`)
- **Local imports last** (e.g., `from tradingagents.agents.utils.agent_utils import ...`)
- Use absolute imports for project modules: `from tradingagents.graph.trading_graph import TradingAgentsGraph`
- Group imports with a blank line between each group

### Type Hints
- Use type hints for function parameters and return types
- Use `typing` module imports: `from typing import Dict, Any, Tuple, List, Optional`
- Use `TypedDict` for state definitions with `Annotated` for metadata
- Example:
  ```python
  def create_llm_client(
      provider: str,
      model: str,
      base_url: Optional[str] = None,
      **kwargs,
  ) -> BaseLLMClient:
  ```

### Naming Conventions
- **Functions/Variables**: `snake_case` (e.g., `create_fundamentals_analyst`, `trade_date`)
- **Classes**: `PascalCase` (e.g., `TradingAgentsGraph`, `AgentState`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CONFIG`)
- **Modules**: `snake_case.py` (e.g., `trading_graph.py`)
- **Private functions**: Prefix with underscore `_get_provider_kwargs`

### Error Handling
- Raise descriptive `ValueError` for invalid inputs with clear messages
- Use type hints to catch errors early
- Example:
  ```python
  raise ValueError(f"Unsupported LLM provider: {provider}")
  ```

### Docstrings
- Use triple-double quotes `"""` for docstrings
- Include Args, Returns, and Raises sections for public functions
- Keep first line as a brief summary

### Configuration
- Use `DEFAULT_CONFIG` dict from `tradingagents/default_config.py`
- Override config by copying: `config = DEFAULT_CONFIG.copy()`
- Environment variables loaded via `python-dotenv`

### Project Structure
```
tradingagents/
├── agents/          # Agent implementations
│   ├── analysts/    # Market, news, sentiment, fundamentals
│   ├── researchers/ # Bull/bear researchers
│   ├── risk_mgmt/   # Risk management agents
│   ├── trader/      # Trader agent
│   ├── managers/    # Research and risk managers
│   └── utils/       # Shared utilities, tools, states
├── dataflows/       # Data fetching (yfinance, alpha_vantage)
├── graph/           # LangGraph setup and orchestration
├── llm_clients/     # LLM provider clients
└── default_config.py
```

### Modern Python Features
- Use Python 3.11+ features (match/case, walrus operator where appropriate)
- Use `|` operator for union types: `str | None` (when supported)
- Use `Annotated` from `typing` for metadata

### Key Patterns
- Agents are created via factory functions returning callable nodes
- State uses `TypedDict` with `Annotated` fields
- Tool nodes use LangGraph's `ToolNode`
- LLM clients follow factory pattern with provider abstraction

### Dependencies
Key dependencies: `langgraph`, `langchain-core`, `pandas`, `yfinance`, `backtrader`, `typer`, `rich`, `chainlit`

Add with: `uv add <package>` or `uv pip install <package>`

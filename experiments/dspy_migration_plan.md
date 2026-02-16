# Migration Plan: TradingAgents from LangGraph to DSPy

## Overview

This document outlines a step-by-step plan to migrate the TradingAgents framework from LangGraph to DSPy, leveraging DSPy's compact syntax and prompt optimization capabilities.

---

## 1. Current Architecture Analysis

### 1.1 LangGraph Implementation Structure

| Component | Location | Description |
|-----------|----------|-------------|
| `TradingAgentsGraph` | `tradingagents/graph/trading_graph.py` | Main orchestrator class |
| `GraphSetup` | `tradingagents/graph/setup.py` | Builds StateGraph with nodes/edges |
| `AgentState` | `tradingagents/agents/utils/agent_states.py` | TypedDict with Annotated fields |
| Analyst Nodes | `tradingagents/agents/analysts/` | Market, social, news, fundamentals |
| Researcher Nodes | `tradingagents/agents/researchers/` | Bull/bear researchers |
| Trader Node | `tradingagents/agents/trader/trader.py` | Investment decision maker |
| Risk Nodes | `tradingagents/agents/risk_mgmt/` | Aggressive/neutral/conservative |
| Manager Nodes | `tradingagents/agents/managers/` | Research/risk managers |
| Tool Nodes | `tradingagents/agents/utils/agent_utils.py` | Data fetching (stock, news, fundamentals) |
| Memories | `tradingagents/agents/utils/memory.py` | FinancialSituationMemory for each agent |

### 1.2 Key Patterns in LangGraph

1. **State Management**: `TypedDict` with `Annotated` fields for state tracking
2. **Node Functions**: Python callables that take state and return state updates
3. **Conditional Edges**: Functions determining next node based on state
4. **Tool Binding**: `llm.bind_tools(tools)` for tool calling
5. **Message Passing**: Using LangChain message objects in state

---

## 2. DSPy Architecture Mapping

### 2.1 Direct Mappings

| LangGraph Concept | DSPy Equivalent |
|------------------|-----------------|
| `StateGraph` + nodes | DSPy Module with sub-modules |
| `AgentState` TypedDict | Signature input/output fields |
| Agent node function | DSPy Module with `forward()` |
| `llm.bind_tools()` | DSPy ReAct or custom module with tools |
| Conditional edges | Python `if/else` in forward() |
| Memory | DSPy module state or external storage |
| Graph edges | Sequential module calls in forward() |

### 2.2 DSPy Building Blocks to Use

- **`dspy.Signature`**: Declarative input/output specs (replace complex prompts)
- **`dspy.Module`**: Base class for custom agents
- **`dspy.Predict`**: Simple prediction without reasoning
- **`dspy.ChainOfThought`**: Reasoning with structured output
- **`dspy.ReAct`**: Tool use capability (replace ToolNode)
- **Optimizers**: `dspy.GEPA`, `dspy.BootstrapFewShot` for prompt tuning

---

## 3. Migration Steps

### Phase 1: Foundation (Weeks 1-2)

#### Step 1.1: Create DSPy Configuration Module
- Create `tradingagents_dspy/config.py`
- Configure LM provider (OpenAI, Anthropic, Google, etc.)
- Set up signature base classes

```python
# tradingagents_dspy/config.py
import dspy
from tradingagents.llm_clients import create_llm_client

def configure_dspy(config: dict):
    """Initialize DSPy with the configured LLM provider."""
    llm_client = create_llm_client(
        provider=config["llm_provider"],
        model=config["deep_think_llm"],
        base_url=config.get("backend_url"),
    )
    lm = dspy.LM(model=f"{config['llm_provider']}/{config['deep_think_llm']}")
    dspy.configure(lm=lm)
```

#### Step 1.2: Define Base Signatures
Create reusable signatures in `tradingagents_dspy/signatures/`:

- `MarketAnalysisSignature`: `company, date -> market_report`
- `SentimentAnalysisSignature`: `company -> sentiment_report`
- `NewsAnalysisSignature`: `company, date -> news_report`
- `FundamentalsAnalysisSignature`: `company -> fundamentals_report`
- `BullArgumentSignature`: `research_data, bear_argument -> bull_argument`
- `BearArgumentSignature`: `research_data, bull_argument -> bear_argument`
- `InvestmentDecisionSignature`: `bull_argument, bear_argument -> investment_plan`
- `RiskAssessmentSignature`: `investment_plan -> risk_assessment`
- `TradeDecisionSignature`: `investment_plan, risk_assessment -> final_decision`

#### Step 1.3: Port Tool Functions
- Keep existing tools from `tradingagents/agents/utils/agent_utils.py`
- Wrap in DSPy-compatible format (similar to dspy-grok `tools.py`)
- Use `@dspy.tool` decorator if available, or custom wrapper

### Phase 2: Agent Implementation (Weeks 3-4)

#### Step 2.1: Convert Analyst Modules

**Before (LangGraph):**
```python
def create_market_analyst(llm):
    def market_analyst_node(state):
        # complex prompt, tool binding, state handling
        ...
    return market_analyst_node
```

**After (DSPy):**
```python
class MarketAnalyst(dspy.Module):
    def __init__(self):
        self.analyze = dspy.ReAct(
            MarketAnalysisSignature,
            tools=[get_stock_data, get_indicators]
        )
    
    def forward(self, company: str, date: str) -> str:
        result = self.analyze(company=company, date=date)
        return result.market_report
```

#### Step 2.2: Convert Researcher Modules

Based on `dspy-grok/ex42_financial_debate.py` pattern:

```python
class BullResearcher(dspy.Module):
    def __init__(self, memory=None):
        super().__init__()
        self.reasoner = dspy.ChainOfThought(
            "research_data, bear_argument, past_memories -> bull_argument"
        )
        self.memory = memory
    
    def forward(self, research_data: str, bear_argument: str) -> str:
        past_memories = self.memory.get_memories(research_data) if self.memory else ""
        result = self.reasoner(
            research_data=research_data,
            bear_argument=bear_argument,
            past_memories=past_memories
        )
        return result.bull_argument
```

#### Step 2.3: Convert Risk Management Modules

- Convert `aggressive_debator`, `neutral_debator`, `conservative_debator`
- Use signature-based debate pattern

### Phase 3: Orchestration (Weeks 5-6)

#### Step 3.1: Create TradingAgentsProgram

```python
class TradingAgentsProgram(dspy.Module):
    def __init__(self, config: dict):
        # Initialize all agent modules
        self.market_analyst = MarketAnalyst()
        self.social_analyst = SocialMediaAnalyst()
        self.news_analyst = NewsAnalyst()
        self.fundamentals_analyst = FundamentalsAnalyst()
        
        self.bull_researcher = BullResearcher()
        self.bear_researcher = BearResearcher()
        self.research_manager = ResearchManager()
        
        self.trader = Trader()
        self.risk_manager = RiskManager()
        
        self.config = config
    
    def forward(self, company: str, date: str) -> str:
        # Phase 1: Analyst reports
        market_report = self.market_analyst(company, date)
        sentiment_report = self.social_analyst(company)
        news_report = self.news_analyst(company, date)
        fundamentals_report = self.fundamentals_analyst(company)
        
        research_data = f"{market_report}\n{sentiment_report}\n{news_report}\n{fundamentals_report}"
        
        # Phase 2: Research debate (iterative)
        bull_arg = self.bull_researcher(research_data, "")
        bear_arg = self.bear_researcher(research_data, "")
        
        # Multiple rounds
        for _ in range(self.config.get("debate_rounds", 3)):
            bull_arg = self.bull_researcher(research_data, bear_arg)
            bear_arg = self.bear_researcher(research_data, bull_arg)
        
        # Phase 3: Investment decision
        investment_plan = self.research_manager(bull_arg, bear_arg)
        
        # Phase 4: Risk assessment
        risk_assessment = self.risk_manager(investment_plan)
        
        # Phase 5: Final decision
        final_decision = self.trader(investment_plan, risk_assessment)
        
        return final_decision
```

#### Step 3.2: Handle State/Memory

- Maintain external memory objects (can still use `FinancialSituationMemory`)
- Pass memory context through signatures explicitly

### Phase 4: Optimization (Weeks 7-8)

#### Step 4.1: Add Optimization Support

```python
# Prepare training data
train_examples = [
    dspy.Example(
        company="AAPL", date="2024-01-15",
        expected_decision="BUY"
    ).with_inputs("company", "date"),
    # ... more examples
]

# Compile with optimizer
from dspy import BootstrapFewShot

optimizer = BootstrapFewShot(metric=accuracy_metric)
compiled_program = optimizer.compile(
    TradingAgentsProgram(config),
    trainset=train_examples
)
```

#### Step 4.2: GEPA Optimization (Optional Advanced)

Based on dspy-grok's GEPA examples:
- Use for evolving prompts in volatile market conditions
- Set up validation with historical trading data

---

## 4. File Structure After Migration

```
tradingagents_dspy/
├── __init__.py
├── config.py              # DSPy configuration
├── signatures/            # Signature definitions
│   ├── __init__.py
│   ├── analyst_signatures.py
│   ├── researcher_signatures.py
│   ├── trader_signatures.py
│   └── risk_signatures.py
├── agents/                # Agent modules
│   ├── __init__.py
│   ├── analysts.py        # Market, social, news, fundamentals
│   ├── researchers.py     # Bull, bear researchers
│   ├── trader.py          # Investment decision
│   └── risk_manager.py   # Risk assessment
├── program.py             # Main TradingAgentsProgram
├── memory.py              # Memory handling
├── tools.py               # Tool wrappers
└── optimizers.py          # Custom optimizers
```

---

## 5. Benefits of Migration

| Aspect | LangGraph (Current) | DSPy (Migrated) |
|--------|-------------------|------------------|
| Code Lines | ~2000+ | ~500-800 |
| Prompt Tuning | Manual | Automatic (GEPA/Bootstrap) |
| State Management | Complex TypedDict | Implicit via signatures |
| Tool Integration | ToolNode | Built-in ReAct |
| Modularity | Graph nodes | Composable modules |
| Optimization | None | Built-in optimizers |

---

## 6. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Tool compatibility | Wrap existing tools in DSPy-compatible format |
| Complex debate flow | Use iterative module calls in forward() |
| Memory state | Keep external memory, pass explicitly |
| Optimization data | Generate training data from existing runs |
| Backward compatibility | Keep LangGraph version, release as v2 |

---

## 7. Implementation Priority

1. **P0 - Must Have**: Signatures, basic agent modules, orchestration program
2. **P1 - Important**: Memory integration, tool wrappers, CLI interface
3. **P2 - Nice to Have**: GEPA optimization, advanced prompt tuning

---

## 8. Reference Examples

- `ref/dspy-grok/ex42_financial_debate.py` - Debate agent pattern
- `ref/dspy-grok/tools.py` - Tool implementation
- `ref/dspy-grok/AGENTS.md` - DSPy best practices

---

*Document created for TradingAgents DSPy Migration Planning*

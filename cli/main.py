# Standard library imports for type hints, date/time handling, file paths, and decorators
from typing import Optional
import datetime
from pathlib import Path
from functools import wraps
from collections import deque
import time

# Typer for building CLI applications with automatic help generation
import typer

# Rich library imports for beautiful terminal UI components
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

# python-dotenv for loading environment variables from .env file
from dotenv import load_dotenv

# Load environment variables immediately (API keys must be set before importing tradingagents)
load_dotenv()

# Import the core TradingAgents framework components
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Import CLI-specific utilities
from cli.models import AnalystType
from cli.utils import *
from cli.announcements import fetch_announcements, display_announcements
from cli.stats_handler import StatsCallbackHandler

# Create a global console instance for Rich output formatting
console = Console()

# Initialize the Typer CLI application with metadata
app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",
    add_completion=True,  # Enable shell tab-completion
)


# MessageBuffer class: Central state management for tracking agent progress, messages, and reports
# Uses deque with maxlen to prevent memory issues during long-running analyses
class MessageBuffer:
    # FIXED_AGENTS: Teams that always run regardless of user selection
    # These agents form the core decision-making pipeline
    FIXED_AGENTS = {
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": [
            "Aggressive Analyst",
            "Neutral Analyst",
            "Conservative Analyst",
        ],
        "Portfolio Management": ["Portfolio Manager"],
    }

    # ANALYST_MAPPING: Maps internal keys to display names for user-selectable analysts
    ANALYST_MAPPING = {
        "market": "Market Analyst",
        "social": "Social Analyst",
        "news": "News Analyst",
        "fundamentals": "Fundamentals Analyst",
    }

    # REPORT_SECTIONS: Maps report section names to (analyst_key, finalizing_agent)
    # analyst_key: which analyst controls this section (None = always included)
    # finalizing_agent: which agent must complete for this report to be "done"
    REPORT_SECTIONS = {
        "market_report": ("market", "Market Analyst"),
        "sentiment_report": ("social", "Social Analyst"),
        "news_report": ("news", "News Analyst"),
        "fundamentals_report": ("fundamentals", "Fundamentals Analyst"),
        "investment_plan": (
            None,
            "Research Manager",
        ),  # Always included, finalized by Research Manager
        "trader_investment_plan": (
            None,
            "Trader",
        ),  # Always included, finalized by Trader
        "final_trade_decision": (
            None,
            "Portfolio Manager",
        ),  # Always included, finalized by Portfolio Manager
    }

    def __init__(self, max_length=100):
        """Initialize the message buffer with fixed-size deques to prevent memory leaks."""
        self.messages = deque(
            maxlen=max_length
        )  # Store (timestamp, type, content) tuples
        self.tool_calls = deque(
            maxlen=max_length
        )  # Store (timestamp, tool_name, args) tuples
        self.current_report = None  # Currently displayed report section
        self.final_report = None  # Complete compiled report
        self.agent_status = {}  # Map of agent_name -> status (pending/in_progress/completed)
        self.current_agent = None  # Which agent is currently running
        self.report_sections = {}  # Map of section_name -> content
        self.selected_analysts = []  # List of analysts user selected
        self._last_message_id = None  # Track last message to avoid duplicates

    def init_for_analysis(self, selected_analysts):
        """Reset buffer state for a new analysis run.

        Args:
            selected_analysts: List of analyst type strings (e.g., ["market", "news"])
        """
        # Normalize analyst keys to lowercase for consistency
        self.selected_analysts = [a.lower() for a in selected_analysts]

        # Build agent_status dictionary dynamically based on user selection
        self.agent_status = {}

        # Add user-selected analysts with "pending" status
        for analyst_key in self.selected_analysts:
            if analyst_key in self.ANALYST_MAPPING:
                self.agent_status[self.ANALYST_MAPPING[analyst_key]] = "pending"

        # Add fixed teams that always run
        for team_agents in self.FIXED_AGENTS.values():
            for agent in team_agents:
                self.agent_status[agent] = "pending"

        # Build report_sections dictionary - only include sections for selected analysts
        self.report_sections = {}
        for section, (analyst_key, _) in self.REPORT_SECTIONS.items():
            # Include section if: no analyst_key required OR analyst was selected
            if analyst_key is None or analyst_key in self.selected_analysts:
                self.report_sections[section] = None

        # Reset all other state variables for fresh analysis
        self.current_report = None
        self.final_report = None
        self.current_agent = None
        self.messages.clear()
        self.tool_calls.clear()
        self._last_message_id = None

    def get_completed_reports_count(self):
        """Count reports that are truly finalized (not just have content).

        A report counts as complete only when:
        1. The report section has content (not None)
        2. The agent responsible for finalizing it has status "completed"

        This prevents counting interim debate updates as "completed" reports.
        """
        count = 0
        for section in self.report_sections:
            if section not in self.REPORT_SECTIONS:
                continue
            _, finalizing_agent = self.REPORT_SECTIONS[section]
            # Check both conditions: has content AND finalizing agent is done
            has_content = self.report_sections.get(section) is not None
            agent_done = self.agent_status.get(finalizing_agent) == "completed"
            if has_content and agent_done:
                count += 1
        return count

    def add_message(self, message_type, content):
        """Add a message to the buffer with current timestamp."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        """Record a tool call (e.g., API request) with timestamp."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        """Update an agent's status and track which agent is currently running."""
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        """Update a report section and trigger display refresh."""
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        """Update the currently displayed report to show the most recent section."""
        # Find the most recently updated section (last non-None entry)
        latest_section = None
        latest_content = None

        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content

        if latest_section and latest_content:
            # Map internal section names to user-friendly titles
            section_titles = {
                "market_report": "Market Analysis",
                "sentiment_report": "Social Sentiment",
                "news_report": "News Analysis",
                "fundamentals_report": "Fundamentals Analysis",
                "investment_plan": "Research Team Decision",
                "trader_investment_plan": "Trading Team Plan",
                "final_trade_decision": "Portfolio Management Decision",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # Also update the complete final report
        self._update_final_report()

    def _update_final_report(self):
        """Compile all report sections into a complete markdown document."""
        report_parts = []

        # Section I: Analyst Team Reports
        analyst_sections = [
            "market_report",
            "sentiment_report",
            "news_report",
            "fundamentals_report",
        ]
        if any(self.report_sections.get(section) for section in analyst_sections):
            report_parts.append("## Analyst Team Reports")
            if self.report_sections.get("market_report"):
                report_parts.append(
                    f"### Market Analysis\n{self.report_sections['market_report']}"
                )
            if self.report_sections.get("sentiment_report"):
                report_parts.append(
                    f"### Social Sentiment\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections.get("news_report"):
                report_parts.append(
                    f"### News Analysis\n{self.report_sections['news_report']}"
                )
            if self.report_sections.get("fundamentals_report"):
                report_parts.append(
                    f"### Fundamentals Analysis\n{self.report_sections['fundamentals_report']}"
                )

        # Section II: Research Team Decision
        if self.report_sections.get("investment_plan"):
            report_parts.append("## Research Team Decision")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # Section III: Trading Team Plan
        if self.report_sections.get("trader_investment_plan"):
            report_parts.append("## Trading Team Plan")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # Section IV & V: Risk Management and Portfolio Management
        if self.report_sections.get("final_trade_decision"):
            report_parts.append("## Portfolio Management Decision")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


# Create a singleton instance of MessageBuffer for global state management
message_buffer = MessageBuffer()


def create_layout():
    """Create the Rich Layout structure for the live terminal display.

    Layout structure:
    - header (3 lines): Welcome banner
    - main: Split into upper (progress + messages) and analysis panels
      - upper: progress panel (agent status) | messages panel (logs)
      - analysis: Current report being generated
    - footer (3 lines): Statistics (agents, tokens, time)
    """
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def format_tokens(n):
    """Format large token counts in human-readable form (e.g., 1500 -> 1.5k)."""
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def update_display(layout, spinner_text=None, stats_handler=None, start_time=None):
    """Update all panels in the Rich layout with current state.

    Args:
        layout: The Rich Layout object to update
        spinner_text: Optional loading text to display
        stats_handler: StatsCallbackHandler for LLM/tool usage statistics
        start_time: Timestamp when analysis started (for elapsed time)
    """
    # HEADER: Display welcome banner with project info
    layout["header"].update(
        Panel(
            "[bold green]Welcome to TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="Welcome to TradingAgents",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # PROGRESS PANEL: Show table of all agents and their current status
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # Use simple header with horizontal lines
        title=None,
        padding=(0, 2),
        expand=True,
    )
    progress_table.add_column("Team", style="cyan", justify="center", width=20)
    progress_table.add_column("Agent", style="green", justify="center", width=20)
    progress_table.add_column("Status", style="yellow", justify="center", width=20)

    # Define all teams and their agents
    all_teams = {
        "Analyst Team": [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": [
            "Aggressive Analyst",
            "Neutral Analyst",
            "Conservative Analyst",
        ],
        "Portfolio Management": ["Portfolio Manager"],
    }

    # Filter to only show teams that have agents in agent_status (user-selected + fixed)
    teams = {}
    for team, agents in all_teams.items():
        active_agents = [a for a in agents if a in message_buffer.agent_status]
        if active_agents:
            teams[team] = active_agents

    # Build the progress table rows
    for team, agents in teams.items():
        # First agent in team shows team name
        first_agent = agents[0]
        status = message_buffer.agent_status.get(first_agent, "pending")
        if status == "in_progress":
            # Show animated spinner for active agents
            spinner = Spinner(
                "dots", text="[blue]in_progress[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            # Color-code status: pending=yellow, completed=green, error=red
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            status_cell = f"[{status_color}]{status}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # Remaining agents in team (no team name shown)
        for agent in agents[1:]:
            status = message_buffer.agent_status.get(agent, "pending")
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text="[blue]in_progress[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                status_cell = f"[{status_color}]{status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # Add separator line after each team
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="Progress", border_style="cyan", padding=(1, 2))
    )

    # MESSAGES PANEL: Show recent messages and tool calls
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,
        box=box.MINIMAL,
        show_lines=True,
        padding=(0, 1),
    )
    messages_table.add_column("Time", style="cyan", width=8, justify="center")
    messages_table.add_column("Type", style="green", width=10, justify="center")
    messages_table.add_column(
        "Content", style="white", no_wrap=False, ratio=1
    )  # Expandable content column

    # Combine tool calls and regular messages
    all_messages = []

    # Add tool calls to the list
    for timestamp, tool_name, args in message_buffer.tool_calls:
        formatted_args = format_tool_args(args)
        all_messages.append((timestamp, "Tool", f"{tool_name}: {formatted_args}"))

    # Add regular messages
    for timestamp, msg_type, content in message_buffer.messages:
        content_str = str(content) if content else ""
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    # Sort by timestamp descending (newest first for display)
    all_messages.sort(key=lambda x: x[0], reverse=True)

    # Show most recent 12 messages
    max_messages = 12
    recent_messages = all_messages[:max_messages]

    # Add messages to table
    for timestamp, msg_type, content in recent_messages:
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    layout["messages"].update(
        Panel(
            messages_table,
            title="Messages & Tools",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # ANALYSIS PANEL: Show the current report section being generated
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="Current Report",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]Waiting for analysis report...[/italic]",
                title="Current Report",
                border_style="green",
                padding=(1, 2),
            )
        )

    # FOOTER: Display statistics and metrics
    # Count completed agents
    agents_completed = sum(
        1 for status in message_buffer.agent_status.values() if status == "completed"
    )
    agents_total = len(message_buffer.agent_status)

    # Count truly completed reports (using get_completed_reports_count logic)
    reports_completed = message_buffer.get_completed_reports_count()
    reports_total = len(message_buffer.report_sections)

    # Build statistics string
    stats_parts = [f"Agents: {agents_completed}/{agents_total}"]

    # Add LLM and tool call statistics from callback handler
    if stats_handler:
        stats = stats_handler.get_stats()
        stats_parts.append(f"LLM: {stats['llm_calls']}")
        stats_parts.append(f"Tools: {stats['tool_calls']}")

        # Token usage with arrow indicators (up for input, down for output)
        if stats["tokens_in"] > 0 or stats["tokens_out"] > 0:
            tokens_str = f"Tokens: {format_tokens(stats['tokens_in'])}↑ {format_tokens(stats['tokens_out'])}↓"
        else:
            tokens_str = "Tokens: --"
        stats_parts.append(tokens_str)

    stats_parts.append(f"Reports: {reports_completed}/{reports_total}")

    # Add elapsed time (⏱ symbol)
    if start_time:
        elapsed = time.time() - start_time
        elapsed_str = f"⏱ {int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
        stats_parts.append(elapsed_str)

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(" | ".join(stats_parts))

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """Interactive questionnaire to get all user inputs before analysis starts.

    Returns a dictionary with all user selections:
    - ticker: Stock symbol to analyze
    - analysis_date: Date for historical analysis
    - analysts: List of selected analyst types
    - research_depth: Number of debate rounds
    - llm_provider: Which LLM provider to use
    - backend_url: API endpoint URL
    - shallow_thinker: Model for quick tasks
    - deep_thinker: Model for complex reasoning
    - google_thinking_level: Gemini thinking mode (if applicable)
    - openai_reasoning_effort: OpenAI reasoning level (if applicable)
    """
    # Step 0: Display welcome banner with ASCII art
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # Build welcome content with workflow explanation
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: Multi-Agents LLM Financial Trading Framework - CLI[/bold green]\n\n"
    welcome_content += "[bold]Workflow Steps:[/bold]\n"
    welcome_content += "I. Analyst Team → II. Research Team → III. Trader → IV. Risk Management → V. Portfolio Management\n\n"
    welcome_content += (
        "[dim]Built by [Tauric Research](https://github.com/TauricResearch)[/dim]"
    )

    # Create styled welcome panel
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="Welcome to TradingAgents",
        subtitle="Multi-Agents LLM Financial Trading Framework",
    )
    console.print(Align.center(welcome_box))
    console.print()
    console.print()

    # Display any announcements from remote source (errors are silent)
    announcements = fetch_announcements()
    display_announcements(console, announcements)

    # Helper function to create consistent question boxes
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]Default: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # STEP 1: Get ticker symbol (default: SPY)
    console.print(
        create_question_box(
            "Step 1: Ticker Symbol", "Enter the ticker symbol to analyze", "SPY"
        )
    )
    selected_ticker = get_ticker()

    # STEP 2: Get analysis date (default: today, cannot be future)
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "Step 2: Analysis Date",
            "Enter the analysis date (YYYY-MM-DD)",
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # STEP 3: Select which analysts to run
    console.print(
        create_question_box(
            "Step 3: Analysts Team", "Select your LLM analyst agents for the analysis"
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]Selected analysts:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # STEP 4: Research depth (number of debate rounds)
    console.print(
        create_question_box(
            "Step 4: Research Depth", "Select your research depth level"
        )
    )
    selected_research_depth = select_research_depth()

    # STEP 5: LLM provider selection
    console.print(
        create_question_box("Step 5: OpenAI backend", "Select which service to talk to")
    )
    selected_llm_provider, backend_url = select_llm_provider()

    # STEP 6: Model selection (shallow vs deep thinking)
    console.print(
        create_question_box(
            "Step 6: Thinking Agents", "Select your thinking agents for analysis"
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)

    # STEP 7: Provider-specific configuration
    thinking_level = None
    reasoning_effort = None

    provider_lower = selected_llm_provider.lower()
    if provider_lower == "google":
        # Google Gemini has special "thinking" mode configuration
        console.print(
            create_question_box(
                "Step 7: Thinking Mode", "Configure Gemini thinking mode"
            )
        )
        thinking_level = ask_gemini_thinking_config()
    elif provider_lower == "openai":
        # OpenAI has reasoning effort levels (low/medium/high)
        console.print(
            create_question_box(
                "Step 7: Reasoning Effort", "Configure OpenAI reasoning effort level"
            )
        )
        reasoning_effort = ask_openai_reasoning_effort()

    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
        "google_thinking_level": thinking_level,
        "openai_reasoning_effort": reasoning_effort,
    }


def get_ticker():
    """Prompt user for ticker symbol with default value."""
    return typer.prompt("", default="SPY")


def get_analysis_date():
    """Prompt user for analysis date with validation.

    Validates:
    - Format is YYYY-MM-DD
    - Date is not in the future
    """
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # Validate date format
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            # Ensure date is not in the future
            if analysis_date.date() > datetime.datetime.now().date():
                console.print("[red]Error: Analysis date cannot be in the future[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                "[red]Error: Invalid date format. Please use YYYY-MM-DD[/red]"
            )


def save_report_to_disk(final_state, ticker: str, save_path: Path):
    """Save complete analysis report to disk with organized subfolders.

    Directory structure:
    save_path/
    ├── 1_analysts/
    │   ├── market.md
    │   ├── sentiment.md
    │   ├── news.md
    │   └── fundamentals.md
    ├── 2_research/
    │   ├── bull.md
    │   ├── bear.md
    │   └── manager.md
    ├── 3_trading/
    │   └── trader.md
    ├── 4_risk/
    │   ├── aggressive.md
    │   ├── conservative.md
    │   └── neutral.md
    ├── 5_portfolio/
    │   └── decision.md
    └── complete_report.md
    """
    save_path.mkdir(parents=True, exist_ok=True)
    sections = []

    # 1. Analyst Team Reports
    analysts_dir = save_path / "1_analysts"
    analyst_parts = []
    if final_state.get("market_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "market.md").write_text(final_state["market_report"])
        analyst_parts.append(("Market Analyst", final_state["market_report"]))
    if final_state.get("sentiment_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "sentiment.md").write_text(final_state["sentiment_report"])
        analyst_parts.append(("Social Analyst", final_state["sentiment_report"]))
    if final_state.get("news_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "news.md").write_text(final_state["news_report"])
        analyst_parts.append(("News Analyst", final_state["news_report"]))
    if final_state.get("fundamentals_report"):
        analysts_dir.mkdir(exist_ok=True)
        (analysts_dir / "fundamentals.md").write_text(
            final_state["fundamentals_report"]
        )
        analyst_parts.append(
            ("Fundamentals Analyst", final_state["fundamentals_report"])
        )
    if analyst_parts:
        content = "\n\n".join(f"### {name}\n{text}" for name, text in analyst_parts)
        sections.append(f"## I. Analyst Team Reports\n\n{content}")

    # 2. Research Team Decision
    if final_state.get("investment_debate_state"):
        research_dir = save_path / "2_research"
        debate = final_state["investment_debate_state"]
        research_parts = []
        if debate.get("bull_history"):
            research_dir.mkdir(exist_ok=True)
            (research_dir / "bull.md").write_text(debate["bull_history"])
            research_parts.append(("Bull Researcher", debate["bull_history"]))
        if debate.get("bear_history"):
            research_dir.mkdir(exist_ok=True)
            (research_dir / "bear.md").write_text(debate["bear_history"])
            research_parts.append(("Bear Researcher", debate["bear_history"]))
        if debate.get("judge_decision"):
            research_dir.mkdir(exist_ok=True)
            (research_dir / "manager.md").write_text(debate["judge_decision"])
            research_parts.append(("Research Manager", debate["judge_decision"]))
        if research_parts:
            content = "\n\n".join(
                f"### {name}\n{text}" for name, text in research_parts
            )
            sections.append(f"## II. Research Team Decision\n\n{content}")

    # 3. Trading Team Plan
    if final_state.get("trader_investment_plan"):
        trading_dir = save_path / "3_trading"
        trading_dir.mkdir(exist_ok=True)
        (trading_dir / "trader.md").write_text(final_state["trader_investment_plan"])
        sections.append(
            f"## III. Trading Team Plan\n\n### Trader\n{final_state['trader_investment_plan']}"
        )

    # 4. Risk Management Team
    if final_state.get("risk_debate_state"):
        risk_dir = save_path / "4_risk"
        risk = final_state["risk_debate_state"]
        risk_parts = []
        if risk.get("aggressive_history"):
            risk_dir.mkdir(exist_ok=True)
            (risk_dir / "aggressive.md").write_text(risk["aggressive_history"])
            risk_parts.append(("Aggressive Analyst", risk["aggressive_history"]))
        if risk.get("conservative_history"):
            risk_dir.mkdir(exist_ok=True)
            (risk_dir / "conservative.md").write_text(risk["conservative_history"])
            risk_parts.append(("Conservative Analyst", risk["conservative_history"]))
        if risk.get("neutral_history"):
            risk_dir.mkdir(exist_ok=True)
            (risk_dir / "neutral.md").write_text(risk["neutral_history"])
            risk_parts.append(("Neutral Analyst", risk["neutral_history"]))
        if risk_parts:
            content = "\n\n".join(f"### {name}\n{text}" for name, text in risk_parts)
            sections.append(f"## IV. Risk Management Team Decision\n\n{content}")

        # 5. Portfolio Manager Decision
        if risk.get("judge_decision"):
            portfolio_dir = save_path / "5_portfolio"
            portfolio_dir.mkdir(exist_ok=True)
            (portfolio_dir / "decision.md").write_text(risk["judge_decision"])
            sections.append(
                f"## V. Portfolio Manager Decision\n\n### Portfolio Manager\n{risk['judge_decision']}"
            )

    # Write the consolidated complete report
    header = f"# Trading Analysis Report: {ticker}\n\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    (save_path / "complete_report.md").write_text(header + "\n\n".join(sections))
    return save_path / "complete_report.md"


def display_complete_report(final_state):
    """Display the complete analysis report in the terminal.

    Shows all sections sequentially with styled panels to avoid truncation.
    """
    console.print()
    console.print(Rule("Complete Analysis Report", style="bold green"))

    # Section I: Analyst Team Reports
    analysts = []
    if final_state.get("market_report"):
        analysts.append(("Market Analyst", final_state["market_report"]))
    if final_state.get("sentiment_report"):
        analysts.append(("Social Analyst", final_state["sentiment_report"]))
    if final_state.get("news_report"):
        analysts.append(("News Analyst", final_state["news_report"]))
    if final_state.get("fundamentals_report"):
        analysts.append(("Fundamentals Analyst", final_state["fundamentals_report"]))
    if analysts:
        console.print(
            Panel("[bold]I. Analyst Team Reports[/bold]", border_style="cyan")
        )
        for title, content in analysts:
            console.print(
                Panel(
                    Markdown(content), title=title, border_style="blue", padding=(1, 2)
                )
            )

    # Section II: Research Team Decision
    if final_state.get("investment_debate_state"):
        debate = final_state["investment_debate_state"]
        research = []
        if debate.get("bull_history"):
            research.append(("Bull Researcher", debate["bull_history"]))
        if debate.get("bear_history"):
            research.append(("Bear Researcher", debate["bear_history"]))
        if debate.get("judge_decision"):
            research.append(("Research Manager", debate["judge_decision"]))
        if research:
            console.print(
                Panel("[bold]II. Research Team Decision[/bold]", border_style="magenta")
            )
            for title, content in research:
                console.print(
                    Panel(
                        Markdown(content),
                        title=title,
                        border_style="blue",
                        padding=(1, 2),
                    )
                )

    # Section III: Trading Team Plan
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel("[bold]III. Trading Team Plan[/bold]", border_style="yellow")
        )
        console.print(
            Panel(
                Markdown(final_state["trader_investment_plan"]),
                title="Trader",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Section IV: Risk Management Team
    if final_state.get("risk_debate_state"):
        risk = final_state["risk_debate_state"]
        risk_reports = []
        if risk.get("aggressive_history"):
            risk_reports.append(("Aggressive Analyst", risk["aggressive_history"]))
        if risk.get("conservative_history"):
            risk_reports.append(("Conservative Analyst", risk["conservative_history"]))
        if risk.get("neutral_history"):
            risk_reports.append(("Neutral Analyst", risk["neutral_history"]))
        if risk_reports:
            console.print(
                Panel(
                    "[bold]IV. Risk Management Team Decision[/bold]", border_style="red"
                )
            )
            for title, content in risk_reports:
                console.print(
                    Panel(
                        Markdown(content),
                        title=title,
                        border_style="blue",
                        padding=(1, 2),
                    )
                )

        # Section V: Portfolio Manager Decision
        if risk.get("judge_decision"):
            console.print(
                Panel(
                    "[bold]V. Portfolio Manager Decision[/bold]", border_style="green"
                )
            )
            console.print(
                Panel(
                    Markdown(risk["judge_decision"]),
                    title="Portfolio Manager",
                    border_style="blue",
                    padding=(1, 2),
                )
            )


def update_research_team_status(status):
    """Batch update status for all research team members."""
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)


# Mapping dictionaries for analyst status transitions
ANALYST_ORDER = ["market", "social", "news", "fundamentals"]  # Fixed processing order
ANALYST_AGENT_NAMES = {
    "market": "Market Analyst",
    "social": "Social Analyst",
    "news": "News Analyst",
    "fundamentals": "Fundamentals Analyst",
}
ANALYST_REPORT_MAP = {
    "market": "market_report",
    "social": "sentiment_report",
    "news": "news_report",
    "fundamentals": "fundamentals_report",
}


def update_analyst_statuses(message_buffer, chunk):
    """Update analyst statuses based on which reports have been generated.

    Logic:
    - Analysts with completed reports -> status "completed"
    - First analyst without report -> status "in_progress"
    - Remaining analysts -> status "pending"
    - When all analysts done -> set Bull Researcher to "in_progress"
    """
    selected = message_buffer.selected_analysts
    found_active = False

    for analyst_key in ANALYST_ORDER:
        if analyst_key not in selected:
            continue

        agent_name = ANALYST_AGENT_NAMES[analyst_key]
        report_key = ANALYST_REPORT_MAP[analyst_key]
        has_report = bool(chunk.get(report_key))

        if has_report:
            message_buffer.update_agent_status(agent_name, "completed")
            message_buffer.update_report_section(report_key, chunk[report_key])
        elif not found_active:
            message_buffer.update_agent_status(agent_name, "in_progress")
            found_active = True
        else:
            message_buffer.update_agent_status(agent_name, "pending")

    # Transition to research team when all analysts complete
    if not found_active and selected:
        if message_buffer.agent_status.get("Bull Researcher") == "pending":
            message_buffer.update_agent_status("Bull Researcher", "in_progress")


def extract_content_string(content):
    """Extract string content from various LangChain message formats.

    Handles: strings, dicts with 'text' key, lists of text objects
    Returns None if no meaningful content found.
    """
    import ast

    def is_empty(val):
        """Check if a value is effectively empty using Python's truthiness."""
        if val is None or val == "":
            return True
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return True
            try:
                return not bool(ast.literal_eval(s))
            except (ValueError, SyntaxError):
                return False  # Can't parse = real text
        return not bool(val)

    if is_empty(content):
        return None

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        text = content.get("text", "")
        return text.strip() if not is_empty(text) else None

    if isinstance(content, list):
        text_parts = [
            item.get("text", "").strip()
            if isinstance(item, dict) and item.get("type") == "text"
            else (item.strip() if isinstance(item, str) else "")
            for item in content
        ]
        result = " ".join(t for t in text_parts if t and not is_empty(t))
        return result if result else None

    return str(content).strip() if not is_empty(content) else None


def classify_message_type(message) -> tuple[str, str | None]:
    """Classify a LangChain message into display type and extract content.

    Returns:
        (type, content) where type is one of: User, Agent, Data, Control, System
    """
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    content = extract_content_string(getattr(message, "content", None))

    if isinstance(message, HumanMessage):
        if content and content.strip() == "Continue":
            return ("Control", content)
        return ("User", content)

    if isinstance(message, ToolMessage):
        return ("Data", content)

    if isinstance(message, AIMessage):
        return ("Agent", content)

    # Fallback for unknown types
    return ("System", content)


def format_tool_args(args, max_length=80) -> str:
    """Format tool arguments for display, truncating if too long."""
    result = str(args)
    if len(result) > max_length:
        return result[: max_length - 3] + "..."
    return result


def run_analysis():
    """Main analysis execution function.

    Orchestrates the entire workflow:
    1. Get user selections
    2. Initialize TradingAgentsGraph with configuration
    3. Set up live display with Rich
    4. Stream analysis results and update display in real-time
    5. Save results and display final report
    """
    # PHASE 1: Get user inputs
    selections = get_user_selections()

    # PHASE 2: Configure TradingAgents framework
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["llm_provider"] = selections["llm_provider"].lower()
    # Provider-specific thinking configuration
    config["google_thinking_level"] = selections.get("google_thinking_level")
    config["openai_reasoning_effort"] = selections.get("openai_reasoning_effort")

    # Create stats callback handler for tracking LLM/tool usage
    stats_handler = StatsCallbackHandler()

    # Normalize analyst selection to predefined order (selection is a set, order is fixed)
    selected_set = {analyst.value for analyst in selections["analysts"]}
    selected_analyst_keys = [a for a in ANALYST_ORDER if a in selected_set]

    # Initialize the graph with callbacks for tracking
    graph = TradingAgentsGraph(
        selected_analyst_keys,
        config=config,
        debug=True,
        callbacks=[stats_handler],
    )

    # Initialize message buffer with selected analysts
    message_buffer.init_for_analysis(selected_analyst_keys)

    # Track start time for elapsed time display
    start_time = time.time()

    # Create output directories for results
    results_dir = (
        Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    )
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    # DECORATOR FUNCTIONS: Wrap MessageBuffer methods to also persist to disk
    def save_message_decorator(obj, func_name):
        """Decorator to save messages to both buffer and log file."""
        func = getattr(obj, func_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")  # Flatten newlines for log
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")

        return wrapper

    def save_tool_call_decorator(obj, func_name):
        """Decorator to save tool calls to both buffer and log file."""
        func = getattr(obj, func_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")

        return wrapper

    def save_report_section_decorator(obj, func_name):
        """Decorator to save report sections to both buffer and markdown file."""
        func = getattr(obj, func_name)

        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if (
                section_name in obj.report_sections
                and obj.report_sections[section_name] is not None
            ):
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(content)

        return wrapper

    # Apply decorators to MessageBuffer methods
    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(
        message_buffer, "add_tool_call"
    )
    message_buffer.update_report_section = save_report_section_decorator(
        message_buffer, "update_report_section"
    )

    # PHASE 3: Start live display and run analysis
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # Initial display setup
        update_display(layout, stats_handler=stats_handler, start_time=start_time)

        # Add initial system messages
        message_buffer.add_message("System", f"Selected ticker: {selections['ticker']}")
        message_buffer.add_message(
            "System", f"Analysis date: {selections['analysis_date']}"
        )
        message_buffer.add_message(
            "System",
            f"Selected analysts: {', '.join(analyst.value for analyst in selections['analysts'])}",
        )
        update_display(layout, stats_handler=stats_handler, start_time=start_time)

        # Set first analyst to in_progress
        first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
        message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout, stats_handler=stats_handler, start_time=start_time)

        # Show analysis spinner
        spinner_text = (
            f"Analyzing {selections['ticker']} on {selections['analysis_date']}..."
        )
        update_display(
            layout, spinner_text, stats_handler=stats_handler, start_time=start_time
        )

        # Initialize graph state
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        args = graph.propagator.get_graph_args(callbacks=[stats_handler])

        # Stream analysis results from LangGraph
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            # Process messages (skip duplicates via message ID)
            if len(chunk["messages"]) > 0:
                last_message = chunk["messages"][-1]
                msg_id = getattr(last_message, "id", None)

                if msg_id != message_buffer._last_message_id:
                    message_buffer._last_message_id = msg_id

                    # Add message to buffer
                    msg_type, content = classify_message_type(last_message)
                    if content and content.strip():
                        message_buffer.add_message(msg_type, content)

                    # Handle tool calls
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        for tool_call in last_message.tool_calls:
                            if isinstance(tool_call, dict):
                                message_buffer.add_tool_call(
                                    tool_call["name"], tool_call["args"]
                                )
                            else:
                                message_buffer.add_tool_call(
                                    tool_call.name, tool_call.args
                                )

            # Update analyst statuses based on report state
            update_analyst_statuses(message_buffer, chunk)

            # Process Research Team results (Investment Debate)
            if chunk.get("investment_debate_state"):
                debate_state = chunk["investment_debate_state"]
                bull_hist = debate_state.get("bull_history", "").strip()
                bear_hist = debate_state.get("bear_history", "").strip()
                judge = debate_state.get("judge_decision", "").strip()

                if bull_hist or bear_hist:
                    update_research_team_status("in_progress")
                if bull_hist:
                    message_buffer.update_report_section(
                        "investment_plan", f"### Bull Researcher Analysis\n{bull_hist}"
                    )
                if bear_hist:
                    message_buffer.update_report_section(
                        "investment_plan", f"### Bear Researcher Analysis\n{bear_hist}"
                    )
                if judge:
                    message_buffer.update_report_section(
                        "investment_plan", f"### Research Manager Decision\n{judge}"
                    )
                    update_research_team_status("completed")
                    message_buffer.update_agent_status("Trader", "in_progress")

            # Process Trading Team results
            if chunk.get("trader_investment_plan"):
                message_buffer.update_report_section(
                    "trader_investment_plan", chunk["trader_investment_plan"]
                )
                if message_buffer.agent_status.get("Trader") != "completed":
                    message_buffer.update_agent_status("Trader", "completed")
                    message_buffer.update_agent_status(
                        "Aggressive Analyst", "in_progress"
                    )

            # Process Risk Management Team results (Risk Debate)
            if chunk.get("risk_debate_state"):
                risk_state = chunk["risk_debate_state"]
                agg_hist = risk_state.get("aggressive_history", "").strip()
                con_hist = risk_state.get("conservative_history", "").strip()
                neu_hist = risk_state.get("neutral_history", "").strip()
                judge = risk_state.get("judge_decision", "").strip()

                if agg_hist:
                    if (
                        message_buffer.agent_status.get("Aggressive Analyst")
                        != "completed"
                    ):
                        message_buffer.update_agent_status(
                            "Aggressive Analyst", "in_progress"
                        )
                    message_buffer.update_report_section(
                        "final_trade_decision",
                        f"### Aggressive Analyst Analysis\n{agg_hist}",
                    )
                if con_hist:
                    if (
                        message_buffer.agent_status.get("Conservative Analyst")
                        != "completed"
                    ):
                        message_buffer.update_agent_status(
                            "Conservative Analyst", "in_progress"
                        )
                    message_buffer.update_report_section(
                        "final_trade_decision",
                        f"### Conservative Analyst Analysis\n{con_hist}",
                    )
                if neu_hist:
                    if (
                        message_buffer.agent_status.get("Neutral Analyst")
                        != "completed"
                    ):
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "in_progress"
                        )
                    message_buffer.update_report_section(
                        "final_trade_decision",
                        f"### Neutral Analyst Analysis\n{neu_hist}",
                    )
                if judge:
                    if (
                        message_buffer.agent_status.get("Portfolio Manager")
                        != "completed"
                    ):
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "in_progress"
                        )
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### Portfolio Manager Decision\n{judge}",
                        )
                        # Mark all risk team as complete when judge decides
                        message_buffer.update_agent_status(
                            "Aggressive Analyst", "completed"
                        )
                        message_buffer.update_agent_status(
                            "Conservative Analyst", "completed"
                        )
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "completed"
                        )
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "completed"
                        )

            # Refresh the live display
            update_display(layout, stats_handler=stats_handler, start_time=start_time)

            trace.append(chunk)

        # Analysis complete - finalize state
        final_state = trace[-1]
        decision = graph.process_signal(final_state["final_trade_decision"])

        # Mark all agents as completed
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")

        message_buffer.add_message(
            "System", f"Completed analysis for {selections['analysis_date']}"
        )

        # Update all report sections from final state
        for section in message_buffer.report_sections.keys():
            if section in final_state:
                message_buffer.update_report_section(section, final_state[section])

        update_display(layout, stats_handler=stats_handler, start_time=start_time)

    # PHASE 4: Post-analysis (outside Live context for clean interaction)
    console.print("\n[bold cyan]Analysis Complete![/bold cyan]\n")

    # Prompt to save report
    save_choice = typer.prompt("Save report?", default="Y").strip().upper()
    if save_choice in ("Y", "YES", ""):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = Path.cwd() / "reports" / f"{selections['ticker']}_{timestamp}"
        save_path_str = typer.prompt(
            "Save path (press Enter for default)", default=str(default_path)
        ).strip()
        save_path = Path(save_path_str)
        try:
            report_file = save_report_to_disk(
                final_state, selections["ticker"], save_path
            )
            console.print(f"\n[green]✓ Report saved to:[/green] {save_path.resolve()}")
            console.print(f"  [dim]Complete report:[/dim] {report_file.name}")
        except Exception as e:
            console.print(f"[red]Error saving report: {e}[/red]")

    # Prompt to display full report
    display_choice = (
        typer.prompt("\nDisplay full report on screen?", default="Y").strip().upper()
    )
    if display_choice in ("Y", "YES", ""):
        display_complete_report(final_state)


@app.command()
def analyze():
    """CLI command entry point."""
    run_analysis()


if __name__ == "__main__":
    app()

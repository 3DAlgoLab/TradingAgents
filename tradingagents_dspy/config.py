"""DSPy configuration module for TradingAgents.

This module provides DSPy initialization and configuration.
"""

import os
from typing import Dict, Any, Optional
import dspy

DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": None,
    "openai_reasoning_effort": None,
    "google_thinking_level": None,
    "num_debate_rounds": 1,
    "enable_memory": False,
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    },
}


def configure_dspy(config: Optional[Dict[str, Any]] = None) -> dspy.LM:
    """Initialize DSPy with the configured LLM provider.

    This function configures DSPy to use the specified LLM provider.

    Args:
        config: Configuration dictionary. If None, uses DEFAULT_CONFIG.
               Expected keys:
               - llm_provider: Provider name (openai, anthropic, google, xai, openrouter)
               - deep_think_llm: Model name for complex reasoning
               - quick_think_llm: Model name for simpler tasks (optional)
               - backend_url: Optional custom API endpoint
               - openai_reasoning_effort: Reasoning effort for OpenAI (low/medium/high)
               - google_thinking_level: Thinking level for Google Gemini

    Returns:
        Configured dspy.LM instance

    Raises:
        ValueError: If configuration is invalid or provider is unsupported
        RuntimeError: If DSPy initialization fails

    Example:
        >>> from tradingagents_dspy.config import configure_dspy, DEFAULT_CONFIG
        >>> lm = configure_dspy(DEFAULT_CONFIG)
        >>> # Now DSPy is ready to use
        >>> print(dspy.settings.lm)
    """
    # Use local default config if none provided
    if config is None:
        config = DEFAULT_CONFIG.copy()

    # Validate that we have actual configuration values
    provider = (
        config.get("llm_provider", "").lower() if config.get("llm_provider") else ""
    )
    model = config.get("deep_think_llm", "") if config.get("deep_think_llm") else ""
    base_url = config.get("backend_url")

    # Validate required configuration
    if not provider:
        raise ValueError("llm_provider must be specified in config")
    if not model:
        raise ValueError("deep_think_llm must be specified in config")

    # Build the model string for DSPy
    # DSPy uses format: "provider/model" or "openai/gpt-4", etc.
    if provider in ("openai", "anthropic", "google", "xai"):
        dspy_model = f"{provider}/{model}"
    elif provider == "openrouter":
        # OpenRouter uses openai-compatible API
        dspy_model = (
            f"openrouter/{model}" if not model.startswith("openrouter/") else model
        )
    elif provider == "ollama":
        # Ollama uses local models
        dspy_model = f"ollama/{model}"
    else:
        raise ValueError(f"Unsupported LLM provider for DSPy: {provider}")

    # Build kwargs for LM initialization
    lm_kwargs: Dict[str, Any] = {}

    # Disable caching to avoid LiteLLM __annotations__ bug
    lm_kwargs["cache"] = False

    # Add base_url if specified (for custom endpoints like OpenRouter)
    if base_url:
        lm_kwargs["api_base"] = base_url

    # Add provider-specific settings
    if provider == "openai":
        reasoning_effort = config.get("openai_reasoning_effort")
        if reasoning_effort:
            lm_kwargs["reasoning_effort"] = reasoning_effort
    elif provider == "google":
        thinking_level = config.get("google_thinking_level")
        if thinking_level:
            lm_kwargs["thinking_level"] = thinking_level

    # Get API key from environment
    api_key = _get_api_key(provider)
    if api_key:
        lm_kwargs["api_key"] = api_key

    try:
        # Create and configure the LM
        lm = dspy.LM(model=dspy_model, **lm_kwargs)

        # Configure DSPy to use this LM globally
        dspy.configure(lm=lm)

        return lm

    except Exception as e:
        raise RuntimeError(f"Failed to initialize DSPy with model {dspy_model}: {e}")


def _get_api_key(provider: str) -> Optional[str]:
    """Get API key from environment variables based on provider.

    Args:
        provider: LLM provider name

    Returns:
        API key string or None if not found
    """
    provider_lower = provider.lower()

    env_var_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "xai": "XAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }

    env_var = env_var_map.get(provider_lower)
    if env_var:
        return os.getenv(env_var)

    return None


def get_lm() -> dspy.LM:
    """Get the currently configured DSPy LM.

    Returns:
        The currently configured dspy.LM instance

    Raises:
        RuntimeError: If DSPy has not been configured yet
    """
    try:
        lm = dspy.settings.lm
        # Check if LM is actually configured (not None)
        if lm is None:
            raise RuntimeError(
                "DSPy has not been configured. Call configure_dspy() first."
            )
        return lm
    except AttributeError:
        raise RuntimeError("DSPy has not been configured. Call configure_dspy() first.")


def reset_dspy() -> None:
    """Reset DSPy configuration.

    This is useful for testing or when you need to reconfigure with different settings.
    """
    dspy.configure(lm=None)


# Convenience function for quick setup
def quick_setup(
    provider: str = "openai",
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> dspy.LM:
    """Quick setup for DSPy without using full TradingAgents config.

    Args:
        provider: LLM provider name
        model: Model name
        api_key: API key (if None, reads from environment)
        base_url: Optional custom API endpoint

    Returns:
        Configured dspy.LM instance
    """
    config = {
        "llm_provider": provider,
        "deep_think_llm": model,
        "backend_url": base_url,
    }

    if api_key:
        os.environ[f"{provider.upper()}_API_KEY"] = api_key

    return configure_dspy(config)

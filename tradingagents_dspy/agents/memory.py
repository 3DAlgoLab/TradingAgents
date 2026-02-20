"""Memory integration wrapper for DSPy agents.

This module provides a simple in-memory storage for trading situations and outcomes,
without depending on the main tradingagents package.
"""

from typing import List, Dict, Optional


class SimpleMemory:
    """Simple in-memory storage for trading memories.

    This is a standalone memory implementation that doesn't require
    the main tradingagents package.
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self.documents: List[Dict] = []
        self.situations: List[str] = []
        self.recommendations: List[str] = []

    def add_situations(self, situations: List[tuple]) -> None:
        """Add situations and recommendations.

        Args:
            situations: List of (situation, recommendation) tuples
        """
        for situation, recommendation in situations:
            self.situations.append(situation)
            self.recommendations.append(recommendation)
            self.documents.append(
                {
                    "situation": situation,
                    "recommendation": recommendation,
                }
            )

    def get_memories(self, situation: str, n_matches: int = 2) -> List[Dict]:
        """Get relevant memories (simple substring matching).

        Args:
            situation: Current situation to match against
            n_matches: Number of matches to return

        Returns:
            List of matching documents
        """
        if not self.situations:
            return []

        # Simple relevance scoring based on word overlap
        situation_words = set(situation.lower().split())
        scores = []
        for i, stored_situation in enumerate(self.situations):
            stored_words = set(stored_situation.lower().split())
            overlap = len(situation_words & stored_words)
            scores.append((i, overlap))

        # Sort by score and return top n_matches
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scores[:n_matches]:
            if score > 0:
                results.append(self.documents[idx])

        return results

    def clear(self) -> None:
        """Clear all memories."""
        self.documents.clear()
        self.situations.clear()
        self.recommendations.clear()


class MemoryWrapper:
    """Wrapper for memory system with DSPy-friendly interface.

    This class provides a simplified interface to the memory system
    for use with DSPy agents.

    Example:
        >>> from tradingagents_dspy.agents.memory import MemoryWrapper
        >>> memory = MemoryWrapper(name="trading_memory")
        >>> memories = memory.get_memories("high tech sector volatility", n_matches=2)
    """

    def __init__(self, name: str = "default", config: Optional[Dict] = None):
        """Initialize the memory wrapper.

        Args:
            name: Name identifier for this memory instance
            config: Configuration dict (ignored in standalone version)
        """
        self.memory = SimpleMemory(name=name)

    def get_memories(self, situation: str, n_matches: int = 2) -> str:
        """Get relevant memories for a given situation.

        Args:
            situation: Current financial situation to match against
            n_matches: Number of top matches to return

        Returns:
            Formatted string of memories and lessons learned
        """
        matches = self.memory.get_memories(situation, n_matches=n_matches)

        if not matches:
            return "No past memories found."

        memories_str = ""
        for i, rec in enumerate(matches, 1):
            memories_str += f"Lesson {i}: {rec.get('recommendation', '')}\n\n"

        return memories_str

    def add_situation(self, situation: str, recommendation: str) -> None:
        """Add a new situation and its outcome to memory.

        Args:
            situation: Description of the financial situation
            recommendation: The recommendation or lesson learned
        """
        self.memory.add_situations([(situation, recommendation)])

    def add_trade_result(
        self,
        market_analysis: str,
        sentiment_analysis: str,
        news_analysis: str,
        fundamentals_analysis: str,
        trade_decision: str,
        outcome: str,
    ) -> None:
        """Add a completed trade result to memory.

        Args:
            market_analysis: Market analysis at time of trade
            sentiment_analysis: Sentiment analysis at time of trade
            news_analysis: News analysis at time of trade
            fundamentals_analysis: Fundamentals analysis at time of trade
            trade_decision: The trade decision made (BUY/SELL/HOLD)
            outcome: The outcome/result of the trade
        """
        situation = (
            f"Market: {market_analysis}\n"
            f"Sentiment: {sentiment_analysis}\n"
            f"News: {news_analysis}\n"
            f"Fundamentals: {fundamentals_analysis}"
        )

        recommendation = f"Decision: {trade_decision}. Outcome: {outcome}"
        self.add_situation(situation, recommendation)

    def clear(self) -> None:
        """Clear all stored memories."""
        self.memory.clear()

    def get_stats(self) -> Dict[str, int | str]:
        """Get memory statistics.

        Returns:
            Dictionary with memory statistics
        """
        return {
            "total_memories": len(self.memory.documents),
            "name": self.memory.name,
        }


def create_memory_wrapper(
    name: str = "trading_memory",
    config: Optional[Dict] = None,
) -> MemoryWrapper:
    """Factory function to create a MemoryWrapper.

    Args:
        name: Name for the memory instance
        config: Optional configuration dict

    Returns:
        MemoryWrapper instance
    """
    return MemoryWrapper(name=name, config=config)


__all__ = [
    "MemoryWrapper",
    "SimpleMemory",
    "create_memory_wrapper",
]

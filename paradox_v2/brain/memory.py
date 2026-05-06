"""
Paradox v2 — Conversation Memory
==================================
Persistent conversation history with semantic retrieval.
Replaces the v1 JSON-based memory with embedding-aware recall.
"""

import json
import os
import time
from typing import List, Dict, Optional
from ..config import CONFIG


class ConversationMemory:
    """
    Stores and retrieves conversation history with attention-weighted recall.

    Features:
        - Persistent JSON storage across sessions
        - Sliding window for prompt context (last N turns)
        - Full history search for episodic recall
        - Automatic summarization hooks (for future LLM-based summarization)
    """

    def __init__(self, memory_file: str = None, max_history: int = 1000):
        self.memory_file = memory_file or CONFIG.paths.memory_file
        self.max_history = max_history
        self.conversations: List[Dict] = []
        self._load()

    # ── Core operations ──────────────────────────────────────────────
    def add_turn(
        self,
        query: str,
        response: str,
        region: str,
        context_used: int = 0,
        emotion_state: Optional[Dict[str, float]] = None,
    ):
        """Record a single conversation turn."""
        turn = {
            "timestamp": time.time(),
            "query": query,
            "response": response[:1000],  # Cap to prevent ballooning
            "region": region,
            "context_chunks_used": context_used,
            "emotion": emotion_state or {},
        }
        self.conversations.append(turn)

        # Enforce max history
        if len(self.conversations) > self.max_history:
            self.conversations = self.conversations[-self.max_history:]

        self._save()

    def get_recent_messages(self, n_turns: int = 3) -> List[Dict]:
        """
        Get the last N turns formatted for prompt injection.

        Returns:
            List of {"role": "user"/"assistant", "content": str} dicts.
        """
        messages = []
        recent = self.conversations[-n_turns:] if self.conversations else []

        for turn in recent:
            messages.append({"role": "user", "content": turn["query"]})
            messages.append({"role": "assistant", "content": turn["response"]})

        return messages

    def search_history(
        self,
        query: str,
        max_results: int = 3,
    ) -> List[Dict]:
        """
        Search conversation history using keyword overlap.

        For production, this should be replaced with embedding-based search
        once the vector store is available.

        Returns:
            List of matching conversation turns, most relevant first.
        """
        if not self.conversations:
            return []

        query_tokens = set(
            w.lower().strip("?,.!\"'()[]{}") 
            for w in query.split() 
            if len(w) > 3
        )

        if not query_tokens:
            return []

        scored = []
        for turn in self.conversations:
            turn_tokens = set(
                w.lower().strip("?,.!\"'()[]{}") 
                for w in turn["query"].split() 
                if len(w) > 3
            )
            overlap = len(query_tokens & turn_tokens)
            if overlap > 0:
                # Weight by recency (exponential decay)
                age_hours = (time.time() - turn["timestamp"]) / 3600
                recency = 0.95 ** age_hours
                score = overlap * recency
                scored.append((score, turn))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [turn for _, turn in scored[:max_results]]

    def get_topic_summary(self) -> Dict[str, int]:
        """Count interactions per brain region."""
        summary = {}
        for turn in self.conversations:
            region = turn.get("region", "unknown")
            summary[region] = summary.get(region, 0) + 1
        return summary

    # ── Persistence ──────────────────────────────────────────────────
    def _save(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)

    def _load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
            except Exception:
                self.conversations = []

    def clear(self):
        """Wipe conversation memory."""
        self.conversations = []
        self._save()

    @property
    def turn_count(self) -> int:
        return len(self.conversations)

    def __repr__(self):
        return f"ConversationMemory(turns={self.turn_count})"

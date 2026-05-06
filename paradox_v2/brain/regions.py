"""
Paradox v2 — Brain Region Router
==================================
Routes queries to the appropriate brain region based on query analysis.
Each region triggers different prompt templates and retrieval strategies.

Region semantics:
    PFC — Prefrontal Cortex: Analytical reasoning, chain-of-thought
    LH  — Left Hemisphere:   Factual precision, definitions, citations
    RH  — Right Hemisphere:  Creative synthesis, analogies, lateral thinking
    HC  — Hippocampus:       Memory recall, contextual continuity
"""

import re
from typing import Tuple, List, Optional
from ..config import CONFIG


class BrainRouter:
    """
    Determines which brain region should handle a given query.

    Strategy:
        1. Keyword-based classification (fast, deterministic)
        2. Query structure analysis (question type detection)
        3. Fallback to PFC (analytical reasoning) as default
    """

    # ── Region classification keywords ───────────────────────────────
    REGION_SIGNALS = {
        "PFC": {
            "keywords": [
                "analyze", "analysis", "explain why", "compare", "contrast",
                "evaluate", "strategy", "plan", "decide", "reason",
                "step by step", "break down", "cause and effect",
                "pros and cons", "trade-off", "implications", "argue",
                "synthesize", "framework", "how does", "methodology",
            ],
            "patterns": [
                r"why\s+(is|are|do|does|did|would|should)",
                r"how\s+(would|should|can|could)\s+",
                r"what\s+(are|is)\s+the\s+(implications|consequences|effects)",
            ],
        },
        "LH": {
            "keywords": [
                "define", "definition", "what is", "what are",
                "meaning of", "formula", "equation", "theorem",
                "law of", "principle of", "fact", "exactly",
                "technically", "specifically", "precise", "accurate",
                "classify", "categorize", "list", "enumerate",
            ],
            "patterns": [
                r"what\s+(is|are)\s+(a|an|the)\s+",
                r"define\s+",
                r"(give|provide)\s+(me\s+)?(a\s+)?definition",
            ],
        },
        "RH": {
            "keywords": [
                "creative", "imagine", "metaphor", "analogy",
                "connect", "relate", "like", "similar to",
                "brainstorm", "idea", "inspiration", "vision",
                "abstract", "conceptual", "philosophy", "art",
                "intuition", "feel", "sense", "pattern",
                "symbolism", "dream", "aesthetic", "beauty",
            ],
            "patterns": [
                r"how\s+(is|are|does)\s+.+\s+(like|similar|related)\s+",
                r"what\s+if\s+",
                r"imagine\s+",
            ],
        },
        "HC": {
            "keywords": [
                "remember", "recall", "previous", "earlier",
                "last time", "before", "we discussed", "you said",
                "history", "conversation", "context", "follow up",
                "continue", "as before", "going back", "revisit",
            ],
            "patterns": [
                r"(do\s+you\s+)?remember\s+",
                r"(what\s+did\s+)?(we|you|i)\s+(discuss|talk|say)",
                r"(earlier|previously|before)\s+",
            ],
        },
    }

    def route(self, query: str) -> str:
        """
        Classify a query into a brain region.

        Returns:
            Region code: "PFC", "LH", "RH", or "HC"
        """
        query_lower = query.lower().strip()
        scores = {region: 0.0 for region in CONFIG.brain.regions}

        for region, signals in self.REGION_SIGNALS.items():
            # Keyword matching
            for kw in signals["keywords"]:
                if kw in query_lower:
                    scores[region] += 1.0

            # Pattern matching
            for pattern in signals["patterns"]:
                if re.search(pattern, query_lower):
                    scores[region] += 2.0  # Patterns are stronger signals

        # Return highest-scoring region, defaulting to PFC
        best = max(scores, key=scores.get)
        if scores[best] == 0.0:
            return "PFC"  # Default: analytical reasoning
        return best

    def route_with_confidence(self, query: str) -> Tuple[str, float]:
        """
        Route with a confidence score.

        Returns:
            (region_code, confidence) where confidence ∈ [0, 1]
        """
        query_lower = query.lower().strip()
        scores = {region: 0.0 for region in CONFIG.brain.regions}

        for region, signals in self.REGION_SIGNALS.items():
            for kw in signals["keywords"]:
                if kw in query_lower:
                    scores[region] += 1.0
            for pattern in signals["patterns"]:
                if re.search(pattern, query_lower):
                    scores[region] += 2.0

        total = sum(scores.values())
        if total == 0.0:
            return "PFC", 0.5  # Default with moderate confidence

        best = max(scores, key=scores.get)
        confidence = scores[best] / total if total > 0 else 0.5
        return best, min(1.0, confidence)

    def explain_routing(self, query: str) -> str:
        """Debug: explain why a query was routed to a specific region."""
        region, confidence = self.route_with_confidence(query)
        query_lower = query.lower()

        matched_keywords = []
        for kw in self.REGION_SIGNALS.get(region, {}).get("keywords", []):
            if kw in query_lower:
                matched_keywords.append(kw)

        matched_patterns = []
        for pattern in self.REGION_SIGNALS.get(region, {}).get("patterns", []):
            if re.search(pattern, query_lower):
                matched_patterns.append(pattern)

        return (
            f"Region: {region} (confidence: {confidence:.2f})\n"
            f"  Keywords matched: {matched_keywords}\n"
            f"  Patterns matched: {len(matched_patterns)}"
        )

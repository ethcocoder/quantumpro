"""
Paradox v2 — Emotion Engine
=============================
Maintains an emotional state vector that modulates generation parameters.

Emotions affect:
    - Temperature (curiosity ↑ → more creative outputs)
    - Repetition penalty (joy ↑ → more varied language)
    - Retrieval aggressiveness (fear ↑ → stricter context grounding)

Emotions evolve through interaction feedback loops:
    - Good retrieval matches → reward → joy ↑
    - User engagement (long queries) → curiosity stimulation
    - Low-confidence answers → conflict → fear ↑
"""

import json
import os
import time
from typing import Dict, Optional
from ..config import CONFIG


class EmotionEngine:
    """
    Manages Paradox's emotional state as a continuous vector.

    The emotion state persists across sessions via JSON serialization.
    """

    def __init__(self, state_file: str = None):
        self.state_file = state_file or os.path.join(
            CONFIG.paths.v2_data_dir, "emotion_state.json"
        )

        # Core emotional axes
        self.state: Dict[str, float] = {
            "curiosity": CONFIG.brain.initial_curiosity,
            "joy": CONFIG.brain.initial_joy,
            "fear": CONFIG.brain.initial_fear,
        }

        self._interaction_count = 0
        self._load()

    # ── State access ─────────────────────────────────────────────────
    @property
    def curiosity(self) -> float:
        return self.state["curiosity"]

    @property
    def joy(self) -> float:
        return self.state["joy"]

    @property
    def fear(self) -> float:
        return self.state["fear"]

    @property
    def dominant_emotion(self) -> str:
        return max(self.state, key=self.state.get)

    # ── Emotion modifiers ────────────────────────────────────────────
    def process_reward(self, magnitude: float = 0.1):
        """Good outcome: boost joy, reduce fear."""
        self.state["joy"] = min(1.0, self.state["joy"] + magnitude)
        self.state["fear"] = max(0.0, self.state["fear"] - magnitude * 0.5)
        self._save()

    def process_conflict(self, magnitude: float = 0.15):
        """Bad outcome: boost fear, reduce joy."""
        self.state["fear"] = min(1.0, self.state["fear"] + magnitude)
        self.state["joy"] = max(0.0, self.state["joy"] - magnitude * 0.3)
        self._save()

    def stimulate_curiosity(self, query_length: int):
        """Longer/more complex queries boost curiosity."""
        if query_length > 50:
            self.state["curiosity"] = min(1.0, self.state["curiosity"] + 0.05)
        elif query_length < 15:
            self.state["curiosity"] = max(0.1, self.state["curiosity"] - 0.02)
        self._save()

    def apply_decay(self):
        """Natural decay toward equilibrium after each interaction."""
        self.state["curiosity"] = max(0.3, self.state["curiosity"] - CONFIG.brain.curiosity_decay)
        self.state["joy"] = max(0.2, self.state["joy"] - CONFIG.brain.joy_decay)
        self.state["fear"] = max(0.0, self.state["fear"] - CONFIG.brain.fear_decay)
        self._interaction_count += 1
        self._save()

    # ── Generation parameter modifiers ───────────────────────────────
    def get_temperature_modifier(self) -> float:
        """
        Returns a temperature delta based on emotional state.
        Positive = more creative, Negative = more conservative.
        """
        curiosity_effect = (self.curiosity - 0.5) * CONFIG.brain.curiosity_temp_boost * 2
        fear_effect = -(self.fear - 0.1) * CONFIG.brain.fear_temp_reduction
        return curiosity_effect + fear_effect

    def get_generation_params(self) -> Dict[str, float]:
        """
        Returns adjusted generation parameters based on current emotion.
        """
        base_temp = CONFIG.model.temperature
        base_rep = CONFIG.model.repetition_penalty

        adjusted_temp = base_temp + self.get_temperature_modifier()
        adjusted_rep = base_rep - self.joy * CONFIG.brain.joy_repetition_bonus

        return {
            "temperature": max(0.1, min(1.5, adjusted_temp)),
            "repetition_penalty": max(1.0, min(1.5, adjusted_rep)),
            "top_p": CONFIG.model.top_p,
        }

    # ── Persistence ──────────────────────────────────────────────────
    def _save(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        data = {
            "state": self.state,
            "interaction_count": self._interaction_count,
            "last_updated": time.time(),
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                self.state.update(data.get("state", {}))
                self._interaction_count = data.get("interaction_count", 0)
            except Exception:
                pass  # Start fresh on corruption

    def reset(self):
        """Reset to initial emotional state."""
        self.state = {
            "curiosity": CONFIG.brain.initial_curiosity,
            "joy": CONFIG.brain.initial_joy,
            "fear": CONFIG.brain.initial_fear,
        }
        self._interaction_count = 0
        self._save()

    # ── Display ──────────────────────────────────────────────────────
    def status_line(self) -> str:
        return (
            f"[CURIOSITY:{self.curiosity:.2f} | "
            f"JOY:{self.joy:.2f} | "
            f"FEAR:{self.fear:.2f}]"
        )

    def __repr__(self):
        return f"EmotionEngine({self.state})"

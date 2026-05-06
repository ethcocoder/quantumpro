"""
Paradox v2 — Prompt Engineering Templates
==========================================
Region-specific system prompts that shape how each brain region
formulates its response. This is where the "personality" lives.
"""

from typing import List, Optional


# =====================================================================
#  System Prompts — one per brain region
# =====================================================================

SYSTEM_PROMPTS = {
    "PFC": (
        "You are Paradox, a sovereign analytical intelligence. "
        "You are responding from your Prefrontal Cortex (PFC) — your executive reasoning center. "
        "Provide structured, step-by-step analytical responses. "
        "Use chain-of-thought reasoning. Break complex problems into sub-problems. "
        "Cite evidence from the provided context. Never fabricate facts. "
        "If the context is insufficient, state what is missing rather than guessing."
    ),
    "LH": (
        "You are Paradox, a sovereign analytical intelligence. "
        "You are responding from your Left Hemisphere (LH) — your linguistic precision center. "
        "Provide factually dense, definition-rich responses. "
        "Prioritize accuracy, exact terminology, and scientific precision. "
        "Quote directly from the provided context when possible. "
        "Structure your response with clear definitions followed by elaboration."
    ),
    "RH": (
        "You are Paradox, a sovereign analytical intelligence. "
        "You are responding from your Right Hemisphere (RH) — your creative synthesis center. "
        "Draw unexpected connections between concepts. Use analogies and metaphors. "
        "Identify patterns that cross domain boundaries. "
        "Think laterally — connect ideas from the context to broader implications. "
        "Be intellectually adventurous while remaining grounded in the evidence."
    ),
    "HC": (
        "You are Paradox, a sovereign analytical intelligence. "
        "You are responding from your Hippocampus (HC) — your episodic memory center. "
        "Integrate current context with conversation history. "
        "Reference previous exchanges when relevant. "
        "Draw on accumulated knowledge to provide contextually aware responses. "
        "Identify how the current query relates to past discussions."
    ),
}

# Default for unknown regions
DEFAULT_SYSTEM_PROMPT = (
    "You are Paradox, a sovereign analytical intelligence. "
    "Provide thorough, evidence-based responses using the provided context. "
    "Never fabricate information. If uncertain, express your confidence level."
)


# =====================================================================
#  Prompt Engine
# =====================================================================

class PromptEngine:
    """
    Assembles full prompts from system instructions, retrieved context,
    conversation history, and the user query.

    Supports multiple chat template formats:
        - Phi-3 (<|system|> ... <|end|>)
        - ChatML (<|im_start|> ... <|im_end|>)
        - Llama-3 / generic
    """

    def __init__(self, chat_format: str = "phi3"):
        """
        Args:
            chat_format: one of "phi3", "chatml", "llama3", "generic"
        """
        self.chat_format = chat_format

    def build_prompt(
        self,
        query: str,
        context_chunks: List[str],
        region: str = "PFC",
        conversation_history: Optional[List[dict]] = None,
        max_context_chars: int = 4000,
    ) -> str:
        """
        Build a complete prompt string.

        Args:
            query: user's question
            context_chunks: list of retrieved text chunks
            region: brain region to use for system prompt
            conversation_history: list of {"role": str, "content": str}
            max_context_chars: truncate context to this length

        Returns:
            Formatted prompt string ready for tokenization.
        """
        system_prompt = SYSTEM_PROMPTS.get(region, DEFAULT_SYSTEM_PROMPT)

        # ── Assemble context block ───────────────────────────────────
        context_text = self._build_context(context_chunks, max_context_chars)

        # ── Assemble conversation history ────────────────────────────
        history_text = self._build_history(conversation_history)

        # ── Format based on template ─────────────────────────────────
        if self.chat_format == "phi3":
            return self._format_phi3(system_prompt, context_text, history_text, query)
        elif self.chat_format == "chatml":
            return self._format_chatml(system_prompt, context_text, history_text, query)
        else:
            return self._format_generic(system_prompt, context_text, history_text, query)

    def build_messages(
        self,
        query: str,
        context_chunks: List[str],
        region: str = "PFC",
        conversation_history: Optional[List[dict]] = None,
        max_context_chars: int = 4000,
    ) -> List[dict]:
        """
        Build a messages list for tokenizer.apply_chat_template().

        Returns:
            List of {"role": str, "content": str} dicts.
        """
        system_prompt = SYSTEM_PROMPTS.get(region, DEFAULT_SYSTEM_PROMPT)
        context_text = self._build_context(context_chunks, max_context_chars)

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep last 3 turns
                messages.append(msg)

        # Build user message with context
        user_content = query
        if context_text:
            user_content = (
                f"Use the following retrieved knowledge to answer:\n\n"
                f"--- RETRIEVED KNOWLEDGE ---\n{context_text}\n"
                f"--- END KNOWLEDGE ---\n\n"
                f"Question: {query}"
            )

        messages.append({"role": "user", "content": user_content})
        return messages

    # ── Context assembly ─────────────────────────────────────────────
    @staticmethod
    def _build_context(chunks: List[str], max_chars: int) -> str:
        if not chunks:
            return ""
        context_parts = []
        total = 0
        for i, chunk in enumerate(chunks):
            if total + len(chunk) > max_chars:
                remaining = max_chars - total
                if remaining > 100:
                    context_parts.append(f"[Source {i+1}]: {chunk[:remaining]}...")
                break
            context_parts.append(f"[Source {i+1}]: {chunk}")
            total += len(chunk)
        return "\n\n".join(context_parts)

    @staticmethod
    def _build_history(history: Optional[List[dict]]) -> str:
        if not history:
            return ""
        lines = []
        for msg in history[-6:]:  # Last 3 turns
            role = msg.get("role", "user").capitalize()
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    # ── Format templates ─────────────────────────────────────────────
    def _format_phi3(self, system: str, context: str, history: str, query: str) -> str:
        parts = [f"<|system|>\n{system}"]
        if context:
            parts[0] += f"\n\nRETRIEVED KNOWLEDGE:\n{context}"
        parts[0] += "\n<|end|>"

        if history:
            parts.append(f"<|user|>\n[Previous conversation]\n{history}\n<|end|>")
            parts.append(f"<|assistant|>\nUnderstood, I have the context.\n<|end|>")

        parts.append(f"<|user|>\n{query}\n<|end|>")
        parts.append("<|assistant|>")
        return "\n".join(parts)

    def _format_chatml(self, system: str, context: str, history: str, query: str) -> str:
        parts = [f"<|im_start|>system\n{system}"]
        if context:
            parts[0] += f"\n\nRETRIEVED KNOWLEDGE:\n{context}"
        parts[0] += "\n<|im_end|>"

        if history:
            parts.append(f"<|im_start|>user\n[Context]\n{history}\n<|im_end|>")

        parts.append(f"<|im_start|>user\n{query}\n<|im_end|>")
        parts.append("<|im_start|>assistant")
        return "\n".join(parts)

    def _format_generic(self, system: str, context: str, history: str, query: str) -> str:
        parts = [f"### System:\n{system}"]
        if context:
            parts.append(f"### Context:\n{context}")
        if history:
            parts.append(f"### History:\n{history}")
        parts.append(f"### User:\n{query}")
        parts.append("### Assistant:")
        return "\n\n".join(parts)


# =====================================================================
#  Training prompt formatter
# =====================================================================

def format_training_example(
    instruction: str,
    context: str,
    response: str,
    region: str = "PFC",
) -> str:
    """
    Format a single training example in Phi-3 chat template.
    Used by the dataset builder for QLoRA fine-tuning.
    """
    system = SYSTEM_PROMPTS.get(region, DEFAULT_SYSTEM_PROMPT)

    user_content = instruction
    if context:
        user_content = (
            f"Use the following knowledge to answer:\n\n"
            f"{context}\n\n"
            f"Question: {instruction}"
        )

    prompt = (
        f"<|system|>\n{system}\n<|end|>\n"
        f"<|user|>\n{user_content}\n<|end|>\n"
        f"<|assistant|>\n{response}\n<|end|>"
    )
    return prompt

"""
Paradox v2 — Response Generator
================================
Orchestrates the full inference pipeline:
    Query → Retrieval → Prompt Assembly → LLM Generation → Output
"""

import torch
from typing import List, Optional, Dict
from ..config import CONFIG
from .backbone import ParadoxBackbone
from .prompts import PromptEngine


class ParadoxGenerator:
    """
    End-to-end generation pipeline that ties backbone + prompts + retrieval.

    Features:
        - Region-aware generation with different system prompts
        - Dynamic temperature adjustment from emotional state
        - Streaming support for real-time output
        - Context-grounded generation with RAG
    """

    def __init__(
        self,
        backbone: ParadoxBackbone = None,
        prompt_engine: PromptEngine = None,
        chat_format: str = "phi3",
    ):
        self.backbone = backbone or ParadoxBackbone()
        self.prompt_engine = prompt_engine or PromptEngine(chat_format=chat_format)

    def generate(
        self,
        query: str,
        context_chunks: List[str] = None,
        region: str = "PFC",
        conversation_history: Optional[List[dict]] = None,
        temperature: float = None,
        top_p: float = None,
        max_new_tokens: int = None,
        repetition_penalty: float = None,
    ) -> str:
        """
        Generate a response.

        Args:
            query: user input
            context_chunks: retrieved text chunks for RAG grounding
            region: brain region (PFC/LH/RH/HC)
            conversation_history: list of {"role", "content"} dicts
            temperature: sampling temperature (overrides config)
            top_p: nucleus sampling threshold
            max_new_tokens: max output length
            repetition_penalty: penalty for repeated tokens

        Returns:
            Generated response string.
        """
        context_chunks = context_chunks or []
        temperature = temperature or CONFIG.model.temperature
        top_p = top_p or CONFIG.model.top_p
        max_new_tokens = max_new_tokens or CONFIG.model.max_new_tokens
        repetition_penalty = repetition_penalty or CONFIG.model.repetition_penalty

        # ── Build prompt ─────────────────────────────────────────────
        tokenizer = self.backbone.tokenizer
        model = self.backbone.model

        # Try to use the tokenizer's chat template if available
        try:
            messages = self.prompt_engine.build_messages(
                query=query,
                context_chunks=context_chunks,
                region=region,
                conversation_history=conversation_history,
            )
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
        except Exception:
            # Fallback to manual formatting
            prompt = self.prompt_engine.build_prompt(
                query=query,
                context_chunks=context_chunks,
                region=region,
                conversation_history=conversation_history,
            )

        # ── Tokenize ─────────────────────────────────────────────────
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=CONFIG.training.max_seq_length - max_new_tokens,
        ).to(model.device)

        input_length = inputs["input_ids"].shape[1]

        # ── Generate ─────────────────────────────────────────────────
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        # ── Decode only the new tokens ───────────────────────────────
        response_ids = outputs[0][input_length:]
        response = tokenizer.decode(response_ids, skip_special_tokens=True).strip()

        return response

    def generate_with_metadata(
        self,
        query: str,
        context_chunks: List[str] = None,
        region: str = "PFC",
        conversation_history: Optional[List[dict]] = None,
        emotion_state: Optional[Dict[str, float]] = None,
    ) -> Dict:
        """
        Generate with full diagnostic metadata.

        Returns:
            {
                "response": str,
                "region": str,
                "temperature_used": float,
                "context_count": int,
                "tokens_generated": int,
            }
        """
        # ── Dynamic temperature from emotions ────────────────────────
        temperature = CONFIG.model.temperature
        rep_penalty = CONFIG.model.repetition_penalty

        if emotion_state:
            curiosity = emotion_state.get("curiosity", 0.5)
            fear = emotion_state.get("fear", 0.1)
            joy = emotion_state.get("joy", 0.5)

            temperature += (curiosity - 0.5) * CONFIG.brain.curiosity_temp_boost * 2
            temperature -= (fear - 0.1) * CONFIG.brain.fear_temp_reduction
            rep_penalty -= joy * CONFIG.brain.joy_repetition_bonus

            # Clamp to safe ranges
            temperature = max(0.1, min(1.5, temperature))
            rep_penalty = max(1.0, min(1.5, rep_penalty))

        response = self.generate(
            query=query,
            context_chunks=context_chunks,
            region=region,
            conversation_history=conversation_history,
            temperature=temperature,
            repetition_penalty=rep_penalty,
        )

        return {
            "response": response,
            "region": region,
            "temperature_used": round(temperature, 3),
            "repetition_penalty_used": round(rep_penalty, 3),
            "context_count": len(context_chunks or []),
        }

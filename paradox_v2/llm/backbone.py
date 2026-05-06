"""
Paradox v2 — LLM Backbone Loader
==================================
Loads a Transformer model with 4-bit quantization (NF4).
Supports both base inference and LoRA-adapted checkpoints.
"""

import os
from typing import Optional
from ..config import CONFIG, ModelConfig


class ParadoxBackbone:
    """
    Lazy-loading LLM backbone with 4-bit quantization.

    Supports:
        - Base model loading with BitsAndBytes NF4
        - LoRA adapter merging for fine-tuned checkpoints
        - Automatic device mapping for GPU/CPU split
    """

    def __init__(self, config: ModelConfig = None):
        self.config = config or CONFIG.model
        self._model = None
        self._tokenizer = None

    # ── Lazy loaders ─────────────────────────────────────────────────
    @property
    def tokenizer(self):
        if self._tokenizer is None:
            self._load()
        return self._tokenizer

    @property
    def model(self):
        if self._model is None:
            self._load()
        return self._model

    def _load(self):
        """Load model and tokenizer with 4-bit quantization."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        except ImportError:
            raise ImportError(
                "transformers and bitsandbytes are required for Paradox v2 LLM.\n"
                "Install: pip install transformers bitsandbytes accelerate"
            )

        print(f"[BACKBONE] Loading: {self.config.base_model}")
        print(f"[BACKBONE] Quantization: {'4-bit NF4' if self.config.load_in_4bit else 'Full precision'}")

        # ── Tokenizer ────────────────────────────────────────────────
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model,
            trust_remote_code=True,
        )
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token
            self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

        # ── Quantization config ──────────────────────────────────────
        model_kwargs = {
            "device_map": self.config.device_map,
            "trust_remote_code": True,
            "torch_dtype": self.config.compute_dtype,
        }

        if self.config.load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
                bnb_4bit_compute_dtype=self.config.compute_dtype,
                bnb_4bit_use_double_quant=self.config.bnb_4bit_use_double_quant,
            )
            model_kwargs["quantization_config"] = bnb_config

        # ── Load model ───────────────────────────────────────────────
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            **model_kwargs,
        )
        self._model.eval()

        # Stats
        param_count = sum(p.numel() for p in self._model.parameters())
        trainable = sum(p.numel() for p in self._model.parameters() if p.requires_grad)
        print(f"[BACKBONE] Loaded: {param_count / 1e9:.2f}B params "
              f"({trainable / 1e6:.1f}M trainable)")

    # ── LoRA adapter loading ─────────────────────────────────────────
    def load_adapter(self, adapter_path: str):
        """Load a LoRA adapter on top of the base model."""
        try:
            from peft import PeftModel
        except ImportError:
            raise ImportError(
                "peft is required for LoRA adapter loading.\n"
                "Install: pip install peft"
            )

        if not os.path.exists(adapter_path):
            raise FileNotFoundError(f"Adapter not found: {adapter_path}")

        print(f"[BACKBONE] Loading LoRA adapter: {adapter_path}")
        self._model = PeftModel.from_pretrained(self.model, adapter_path)
        self._model.eval()
        print("[BACKBONE] LoRA adapter merged successfully.")

    # ── Utilities ────────────────────────────────────────────────────
    @property
    def device(self):
        """Return the device of the first parameter."""
        return next(self.model.parameters()).device

    def memory_footprint(self) -> str:
        """Return approximate GPU memory usage."""
        import torch
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            return f"Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB"
        return "No CUDA device"

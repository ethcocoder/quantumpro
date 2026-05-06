"""
Paradox v2 — Central Configuration
===================================
All hyperparameters, paths, and model identifiers live here.
Nothing is hardcoded inside modules.
"""

import os
import torch
from dataclasses import dataclass, field
from typing import List, Optional

# ─── Resolve project root relative to this file ───────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(_THIS_DIR)


# =====================================================================
#  Model Configuration
# =====================================================================
@dataclass
class ModelConfig:
    """LLM backbone settings — tuned for T4 (15 GB VRAM)."""

    # ── Base model ────────────────────────────────────────────────────
    base_model: str = "microsoft/Phi-3.5-mini-instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"

    # ── 4-bit Quantization (BitsAndBytes NF4) ─────────────────────────
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True

    # ── LoRA Adapter ──────────────────────────────────────────────────
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])

    # ── Generation defaults ───────────────────────────────────────────
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.15

    @property
    def compute_dtype(self):
        return getattr(torch, self.torch_dtype, torch.float16)


# =====================================================================
#  Retrieval Configuration
# =====================================================================
@dataclass
class RetrievalConfig:
    """Dense vector retrieval settings."""

    encoder_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    chunk_size: int = 512          # tokens per chunk
    chunk_overlap: int = 64        # overlap between consecutive chunks
    top_k: int = 5                 # chunks returned per query
    similarity_threshold: float = 0.25


# =====================================================================
#  Training Configuration
# =====================================================================
@dataclass
class TrainingConfig:
    """QLoRA fine-tuning settings for Colab T4."""

    epochs: int = 3
    per_device_batch_size: int = 2
    gradient_accumulation_steps: int = 8   # effective batch = 16
    learning_rate: float = 2e-4
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = 0.03
    max_seq_length: int = 1024
    gradient_checkpointing: bool = True
    optim: str = "paged_adamw_8bit"
    fp16: bool = False
    bf16: bool = False
    logging_steps: int = 10
    save_steps: int = 100
    save_total_limit: int = 3
    output_dir: str = os.path.join(PROJECT_ROOT, "paradox_qlora_checkpoints")
    report_to: str = "none"        # set to "wandb" if you want W&B logging


# =====================================================================
#  Brain / Emotion Configuration
# =====================================================================
@dataclass
class BrainConfig:
    """Brain-region routing and emotion parameters."""

    regions: List[str] = field(default_factory=lambda: ["PFC", "LH", "RH", "HC"])

    # Temperature modifiers per emotion axis
    curiosity_temp_boost: float = 0.15     # high curiosity → more creative
    fear_temp_reduction: float = 0.20      # high fear → more conservative
    joy_repetition_bonus: float = 0.05     # high joy → less repetition penalty

    # Emotion decay rates (per interaction)
    curiosity_decay: float = 0.02
    joy_decay: float = 0.01
    fear_decay: float = 0.05

    # Initial emotion state
    initial_curiosity: float = 0.8
    initial_joy: float = 0.5
    initial_fear: float = 0.1


# =====================================================================
#  Path Configuration
# =====================================================================
@dataclass
class PathConfig:
    """All filesystem paths."""

    project_root: str = PROJECT_ROOT
    brain_dir: str = os.path.join(PROJECT_ROOT, "paradox_brain")
    v2_data_dir: str = os.path.join(PROJECT_ROOT, "paradox_v2_data")
    faiss_index_path: str = os.path.join(PROJECT_ROOT, "paradox_v2_data", "faiss_index")
    chunks_store_path: str = os.path.join(PROJECT_ROOT, "paradox_v2_data", "chunks.pkl")
    memory_file: str = os.path.join(PROJECT_ROOT, "paradox_v2_data", "conversation_memory.json")
    training_data_path: str = os.path.join(PROJECT_ROOT, "paradox_v2_data", "training_data.jsonl")
    v1_shards: List[str] = field(default_factory=lambda: ["PFC", "LH", "RH", "HC"])

    def ensure_dirs(self):
        """Create all required directories."""
        for d in [self.brain_dir, self.v2_data_dir,
                  os.path.dirname(self.faiss_index_path)]:
            os.makedirs(d, exist_ok=True)


# =====================================================================
#  Master Config — single import point
# =====================================================================
@dataclass
class ParadoxConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    brain: BrainConfig = field(default_factory=BrainConfig)
    paths: PathConfig = field(default_factory=PathConfig)

    def __post_init__(self):
        self.paths.ensure_dirs()


# Singleton for quick access
CONFIG = ParadoxConfig()

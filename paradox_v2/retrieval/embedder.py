"""
Paradox v2 — Embedding Engine
==============================
Wraps sentence-transformers for dense vector encoding.
Lazy-loads the model on first use to avoid import-time GPU allocation.
"""

import numpy as np
from typing import List, Optional
from ..config import CONFIG


class ParadoxEmbedder:
    """
    Encodes text into dense vectors using a sentence-transformer model.

    Features:
        - Lazy model loading (no GPU grab until first encode call)
        - Batch encoding with progress bar for large corpora
        - L2-normalised output for cosine similarity via inner product
    """

    def __init__(self, model_name: str = None, device: str = None):
        self.model_name = model_name or CONFIG.retrieval.encoder_model
        self.device = device  # None = auto-detect
        self._model = None

    # ── Lazy loader ──────────────────────────────────────────────────
    @property
    def model(self):
        if self._model is None:
            self._load()
        return self._model

    def _load(self):
        """Lazy load the transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for Paradox v2 retrieval.\n"
                    "Install: pip install sentence-transformers"
                )
            print(f"[EMBEDDER] Loading encoder: {self.model_name} ...")
            
            # Load model
            self._model = SentenceTransformer(self.model_name, device=self.device)
            
            # Use updated method name to avoid FutureWarnings
            self.dimension = self._model.get_embedding_dimension()
            print(f"[EMBEDDER] Encoder ready. Dim={self.dimension}")

    # ── Encode ───────────────────────────────────────────────────────
    def encode(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress: bool = False,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Encode a list of texts into dense vectors.

        Args:
            texts: list of strings to encode.
            batch_size: encoding batch size (64 is safe for T4).
            show_progress: show tqdm progress bar.
            normalize: L2-normalize vectors (required for inner-product search).

        Returns:
            np.ndarray of shape (len(texts), embedding_dim), dtype float32.
        """
        if not texts:
            return np.empty((0, CONFIG.retrieval.embedding_dim), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """Encode a single query string. Returns shape (1, dim)."""
        return self.encode([query], normalize=normalize)

    @property
    def dim(self) -> int:
        """Return embedding dimensionality."""
        return self.model.get_sentence_embedding_dimension()

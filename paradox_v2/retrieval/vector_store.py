"""
Paradox v2 — FAISS Vector Store
=================================
Production-grade vector index with region-tagged chunk storage.
Supports add, search, save/load, and per-region filtering.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
from ..config import CONFIG


class ParadoxVectorStore:
    """
    Dense vector store backed by FAISS with metadata sidecar.

    Each chunk is stored with:
        - text (str): the actual text content
        - region (str): brain region tag (PFC/LH/RH/HC)
        - topic (str): source topic name
        - index (int): position within the source document

    The FAISS index uses Inner Product (IP) similarity on L2-normalised
    vectors, which is equivalent to cosine similarity but faster.
    """

    def __init__(
        self,
        dim: int = None,
        index_path: str = None,
        chunks_path: str = None,
    ):
        self.dim = dim or CONFIG.retrieval.embedding_dim
        self.index_path = index_path or CONFIG.paths.faiss_index_path
        self.chunks_path = chunks_path or CONFIG.paths.chunks_store_path

        self._index = None
        self.chunks: List[dict] = []       # parallel array to FAISS index
        self._loaded = False

    # ── Lazy FAISS init ──────────────────────────────────────────────
    @property
    def index(self):
        if self._index is None:
            try:
                import faiss
            except ImportError:
                raise ImportError(
                    "faiss-cpu is required for Paradox v2 retrieval.\n"
                    "Install: pip install faiss-cpu"
                )
            # Inner Product index — cosine sim on normalised vectors
            self._index = faiss.IndexFlatIP(self.dim)
            print(f"[VECTOR STORE] Created new FAISS index (dim={self.dim})")
        return self._index

    # ── Core operations ──────────────────────────────────────────────
    def add(
        self,
        embeddings: np.ndarray,
        chunk_metadata: List[dict],
    ):
        """
        Add vectors and their metadata to the store.

        Args:
            embeddings: float32 array of shape (n, dim)
            chunk_metadata: list of dicts with at least {"text": str}
        """
        assert len(embeddings) == len(chunk_metadata), \
            f"Mismatch: {len(embeddings)} embeddings vs {len(chunk_metadata)} chunks"

        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        self.index.add(embeddings)
        self.chunks.extend(chunk_metadata)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = None,
        region_filter: Optional[str] = None,
        threshold: float = None,
    ) -> List[Tuple[dict, float]]:
        """
        Search for nearest chunks.

        Args:
            query_embedding: float32 array of shape (1, dim)
            top_k: number of results to return
            region_filter: if set, only return chunks from this brain region
            threshold: minimum similarity score

        Returns:
            List of (chunk_dict, similarity_score) tuples, highest first.
        """
        top_k = top_k or CONFIG.retrieval.top_k
        threshold = threshold or CONFIG.retrieval.similarity_threshold

        if self.index.ntotal == 0:
            return []

        # Search more than top_k if filtering by region
        search_k = min(top_k * 4, self.index.ntotal) if region_filter else min(top_k, self.index.ntotal)

        query_embedding = np.ascontiguousarray(query_embedding, dtype=np.float32)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, search_k)

        results = []
        for j, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            score = float(scores[0][j])
            if score < threshold:
                continue
            chunk = self.chunks[idx]
            if region_filter and chunk.get("region") != region_filter:
                continue
            results.append((chunk, score))
            if len(results) >= top_k:
                break

        return results

    # ── Persistence ──────────────────────────────────────────────────
    def save(self):
        """Save FAISS index and chunk metadata to disk."""
        import faiss

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)

        print(f"[VECTOR STORE] Saved {self.index.ntotal} vectors → {self.index_path}")
        print(f"[VECTOR STORE] Saved {len(self.chunks)} chunks → {self.chunks_path}")

    def load(self) -> bool:
        """Load FAISS index and chunk metadata from disk."""
        if not os.path.exists(self.index_path) or not os.path.exists(self.chunks_path):
            return False

        try:
            import faiss
            self._index = faiss.read_index(self.index_path)

            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)

            self._loaded = True
            print(f"[VECTOR STORE] Loaded {self._index.ntotal} vectors, {len(self.chunks)} chunks")
            return True
        except Exception as e:
            print(f"[VECTOR STORE] Load failed: {e}")
            return False

    # ── Stats ────────────────────────────────────────────────────────
    @property
    def total_vectors(self) -> int:
        return self.index.ntotal if self._index else 0

    def region_stats(self) -> Dict[str, int]:
        """Count chunks per brain region."""
        stats = {}
        for chunk in self.chunks:
            region = chunk.get("region", "unknown")
            stats[region] = stats.get(region, 0) + 1
        return stats

    def __repr__(self):
        return (f"ParadoxVectorStore(vectors={self.total_vectors}, "
                f"chunks={len(self.chunks)}, dim={self.dim})")

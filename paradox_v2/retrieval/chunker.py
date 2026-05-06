"""
Paradox v2 — Intelligent Text Chunker
======================================
Splits documents into overlapping windows optimised for embedding models.
Respects sentence boundaries to avoid cutting mid-thought.
"""

import re
from typing import List, Tuple
from ..config import CONFIG


class TextChunker:
    """
    Splits raw text into overlapping chunks suitable for dense retrieval.

    Strategy:
        1. Split text into sentences.
        2. Greedily pack sentences into windows of ≤ `chunk_size` words.
        3. Overlap the last `chunk_overlap` words from the previous chunk
           into the start of the next chunk for context continuity.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or CONFIG.retrieval.chunk_size
        self.chunk_overlap = chunk_overlap or CONFIG.retrieval.chunk_overlap

    # ── Sentence splitter ────────────────────────────────────────────
    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences, handling common abbreviations."""
        # Clean structural noise
        text = re.sub(r'\n{2,}', '. ', text)
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        # Split on sentence-ending punctuation followed by space + capital
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in parts if len(s.strip()) > 10]

    # ── Main chunking logic ──────────────────────────────────────────
    def chunk(
        self,
        text: str,
        metadata: dict = None,
    ) -> List[dict]:
        """
        Chunk a document into overlapping windows.

        Returns a list of dicts:
            {"text": str, "index": int, "word_count": int, **metadata}
        """
        if not text or not text.strip():
            return []

        sentences = self._split_sentences(text)
        if not sentences:
            return [{"text": text[:2000].strip(), "index": 0,
                     "word_count": len(text.split()), **(metadata or {})}]

        chunks = []
        current_words: List[str] = []
        chunk_idx = 0

        for sentence in sentences:
            sent_words = sentence.split()

            # If adding this sentence exceeds the window, flush
            if len(current_words) + len(sent_words) > self.chunk_size and current_words:
                chunk_text = " ".join(current_words)
                chunks.append({
                    "text": chunk_text,
                    "index": chunk_idx,
                    "word_count": len(current_words),
                    **(metadata or {}),
                })
                chunk_idx += 1

                # Keep the overlap tail for context continuity
                overlap_words = current_words[-self.chunk_overlap:] if self.chunk_overlap else []
                current_words = overlap_words

            current_words.extend(sent_words)

        # Flush remaining
        if current_words:
            chunk_text = " ".join(current_words)
            chunks.append({
                "text": chunk_text,
                "index": chunk_idx,
                "word_count": len(current_words),
                **(metadata or {}),
            })

        return chunks

    # ── Batch chunking ───────────────────────────────────────────────
    def chunk_documents(
        self,
        documents: List[Tuple[str, dict]],
    ) -> List[dict]:
        """
        Chunk multiple documents.

        Args:
            documents: list of (text, metadata_dict) tuples.

        Returns:
            Flat list of chunk dicts across all documents.
        """
        all_chunks = []
        for text, meta in documents:
            doc_chunks = self.chunk(text, metadata=meta)
            all_chunks.extend(doc_chunks)
        return all_chunks

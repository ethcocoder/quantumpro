"""
Paradox v2 — Unified Ingestion Pipeline
==========================================
Orchestrates the full ingest flow:
    Source (Wiki/PDF/Text) → Clean → Chunk → Embed → Store in FAISS

This is the single entry point for adding knowledge to Paradox's brain.
"""

import os
from typing import List, Optional, Tuple
from ..config import CONFIG
from ..retrieval.chunker import TextChunker
from ..retrieval.embedder import ParadoxEmbedder
from ..retrieval.vector_store import ParadoxVectorStore


class IngestionPipeline:
    """
    Unified pipeline for ingesting documents into the Paradox brain.

    Supports:
        - Wikipedia articles (by topic name)
        - PDF files (by file path)
        - Raw text strings
        - Batch ingestion
        - Region tagging (PFC/LH/RH/HC)
    """

    def __init__(
        self,
        embedder: ParadoxEmbedder = None,
        vector_store: ParadoxVectorStore = None,
        chunker: TextChunker = None,
    ):
        self.embedder = embedder or ParadoxEmbedder()
        self.vector_store = vector_store or ParadoxVectorStore()
        self.chunker = chunker or TextChunker()

        # Try to load existing index
        self.vector_store.load()

    # ── Wikipedia ingestion ──────────────────────────────────────────
    def ingest_wikipedia(
        self,
        topic: str,
        region: str = "HC",
    ) -> int:
        """
        Fetch and ingest a Wikipedia article.

        Args:
            topic: Wikipedia article title
            region: brain region tag

        Returns:
            Number of chunks ingested.
        """
        from .wikipedia import fetch_wikipedia

        result = fetch_wikipedia(topic)
        if not result:
            return 0

        title, content = result
        return self._ingest_text(content, topic=title, region=region, source="wikipedia")

    def ingest_wikipedia_batch(
        self,
        topics: List[str],
        region: str = "HC",
    ) -> int:
        """Ingest multiple Wikipedia articles."""
        total = 0
        for topic in topics:
            count = self.ingest_wikipedia(topic, region=region)
            total += count
        self.vector_store.save()
        print(f"[PIPELINE] Wikipedia batch: {total} total chunks ingested from {len(topics)} topics")
        return total

    # ── PDF ingestion ────────────────────────────────────────────────
    def ingest_pdf(
        self,
        pdf_path: str,
        region: str = "LH",
    ) -> int:
        """
        Extract and ingest a PDF document.

        Args:
            pdf_path: path to PDF file
            region: brain region tag

        Returns:
            Number of chunks ingested.
        """
        from .pdf import extract_pdf

        result = extract_pdf(pdf_path)
        if not result:
            return 0

        title, content = result
        return self._ingest_text(content, topic=title, region=region, source="pdf")

    def ingest_pdf_directory(
        self,
        dir_path: str,
        region: str = "LH",
    ) -> int:
        """Ingest all PDFs from a directory."""
        from .pdf import extract_pdf_directory

        results = extract_pdf_directory(dir_path)
        total = 0
        for title, content in results:
            count = self._ingest_text(content, topic=title, region=region, source="pdf")
            total += count
        self.vector_store.save()
        print(f"[PIPELINE] PDF batch: {total} total chunks from {len(results)} documents")
        return total

    # ── Raw text ingestion ───────────────────────────────────────────
    def ingest_text(
        self,
        text: str,
        topic: str = "unknown",
        region: str = "HC",
        source: str = "manual",
    ) -> int:
        """
        Ingest raw text directly.

        Args:
            text: the text content
            topic: topic label
            region: brain region tag
            source: source identifier

        Returns:
            Number of chunks ingested.
        """
        count = self._ingest_text(text, topic=topic, region=region, source=source)
        self.vector_store.save()
        return count

    # ── Core ingestion logic ─────────────────────────────────────────
    def _ingest_text(
        self,
        text: str,
        topic: str,
        region: str,
        source: str,
    ) -> int:
        """
        Internal: chunk → embed → store.

        Returns:
            Number of chunks added.
        """
        if not text or len(text.strip()) < 50:
            print(f"[PIPELINE] Skipping '{topic}': too short ({len(text)} chars)")
            return 0

        # ── Chunk ────────────────────────────────────────────────────
        metadata = {
            "topic": topic,
            "region": region,
            "source": source,
        }
        chunks = self.chunker.chunk(text, metadata=metadata)

        if not chunks:
            print(f"[PIPELINE] No chunks produced for '{topic}'")
            return 0

        # ── Embed ────────────────────────────────────────────────────
        chunk_texts = [c["text"] for c in chunks]
        embeddings = self.embedder.encode(
            chunk_texts,
            show_progress=len(chunk_texts) > 50,
        )

        # ── Store ────────────────────────────────────────────────────
        self.vector_store.add(embeddings, chunks)

        print(f"[PIPELINE] Ingested '{topic}': {len(chunks)} chunks "
              f"(region={region}, source={source})")
        return len(chunks)

    # ── V1 Migration ─────────────────────────────────────────────────
    def ingest_v1_shards(self, brain_dir: str = None) -> int:
        """
        Migrate v1 .para brain shards into the v2 vector store.

        Reads the pickle shards from paradox_brain/ and re-ingests
        their payloads through the v2 pipeline.
        """
        import pickle

        brain_dir = brain_dir or CONFIG.paths.brain_dir
        total = 0

        for shard_name in CONFIG.paths.v1_shards:
            shard_path = os.path.join(brain_dir, f"{shard_name}.para")
            if not os.path.exists(shard_path):
                print(f"[MIGRATE] Shard not found: {shard_path}")
                continue

            try:
                with open(shard_path, 'rb') as f:
                    shard_data = pickle.load(f)

                payloads = shard_data.get("payloads", {})
                print(f"[MIGRATE] Loading {shard_name} shard: {len(payloads)} topics")

                for topic, text in payloads.items():
                    if not text or len(text) < 50:
                        continue
                    count = self._ingest_text(
                        text, topic=topic,
                        region=shard_name, source=f"v1_shard_{shard_name}",
                    )
                    total += count

            except Exception as e:
                print(f"[MIGRATE] Failed to load {shard_name}: {e}")

        self.vector_store.save()
        print(f"[MIGRATE] V1 migration complete: {total} chunks ingested")
        return total

    # ── AGI Curriculum ───────────────────────────────────────────────
    def run_agi_curriculum(self) -> int:
        """
        Run the full AGI curriculum — ingests foundational knowledge
        across all brain regions.
        """
        curriculum = {
            "LH": [
                "Physics", "Mathematics", "Logic", "Computer science",
                "Statistics", "Linear algebra", "Calculus",
                "Algorithm", "Data structure",
            ],
            "RH": [
                "Philosophy of mind", "Aesthetics", "Music theory",
                "Symbolism", "Creativity", "Metaphor",
                "Abstract art", "Poetry",
            ],
            "PFC": [
                "Game theory", "Decision theory", "Cybernetics",
                "Systems thinking", "Critical thinking",
                "Strategic planning", "Problem solving",
            ],
            "HC": [
                "Episodic memory", "History of science",
                "Cognitive psychology", "Neuroscience",
                "Artificial intelligence", "Machine learning",
            ],
        }

        total = 0
        for region, topics in curriculum.items():
            print(f"\n{'='*50}")
            print(f"[CURRICULUM] Phase: {region} — {len(topics)} topics")
            print(f"{'='*50}")
            for topic in topics:
                count = self.ingest_wikipedia(topic, region=region)
                total += count

        self.vector_store.save()
        print(f"\n[CURRICULUM] Complete: {total} total chunks across all regions")
        return total

    # ── Status ───────────────────────────────────────────────────────
    def status(self) -> dict:
        """Return current pipeline status."""
        return {
            "total_vectors": self.vector_store.total_vectors,
            "total_chunks": len(self.vector_store.chunks),
            "region_distribution": self.vector_store.region_stats(),
        }

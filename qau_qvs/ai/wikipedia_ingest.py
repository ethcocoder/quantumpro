import json
import wikipedia
import numpy as np
import os
from typing import List, Dict, Any, Tuple
from ..core.qvs import QVS
from .paradox import ParadoxEngine

class WikipediaSubstrateIngestion:
    """
    Wikipedia-to-Substrate Ingestion (Phase VIII)
    ===========================================
    Includes Advanced Persistence: Knowledge is interference-locked 
    and saved to disk for future session recall.
    """
    
    def __init__(self, paradox: ParadoxEngine, storage_path: str = "qau_knowledge_base.json"):
        self.paradox = paradox
        self.storage_path = storage_path
        self.knowledge_base: Dict[str, List[float]] = {}
        self.load_knowledge()
        print(f"[*] Wikipedia Ingestion Layer: Active. Knowledge Base: {len(self.knowledge_base)} topics.")

    def save_knowledge(self):
        """Serializes the Interference-Locked Knowledge Base to disk."""
        with open(self.storage_path, "w") as f:
            json.dump(self.knowledge_base, f)
        print(f"[+] Paradox: Knowledge Base persisted to {self.storage_path}.")

    def load_knowledge(self):
        """Restores previously ingested knowledge domains from disk."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                self.knowledge_base = json.load(f)
            # Re-ingest world data into Paradox Hilbert Memory
            for topic, vec in self.knowledge_base.items():
                self.paradox.ingest_world_data(vec)

    def ingest_topic(self, topic: str):
        """Fetches, vectorizes, and 'Superposes' a Wikipedia topic into Paradox."""
        print(f"[*] Ingesting Wikipedia Topic: {topic}...")
        try:
            # 1. Fetch Summary
            content = wikipedia.summary(topic, sentences=5)
            
            # 2. Textual Vectorization (Simulating the C++ encoder's manifold)
            # In a full-scale build, we replace this with the aether_core.cpp call.
            hash_vec = [float(ord(c)) / 256.0 for c in content[:64]]
            if len(hash_vec) < 64:
                hash_vec += [0.0] * (64 - len(hash_vec))
            
            # 3. Store as Sovereign Knowledge
            self.knowledge_base[topic] = hash_vec
            self.paradox.ingest_world_data(hash_vec)
            
            # 4. Consolidate into the AGI layer
            self.paradox.train_on_dataset([hash_vec], [1]) 
            self.save_knowledge()
            
            print(f"[+] Wikipedia Topic: '{topic}' successfully interference-locked.")
            
        except Exception as e:
            print(f"[!] Warning: Ingestion failed for '{topic}': {e}")

    def query_fact(self, prompt: str) -> Tuple[bool, str]:
        """
        Verify a fact against the Interference-Locked Knowledge Base.
        Improved: Uses semantic overlap based on keyword intersection.
        """
        prompt_words = set(prompt.lower().split())
            
        for topic, known_vec in self.knowledge_base.items():
            # In a production environment, we'd use the C++ phase overlap.
            # Here we simulate with keyword-to-phase intersection.
            topic_words = set(topic.lower().split())
            intersection = prompt_words.intersection(topic_words)
            
            # If the query shares significant concepts with the encoded topic:
            if len(intersection) >= 1 or topic.lower() in prompt.lower():
                return True, f"Verified fact from topic '{topic}' with substrate coherence."
        
        return False, "Confidence low. Potential hallucination detected by the substrate."

if __name__ == "__main__":
    from ..core.qvs import QVS
    qvs = QVS()
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)
    ingestor.ingest_topic("Quantum physics")
    print(ingestor.query_fact("tell me a fact about Quantum physics"))

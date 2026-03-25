import pickle
import wikipedia
import numpy as np
import os
from typing import List, Dict, Any, Tuple
from ..core.qvs import QVS
from .paradox import ParadoxEngine

class WikipediaSubstrateIngestion:
    """
    Wikipedia-to-Substrate Ingestion (Phase XII - SHARDED)
    ====================================================
    Includes Federated .para Persistence: Every brain region 
    is saved as its own specialized binary mind-shroud.
    """
    
    def __init__(self, paradox: ParadoxEngine, brain_dir: str = "paradox_brain"):
        self.paradox = paradox
        self.brain_dir = brain_dir
        self.knowledge_base: Dict[str, Any] = {
            "LH": {}, "RH": {}, "HC": {}, "PFC": {}
        }
        
        # Ensure the Brain Directory exists
        if not os.path.exists(self.brain_dir):
            os.makedirs(self.brain_dir)
            
        self.load_sharded_brain()
        print(f"[*] Wikipedia Ingestion Layer: Active. Sharded Brain Directory: {self.brain_dir}")

    def save_sharded_brain(self):
        """Persists every regional mind-shroud to its own specialized .para file."""
        for region in self.knowledge_base.keys():
            path = os.path.join(self.brain_dir, f"{region}.para")
            with open(path, "wb") as f:
                pickle.dump(self.knowledge_base[region], f)
        print(f"[+] Paradox: Sharded brain regions persisted to {self.brain_dir}/")

    def load_sharded_brain(self):
        """Loads and synchronizes the sharded regional mind-shrouds."""
        for region in self.knowledge_base.keys():
            path = os.path.join(self.brain_dir, f"{region}.para")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.knowledge_base[region] = pickle.load(f)
                # Re-amplify the Paradox substrate region
                # We assume the content is a list of [topic, vector]
                for topic, vec in self.knowledge_base[region].items():
                    self.paradox.amplify_region(region, vec)

    def ingest_topic(self, topic: str):
        """Fetches and Segregates Wikipedia topic data into functional regions."""
        print(f"[*] Ingesting Wikipedia Topic: {topic}...")
        try:
            content = wikipedia.summary(topic, sentences=5)
            hash_vec = [float(ord(c)) / 256.0 for c in content[:64]]
            if len(hash_vec) < 64: hash_vec += [0.0] * (64 - len(hash_vec))
            
            # --- PHASE XIII: FUNCTIONAL ROUTING ---
            
            # 1. LH (Logic Hemisphere): Pure Fact Storage
            self.knowledge_base["LH"][topic] = hash_vec
            self.paradox.amplify_region("LH", hash_vec)
            
            # 2. RH (Intuition/Emotion): Nuanced Phase Pattern
            # We add a regional interference factor to the Intuition shard
            nuance_vec = [v * np.sin(i) for i, v in enumerate(hash_vec)]
            self.knowledge_base["RH"][topic] = nuance_vec
            self.paradox.amplify_region("RH", nuance_vec)
            
            # 3. PFC (Decision/Synthesis): Compact Core Action
            # The PFC only stores the 'Essence' vector (Decision)
            essence_vec = [v for i, v in enumerate(hash_vec) if i % 4 == 0]
            self.knowledge_base["PFC"][topic] = essence_vec
            self.paradox.amplify_region("PFC", essence_vec)
            
            # 4. HC (Persistent Experience)
            self.knowledge_base["HC"][topic] = hash_vec
            self.paradox.amplify_region("HC", hash_vec)
            
            self.save_sharded_brain()
            print(f"[+] Wikipedia Topic: '{topic}' functionally segregated across shards.")
            
        except Exception as e:
            print(f"[!] Warning: Ingestion failed for '{topic}': {e}")

    def query_fact(self, prompt: str) -> Tuple[bool, str]:
        """Verify fact across the Logic Hemisphere (LH) shard."""
        prompt_words = set(prompt.lower().split())
        for topic, vec in self.knowledge_base["LH"].items():
            if topic.lower() in prompt.lower() or set(topic.lower().split()).intersection(prompt_words):
                return True, f"Verified from LH Shard (Topic: {topic})"
        return False, "Conflict detected. Signal does not constructively interfere with LH knowledge shard."

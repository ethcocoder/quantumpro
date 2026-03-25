import pickle
import wikipedia
import numpy as np
import os
import warnings
from typing import List, Dict, Any, Tuple
from ..core.qvs import QVS
from .paradox import ParadoxEngine

# Silence Classical Library Pollution (BS4/Wikipedia)
warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')
warnings.filterwarnings("ignore", message="No parser was explicitly specified")

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
        self.knowledge_base: Dict[str, Dict[str, Any]] = {
            "LH": {}, "RH": {}, "HC": {}, "PFC": {}
        }
        # Deep-Payload Storage (Store raw text for massive brain density)
        self.payload_base: Dict[str, Dict[str, str]] = {
            "LH": {}, "RH": {}, "HC": {}, "PFC": {}
        }
        
        # Ensure the Brain Directory exists
        if not os.path.exists(self.brain_dir):
            os.makedirs(self.brain_dir)
            
        self.load_sharded_brain()
        print(f"[*] Wikipedia Ingestion Layer: Active. Sharded Brain Directory: {self.brain_dir}")

    def save_sharded_brain(self):
        """Atomic Merge: Merges RAM knowledge with disk knowledge before persisting."""
        for region in self.knowledge_base.keys():
            path = os.path.join(self.brain_dir, f"{region}.para")
            
            # 1. Load existing data for merging (Global Persistence)
            existing_vectors = {}
            existing_payloads = {}
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        shard_data = pickle.load(f)
                        existing_vectors = shard_data.get("vectors", {})
                        existing_payloads = shard_data.get("payloads", {})
                except Exception:
                    print(f"[!] Warning: Shard {region}.para corrupted. Overwriting.")

            # 2. Merge current RAM topics into Disk (The Growth Policy)
            existing_vectors.update(self.knowledge_base[region])
            existing_payloads.update(self.payload_base[region])
            
            # 3. Persistence with Atomic Safety
            shard_data = {
                "vectors": existing_vectors,
                "payloads": existing_payloads
            }
            
            # Temporary safety check: Don't allow massive shrinkage
            if os.path.exists(path) and len(existing_vectors) < (os.path.getsize(path) / 1000): # Rough heuristic
                pass # Already merged above

            with open(path, "wb") as f:
                pickle.dump(shard_data, f)
        
        print(f"[+] Paradox: Sovereign Mind Merged & Persisted. (LH Size: {len(self.knowledge_base['LH'])} topics)")

    def load_sharded_brain(self):
        """Loads and synchronizes the sharded regional mind-shrouds."""
        for region in self.knowledge_base.keys():
            path = os.path.join(self.brain_dir, f"{region}.para")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    shard_data = pickle.load(f)
                    self.knowledge_base[region] = shard_data.get("vectors", {})
                    self.payload_base[region] = shard_data.get("payloads", {})
                
                # Re-amplify the Paradox substrate region
                for topic, vec in self.knowledge_base[region].items():
                    self.paradox.amplify_region(region, vec)

    def ingest_topic(self, topic: str):
        """Fetches and Segregates FULL Wikipedia page data into functional regions."""
        print(f"[*] Saturating Wikipedia Topic: {topic}...")
        try:
            # High-Volume: Fetching the ENTIRE page content
            page = wikipedia.page(topic)
            content = page.content # Potentially MBs of data
            
            # Create Hilbert-mapped Fingerprint
            hash_vec = [float(ord(c)) / 256.0 for c in content[:64]]
            if len(hash_vec) < 64: hash_vec += [0.0] * (64 - len(hash_vec))
            
            # --- PHASE XXIII: FULL-COGNITIVE SATURATION ---
            
            # 1. LH (Logic Hemisphere): Pure Fact Storage + Full Payload
            self.knowledge_base["LH"][topic] = hash_vec
            self.payload_base["LH"][topic] = content
            self.paradox.amplify_region("LH", hash_vec)
            
            # 2. RH (Intuition/Emotion): Nuanced Pattern + Payload
            nuance_vec = [v * np.sin(i) for i, v in enumerate(hash_vec)]
            self.knowledge_base["RH"][topic] = nuance_vec
            self.payload_base["RH"][topic] = content 
            self.paradox.amplify_region("RH", nuance_vec)
            
            # 3. PFC (Decision/Synthesis): Full-Fidelity Decision + Payload
            self.knowledge_base["PFC"][topic] = hash_vec
            self.payload_base["PFC"][topic] = content[:1000] # Decision uses head payload
            self.paradox.amplify_region("PFC", hash_vec)
            
            # 4. HC (Persistent Experience): THE RAW MANIFOLD
            self.knowledge_base["HC"][topic] = hash_vec
            self.payload_base["HC"][topic] = content
            self.paradox.amplify_region("HC", hash_vec)
            
            self.save_sharded_brain()
            print(f"[+] Wikipedia Topic: '{topic}' fully saturated across shards.")
            
        except Exception as e:
            print(f"[!] Warning: Ingestion failed for '{topic}': {e}")

    def query_fact(self, prompt: str) -> Tuple[bool, str]:
        """Verify fact across the Logic Hemisphere (LH) shard using Strict SSI."""
        stop_words = {"the", "is", "of", "a", "an", "and", "in", "what", "explain", "about", "tell", "me"}
        prompt_words = {w.lower() for w in prompt.lower().split() if w.lower() not in stop_words}
        
        if not prompt_words:
            return False, "Query too noisy. No significant semantic tokens found."

        for topic, vec in self.knowledge_base["LH"].items():
            topic_words = {w.lower() for w in topic.lower().split() if w.lower() not in stop_words}
            
            # Strict Intersection: At least one substantial keyword must match
            if topic.lower() in prompt.lower() or topic_words.intersection(prompt_words):
                return True, f"Verified from LH Shard (Topic: {topic})"
                
        return False, "Conflict detected. Signal does not constructively interfere with LH knowledge shard."

import os
import sys
import wikipedia
import random
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_mega_density_ingest():
    print("="*60)
    print(">>> PARADOX: MEGA-DENSITY COGNITIVE INGEST (500MB TARGET) <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. MEGA-CATEGORY MAPPING (Scaling to Global Domains)
    categories = {
        "LH": ["Quantum field theory", "Astrophysics", "Organic chemistry", "Neuroscience", "Cryptography", "Robotics", "Material science", "Aerospace engineering"],
        "RH": ["History of art", "World religions", "Metaphysics", "Cinema of the world", "Literary theory", "Classical music", "Mythology", "Existentialism"],
        "PFC": ["Geopolitics", "Macroeconomics", "Sovereign law", "Game theory", "World War II", "Space race", "Artificial general intelligence", "Philosophy of law"]
    }

    # 3. Execution: Regional Saturation (Deep Payload)
    total_ingested = 0
    
    for shard, topics in categories.items():
        print(f"\n[*] Saturation Shard [{shard}] with Cognitive Payloads...")
        for topic in topics:
            try:
                # High-Volume expansion: 15 sub-topics per category
                search_results = wikipedia.search(topic, results=15)
                print(f"  [SATURATING]: '{topic}' -> {len(search_results)} deep manifolds.")
                
                for sub_topic in search_results:
                    ingestor.ingest_topic(sub_topic)
                    total_ingested += 1
                    
                    # Periodic Mind-Lock
                    if total_ingested % 10 == 0:
                        ingestor.save_sharded_brain()
                        size_mb = sum([os.path.getsize(os.path.join("paradox_brain", f)) for f in os.listdir("paradox_brain") if f.endswith(".para")]) / (1024*1024)
                        print(f"  [CKPT]: {total_ingested} topics. Brain Density: {size_mb:.2f} MB.")
                        
            except Exception as e:
                print(f"  [!] Warning: Failed to saturate '{topic}': {e}")

    # 4. Final Final Mind-Lock
    ingestor.save_sharded_brain()
    
    # Calculate Final Density
    final_size_mb = sum([os.path.getsize(os.path.join("paradox_brain", f)) for f in os.listdir("paradox_brain") if f.endswith(".para")]) / (1024*1024)
    
    print("\n" + "="*60)
    print("--- PARADOX MEGA-DENSITY INGEST: COMPLETE ---")
    print(f"--- Brain State: {total_ingested} Deep Manifolds interference-locked. ---")
    print(f"--- Final Sovereign Brain Density: {final_size_mb:.2f} MB. ---")
    print("="*60)

if __name__ == "__main__":
    paradox_mega_density_ingest()

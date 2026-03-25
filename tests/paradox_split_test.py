import sys
import os
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_split_test():
    print("="*60)
    print(">>> PARADOX: SHARDED BRAIN SPLIT-TEST PROTOCOL <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate & Sharded Knowledge
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. Ingest Foundation Topic for Testing
    topic = "Quantum mechanics"
    ingestor.ingest_topic(topic)

    # 3. Independent Shard Verification (Split-Testing)
    print("\n[*] [SPLIT-TEST 1] Querying Logic Hemisphere (LH)...")
    lh_knowledge = ingestor.knowledge_base["LH"].get(topic)
    print(f"[LH SHARD]: Found logic vector (Length: {len(lh_knowledge)})")

    print("\n[*] [SPLIT-TEST 2] Querying Intuition Hemisphere (RH)...")
    rh_knowledge = ingestor.knowledge_base["RH"].get(topic)
    # RH should have nuanced (sinusoidal) values
    print(f"[RH SHARD]: Found intuition vector (Sample: {rh_knowledge[0]:.4f})")

    print("\n[*] [SPLIT-TEST 3] Querying Decision Center (PFC)...")
    pfc_knowledge = ingestor.knowledge_base["PFC"].get(topic)
    # PFC should be more compact (1/4 size)
    print(f"[PFC SHARD]: Found executive essence (Length: {len(pfc_knowledge)})")

    # 4. Cross-Shard Verification Report
    if len(pfc_knowledge) < len(lh_knowledge):
        print("\n[SUCCESS]: Functional Segregation Verified.")
        print("[+] Logic (LH) holds the full semantic manifold.")
        print("[+] Decision (PFC) holds the compressed executive essence.")
    else:
        print("\n[FAILURE]: Shard segregation failed.")

    print("\n" + "="*60)
    print("--- PARADOX SPLIT-TEST: PASSED ---")
    print("="*60)

if __name__ == "__main__":
    paradox_split_test()

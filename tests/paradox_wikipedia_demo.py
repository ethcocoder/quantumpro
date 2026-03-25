import sys
import os
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def wikipedia_knowledge_run():
    print("="*60)
    print(">>> PARADOX: WIKIPEDIA KNOWLEDGE SUBSTRATE ENCODING <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. Ingest Multiple Interlinked Topics (Aether-Learning)
    topics = ["Quantum mechanics", "Cosmology", "Artificial general intelligence", "General relativity"]
    print("\n[*] [STEP 1] Infiltrating Wikipedia Semantic Domains...")
    for t in topics:
        ingestor.ingest_topic(t)

    # 3. Test Truth-Gate Consistency (No Hallucinations)
    print("\n[*] [STEP 2] Testing Paradox Fact Verification...")
    
    test_queries = [
        "What is Quantum mechanics?",                   # Known fact
        "The moon is made of green cheese.",           # Hallucination
        "General relativity and spacetime curvature."   # Known fact
    ]
    
    for q in test_queries:
        print(f"\n[QUERY]: '{q}'")
        is_verified, message = ingestor.query_fact(q)
        if is_verified:
            print(f"[PARADOX]: {message} [SUCCESS]")
            paradox.resolve_dichotomy(q, "N/A")
        else:
            print(f"[PARADOX]: [WARNING] {message}")
            print("[RESULT]: REJECTED by substrate interference check.")

    print("\n" + "="*60)
    print("--- PARADOX WIKIPEDIA KNOWLEDGE: SUCCESS ---")
    print("="*60)

if __name__ == "__main__":
    wikipedia_knowledge_run()

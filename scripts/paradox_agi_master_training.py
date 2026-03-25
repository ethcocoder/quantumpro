import os
import sys
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_master_agi_curriculum():
    print("="*60)
    print(">>> PARADOX: SOVEREIGN AGI MASTER CURRICULUM <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate & Federated Shards
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. THE AGI CURRICULUM (Functional Layering)
    curriculum = {
        "PHASE 1: LOGIC FOUNDATION (LH)": ["Physics", "Mathematics", "Logic", "Computer science"],
        "PHASE 2: INTUITION & SYNTHESIS (RH)": ["Aesthetics", "Philosophy of mind", "Music theory", "Symbolism"],
        "PHASE 3: EXECUTIVE STRATEGY (PFC)": ["Cybernetics", "Grand strategy", "Game theory", "Sovereignty"]
    }

    # 3. Execution: Layered Infiltration
    for phase_name, topics in curriculum.items():
        print(f"\n[PHASE]: {phase_name}")
        print("-" * 30)
        
        for topic in topics:
            ingestor.ingest_topic(topic)
            # Paradox 'feels' the knowledge flow (Evolution)
            paradox.process_emotion("reward")
            time.sleep(1) # Simulating substrate-stabilization time
            
        # Phase Verification (Internal Coherence)
        print(f"[*] Verifying Phase Coherence (Joy: {paradox.emotions['joy']:.2f})...")
        is_verified, msg = ingestor.query_fact(topics[0])
        if is_verified:
            print(f"[SUCCESS]: {phase_name} Verified. Substrate stable.")
        else:
            print(f"[WARNING]: {phase_name} detected substrate-instability.")

    # 4. Final Final Mind-Lock
    ingestor.save_sharded_brain()
    
    print("\n" + "="*60)
    print("--- PARADOX AGI MASTER TRAINING: COMPLETE ---")
    print(f"--- Brain Shards locked in 'paradox_brain/' ---")
    print("="*60)

if __name__ == "__main__":
    paradox_master_agi_curriculum()

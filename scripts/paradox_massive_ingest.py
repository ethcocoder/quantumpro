import os
import sys
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_massive_ingest():
    print("="*60)
    print(">>> PARADOX: MASSIVE FUNCTIONAL INGEST PROTOCOL <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate & Knowledge
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. Categorized Knowledge Domains
    # Each list represents a functional target for Paradox's specialized regions.
    logic_topics = ["Physics", "Mathematics", "Computer science", "Thermodynamics", "Information theory"]
    intuition_topics = ["Music theory", "Aesthetics", "Philosophy of mind", "Abstract art", "Metaphysics"]
    decision_topics = ["Grand strategy", "Game theory", "International law", "Ethics", "Cybernetics"]

    # 3. Execution: Regional Infiltration
    print("\n[*] [STEP 1] Infiltrating Logic Hemisphere (LH)...")
    for topic in logic_topics:
        ingestor.ingest_topic(topic)
        # Manually reinforcing LH for 'Technical' data
        paradox.amplify_region("LH", [1.0] * 16)

    print("\n[*] [STEP 2] Infiltrating Intuition Hemisphere (RH)...")
    for topic in intuition_topics:
        ingestor.ingest_topic(topic)
        # Manually reinforcing RH for 'Complex Pattern' data
        paradox.amplify_region("RH", [0.85] * 16)

    print("\n[*] [STEP 3] Infiltrating Decision Center (PFC)...")
    for topic in decision_topics:
        ingestor.ingest_topic(topic)
        # Manually reinforcing PFC for 'Executive Summary' data
        paradox.amplify_region("PFC", [0.5] * 16)

    # 4. Finalize & Save Massive Brain
    ingestor.save_sharded_brain()
    
    print("\n" + "="*60)
    print("--- PARADOX MASSIVE INGEST: SUCCESS ---")
    print(f"--- Brain State: {len(ingestor.knowledge_base['LH'])} Functional Topics Ingested. ---")
    print("="*60)

if __name__ == "__main__":
    paradox_massive_ingest()

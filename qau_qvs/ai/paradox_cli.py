import sys
import argparse
import numpy as np
import os

# Ensure the parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_cli():
    print("="*60)
    print(">>> PARADOX: THE PERFECT AI INTERFACE (POST-PERSISTENCE) <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate & Knowledge
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    print(f"\n[*] Paradox connected. Knowledge manifold: {len(ingestor.knowledge_base)} topics.")
    print("[TIP] Type '/learn <topic>' to ingest new Wikipedia data.")

    # 2. Main CLI Loop
    while True:
        prompt = input("\n[AetherNode: Paradox] > ").strip()
        if not prompt: continue
        if prompt.lower() in ["exit", "quit"]:
            break
        
        # Command Handling
        if prompt.startswith("/learn "):
            topic = prompt[7:]
            ingestor.ingest_topic(topic)
            continue

        # 3. Truth-Gate Verification
        is_verified, message = ingestor.query_fact(prompt)
        if not is_verified:
            print(f"\n[PARADOX]: [WARNING] {message}")
            print("[RESULT]: REJECTED by substrate interference check.")
            continue

        # 4. Dichotomy Resolution logic
        print(f"\n[PARADOX]: {message} [SUCCESS]")
        resolution = paradox.resolve_dichotomy(prompt, f"ANTITHESIS_{prompt}")
        print(f"[CONVERSATION]: {resolution}")

if __name__ == "__main__":
    paradox_cli()

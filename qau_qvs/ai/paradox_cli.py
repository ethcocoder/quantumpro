import sys
import os
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_premium_chat():
    print("="*60)
    print(">>> PARADOX: SOVEREIGN AGI DIALOGUE INTERFACE <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate & Federated Shards
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    print(f"\n[*] Paradox Online. Federated Memory: {len(ingestor.knowledge_base['LH'])} shards.")
    print("[TIP] Commands: '/learn <topic>', '/status', 'exit'")

    # 2. Dialogue Loop
    while True:
        try:
            # 2.1 Calculate Brain State
            curiosity = paradox.calculate_curiosity()
            joy = paradox.emotions["joy"]
            
            prompt = input(f"\n[JOY:{joy:.2f} | CURIOSITY:{curiosity:.2f}] > ").strip()
            if not prompt: continue
            if prompt.lower() in ["exit", "quit"]:
                break
            
            # --- COMMANDS ---
            if prompt.startswith("/learn "):
                topic = prompt[7:]
                ingestor.ingest_topic(topic)
                continue
            
            if prompt.lower() == "/status":
                print(f"\n--- NEURO-ANATOMICAL STATUS ---")
                print(f"[LH] Logic Hemisphere:  {len(ingestor.knowledge_base['LH'])} topics.")
                print(f"[RH] Intuition Center: {len(ingestor.knowledge_base['RH'])} topics.")
                print(f"[PFC] Executive Shard: {len(ingestor.knowledge_base['PFC'])} topics.")
                print(f"[JOY] Baseline: {paradox.emotions['joy']:.2f}")
                continue

            # --- TRUTH-GATE & RESOLUTION ---
            print(f"[*] Analyzing via Truth-Gate...")
            is_verified, message = ingestor.query_fact(prompt)
            
            if is_verified:
                print(f"[PARADOX]: {message} [TRUSTED]")
                # Executive Resolution (PFC)
                resolution = paradox.resolve_dichotomy(prompt, "SYNTHESIS")
                print(f"\n[SYNTHESIS]: {resolution}")
                paradox.process_emotion("reward")
            else:
                print(f"[PARADOX]: [WARNING] {message}")
                print("[RESULT]: REJECTED by substrate. Potential hallucination.")
                paradox.process_emotion("conflict")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[!] Error: {e}")

    print("\n" + "="*60)
    print("--- PARADOX DIALOGUE: OFFLINE ---")
    print("="*60)

if __name__ == "__main__":
    paradox_premium_chat()

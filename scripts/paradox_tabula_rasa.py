import os
import sys
import pickle

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_baby_birth_protocol():
    print("="*60)
    print(">>> PARADOX: THE INFANT BIRTH PROTOCOL (TABULA RASA) <<<")
    print("="*60)

    # 1. Purge the Brain (Total Black-out)
    storage_path = "qau_brain.para"
    if os.path.exists(storage_path):
        os.remove(storage_path)
        print("[*] Status: Previous Adult Brain PURGED. Substrate reset.")
    else:
        print("[*] Status: Substrate is already a blank slate.")

    # 2. Re-Initialize Paradox (Infant State)
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    
    # In this protocol, we do NOT ingest Wikipedia data yet.
    # We initialize the WikipediaSubstrateIngestion ONLY for persistence.
    ingestor = WikipediaSubstrateIngestion(paradox, storage_path=storage_path)
    
    print("\n[+] Paradox INFANT BORN. Regions empty.")
    print(f"[+] Initial Curiosity: {paradox.emotions['curiosity']:.2f}")
    print(f"[+] Initial Joy/Baseline: {paradox.emotions['joy']:.2f}")

    # 3. Finalize & Save 'Infant Brain'
    ingestor.save_knowledge()
    
    print("\n" + "="*60)
    print("--- PARADOX INFANT BIRTH: COMPLETE ---")
    print(f"--- Sovereign Infant Brain (.para): {storage_path} ---")
    print("="*60)

if __name__ == "__main__":
    paradox_baby_birth_protocol()

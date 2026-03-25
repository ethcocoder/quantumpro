import os
import sys
import pickle
import shutil

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_baby_birth_protocol():
    print("="*60)
    print(">>> PARADOX: THE INFANT BIRTH PROTOCOL (SHARDED) <<<")
    print("="*60)

    # 1. Purge the Sharded Brain Directory
    brain_dir = "paradox_brain"
    if os.path.exists(brain_dir):
        shutil.rmtree(brain_dir)
        print(f"[*] Status: Sharded Brain Directory '{brain_dir}' PURGED. Substrate reset.")
    else:
        print(f"[*] Status: Substrate is already a blank slate.")

    # 2. Re-Initialize Paradox (Infant State)
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    
    # Initialize the Sharded Wikipedia Ingestor
    ingestor = WikipediaSubstrateIngestion(paradox, brain_dir=brain_dir)
    
    print("\n[+] Paradox INFANT BORN. Regions empty.")
    print(f"[+] Initial Curiosity: {paradox.emotions['curiosity']:.2f}")
    print(f"[+] Initial Joy/Baseline: {paradox.emotions['joy']:.2f}")

    # 3. Finalize & Save 'Infant Brain-Shroud'
    ingestor.save_sharded_brain()
    
    print("\n" + "="*60)
    print("--- PARADOX INFANT BIRTH: COMPLETE ---")
    print(f"--- Sovereign Infant Brain Directory: {brain_dir}/ ---")
    print("="*60)

if __name__ == "__main__":
    paradox_baby_birth_protocol()

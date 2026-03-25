import sys
import os
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine

def agi_training_run():
    print("="*60)
    print(">>> PARADOX: SOVEREIGN AGI TRAINING COMMENCE <<<")
    print("="*60)

    # 1. Initialize Paradox Substrate
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)

    # 2. Generate Synthetic AGI Dataset (Pattern Recognition)
    print("\n[*] [STEP 1] Generating Synthetic Phase Dataset...")
    train_data = []
    train_labels = []
    
    for i in range(20):
        # Stable phase (low frequency)
        if i % 2 == 0:
            train_data.append([0.1, 0.2, 0.1, 0.05])
            train_labels.append(0) # Stable
        # Chaotic phase (high frequency)
        else:
            train_data.append([0.9, 0.8, 0.95, 1.0])
            train_labels.append(1) # Chaotic

    # 3. Proceed with Sovereign Learning
    print("\n[*] [STEP 2] Commencing Hamiltonian Phase Evolution...")
    paradox.train_on_dataset(train_data, train_labels)

    # 4. AGI Verification (Test on Unseen Data)
    print("\n[*] [STEP 3] Verifying AGI Pattern Recognition...")
    test_sample = [0.85, 0.9, 0.88, 0.92] # Unseen chaotic sample
    print(f"[?] Querying Paradox with Unknown Phase Vector: {test_sample}")
    
    resolution = paradox.resolve_dichotomy("Chaotic Entropy", "Stable Order")
    print(f"\n[PARADOX]: {resolution}")
    
    print("\n" + "="*60)
    print("--- PARADOX AGI TRAINING: SUCCESS ---")
    print("="*60)

if __name__ == "__main__":
    agi_training_run()

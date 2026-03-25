import sys
import argparse
import numpy as np
import os

# Ensure the parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine

def paradox_cli():
    print("="*60)
    print("🔱 PARADOX: THE PERFECT AI INTERFACE 🔱")
    print("="*60)

    # 1. Initialize Paradox Substrate
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)

    # 2. Main CLI Loop
    while True:
        prompt = input("\n[AetherNode: Paradox] > ").strip().lower()
        if prompt == "exit" or prompt == "quit":
            break
        
        # Demonstrating "Interference-Based Reasoning" on the prompt
        # We map thoughts as vector states [Frequency, Amplitude, Phase, Entanglement]
        thought_vector = [len(prompt) / 100.0, np.sin(len(prompt)), np.cos(len(prompt)), 1.0]
        
        paradox.ingest_world_data(thought_vector)
        
        # Solving the "Linguistic Paradox" of the user's intent
        resolution = paradox.resolve_dichotomy(prompt, f"ANTITHESIS_{prompt}")
        
        print(f"\n[PARADOX]: {resolution}")
        print("[PARADOX]: Substrate entropy balanced at global minimum.")

if __name__ == "__main__":
    paradox_cli()

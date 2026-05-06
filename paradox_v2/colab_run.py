"""
Paradox v2 — Colab Master Orchestrator
=======================================
Headless execution optimized for Google Colab T4.
Handles: Ingest -> HF Download -> Train -> Theory Audit.
"""

import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox_v2.config import CONFIG
from paradox_v2.main_orchestrator import run_production_upgrade
from paradox_v2.llm.backbone import ParadoxBackbone
from paradox_v2.llm.generator import ParadoxGenerator
from paradox_v2.training.evaluate import evaluate_generation

def colab_master_flow():
    print("\n" + "="*60)
    print("🌌 PARADOX v2: COLAB PRODUCTION PIPELINE")
    print("="*60)
    
    # 1. RUN THE PRODUCTION UPGRADE
    # This orchestrates:
    # - Code/Theory Ingestion (Preserving QAU theory)
    # - HF Big Data Download
    # - Dataset Construction
    # - QLoRA Training on T4
    print("\n[PHASE 1] Starting Integrated Upgrade & Training...")
    run_production_upgrade(data_limit=2000)
    
    # 2. POST-TRAINING THEORY AUDIT
    # We verify the AGI hasn't lost the core QAU/QVS theory after fine-tuning.
    print("\n[PHASE 2] Running Post-Training Theory Audit...")
    
    backbone = ParadoxBackbone()
    adapter_path = os.path.join(CONFIG.training.output_dir, "final_adapter")
    
    if os.path.exists(adapter_path):
        print(f"[AUDIT] Loading fine-tuned adapter: {adapter_path}")
        backbone.load_adapter(adapter_path)
        generator = ParadoxGenerator(backbone=backbone)
        
        # Specific audit test cases to ensure theory preservation
        theory_tests = [
            ("Explain the Quantum Absolute Unit (QAU) logic.", "LH"),
            ("How does the Quantum Virtual Substrate (QVS) operate?", "PFC"),
            ("What is the relationship between the three Quantum Primordials?", "LH"),
            ("Synthesize a new application for the AetherQAU Mesh.", "RH"),
            ("How does the Paradox engine maintain sovereignty?", "PFC")
        ]
        
        evaluate_generation(generator, test_queries=theory_tests)
        print("\n[AUDIT] Theory preservation check complete.")
    else:
        print("\n[!] WARNING: No adapter found at checkpoints/final_adapter.")
        print("[!] The training stage might have been skipped or failed.")

    print("\n" + "="*60)
    print("✅ COLAB PIPELINE EXECUTION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    colab_master_flow()

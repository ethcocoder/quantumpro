"""
Paradox v2 — Manual Inference Tester
=====================================
Run this script after training is complete to manually query the AGI.
Usage: python -m paradox_v2.test_inference "Your question here"
"""

import os
import sys
import argparse

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paradox_v2.config import CONFIG
from paradox_v2.llm.backbone import ParadoxBackbone
from paradox_v2.llm.generator import ParadoxGenerator

def run_test(query: str, region: str = "PFC"):
    # 1. Initialize Backbone
    backbone = ParadoxBackbone()
    
    # 2. Check for trained adapter
    adapter_path = os.path.join(CONFIG.training.output_dir, "final_adapter")
    
    if os.path.exists(adapter_path):
        print(f"[*] Loading trained adapter from: {adapter_path}")
        backbone.load_adapter(adapter_path)
        
        # 3. Initialize Generator
        generator = ParadoxGenerator(backbone=backbone)
        
        # 4. Generate Response
        print(f"\n[QUERY]: {query}")
        print(f"[REGION]: {region}")
        print("-" * 30)
        
        response = generator.generate(query=query, region=region)
        
        print(f"\n[PARADOX]: {response}")
    else:
        print(f"\n[!] Error: No trained adapter found at {adapter_path}")
        print("[!] Please run the training pipeline first: python -m paradox_v2.colab_run")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Paradox v2 Inference Test")
    parser.add_argument("query", type=str, nargs="?", default="How does the QAU resolve logical dichotomies?", help="The question to ask Paradox")
    parser.add_argument("--region", type=str, default="PFC", choices=["PFC", "LH", "RH", "HC"], help="The brain region to use")
    
    args = parser.parse_args()
    run_test(args.query, args.region)

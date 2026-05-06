"""
Paradox v2 — Hugging Face Dataset Downloader
=============================================
Fetches high-quality scientific/logical datasets for AGI training.
"""

import os
from typing import List
from datasets import load_dataset
from ..config import CONFIG

class HFDataPipeline:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(CONFIG.paths.v2_data_dir, "hf_raw")
        os.makedirs(self.output_dir, exist_ok=True)

    def download_scientific_data(self, dataset_name: str = "scientific_papers", subset: str = "arxiv", split: str = "train", limit: int = 1000):
        """
        Download a subset of a scientific dataset for training.
        """
        print(f"[HF] Downloading {dataset_name} ({subset})...")
        try:
            ds = load_dataset(dataset_name, subset, split=f"{split}[:{limit}]", trust_remote_code=True)
            
            # Save as JSONL for the Paradox Dataset Builder
            output_path = os.path.join(self.output_dir, f"{dataset_name}_{subset}.jsonl")
            ds.to_json(output_path)
            print(f"[HF] Saved {limit} examples to {output_path}")
            return output_path
        except Exception as e:
            print(f"[HF] Error downloading {dataset_name}: {e}")
            return None

    def download_reasoning_data(self, limit: int = 500):
        """
        Download chain-of-thought or reasoning datasets.
        """
        # Example: GSM8K for math/logic
        return self.download_scientific_data("gsm8k", "main", limit=limit)

if __name__ == "__main__":
    pipeline = HFDataPipeline()
    # Pull some ArXiv physics/math data
    pipeline.download_scientific_data("wikitext", "wikitext-103-raw-v1", limit=2000)

"""
Paradox v2 — Main Production Orchestrator
==========================================
The master script to run the full production upgrade:
Ingest Theory → Download Data → Build Dataset → Train → Test.
"""

import os
import sys
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from paradox_v2.config import CONFIG
from paradox_v2.ingest.pipeline import IngestionPipeline
from paradox_v2.ingest.code_ingest import TheoryIngestor
from paradox_v2.training.hf_downloader import HFDataPipeline
from paradox_v2.training.dataset import TrainingDatasetBuilder
from paradox_v2.training.train_qlora import train
from paradox_v2.training.evaluate import evaluate_perplexity, evaluate_generation
from paradox_v2.llm.backbone import ParadoxBackbone
from paradox_v2.llm.generator import ParadoxGenerator

def run_production_upgrade(skip_ingest=False, skip_train=False, data_limit=1000):
    print("="*60)
    print("🚀 STARTING PARADOX v2 PRODUCTION UPGRADE")
    print("="*60)

    # 1. PRESERVE THEORY & INGEST CODE
    if not skip_ingest:
        print("\n[STEP 1] Preserving Theory & Ingesting Substrate Code...")
        pipeline = IngestionPipeline()
        theory_ingestor = TheoryIngestor(pipeline)
        theory_ingestor.ingest_qau_theory(CONFIG.paths.project_root)
        
        print("[STEP 1.1] Migrating v1 Brain Shards...")
        pipeline.ingest_v1_shards()
        
        print("[STEP 1.2] Running AGI Curriculum...")
        pipeline.run_agi_curriculum()
        pipeline.vector_store.save()

    # 2. DOWNLOAD BIG DATA FROM HF
    if not skip_ingest:
        print("\n[STEP 2] Downloading Big Data from Hugging Face...")
        hf_pipeline = HFDataPipeline()
        # Download some high-quality scientific/wiki data
        hf_pipeline.download_scientific_data("wikitext", "wikitext-103-raw-v1", limit=data_limit)
        hf_pipeline.download_reasoning_data(limit=data_limit // 2)

    # 3. BUILD DATASET
    print("\n[STEP 3] Building Unified Training Dataset...")
    builder = TrainingDatasetBuilder()
    builder.add_from_v1_shards()
    builder.add_bootstrap_pairs()
    builder.add_from_memory()
    
    # Add HF data
    hf_data_dir = os.path.join(CONFIG.paths.v2_data_dir, "hf_raw")
    if os.path.exists(hf_data_dir):
        for f in os.listdir(hf_data_dir):
            if f.endswith(".jsonl"):
                builder.add_from_jsonl(os.path.join(hf_data_dir, f))
                
    dataset_path = builder.build()

    # 4. TRAINING (QLoRA)
    if not skip_train:
        print("\n[STEP 4] Starting QLoRA Fine-Tuning...")
        adapter_path = train(
            dataset_path=dataset_path,
            epochs=CONFIG.training.epochs,
            batch_size=CONFIG.training.per_device_batch_size
        )
    else:
        adapter_path = os.path.join(CONFIG.training.output_dir, "final_adapter")

    # 5. TEST & EVALUATE
    print("\n[STEP 5] Post-Training Testing & Evaluation...")
    backbone = ParadoxBackbone()
    if os.path.exists(adapter_path):
        backbone.load_adapter(adapter_path)
    
    # 5.1 Perplexity test
    evaluate_perplexity(backbone.model, backbone.tokenizer, dataset_path)
    
    # 5.2 Qualitative generation test
    generator = ParadoxGenerator(backbone=backbone)
    evaluate_generation(generator)

    print("\n" + "="*60)
    print("✅ PRODUCTION UPGRADE COMPLETE")
    print(f"  Knowledge Base: {CONFIG.paths.faiss_index_path}")
    print(f"  Model Adapter:  {adapter_path}")
    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-ingest", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()
    
    run_production_upgrade(args.skip_ingest, args.skip_train, args.limit)

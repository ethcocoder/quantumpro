"""
Paradox v2 — Code & Theory Ingestion
======================================
Specifically designed to ingest the QAU/QVS theory and codebase.
Ensures the model 'understands' its own quantum substrate.
"""

import os
from typing import List
from ..ingest.pipeline import IngestionPipeline

class TheoryIngestor:
    def __init__(self, pipeline: IngestionPipeline = None):
        self.pipeline = pipeline or IngestionPipeline()

    def ingest_qau_theory(self, project_root: str):
        """
        Ingest the core theory documents and codebase.
        """
        # 1. Ingest the massive architecture summary
        summary_path = os.path.join(project_root, "qau_architecture_summary.md")
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.pipeline.ingest_text(
                content, 
                topic="QAU Architecture Summary", 
                region="LH", 
                source="theory_doc"
            )

        # 2. Ingest the QAU Quantum Roadmap
        roadmap_path = os.path.join(project_root, "qau_quantum_roadmap.md")
        if os.path.exists(roadmap_path):
            with open(roadmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.pipeline.ingest_text(
                content, 
                topic="QAU Quantum Roadmap", 
                region="PFC", 
                source="theory_doc"
            )

        # 3. Ingest the QVS Python Source Code
        qvs_dir = os.path.join(project_root, "qau_qvs")
        if os.path.isdir(qvs_dir):
            self.ingest_code_directory(qvs_dir, region="LH")

    def ingest_code_directory(self, directory: str, region: str = "LH"):
        """Recursive code ingestion."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.hpp', '.cpp')):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, directory)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        if len(code) > 50:
                            self.pipeline.ingest_text(
                                f"FILE: {rel_path}\n\n{code}",
                                topic=f"Code: {rel_path}",
                                region=region,
                                source="source_code"
                            )
                    except Exception as e:
                        print(f"[THEORY] Failed to ingest {rel_path}: {e}")

if __name__ == "__main__":
    from ..config import CONFIG
    ingestor = TheoryIngestor()
    ingestor.ingest_qau_theory(CONFIG.paths.project_root)

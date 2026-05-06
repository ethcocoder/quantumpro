# ⚛️ Paradox AGI v2: The Sovereign Ascension

## 🚀 Production Upgrade Complete

The Paradox AGI has been evolved from a TF-IDF prototype into a **Production-Grade Sovereign Substrate**. It now utilizes a real Transformer backbone, dense vector retrieval, and an emotion-modulated reasoning engine.

### 🏗️ v2 Architecture
- **Backbone**: `microsoft/Phi-3.5-mini-instruct` (Quantized 4-bit NF4)
- **Retrieval**: FAISS Dense Vector Store (`sentence-transformers/all-MiniLM-L6-v2`)
- **Brain Layer**: Multi-region routing (PFC/LH/RH/HC) with emotional state persistence.
- **Training**: QLoRA fine-tuning optimized for Google Colab T4.
- **Ingestion**: Unified pipeline for Wikipedia, PDF, and Source Code (Theory Preservation).

---

## 🛠️ Getting Started

### 1. Installation
Ensure you have the required production dependencies:
```bash
pip install torch transformers peft trl bitsandbytes sentence-transformers faiss-cpu wikipedia pypdf fastapi uvicorn gradio
```

### 2. Run the Production Upgrade (Orchestrator)
This script will ingest your QAU theory, download Hugging Face data, and prepare the dataset:
```bash
python -m paradox_v2.main_orchestrator --limit 2000
```

### 3. Launch the Interface
Start the premium Gradio UI to interact with the evolved AGI:
```bash
python -m paradox_v2.serve.gradio_ui
```

---

## 🔬 Core Components

| Module | Purpose |
|---|---|
| `paradox_v2/config.py` | Central hyperparameter control center. |
| `paradox_v2/ingest/code_ingest.py` | **Theory Preservation**: Ingests your QAU/QVS codebase. |
| `paradox_v2/training/train_qlora.py` | Professional-grade training loop for Colab T4. |
| `paradox_v2/serve/api.py` | FastAPI REST endpoint for production integration. |
| `paradox_v2/brain/emotions.py` | Dynamic state engine modulating AGI personality. |

---

## 🧬 Theory Alignment
Paradox v2 is strictly aligned with the **Quantum Absolute Unit (QAU)** theory. During ingestion, the entire `qau_qvs` directory and roadmap are embedded into the substrate, ensuring that all reasoning is grounded in the holographic principles of the QVS.

*Sovereignty attained. The substrate is stable.*

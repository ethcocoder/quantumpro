# 🧪 Paradox AGI v2: Google Colab Training Guide

This guide provides the exact steps to train and test Paradox v2 on a **Google Colab T4 GPU**.

## 1. Setup Environment
Open a new Colab Notebook and ensure the runtime is set to **T4 GPU**.

### 📥 Clone Repository
```python
# Replace with your actual repository URL
!git clone -b paradox-agi https://github.com/ethcocoder/quantumpro.git
%cd quantumpro
```

### 📦 Install Dependencies
```python
# core ML stack for training and inference
!pip install -q torch transformers peft trl bitsandbytes sentence-transformers faiss-cpu wikipedia pypdf datasets accelerate
```

## 2. Run the Integrated Pipeline
Execute the master Colab script. This single command handles:
1.  **Theory Ingestion**: Ingests the `qau_qvs` codebase and architecture.
2.  **Big Data**: Downloads scientific data from Hugging Face.
3.  **Training**: Runs QLoRA fine-tuning (takes ~1-2 hours).
4.  **Audit**: Tests the model on QAU theory immediately after training.

```python
!python -m paradox_v2.colab_run
```

## 3. Manual Testing
After training, you can query Paradox directly from the command line:

```python
!python -m paradox_v2.test_inference "How does the QAU resolve logical dichotomies?" --region "PFC"
```

## 📊 Expected Performance on T4
- **Training Time**: ~45-60 mins for 3 epochs (2000 samples).
- **VRAM Usage**: ~5.5 GB (out of 15 GB).
- **Inference Speed**: ~20-30 tokens/sec.

---
*Note: Ensure your `paradox_brain/` folder (v1 shards) is uploaded if you want to include old memories in the v2 training dataset.*

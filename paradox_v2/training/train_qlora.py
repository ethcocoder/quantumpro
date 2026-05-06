"""
Paradox v2 — QLoRA Training Script
====================================
Fine-tunes the LLM backbone with QLoRA for Colab T4.

Usage:
    python -m paradox_v2.training.train_qlora
    python -m paradox_v2.training.train_qlora --epochs 5
"""

import os, sys, argparse, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def train(base_model=None, dataset_path=None, output_dir=None,
          epochs=None, batch_size=None, learning_rate=None,
          max_seq_length=None, lora_r=None, lora_alpha=None, resume_from=None):
    import torch
    from datasets import Dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    from paradox_v2.config import CONFIG

    base_model = base_model or CONFIG.model.base_model
    dataset_path = dataset_path or CONFIG.paths.training_data_path
    output_dir = output_dir or CONFIG.training.output_dir
    epochs = epochs or CONFIG.training.epochs
    batch_size = batch_size or CONFIG.training.per_device_batch_size
    learning_rate = learning_rate or CONFIG.training.learning_rate
    max_seq_length = max_seq_length or CONFIG.training.max_seq_length
    lora_r = lora_r or CONFIG.model.lora_r
    lora_alpha = lora_alpha or CONFIG.model.lora_alpha

    print("=" * 60)
    print("PARADOX v2 — QLoRA SOVEREIGN TRAINING")
    print(f"  Model: {base_model} | Epochs: {epochs} | LR: {learning_rate}")
    print("=" * 60)

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found: {dataset_path}")
        return

    # Load dataset
    examples = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    dataset = Dataset.from_list(examples)
    print(f"[1/5] Loaded {len(dataset)} training examples")

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Model with 4-bit quantization
    print("[2/5] Loading model with 4-bit NF4...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        base_model, quantization_config=bnb_config, device_map="auto",
        trust_remote_code=True, torch_dtype=torch.float16,
    )
    model = prepare_model_for_kbit_training(model)

    # LoRA
    print("[3/5] Configuring LoRA...")
    lora_config = LoraConfig(
        r=lora_r, lora_alpha=lora_alpha, lora_dropout=CONFIG.model.lora_dropout,
        target_modules=CONFIG.model.lora_target_modules, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    
    # ── Hard Force: T4 Compatibility ─────────────────────────────────
    print("[*] Hard-casting model parameters and config to float16...")
    model.config.torch_dtype = torch.float16
    for name, param in model.named_parameters():
        if param.dtype == torch.bfloat16:
            param.data = param.data.to(torch.float16)
    for name, buffer in model.named_buffers():
        if buffer.dtype == torch.bfloat16:
            buffer.data = buffer.data.to(torch.float16)
    
    print(f"[*] Verified Model Config Dtype: {model.config.torch_dtype}")
    
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  Trainable: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    # ── Training Configuration (TRL Version Aware) ───────────────────
    from trl import SFTTrainer
    try:
        from trl import SFTConfig
        HAS_SFT_CONFIG = True
    except ImportError:
        HAS_SFT_CONFIG = False

    if HAS_SFT_CONFIG:
        print("[4/5] Using SFTConfig (trl v0.12+)...")
        # Initialize with core arguments, then set SFT-specifics as attributes for safety
        training_args = SFTConfig(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=CONFIG.training.gradient_accumulation_steps,
            learning_rate=learning_rate,
            lr_scheduler_type=CONFIG.training.lr_scheduler_type,
            warmup_ratio=CONFIG.training.warmup_ratio,
            optim=CONFIG.training.optim,
            fp16=False,
            bf16=False,
            gradient_checkpointing=True,
            logging_steps=CONFIG.training.logging_steps,
            save_steps=CONFIG.training.save_steps,
            save_total_limit=3,
            report_to="none",
        )
        # Manually set SFT-specific attributes to bypass constructor quirks
        training_args.max_seq_length = 1024
        training_args.dataset_text_field = "text"
        training_args.packing = True
        
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            processing_class=tokenizer,
        )
    else:
        print("[4/5] Using Legacy SFTTrainer (pre-trl v0.12)...")
        from transformers import TrainingArguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=CONFIG.training.gradient_accumulation_steps,
            learning_rate=learning_rate,
            lr_scheduler_type=CONFIG.training.lr_scheduler_type,
            warmup_ratio=CONFIG.training.warmup_ratio,
            optim=CONFIG.training.optim,
            fp16=False,
            bf16=False,
            gradient_checkpointing=True,
            logging_steps=CONFIG.training.logging_steps,
            save_steps=CONFIG.training.save_steps,
            save_total_limit=3,
            report_to="none",
        )
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=tokenizer,
            max_seq_length=1024,
            dataset_text_field="text",
            packing=True,
        )

    print("[*] Starting training loop...")
    trainer.train(resume_from_checkpoint=resume_from if resume_from and os.path.exists(resume_from) else None)

    # Save
    final_path = os.path.join(output_dir, "final_adapter")
    model.save_pretrained(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"\n[5/5] DONE — Adapter saved: {final_path}")
    if torch.cuda.is_available():
        print(f"  Peak GPU: {torch.cuda.max_memory_allocated()/1024**3:.2f} GB")
    return final_path


def main():
    p = argparse.ArgumentParser(description="Paradox v2 QLoRA Training")
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--dataset", type=str, default=None)
    p.add_argument("--output", type=str, default=None)
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--max-seq-len", type=int, default=None)
    p.add_argument("--lora-r", type=int, default=None)
    p.add_argument("--lora-alpha", type=int, default=None)
    p.add_argument("--resume", type=str, default=None)
    a = p.parse_args()
    train(a.model, a.dataset, a.output, a.epochs, a.batch_size, a.lr, a.max_seq_len, a.lora_r, a.lora_alpha, a.resume)


if __name__ == "__main__":
    main()

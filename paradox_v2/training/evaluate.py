"""
Paradox v2 — Model Evaluation
===============================
Measures model quality: perplexity, sample generation, region coherence.
"""

import os, sys, json, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def evaluate_perplexity(model, tokenizer, dataset_path: str, max_samples: int = 50):
    """Compute perplexity on held-out examples."""
    import torch

    if not os.path.exists(dataset_path):
        print(f"[EVAL] Dataset not found: {dataset_path}")
        return float('inf')

    examples = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    # Use last 10% as eval set
    eval_set = examples[-max(1, len(examples)//10):][:max_samples]

    total_loss = 0.0
    total_tokens = 0

    model.eval()
    with torch.no_grad():
        for ex in eval_set:
            text = ex.get("text", "")
            if not text:
                continue
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            inputs["labels"] = inputs["input_ids"].clone()

            outputs = model(**inputs)
            total_loss += outputs.loss.item() * inputs["input_ids"].shape[1]
            total_tokens += inputs["input_ids"].shape[1]

    if total_tokens == 0:
        return float('inf')

    avg_loss = total_loss / total_tokens
    perplexity = math.exp(avg_loss)
    print(f"[EVAL] Perplexity: {perplexity:.2f} (avg loss: {avg_loss:.4f}, tokens: {total_tokens})")
    return perplexity


def evaluate_generation(generator, test_queries: list = None):
    """Run sample generations and print results for manual inspection."""
    if test_queries is None:
        test_queries = [
            ("What is game theory?", "LH"),
            ("Explain how neural networks learn.", "PFC"),
            ("How does consciousness relate to computation?", "RH"),
            ("What did we discuss previously?", "HC"),
        ]

    print("\n" + "=" * 60)
    print("PARADOX v2 — GENERATION EVALUATION")
    print("=" * 60)

    for query, region in test_queries:
        print(f"\n--- Region: {region} ---")
        print(f"Q: {query}")
        response = generator.generate(query=query, region=region)
        print(f"A: {response[:500]}")
        print()


def main():
    """Standalone evaluation entry point."""
    from paradox_v2.config import CONFIG
    from paradox_v2.llm.backbone import ParadoxBackbone
    from paradox_v2.llm.generator import ParadoxGenerator

    backbone = ParadoxBackbone()

    # Check for fine-tuned adapter
    adapter_path = os.path.join(CONFIG.training.output_dir, "final_adapter")
    if os.path.exists(adapter_path):
        print(f"[EVAL] Loading fine-tuned adapter: {adapter_path}")
        backbone.load_adapter(adapter_path)

    # Perplexity
    evaluate_perplexity(backbone.model, backbone.tokenizer, CONFIG.paths.training_data_path)

    # Generation samples
    generator = ParadoxGenerator(backbone=backbone)
    evaluate_generation(generator)


if __name__ == "__main__":
    main()

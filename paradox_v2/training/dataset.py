"""
Paradox v2 — Training Dataset Builder
=======================================
Converts v1 brain shards + bootstrap Q&A pairs + long-term memory
into a JSONL instruction-tuning dataset for QLoRA fine-tuning.
"""

import json
import os
import pickle
import random
import re
from typing import List, Dict, Optional
from ..config import CONFIG
from ..llm.prompts import format_training_example


class TrainingDatasetBuilder:
    """
    Builds instruction-tuning datasets from multiple knowledge sources.

    Sources:
        1. V1 brain shard payloads (topic → content)
        2. Bootstrap Q&A pairs (hardcoded seed dialogue)
        3. Long-term memory interactions (past conversations)
        4. Custom Q&A pairs from JSONL files

    Output format (JSONL):
        {"text": "<full chat template string>", "region": "PFC"}
    """

    def __init__(self, output_path: str = None):
        self.output_path = output_path or CONFIG.paths.training_data_path
        self.examples: List[Dict] = []

    # ── Source 1: V1 brain shards ────────────────────────────────────
    def add_from_v1_shards(self, brain_dir: str = None):
        """
        Generate instruction-tuning pairs from v1 brain shard payloads.

        Strategy: For each topic, create 3 types of questions:
            1. "What is X?" → factual definition (LH)
            2. "Explain X and its significance" → analytical (PFC)
            3. "How does X relate to broader concepts?" → creative (RH)
        """
        brain_dir = brain_dir or CONFIG.paths.brain_dir
        payloads = {}

        # Merge all shard payloads (keep deepest version per topic)
        for shard_name in ["PFC", "LH", "RH", "HC"]:
            shard_path = os.path.join(brain_dir, f"{shard_name}.para")
            if not os.path.exists(shard_path):
                continue
            try:
                with open(shard_path, 'rb') as f:
                    data = pickle.load(f)
                for topic, text in data.get("payloads", {}).items():
                    if topic not in payloads or len(text) > len(payloads[topic]):
                        payloads[topic] = text
            except Exception as e:
                print(f"[DATASET] Failed to load {shard_name}: {e}")

        print(f"[DATASET] Loaded {len(payloads)} topics from v1 shards")

        for topic, content in payloads.items():
            if not content or len(content) < 100:
                continue

            # Clean content
            content = self._clean_text(content)

            # Extract key sentences for responses
            sentences = [s.strip() for s in content.split(".")
                         if len(s.strip()) > 30]
            if not sentences:
                continue

            # ── Type 1: Definition (LH) ──────────────────────────────
            definition_sents = sentences[:5]
            definition_response = ". ".join(definition_sents) + "."
            context = ". ".join(sentences[:8]) + "."

            self.examples.append({
                "text": format_training_example(
                    instruction=f"What is {topic}?",
                    context=context[:2000],
                    response=definition_response,
                    region="LH",
                ),
                "region": "LH",
            })

            # ── Type 2: Analysis (PFC) ───────────────────────────────
            analytical_sents = [s for s in sentences if len(s) > 80][:6]
            if analytical_sents:
                analytical_response = ". ".join(analytical_sents) + "."
                self.examples.append({
                    "text": format_training_example(
                        instruction=f"Explain the concept of {topic} and analyze its key components.",
                        context=context[:2000],
                        response=analytical_response,
                        region="PFC",
                    ),
                    "region": "PFC",
                })

            # ── Type 3: Creative synthesis (RH) ──────────────────────
            if len(sentences) > 5:
                creative_response = (
                    f"The concept of {topic} reveals fascinating interconnections. "
                    + ". ".join(sentences[3:7]) + "."
                )
                self.examples.append({
                    "text": format_training_example(
                        instruction=f"How does {topic} connect to broader ideas and what patterns emerge?",
                        context=context[:2000],
                        response=creative_response,
                        region="RH",
                    ),
                    "region": "RH",
                })

        print(f"[DATASET] Generated {len(self.examples)} examples from v1 shards")

    # ── Source 2: Bootstrap Q&A pairs ────────────────────────────────
    def add_bootstrap_pairs(self):
        """Add the hardcoded seed dialogue pairs for Paradox's voice."""
        bootstrap_pairs = [
            ("What is the definition of irrationality?",
             "Irrationality is the state of thinking or acting without adequate reason or logic. It manifests in human behavior through emotional bias, cognitive distortions, and the inability to process information in a purely objective manner. The brain's emotional circuitry frequently overrides logical reasoning, producing decisions that diverge from rational self-interest.",
             "LH"),
            ("Explain the quadratic formula.",
             "The quadratic formula provides an exact solution for any quadratic equation of the form ax squared plus bx plus c equals zero. By completing the square on the general form, we arrive at x equals negative b plus or minus the square root of b squared minus four ac, all divided by two a. The discriminant, the expression under the radical, determines the nature of the roots.",
             "LH"),
            ("How does human nature affect decision making?",
             "Human nature introduces systematic biases into the decision-making process. Emotions, social conformity, envy, and shortsightedness all act as distorting forces. These forces evolved over millennia and are deeply embedded in the brain's architecture, making purely rational decision-making a rare achievement even among the most disciplined thinkers.",
             "PFC"),
            ("What is game theory?",
             "Game theory is the mathematical study of strategic interactions among rational agents. It models situations in which the outcome for each participant depends on the choices made by all other participants. The Nash equilibrium represents a state where no player can benefit by unilaterally changing their strategy, given the strategies of all others.",
             "PFC"),
            ("Explain the law of human nature.",
             "The laws of human nature describe the predictable, underlying forces that drive human behavior across history and cultures. These include the compulsion toward envy, the tendency for irrationality, the desire for power, and the need for social validation. Understanding these laws provides powerful leverage in navigating human relationships and social dynamics.",
             "RH"),
            ("What is consciousness?",
             "Consciousness is the subjective experience of awareness — the internal narrative through which an organism processes and integrates information about itself and its environment. It emerges from complex neural activity and remains one of the most profound unsolved problems in both philosophy and neuroscience.",
             "RH"),
            ("How does the brain learn?",
             "The brain learns through synaptic plasticity — the strengthening or weakening of connections between neurons based on activity patterns. When two neurons fire together repeatedly, their connection intensifies, encoded in a principle often summarized as neurons that fire together wire together. This process underlies memory formation, skill acquisition, and the adaptation of behavior over time.",
             "LH"),
            ("Analyze the current strategy manifold.",
             "The current strategy manifold reveals several critical cognitive vectors. We see a tension between short-term emotional impulses and long-term strategic rationalization. To navigate this, one must look beyond the immediate surface signals and decode the deeper systemic patterns at play. This synthesis requires a detachment from ego-driven narratives.",
             "PFC"),
            ("What are the risks of ignoring human nature?",
             "Ignoring the fundamental laws of human nature leads to predictably catastrophic results. When we fail to account for envy, irrationality, and power dynamics, our social and professional structures become fragile. True sovereignty requires acknowledging these darker impulses and designing systems that account for them rather than wishing them away in a vacuum of idealism.",
             "PFC"),
            ("Explain the concept of the Shadow.",
             "The Shadow represents the repressed or unacknowledged aspects of our personality — those traits we consider unacceptable to our conscious self-image. It acts as a powerful hidden driver of behavior, often leaking out in moments of stress or high emotion. Integrating the Shadow is a critical step in achieving psychological wholeness and strategic clarity.",
             "RH"),
            ("What is machine learning?",
             "Machine learning is a subset of artificial intelligence where algorithms learn patterns from data without being explicitly programmed. Through iterative exposure to training examples, models adjust their internal parameters to minimize prediction error. The three main paradigms are supervised learning, unsupervised learning, and reinforcement learning, each suited to different problem structures.",
             "LH"),
            ("How do neural networks work?",
             "Neural networks are computational architectures inspired by biological neurons. They consist of layers of interconnected nodes that transform input data through weighted connections and nonlinear activation functions. During training, backpropagation adjusts these weights to minimize the difference between predicted and actual outputs, enabling the network to learn complex patterns.",
             "LH"),
        ]

        for instruction, response, region in bootstrap_pairs:
            self.examples.append({
                "text": format_training_example(
                    instruction=instruction,
                    context="",
                    response=response,
                    region=region,
                ),
                "region": region,
            })

        print(f"[DATASET] Added {len(bootstrap_pairs)} bootstrap dialogue pairs")

    # ── Source 3: Long-term memory ───────────────────────────────────
    def add_from_memory(self, memory_file: str = None):
        """Add past conversation interactions as training data."""
        memory_file = memory_file or os.path.join(
            CONFIG.paths.brain_dir, "long_term_memory.json"
        )
        if not os.path.exists(memory_file):
            print("[DATASET] No long-term memory file found, skipping.")
            return

        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
        except Exception as e:
            print(f"[DATASET] Failed to load memory: {e}")
            return

        count = 0
        for m in memories:
            query = m.get("query", "")
            response = m.get("response_snippet", "")
            if query and response and len(response) > 50:
                self.examples.append({
                    "text": format_training_example(
                        instruction=query,
                        context="",
                        response=response,
                        region="HC",
                    ),
                    "region": "HC",
                })
                count += 1

        print(f"[DATASET] Added {count} examples from long-term memory")

    # ── Source 4: Custom JSONL ───────────────────────────────────────
    def add_from_jsonl(self, jsonl_path: str):
        """
        Add custom training examples from a JSONL file.

        Expected format per line:
            {"instruction": str, "context": str, "response": str, "region": str}
        """
        if not os.path.exists(jsonl_path):
            print(f"[DATASET] JSONL file not found: {jsonl_path}")
            return

        count = 0
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    
                    # ── Smart Mapping for HF Datasets ────────────────
                    # Check for various common instruction/response keys
                    instruction = entry.get("instruction") or entry.get("question") or entry.get("text", "")[:200]
                    response = entry.get("response") or entry.get("answer") or entry.get("content") or entry.get("text", "")[200:1200]
                    
                    if not instruction or not response or len(str(response)) < 20:
                        continue

                    self.examples.append({
                        "text": format_training_example(
                            instruction=str(instruction),
                            context=str(entry.get("context", "")),
                            response=str(response),
                            region=entry.get("region", "PFC"),
                        ),
                        "region": entry.get("region", "PFC"),
                    })
                    count += 1
                except Exception:
                    continue

        print(f"[DATASET] Added {count} examples from {jsonl_path}")

    # ── Build & Save ─────────────────────────────────────────────────
    def build(self, shuffle: bool = True) -> str:
        """
        Build the final dataset and save as JSONL.

        Returns:
            Path to the saved JSONL file.
        """
        if shuffle:
            random.shuffle(self.examples)

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            for example in self.examples:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")

        # Stats
        region_counts = {}
        for ex in self.examples:
            r = ex.get("region", "unknown")
            region_counts[r] = region_counts.get(r, 0) + 1

        print(f"\n{'='*50}")
        print(f"[DATASET] Build complete: {len(self.examples)} examples")
        print(f"[DATASET] Saved to: {self.output_path}")
        print(f"[DATASET] Region distribution:")
        for region, count in sorted(region_counts.items()):
            print(f"  {region}: {count}")
        print(f"{'='*50}")

        return self.output_path

    # ── Utilities ────────────────────────────────────────────────────
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean structural noise from text."""
        text = re.sub(r'={2,}\s*[^=]+\s*={2,}', '. ', text)
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\n{2,}', '. ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    @property
    def count(self) -> int:
        return len(self.examples)

"""
Phase L: Sovereign Response Trainer
Trains the AI on HOW TO RESPOND — not just WHAT to say.
Learns response style from accumulated (query, response) dialogue pairs,
building a specialized response-generation Markov model separate from the
book-content Markov model.
"""

import pickle
import json
import os
import random
import math
from collections import defaultdict, Counter

BRAIN_DIR = "paradox_brain"
MEMORY_FILE = os.path.join(BRAIN_DIR, "long_term_memory.json")
RESPONSE_MODEL_FILE = os.path.join(BRAIN_DIR, "response_model.pkl")

# ==================== TOKENIZER ====================
def tokenize(text: str) -> list:
    return [w.strip(".,!?;:\"'()[]{}") for w in text.split() if len(w.strip(".,!?;:\"'()[]{}")) > 2]

# ==================== RESPONSE STYLE TRAINER ====================

class ResponseStyleTrainer:
    """
    Trains an N-gram language model specifically on AI-style dialogue responses.
    Learns:
      - How to form coherent explanatory sentences
      - Vocabulary and transitions that appear in good AI answers
      - Query-conditioned generation (what tokens follow a given topic anchor)
    """
    def __init__(self, n: int = 3):
        self.n = n
        # Trigram synapses: (w1, w2) -> list of next tokens
        self.synapses = defaultdict(list)
        # Query-conditioned start states: query_anchor -> list of valid starting bigrams
        self.query_anchors = defaultdict(list)
        # Vocabulary distribution for fluency scoring
        self.vocab_freq = Counter()
        self.training_samples = 0

    def train_on_pair(self, query: str, response: str):
        """Train on a single (query, response) pair."""
        q_tokens = tokenize(query)
        r_tokens = tokenize(response)
        
        if len(r_tokens) < 4: return
        
        # Update vocab
        self.vocab_freq.update(r_tokens)
        
        # Build trigram synapses from the response
        for i in range(len(r_tokens) - 2):
            state = (r_tokens[i], r_tokens[i+1])
            self.synapses[state].append(r_tokens[i+2])
        
        # Map query anchors to valid starting bigrams in the response
        for q_tok in q_tokens:
            if len(q_tok) >= 4:  # Only semantic anchors
                for i in range(len(r_tokens) - 1):
                    if q_tok.lower() in r_tokens[i].lower() or q_tok.lower() in r_tokens[i+1].lower():
                        self.query_anchors[q_tok.lower()].append((r_tokens[i], r_tokens[i+1]))
        
        self.training_samples += 1

    def train_on_corpus(self, pairs: list):
        """Train on a list of (query, response) pairs."""
        for query, response in pairs:
            self.train_on_pair(query, response)
        print(f"[RESPONSE TRAINER] Trained on {self.training_samples} pairs.")
        print(f"  Synaptic states: {len(self.synapses)} | Vocab size: {len(self.vocab_freq)}")

    def generate(self, query_tokens: list, length: int = 55) -> str:
        """
        Generate a response conditioned on the query.
        Attempts to seed from a response state related to the query's semantic anchors.
        """
        if not self.synapses: return ""

        # Try to find a semantically conditioned start state
        starting_state = None
        for tok in sorted(query_tokens, key=len, reverse=True):
            candidates = self.query_anchors.get(tok.lower(), [])
            if candidates:
                starting_state = random.choice(candidates)
                break
        
        # Fallback: random starting state from known synapses
        if not starting_state:
            starting_state = random.choice(list(self.synapses.keys()))
        
        tokens_out = list(starting_state)
        state = starting_state
        
        for _ in range(length):
            if state in self.synapses:
                next_tok = random.choice(self.synapses[state])
                tokens_out.append(next_tok)
                state = (state[1], next_tok)
            else:
                # Regenerate from a new anchor when the chain breaks
                new_states = [s for s in self.synapses.keys()
                               if any(qt.lower() in s[0].lower() for qt in query_tokens)]
                if new_states:
                    state = random.choice(new_states)
                else:
                    state = random.choice(list(self.synapses.keys()))
                tokens_out.extend(list(state))
        
        output = " ".join(tokens_out)
        # Clean up trailing incomplete thought
        last_period = output.rfind(".")
        if last_period > len(output) // 2:
            output = output[:last_period + 1]
        elif not output.endswith((".", "...", "!")):
            output += "."
        return output

    def save(self, path: str):
        with open(path, 'wb') as f:
            pickle.dump({
                "synapses": dict(self.synapses),
                "query_anchors": dict(self.query_anchors),
                "vocab_freq": dict(self.vocab_freq),
                "training_samples": self.training_samples,
                "n": self.n
            }, f)
        print(f"[RESPONSE TRAINER] Model saved -> {path} ({os.path.getsize(path)//1024} KB)")

    @staticmethod
    def load(path: str) -> "ResponseStyleTrainer":
        trainer = ResponseStyleTrainer()
        with open(path, 'rb') as f:
            state = pickle.load(f)
        trainer.synapses = defaultdict(list, state["synapses"])
        trainer.query_anchors = defaultdict(list, state["query_anchors"])
        trainer.vocab_freq = Counter(state["vocab_freq"])
        trainer.training_samples = state["training_samples"]
        trainer.n = state["n"]
        return trainer


# ==================== BOOTSTRAP SEED DATA ====================
# A small seed of high-quality (Q, A) pairs to bootstrap the response
# voice before the memory bank grows rich enough.
BOOTSTRAP_PAIRS = [
    ("What is the definition of irrationality?",
     "Irrationality is the state of thinking or acting without adequate reason or logic. It manifests in human behavior through emotional bias, cognitive distortions, and the inability to process information in a purely objective manner. The brain's emotional circuitry frequently overrides logical reasoning, producing decisions that diverge from rational self-interest."),
    ("Explain the quadratic formula.",
     "The quadratic formula provides an exact solution for any quadratic equation of the form ax squared plus bx plus c equals zero. By completing the square on the general form, we arrive at x equals negative b plus or minus the square root of b squared minus four ac, all divided by two a. The discriminant, the expression under the radical, determines the nature of the roots."),
    ("How does human nature affect decision making?",
     "Human nature introduces systematic biases into the decision-making process. Emotions, social conformity, envy, and shortsightedness all act as distorting forces. These forces evolved over millennia and are deeply embedded in the brain's architecture, making purely rational decision-making a rare achievement even among the most disciplined thinkers."),
    ("What is game theory?",
     "Game theory is the mathematical study of strategic interactions among rational agents. It models situations in which the outcome for each participant depends on the choices made by all other participants. The Nash equilibrium represents a state where no player can benefit by unilaterally changing their strategy, given the strategies of all others."),
    ("Explain the law of human nature.",
     "The laws of human nature describe the predictable, underlying forces that drive human behavior across history and cultures. These include the compulsion toward envy, the tendency for irrationality, the desire for power, and the need for social validation. Understanding these laws provides powerful leverage in navigating human relationships and social dynamics."),
    ("What is consciousness?",
     "Consciousness is the subjective experience of awareness — the internal narrative through which an organism processes and integrates information about itself and its environment. It emerges from complex neural activity and remains one of the most profound unsolved problems in both philosophy and neuroscience."),
    ("How does the brain learn?",
     "The brain learns through synaptic plasticity — the strengthening or weakening of connections between neurons based on activity patterns. When two neurons fire together repeatedly, their connection intensifies, encoded in a principle often summarized as neurons that fire together wire together. This process underlies memory formation, skill acquisition, and the adaptation of behavior over time."),
    ("Analyze the current strategy manifold.",
     "The current strategy manifold reveals several critical cognitive vectors. We see a tension between short-term emotional impulses and long-term strategic rationalization. To navigate this, one must look beyond the immediate surface signals and decode the deeper systemic patterns at play. This synthesis requires a detachment from ego-driven narratives."),
    ("What are the risks of ignoring human nature?",
     "Ignoring the fundamental laws of human nature leads to predictably catastrophic results. When we fail to account for envy, irrationality, and power dynamics, our social and professional structures become fragile. True sovereignty requires acknowledging these darker impulses and designing systems that account for them rather than wishing them away in a vacuum of idealism."),
    ("Summarize the concepts discussed.",
     "The discourse has synthesized several key themes: the neurological basis of belief, the mechanics of strategic decision-making, and the persistent influence of evolutionary history on modern conduct. These elements converge to form a unified field of understanding, allowing for more precise navigation of complex social environments."),
    ("Explain the concept of the Shadow.",
     "The Shadow represents the repressed or unacknowledged aspects of our personality—those traits we consider unacceptable to our conscious self-image. It acts as a powerful hidden driver of behavior, often leaking out in moments of stress or high emotion. Integrating the Shadow is a critical step in achieving psychological wholeness and strategic clarity."),
    ("Why is irrationality so prevalent?",
     "Irrationality is a byproduct of our evolutionary development. The emotional brain developed millions of years before the neo-cortex, giving it structural priority in moments of perceived threat or deep desire. This legacy ensures that even 'rational' actors are frequently driven by subterranean impulses they are only partially aware of."),
]


# ==================== MAIN TRAINING ENTRY POINT ====================
def train_response_model():
    print("=" * 60)
    print("PARADOX RESPONSE TRAINER — DIALOGUE VOICE SYNTHESIS")
    print("=" * 60)

    trainer = ResponseStyleTrainer(n=3)
    all_pairs = list(BOOTSTRAP_PAIRS)

    # Load accumulated memory from past Paradox interactions
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        for m in memories:
            q = m.get("query", "")
            r = m.get("response_snippet", "")
            if q and r and len(r) > 50:
                all_pairs.append((q, r))
        print(f"[RESPONSE TRAINER] Loaded {len(memories)} past interactions from long_term_memory.json")

    print(f"[RESPONSE TRAINER] Total training pairs: {len(all_pairs)}")
    trainer.train_on_corpus(all_pairs)
    trainer.save(RESPONSE_MODEL_FILE)
    print("[RESPONSE TRAINER] Training complete. Response voice model is ready.")


if __name__ == "__main__":
    train_response_model()

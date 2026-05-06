import re
import math
import random
import os
import pickle
from collections import defaultdict, Counter


# ==================== PAYLOAD CLEANER ====================
class ManifoldScrubber:
    """
    Manifold Scrubber: Payload cleaning and direct text access.
    """
    @staticmethod
    def clean_payload(text: str) -> str:
        text = text.encode("ascii", "ignore").decode("ascii")
        text = text.replace("- ", "").replace("\n", " ")
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'(?<= )([a-z]) (?=[a-z] )', r'\1', text, flags=re.IGNORECASE)
        return text.strip()


# ==================== RESPONSE STYLE MODEL ====================
class TrainedResponseModel:
    """
    Phase L: Sovereign trained response voice.
    Loads the pre-trained response_model.pkl and generates AI-styled
    dialogue from query-conditioned trigram synapses.
    """
    def __init__(self):
        # Trigram synapses: (w1, w2) -> [list of next words]
        self.synapses = {}
        # Query-conditioned start states: query_anchor -> [(start_w1, start_w2)]
        self.query_anchors = {}
        self.ready = False

    def load(self) -> bool:
        """Attempt to load the trained response model."""
        brain_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "paradox_brain")
        )
        model_path = os.path.join(brain_dir, "response_model.pkl")
        if not os.path.exists(model_path): return False
        try:
            with open(model_path, 'rb') as f:
                state = pickle.load(f)
            self.synapses = state["synapses"]
            self.query_anchors = state["query_anchors"]
            self.ready = True
            return True
        except Exception:
            return False

    def generate(self, keywords: list, context_text: str, length: int = 55) -> str:
        """
        Generates a grounded AI response.
        Prioritizes factual transitions from the book context while 
        maintaining the dialogue flow learned during training.
        """
        if not self.ready: return ""

        # 1. Build a local content-markov from the book context (PFC text)
        context_synapses = defaultdict(list)
        context_words = context_text.split()
        for i in range(len(context_words) - 2):
            s = (context_words[i], context_words[i+1])
            context_synapses[s].append(context_words[i+2])

        # 2. Pick a start state grounded in keywords
        starting_state = None
        for kw in sorted(keywords, key=len, reverse=True):
            if kw.lower() in self.query_anchors:
                starting_state = random.choice(self.query_anchors[kw.lower()])
                break
        
        # Fallback to book context start states
        if not starting_state and context_synapses:
            starting_state = random.choice(list(context_synapses.keys()))
        
        # Absolute fallback
        if not starting_state:
            starting_state = random.choice(list(self.synapses.keys()))

        tokens_out = list(starting_state)
        current_state = starting_state

        for _ in range(length):
            candidates = []
            # Probability 1: If current_state exists in the Book Context, use it strongly (Factuality)
            if current_state in context_synapses:
                candidates.extend(context_synapses[current_state] * 3) # Factual boost
            
            # Probability 2: If current_state exists in Trained Resp Model, use it (Style)
            if current_state in self.synapses:
                candidates.extend(self.synapses[current_state])
            
            if candidates:
                next_tok = random.choice(candidates)
                tokens_out.append(next_tok)
                current_state = (current_state[1], next_tok)
            else:
                # If chain breaks, seek a new anchor keyword in the Book or Resp Model
                found = False
                for kw in keywords:
                    possible = [s for s in context_synapses.keys() if kw.lower() in s[0].lower()]
                    if possible:
                        current_state = random.choice(possible)
                        tokens_out.extend(list(current_state))
                        found = True
                        break
                if not found: break # End of thought

        output = " ".join(tokens_out)
        # Final polish (ensure it doesn't end mid-sentence)
        last_dot = output.rfind(".")
        if last_dot > len(output) * 0.4:
            output = output[:last_dot + 1]
        elif not output.endswith((".", "!", "...")):
            output += "."
            
        return output


# ==================== SINGLETON LOADER ====================
_response_model = None

def get_response_model() -> TrainedResponseModel:
    global _response_model
    if _response_model is None:
        _response_model = TrainedResponseModel()
        _response_model.load()
    return _response_model


# ==================== SYNTHESIS ENTRY POINT ====================
def synthesize(text_chunk: str, keywords: list, topic: str) -> str:
    """
    Phase LI: Hybrid Sovereign Synthesis (No Word-Salad)
    The Response Model fluently generates an introductory cognitive thought 
    strictly in its trained AI voice. Then, the Scrubber extracts the literal 
    dense logic from the PFC text chunk to guarantee perfect factual coherence.
    """
    rm = get_response_model()
    
    # 1. Generate the trained AI Voice opening (without confusing it with raw PDF text)
    ai_voice_intro = rm.generate(keywords, context_text="", length=15)
    
    # Clean up the generated intro so it trails off gracefully into the facts
    if ai_voice_intro.endswith("."): ai_voice_intro = ai_voice_intro[:-1]
    if not ai_voice_intro.endswith("..."): ai_voice_intro += "..."
    # Capitalize first letter
    if len(ai_voice_intro) > 1:
        ai_voice_intro = ai_voice_intro[0].upper() + ai_voice_intro[1:]

    # 2. Extract the densest factual sentences from the PFC chunk
    sentences = [s.strip() for s in text_chunk.split(".") if len(s.strip()) > 15]
    
    clean_sents = []
    for s in sentences:
        # Reject table of contents noise just in case
        if "table of contents" in s.lower() or "page" in s.lower(): continue
        
        # Score the sentence
        score = sum(3 for k in keywords if k.lower() in s.lower()) + (len(s) / 100.0)
        clean_sents.append((score, s + "."))
        
    clean_sents.sort(reverse=True)
    best_facts = " ".join([s for _, s in clean_sents[:3]])
    
    if not best_facts:
        best_facts = "The manifold structure lacked coherent dense logic on this specific vector."

    synthesis = f"{ai_voice_intro}\n  {best_facts}"

    # Dynamic preamble
    topic_words = [w.strip("(),.") for w in topic.split() if len(w) > 3]
    manifold_anchor = topic_words[-1] if topic_words else "domain"
    action_words = [w.lower().strip(".,:;!?'\"") for w in text_chunk.split()
                    if w.endswith("ing") and len(w) > 6]
    action = action_words[len(keywords) % len(action_words)] if action_words else "synthesizing"
    
    preamble = f"By {action} the `{topic}` {manifold_anchor}, my trained thought process converged on:"
    return f"{preamble}\n  {synthesis}"


class ManifoldScrubber:
    @staticmethod
    def clean_payload(text: str) -> str:
        return text.strip()

    def synthesize_insight(self, text_chunk: str, keywords: list, topic: str) -> str:
        return synthesize(text_chunk, keywords, topic)

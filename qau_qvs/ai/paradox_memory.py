import json
import os
import time
import math

class ParadoxMemoryManager:
    """
    Sovereign Continuous Mind Core.
    Stores prior cognitive states and utilizes an Attention Mechanism to 
    simulate RAG (Retrieval-Augmented Generation). Allows Paradox to remember.
    """
    def __init__(self, memory_file="paradox_brain/long_term_memory.json"):
        self.memory_file = memory_file
        self.memories = []
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
            except Exception:
                self.memories = []
        else:
            # Ensure folder exists
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            self.memories = []

    def _save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=4)

    def memorize(self, query: str, response: str, coherence_pct: float, topic: str):
        """Archives a completed interaction into the continuous cognitive stream."""
        # Store a condensed memory to prevent extreme ballooning
        memory_state = {
            "query": query,
            "response_snippet": response[:300] + "..." if len(response) > 300 else response,
            "coherence": coherence_pct,
            "topic": topic,
            "timestamp": time.time()
        }
        self.memories.append(memory_state)
        self._save_memory()

    def _clean_tokens(self, text: str) -> set:
        """Strips structural noise to find semantic anchors."""
        return set([w.strip(".,!?\"'()[]") for w in text.lower().split() if len(w) > 3])

    def attention_score(self, query: str, memory: dict) -> float:
        """
        Calculates Semantic Attention Weight.
        Combines Term-Frequency Overlap with Exponential Time Decay and Coherence Weight.
        """
        q_tokens = self._clean_tokens(query)
        m_tokens = self._clean_tokens(memory["query"])
        
        if not q_tokens: return 0.0
        
        # 1. Semantic Overlap
        overlap = len(q_tokens.intersection(m_tokens))
        semantic_score = overlap / float(len(q_tokens))
        
        # 2. Exponential Time Decay 
        # (Recent interactions strongly influence the current thought process)
        seconds_passed = time.time() - memory["timestamp"]
        hours_passed = seconds_passed / 3600.0
        decay = math.exp(-0.01 * hours_passed) 
        
        # 3. Truth Confidence Multiplier (It trusts its best memories more)
        confidence_mult = (memory["coherence"] / 100.0)
        
        attention = semantic_score * decay * confidence_mult
        
        return attention

    def recall_context(self, current_query: str, threshold: float = 0.25):
        """
        Retrieves the top memory that clears the attention threshold.
        Returns the memory dict or None.
        """
        if not self.memories: return None
        
        scored_memories = []
        for m in self.memories:
            score = self.attention_score(current_query, m)
            if score > threshold:
                scored_memories.append((score, m))
                
        if scored_memories:
            # Sort by highest attention score
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            return scored_memories[0][1] 
            
        return None

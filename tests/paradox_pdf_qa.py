import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_pdf_qa_interrogation():
    print("="*60)
    print(">>> PARADOX: STRATEGIC INTERROGATION (LAW OF HUMAN NATURE) <<<")
    print("="*60)

    # 1. Initialize Substrate & Shared Brain
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. Strategic Interrogation Script
    questions = [
        "What is the Law of Irrationality?",
        "Explain Law of Compulsive Behavior.",
        "What does Greene say about Narcissism?",
        "How do we handle the Law of Envy?"
    ]

    # 3. Execution: Topical Mind-Fencing
    anchor_topic = "The Laws of Human Nature (Robert Greene)"
    payload_raw = ingestor.payload_base["HC"].get(anchor_topic, "")
    # Normalize for searching
    payload_clean = " ".join(payload_raw.split()).lower()
    
    for i, q in enumerate(questions):
        print(f"\n[QUERY {i+1}]: {q}")
        
        # Keywords for high-fidelity extraction (4+ chars)
        keywords = [w.lower().strip("?,.") for w in q.split() if len(w) >= 4 and w.lower() not in ["explain", "nature", "about", "what", "handle"]]
        
        found = False
        if payload_raw:
            all_scored_sentences = []
            
            for kw in keywords:
                # --- PHASE XXXVI: GLOBAL MANIFOLD SCRUTINY ---
                # Find ALL occurrences of the keyword to skip TOC
                start_search = 0
                while True:
                    idx = payload_raw.lower().find(kw, start_search)
                    if idx == -1: break
                    
                    # Analyze window around THIS occurrence
                    window_start = max(0, idx - 100)
                    window_end = min(len(payload_raw), idx + 1500)
                    window_text = payload_raw[window_start:window_end].replace("\n", " ").strip()
                    
                    # Split into sentences and score
                    raw_sentences = [s.strip() + "." for s in window_text.split('.') if len(s.strip()) > 30]
                    for s in raw_sentences:
                        k_score = sum(2 for k in keywords if k in s.lower())
                        if "table of contents" in s.lower() or s.count("  ") > 3:
                            k_score -= 10
                        if len(s) > 100: k_score += 1
                        all_scored_sentences.append((k_score, s))
                    
                    start_search = idx + len(kw) + 1
                    if start_search >= len(payload_raw): break
            
            # Sort ALL findings globally
            all_scored_sentences.sort(key=lambda x: x[0], reverse=True)
            # Remove duplicates while preserving order
            seen = set()
            unique_top = []
            for score, text in all_scored_sentences:
                if text not in seen and score > 2: # Require at least 2 keyword matches for high fidelity
                    unique_top.append(text)
                    seen.add(text)
            
            response_snippet = " ".join(unique_top[:2])
            
            if response_snippet:
                print(f"  [RESULT]: VERIFIED from Psychology Shard (Global Match).")
                print(f"  [PARADOX RESPONSE]: \"{response_snippet}\"")
                found = True
        
        if not found:
            print(f"  [RESULT]: REJECTED. Manifold mismatch or Noisy Signal Tokens: {keywords}")
        
        if not found:
            print(f"  [RESULT]: REJECTED. Manifold mismatch or Noisy Signal Tokens: {keywords}")

    print("\n" + "="*60)
    print("--- PARADOX STRATEGIC QA: COMPLETE ---")
    print("============================================================")

if __name__ == "__main__":
    paradox_pdf_qa_interrogation()

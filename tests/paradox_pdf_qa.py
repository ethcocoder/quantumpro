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
            for kw in keywords:
                if kw in payload_clean:
                    # Find approximate location in raw payload
                    idx = payload_raw.lower().find(kw)
                    if idx != -1:
                        # Window-based retrieval 
                        start = max(0, idx - 100)
                        end = min(len(payload_raw), idx + 2000)
                        window_text = payload_raw[start:end].replace("\n", " ").strip()
                        
                        # --- PHASE XXXIV: SENTENCE-LEVEL SCORING ---
                        all_sentences = [s.strip() + "." for s in window_text.split('.') if len(s.strip()) > 10]
                        scored_sentences = []
                        for s in all_sentences:
                            score = sum(1 for k in keywords if k in s.lower())
                            scored_sentences.append((score, s))
                        
                        # Sort and extract specific answers
                        scored_sentences.sort(key=lambda x: x[0], reverse=True)
                        top_sentences = [s[1] for s in scored_sentences[:2] if s[0] > 0]
                        response_snippet = " ".join(top_sentences)
                        
                        if response_snippet:
                            print(f"  [RESULT]: VERIFIED from Psychology Shard.")
                            print(f"  [PARADOX RESPONSE]: \"{response_snippet}\"")
                            found = True
                            break
        
        if not found:
            print(f"  [RESULT]: REJECTED. Manifold mismatch or Noisy Signal Tokens: {keywords}")
        
        if not found:
            print(f"  [RESULT]: REJECTED. Manifold mismatch or Noisy Signal Tokens: {keywords}")

    print("\n" + "="*60)
    print("--- PARADOX STRATEGIC QA: COMPLETE ---")
    print("============================================================")

if __name__ == "__main__":
    paradox_pdf_qa_interrogation()

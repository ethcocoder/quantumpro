import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_strategy_interrogator():
    print("="*60)
    print(">>> PARADOX: SOVEREIGN STRATEGIC INTERROGATOR <<<")
    print(">>>       - MANIFOLD: THE LAWS OF HUMAN NATURE")
    print("="*60)
    
    # 1. Initialize Substrate & Engine
    qvs = QVS()
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)
    anchor_topic = "The Laws of Human Nature (Robert Greene)"
    payload_raw = ingestor.payload_base["HC"].get(anchor_topic, "")
    
    if not payload_raw:
        print("[!] ERROR: Strategic Shard MISSING. Run PDF Ingestor first.")
        return
        
    payload_clean = " ".join(payload_raw.split()).lower()
    print(f"[*] Mind Residency: LOADED ({len(payload_raw)} char payload).")
    print("[*] Ready for interrogation. Type 'exit' to leave.\n")

    while True:
        q = input(">>> YOUR STRATEGIC QUERY: ")
        if q.lower() in ["exit", "quit"]: break
        
        # 2. Extract Specific Keywords
        keywords = [w.lower().strip("?,.") for w in q.split() if len(w) >= 4 and w.lower() not in ["explain", "nature", "about", "what", "handle", "tell"]]
        
        if not keywords:
            print("  [AGI]: Query too noisy. Please be more specific.")
            continue
            
        # 3. GLOBAL MANIFOLD SCRUTINY (Exhaustive Scan)
        all_scored_sentences = []
        for kw in keywords:
            start_search = 0
            while True:
                idx = payload_raw.lower().find(kw, start_search)
                if idx == -1: break
                
                window_start = max(0, idx - 100)
                window_end = min(len(payload_raw), idx + 2000)
                window_text = payload_raw[window_start:window_end].replace("\n", " ").strip()
                
                # Split and filter for Wisdom Density
                sentences = [s.strip() + "." for s in window_text.split('.') if len(s.strip()) > 30]
                for s in sentences:
                    score = sum(3 for k in keywords if k in s.lower()) # 3x keyword weight
                    if "table of contents" in s.lower() or s.count("  ") > 3: score -= 15
                    if len(s) > 100: score += 2 # Fidelity Bonus
                    all_scored_sentences.append((score, s))
                    
                start_search = idx + len(kw) + 1
                if start_search >= len(payload_raw): break
                
        # 4. Rank Globally
        all_scored_sentences.sort(key=lambda x: x[0], reverse=True)
        seen = set()
        unique_top = []
        for score, text in all_scored_sentences:
            if text not in seen and score > 2:
                unique_top.append(text)
                seen.add(text)
                
        # 5. Presentation
        response = " ".join(unique_top[:2]) if unique_top else ""
        if response:
            print(f"  [RESULT]: VERIFIED Strategic Manifold.")
            print(f"  [PARADOX]: \"{response}\"\n")
        else:
            print(f"  [RESULT]: No verified signal for tokens {keywords}.\n")

    print("\n" + "="*60)
    print("--- PARADOX INTERROGATION: COMPLETE ---")

if __name__ == "__main__":
    paradox_strategy_interrogator()

import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion
from qau_qvs.ai.manifold_scrubber import ManifoldScrubber

def paradox_strategy_interrogator():
    scrubber = ManifoldScrubber()
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
        
    # Phase XXXVIII: Clean-Sweep Sanitization
    payload_raw = scrubber.clean_payload(payload_raw)
    print(f"[*] Mind Residency: LOADED & SANITIZED ({len(payload_raw)} char payload).")
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
                
        # 4. Global Wisdom-Seeker (Phase XLI: Nuclear TOC-Filter)
        all_scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        seen = set()
        candidates = []
        for score, text in all_scored_sentences:
            idx_in_payload = payload_raw.find(text)
            
            if text not in seen and score > 2:
                # NUCLEAR TOC PENALTY:
                # Skip the first 100KB (TOC is here) and penalize short fragments
                if idx_in_payload < 100000 or len(text) < 120:
                    score -= 30 
                
                # Linguistic Complexity Bonus
                if text.count(" ") > 20: score += 2
                
                candidates.append((score, text))
                seen.add(text)
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [c[1] for c in candidates if c[0] > 0] # Filter out penalized TOC
        top_slice = " ".join(top_sentences[:25]) 
        
        # --- PHASE XXXVIII: THINKING LAYER (Synthesis) ---
        wisdom = scrubber.extract_definition(top_slice, keywords)
        strategy = scrubber.extract_advice(top_slice, keywords)
        evidence = top_sentences[0] if top_sentences else "No chapter-level evidence found."
        
        # 5. Professional AGI Presentation
        if wisdom != "Concept unverifiable.":
            print(f"\n  [WISDOM]: {wisdom}")
            print(f"  [STRATEGY]: {strategy}")
            print(f"  [EVIDENCE]: \"{evidence[:250]}...\"\n")
        else:
            print(f"  [RESULT]: No verified signal for tokens {keywords}.\n")

    print("\n" + "="*60)
    print("--- PARADOX INTERROGATION: COMPLETE ---")

if __name__ == "__main__":
    paradox_strategy_interrogator()

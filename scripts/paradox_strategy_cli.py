import os
import sys
import pickle

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qau_qvs.ai.manifold_scrubber import ManifoldScrubber

BRAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "paradox_brain"))

# ===================== BRAIN REGION LOADER =====================
def load_region(name: str) -> dict:
    path = os.path.join(BRAIN_DIR, f"{name}_trained.pkl")
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return {}

# ===================== NEUROLOGICAL RETRIEVAL =====================
def combined_retrieve(query_tokens: list, lh: dict, rh: dict) -> tuple:
    """
    Neurological consensus retrieval: accumulate LH (precision) + RH (entropy) weights
    across ALL query tokens with NO caps or human biases. Purely statistical emergence.
    """
    lh_inv = lh.get("inverted_index", {})
    rh_inv = rh.get("inverted_index", {})
    topic_scores = {}
    
    for tok in query_tokens:
        # LH: linguistic precision vote
        for topic, weight in lh_inv.get(tok, []):
            topic_scores[topic] = topic_scores.get(topic, 0.0) + weight
        # RH: conceptual entropy vote (squared IDF makes rare terms more powerful)
        for topic, weight in rh_inv.get(tok, []):
            topic_scores[topic] = topic_scores.get(topic, 0.0) + weight

    if not topic_scores:
        return None, 0.0, 0.0, 0.0

    best = max(topic_scores, key=topic_scores.get)
    best_score = topic_scores[best]
    lh_score = sum(w for t, w in lh_inv.get(tok, []) for tok in query_tokens if t == best)
    rh_score = best_score - lh_score
    return best, best_score, lh_score, rh_score

def pfc_synthesize(best_topic: str, query_tokens: list, pfc: dict) -> str:
    """PFC: Analytical synthesis — pulls the reasoning-dense fragments for the topic."""
    payloads = pfc.get("payloads", {})
    text = payloads.get(best_topic, "")
    if not text: return ""
    # PFC payload is already pre-filtered for complex sentences — take top 6
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 40]
    # Re-rank by keyword density on the fly
    scored = []
    for s in sentences:
        score = sum(1 for t in query_tokens if t in s.lower())
        scored.append((score, s))
    scored.sort(reverse=True)
    return ". ".join(s for _, s in scored[:6]) + "."

def hc_associate(best_topic: str, query_tokens: list, hc: dict) -> str:
    """HC: Hippocampal association — checks episodic memory for related topics."""
    associations = hc.get("associations", {})
    related = associations.get(best_topic, [])[:3]
    if related:
        names = ", ".join(f"'{t}'" for t, _ in related)
        return f"  > [HC RECALL]: Associative pathways activated — related manifolds: {names}."
    return ""

# ===================== MAIN REPL =====================
def paradox_strategy_interrogator():
    scrubber = ManifoldScrubber()
    print("=" * 60)
    print(">>> PARADOX: SOVEREIGN NEUROLOGICAL AGI <<<")
    print(">>>  LH | RH | PFC | HC  —  4-Region Brain Active")
    print("=" * 60)

    # Load all 4 trained brain regions
    lh  = load_region("LH")
    rh  = load_region("RH")
    pfc = load_region("PFC")
    hc  = load_region("HC")

    if not lh or not pfc:
        print("[!] ERROR: Trained brain not found. Run scripts/paradox_brain_trainer.py first.")
        return

    # All payloads available via HC (deepest full-text store)
    all_payloads = hc.get("payloads", pfc.get("payloads", {}))

    print(f"[*] LH: {len(lh.get('inverted_index', {}))} precision terms trained.")
    print(f"[*] RH: {len(rh.get('inverted_index', {}))} conceptual entropy terms trained.")
    print(f"[*] PFC: {len(pfc.get('inverted_index', {}))} analytical patterns trained.")
    print(f"[*] HC: {len(hc.get('associations', {}))} associative episodic links indexed.")
    print("\n[*] Sovereign Interrogator Ready. Type 'exit' to leave.\n")

    # Initialize Memory Manager (Phase XLVII — Hippocampal RAG)
    try:
        from qau_qvs.ai.paradox_memory import ParadoxMemoryManager
        memory_manager = ParadoxMemoryManager()
    except Exception as e:
        print(f"[!] Warning: RAG Memory Manager failed to initialize. {e}")
        memory_manager = None

    while True:
        try:
            q = input(">>> YOUR STRATEGIC QUERY: ")
        except EOFError:
            break
        if q.lower() in ["exit", "quit"]: break

        # HC: Check long-term memory first (RAG recall)
        memory_context_msg = ""
        if memory_manager:
            past_thought = memory_manager.recall_context(q)
            if past_thought:
                memory_context_msg = f"  > [HC MEMORY]: Recalling our previous discourse on '{past_thought['topic']}'..."

        # Emergent keyword extraction (no hardcoding)
        raw_tokens = [w.lower().strip("?,.!") for w in q.split() if len(w.strip("?,.!")) >= 4]
        keywords = sorted(raw_tokens, key=len, reverse=True)[:4]

        if not keywords:
            print("  [AGI]: Query entropy too low. Please elaborate.")
            continue

        # Neurological Consensus: LH + RH combined pure statistical vote
        best_topic, combined_score, lh_score, rh_score = combined_retrieve(keywords, lh, rh)

        if not best_topic:
            best_topic = list(all_payloads.keys())[0]
            combined_score, lh_score, rh_score = 0.0, 0.0, 0.0

        # PFC: Pull analytical synthesis fragments for this topic
        pfc_text = pfc_synthesize(best_topic, keywords, pfc)
        full_payload = all_payloads.get(best_topic, pfc_text)
        text_for_generation = pfc_text if pfc_text else full_payload

        print(f"\n[*] Consensus manifold: '{best_topic}' (combined:{combined_score:.3f} | LH:{lh_score:.3f} | RH:{rh_score:.3f})")

        # HC: Associative memory links
        hc_msg = hc_associate(best_topic, keywords, hc)

        # PFC: Language model generates the response
        cognitive_stream = scrubber.synthesize_insight(text_for_generation, keywords, best_topic)

        # QUANTUM DEEP LEARNING (Phase XLV-XLVI)
        try:
            from qau_qvs.ai.quantum_neural import SovereignQuantumNetwork
            q_features = [
                len(keywords) / 4.0,
                lh_score / 10.0,
                rh_score / 10.0,
                len(text_for_generation) / 5000.0,
            ]
            q_net = SovereignQuantumNetwork(input_features=len(q_features))
            wave_val = q_net.evaluate_cognitive_resonance(q_features)
            training_msg = ""
            if wave_val > 0.50:
                init_loss = q_net.train_step(q_features, 0.99, 0.1)
                for _ in range(4): q_net.train_step(q_features, 0.99, 0.1)
                final_val = q_net.evaluate_cognitive_resonance(q_features)
                final_loss = (final_val - 0.99) ** 2
                training_msg = f"  > [QUANTUM AUTODIDACT]: MSE Loss {init_loss:.4f} -> {final_loss:.4f}"
                wave_val = final_val
            resonance_pct = round(wave_val * 100.0, 2)
        except Exception:
            resonance_pct = 0.0
            training_msg = ""

        # COGNITIVE STREAM OUTPUT
        if "Insufficient cognitive density" not in cognitive_stream:
            print(f"\n[PARADOX COGNITIVE STREAM]")
            if memory_context_msg: print(memory_context_msg)
            if hc_msg: print(hc_msg)
            print(f"  > [QUANTUM OBSERVER]: Superposition collapsed at {resonance_pct}% Truth Confidence.")
            if training_msg: print(training_msg)
            print(f"{cognitive_stream}\n")

            if memory_manager:
                memory_manager.memorize(q, cognitive_stream, resonance_pct, best_topic)
        else:
            print(f"\n  [RESULT]: Manifold '{best_topic}' yielded insufficient density for tokens {keywords}.\n")

    print("\n" + "=" * 60)
    print("--- PARADOX INTERROGATION: COMPLETE ---")

if __name__ == "__main__":
    paradox_strategy_interrogator()

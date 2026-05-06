"""
Phase XLIX: Sovereign Neurological Brain Trainer
Trains each brain region independently — like a real human brain:

  PFC (Prefrontal Cortex):  High-scoring analytical sentences. Reasoning & synthesis.
  LH  (Left Hemisphere):    Maximum linguistic precision — definitions, exact term density.
  RH  (Right Hemisphere):   Conceptual entropy — unusual/rare words, lateral associations.
  HC  (Hippocampus):        Associative index — links topics to each other by co-occurrence.
"""

import pickle
import math
import os
import re
from collections import defaultdict, Counter

BRAIN_DIR = "paradox_brain"

# ===================== SHARED UTILITIES =====================

def tokenize(text: str) -> list:
    return [w.strip(".,!?;:\"'()[]{}") for w in text.lower().split()
            if len(w.strip(".,!?;:\"'()[]{}")) > 3]

def build_tf(tokens: list) -> dict:
    """
    Sub-linear Term Frequency Scaling.
    Removes the 'Document Length Penalty' that standard TF-IDF imposes on 
    massive textbooks, allowing Greene/Sullivan to compete fairly with 
    small Wikipedia snippets.
    """
    if not tokens: return {}
    c = Counter(tokens)
    # Returns (1 + log(count)) for every word that appears
    return {w: 1.0 + math.log(c[w]) for w in c}

def build_idf(all_tf: list) -> dict:
    N = len(all_tf)
    df = defaultdict(int)
    for tf in all_tf:
        for w in tf:
            df[w] += 1
    return {w: math.log((N + 1) / (n + 1)) + 1.0 for w, n in df.items()}

def build_tfidf(tf: dict, idf: dict) -> dict:
    return {w: tf[w] * idf.get(w, 0.0) for w in tf}

def build_inverted_index(tfidf_matrix: list, topics: list, min_weight=0.005) -> dict:
    inv = defaultdict(list)
    for i, vec in enumerate(tfidf_matrix):
        for term, w in vec.items():
            if w > min_weight:
                inv[term].append((topics[i], w))
    for t in inv:
        inv[t].sort(key=lambda x: x[1], reverse=True)
    return dict(inv)

def load_raw_shards() -> tuple:
    """Merge payloads from all 4 shards, keeping the deepest version per topic."""
    merged: dict = {}
    for shard in ["PFC", "LH", "RH", "HC"]:
        path = os.path.join(BRAIN_DIR, f"{shard}.para")
        with open(path, 'rb') as f:
            data = pickle.load(f)
        for topic, text in data.get("payloads", {}).items():
            if topic not in merged or len(text) > len(merged[topic]):
                merged[topic] = text
    return merged

# ===================== REGION TRAINERS =====================

def train_LH(topics: list, payloads: dict) -> dict:
    """
    LEFT HEMISPHERE: Linguistic Precision Engine
    Trains on the FULL text of each topic but applies a precision multiplier
    to tokens appearing in definitional sentences. No filtering — full indexing.
    """
    print("[LH] Training Linguistic Precision Engine...")
    # Define definitional markers statistically (most common phrase anchors for definitions)
    definition_markers = ["is a", "refers to", "defined as", "means", "is the", "is an",
                          "can be", "consists of", "involves", "represents", "describes"]
    all_tf_boosted = []
    for topic in topics:
        text = payloads[topic]
        sentences = text.split(".")
        base_tf = build_tf(tokenize(text))
        # Identify tokens in definition sentences and apply a 2x precision boost
        def_tokens = set()
        for s in sentences:
            if any(m in s.lower() for m in definition_markers):
                def_tokens.update(tokenize(s))
        # Boost definition tokens — emergent linguistic prioritization
        boosted = {w: (v * 2.0 if w in def_tokens else v) for w, v in base_tf.items()}
        all_tf_boosted.append(boosted)

    idf = build_idf(all_tf_boosted)
    tfidf = [build_tfidf(tf, idf) for tf in all_tf_boosted]
    inv_index = build_inverted_index(tfidf, topics)

    return {"region": "LH", "topics": topics, "idf": idf,
            "tfidf_matrix": tfidf, "inverted_index": inv_index,
            "payloads": {t: payloads[t] for t in topics}}


def train_RH(topics: list, payloads: dict) -> dict:
    """
    RIGHT HEMISPHERE: Conceptual Entropy Engine
    Weights rare/unusual words more heavily — promotes lateral, creative associations
    between unlike topics. Uses inverse document frequency as the primary score.
    """
    print("[RH] Training Conceptual Entropy Engine...")
    all_tf = [build_tf(tokenize(payloads[t])) for t in topics]
    idf = build_idf(all_tf)

    # RH bias: amplify weights for high-IDF (rare, conceptually distinct) terms
    rh_tfidf = []
    for tf in all_tf:
        # Strongly weight rare terms — the "creative leap" neurons
        vec = {w: tf[w] * (idf.get(w, 0.0) ** 2) for w in tf}
        rh_tfidf.append(vec)

    inv_index = build_inverted_index(rh_tfidf, topics, min_weight=0.0001)

    return {"region": "RH", "topics": topics, "idf": idf,
            "tfidf_matrix": rh_tfidf, "inverted_index": inv_index,
            "payloads": {t: payloads[t] for t in topics}}


def train_PFC(topics: list, payloads: dict) -> dict:
    """
    PREFRONTAL_CORTEX: Analytical Synthesis Engine
    Learns to identify structural logic. Scores sentences by relative complexity
    (length vs average) and clause density. Stores the top analytical fragments.
    """
    print("[PFC] Training Analytical Synthesis Engine...")
    pfc_docs = {}
    for topic in topics:
        text = payloads[topic]
        # Calculate mean length for this topic to be adaptive (not hardcoded)
        all_sents = [s.strip() for s in text.split(".") if len(s.strip()) > 10]
        if not all_sents: 
            pfc_docs[topic] = text[:2000]
            continue
            
        mean_len = sum(len(s) for s in all_sents) / len(all_sents)
        # Threshold is relative: sentences longer than mean carry more structure
        target_sents = [s for s in all_sents if len(s) > mean_len]
        
        # Complexity = (word count × clause markers) - (digit density penalty)
        def complexity(s):
            # Ignore sentences that are mostly numbers (likely an index)
            digit_count = sum(c.isdigit() for c in s)
            if digit_count > len(s) * 0.1:
                return -1000
            
            # Penalize very short or very repetitive sentences
            words = s.split()
            if len(words) < 8: return -500
            
            cl_markers = sum(1 for m in [", ", " and ", " but ", " however ", " therefore ", " because "] if m in s)
            return len(words) + (cl_markers * 10)
            
        target_sents.sort(key=complexity, reverse=True)
        # Keep only segments with positive complexity (actual prose)
        valid_sents = [s for s in target_sents if complexity(s) > 0]
        pfc_docs[topic] = ". ".join(valid_sents[:50]) + "."

    all_tf = [build_tf(tokenize(pfc_docs[t])) for t in topics]
    idf = build_idf(all_tf)
    tfidf = [build_tfidf(tf, idf) for tf in all_tf]
    inv_index = build_inverted_index(tfidf, topics)

    return {"region": "PFC", "topics": topics, "idf": idf,
            "tfidf_matrix": tfidf, "inverted_index": inv_index, "payloads": pfc_docs}


def train_HC(topics: list, payloads: dict) -> dict:
    """
    HIPPOCAMPUS: Associative Memory Index
    Builds bi-directional topic association weights — if topic A and topic B share many
    rare terms, they are strongly associated and can be recalled together (episodic memory).
    """
    print("[HC] Training Associative Memory Index...")
    all_tf = [build_tf(tokenize(payloads[t])) for t in topics]
    idf = build_idf(all_tf)
    tfidf = [build_tfidf(tf, idf) for tf in all_tf]

    # Build topic-to-topic association map (episodic memory connections)
    topic_top_terms: dict = {}
    for i, vec in enumerate(tfidf):
        # Keep the 20 most weighted terms per topic as its "memory signature"
        top = sorted(vec.items(), key=lambda x: x[1], reverse=True)[:20]
        topic_top_terms[topics[i]] = set(t for t, _ in top)

    associations: dict = defaultdict(list)
    for i, topic_a in enumerate(topics):
        for j, topic_b in enumerate(topics):
            if i == j: continue
            # Association strength = shared memory signatures
            shared = topic_top_terms[topic_a].intersection(topic_top_terms[topic_b])
            if len(shared) >= 3:
                associations[topic_a].append((topic_b, len(shared)))
        if associations[topic_a]:
            associations[topic_a].sort(key=lambda x: x[1], reverse=True)

    inv_index = build_inverted_index(tfidf, topics)

    return {"region": "HC", "topics": topics, "idf": idf,
            "tfidf_matrix": tfidf, "inverted_index": inv_index,
            "associations": dict(associations),
            "payloads": {t: payloads[t] for t in topics}}


# ===================== ENTRY POINT =====================

def train_all():
    print("=" * 60)
    print("PARADOX SOVEREIGN BRAIN TRAINER — NEUROLOGICAL MODE")
    print("=" * 60)

    payloads = load_raw_shards()
    topics = sorted(payloads.keys())
    print(f"[TRAINER] Loaded {len(topics)} unique topics from all shards.\n")

    regions = {
        "LH":  train_LH(topics, payloads),
        "RH":  train_RH(topics, payloads),
        "PFC": train_PFC(topics, payloads),
        "HC":  train_HC(topics, payloads),
    }

    # Save each region as its own trained shard
    for region_name, region_data in regions.items():
        out_path = os.path.join(BRAIN_DIR, f"{region_name}_trained.pkl")
        with open(out_path, 'wb') as f:
            pickle.dump(region_data, f)
        size_kb = os.path.getsize(out_path) / 1024
        inv_size = len(region_data.get("inverted_index", {}))
        print(f"  [{region_name}] Saved -> {out_path} ({size_kb:.0f} KB | {inv_size} index terms)")

    print("\n[TRAINER] All 4 neurological regions trained and saved.")
    print("[TRAINER] Paradox now has a fully trained, human-architecture brain.")


if __name__ == "__main__":
    train_all()

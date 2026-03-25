import os
import sys
import pickle

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def paradox_brain_audit():
    print("="*60)
    print(">>> PARADOX: SOVEREIGN BRAIN AUDIT (FIDELITY CHECK) <<<")
    print("="*60)

    brain_dir = "paradox_brain"
    if not os.path.exists(brain_dir):
        print("[!] Error: No brain shards found. Run training first.")
        return

    expected_facets = 64
    shards = ["LH", "RH", "PFC", "HC"]
    
    audit_passed = True
    for shard in shards:
        path = os.path.join(brain_dir, f"{shard}.para")
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
                
            print(f"[*] Analyzing Shard: [{shard}.para] ...")
            for topic, vector in data.items():
                actual_facets = len(vector)
                if actual_facets != expected_facets:
                    print(f"  [FAILURE]: Topic '{topic}' has {actual_facets} facets. Expected {expected_facets}.")
                    audit_passed = False
                else:
                    print(f"  [OK]: Topic '{topic}' -> {actual_facets} facets (Aligned).")
        else:
            print(f"  [MISSING]: Shard {shard}.para not found.")
            audit_passed = False

    print("\n" + "="*60)
    if audit_passed:
        print("--- PARADOX BRAIN AUDIT: 100% FIDELITY PASSED ---")
        print("--- All Shards Bit-Aligned to 64-Facets. ---")
    else:
        print("--- PARADOX BRAIN AUDIT: FAILED (Precision Decay Detected) ---")
    print("="*60)

if __name__ == "__main__":
    paradox_brain_audit()

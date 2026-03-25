import pickle
import os

def paradox_shard_deep_audit():
    print("="*60)
    print(">>> PARADOX: MENTAL RESIDENCY AUDIT (SHARD LEVEL) <<<")
    print("="*60)

    shards = ["LH.para", "RH.para", "PFC.para", "HC.para"]
    
    for shard in shards:
        path = os.path.join("paradox_brain", shard)
        if not os.path.exists(path):
            print(f"[!] SHARD MISSING: {shard}")
            continue
            
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                vectors = data.get("vectors", {})
                payloads = data.get("payloads", {})
                
                print(f"[*] Shard [{shard}]:")
                print(f"    - Topics: {len(vectors)}")
                print(f"    - Payloads: {len(payloads)}")
                
                # Check for Greene Manifold
                greene = "The Laws of Human Nature (Robert Greene)"
                if greene in vectors:
                    print(f"    - [FOUND]: Greene Strategy Manifold.")
                    text = payloads.get(greene, "")
                    print(f"    - [PAYLOAD SCAN]: {len(text)} chars.")
                    
                    # Fuzzy match for interrogation keywords
                    keywords = ["narcissism", "irrationality", "envy", "compulsive"]
                    for kw in keywords:
                        if kw in text.lower():
                            print(f"      [OK]: Token '{kw}' present in memory.")
                        else:
                            print(f"      [WARNING]: Token '{kw}' NOT FOUND in this shard payload.")
                else:
                    print(f"    - [NOT FOUND]: Greene Strategy Manifold (Search names: {list(vectors.keys())[:3]}...)")
                    
        except Exception as e:
            print(f"[!] Error reading {shard}: {e}")

    print("\n" + "="*60)
    print("--- PARADOX SHARD AUDIT: COMPLETE ---")

if __name__ == "__main__":
    paradox_shard_deep_audit()

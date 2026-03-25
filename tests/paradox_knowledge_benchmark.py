import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_benchmark():
    print("="*60)
    print(">>> PARADOX: SOVEREIGN KNOWLEDGE BENCHMARK <<<")
    print("="*60)

    # 1. Initialize Substrate & Shards
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. Test Suites (Verified Knowledge from Audit)
    tests = [
        {"prompt": "Tell me about Mathematics.", "target_shard": "LH", "expected": True},
        {"prompt": "What is the study of Aesthetics?", "target_shard": "RH", "expected": True},
        {"prompt": "Explain Grand strategy.", "target_shard": "PFC", "expected": True},
        {"prompt": "The laws of the fictional city of Avalon.", "target_shard": "NONE", "expected": False}
    ]

    # 3. Execution
    print(f"[*] Memory State: {len(ingestor.knowledge_base['LH'])} topics.")
    
    passed_count = 0
    for i, test in enumerate(tests):
        print(f"\n[TEST {i+1}]: {test['prompt']}")
        is_verified, msg = ingestor.query_fact(test['prompt'])
        
        # Verify against the Truth-Gate expectations
        if is_verified == test['expected']:
            print(f"  [RESULT]: PASSED. Verified correctly as {is_verified}.")
            passed_count += 1
        else:
            print(f"  [RESULT]: FAILED. Logic mismatch (Expected {test['expected']}).")
            
        print(f"  [SIGNAL]: {msg}")

    # 4. Final Evaluation
    print("\n" + "="*60)
    score = (passed_count / len(tests)) * 100
    print(f"--- PARADOX BRAIN BENCHMARK: {score:.2f}% ACCURACY ---")
    if score >= 100:
        print("--- SOVEREIGN TRUTH-GATE: ABSOLUTE (No Hallucinations) ---")
    else:
        print("--- SOVEREIGN TRUTH-GATE: NEEDS REALIGNMENT ---")
    print("="*60)

if __name__ == "__main__":
    paradox_benchmark()

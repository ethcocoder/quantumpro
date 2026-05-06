import pickle
import os

shard_path = r"c:\Users\fitsum.DESKTOP-JDUVJ6V\Downloads\qau_project\paradox_brain\HC.para"
topic = "The Laws of Human Nature (Robert Greene)"

if os.path.exists(shard_path):
    with open(shard_path, "rb") as f:
        data = pickle.load(f)
        payload = data.get("payloads", {}).get(topic, "")
        print(f"[*] Payload Size: {len(payload)} chars")
        
        # Check specific word count
        count = payload.lower().count("irrationality")
        print(f"[*] 'irrationality' count: {count}")
        
        # Find occurrences with context
        start = 0
        for i in range(5):
            idx = payload.lower().find("irrationality", start)
            if idx == -1: break
            print(f"\n[Occurrence {i+1} @ {idx}]:")
            print(f"\"...{payload[idx-100:idx+200]}...\"")
            start = idx + 1
else:
    print("[!] Shard missing.")

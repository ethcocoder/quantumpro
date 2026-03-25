import os
import sys
from pypdf import PdfReader

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion

def paradox_pdf_ingest(pdf_path: str):
    print("="*60)
    print(">>> PARADOX: PDF SEMANTIC INFILTRATION (PSYCHOLOGY) <<<")
    print(f"[*] Target: {os.path.basename(pdf_path)}")
    print("="*60)

    if not os.path.exists(pdf_path):
        print(f"[!] Error: File not found at {pdf_path}")
        return

    # 1. Initialize Paradox Substrate
    qvs = QVS(use_hal=True)
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)

    # 2. Extract Text (Full Infiltration)
    print("[*] Extracting Human Nature Manifold...")
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        print(f"[+] Extracted {len(full_text)} semantic bits.")
        
        # 3. Router-to-Substrate: Multi-Shard Fidelity
        # Psychology goes to PFC (Decision) and RH (Intuition)
        topic_name = "The Laws of Human Nature (Robert Greene)"
        
        # A. LH (Logic Hemisphere): Pure Fact Structure
        hash_vec = [float(ord(c)) / 256.0 for c in full_text[:64]]
        if len(hash_vec) < 64: hash_vec += [0.0] * (64 - len(hash_vec))
        
        ingestor.knowledge_base["LH"][topic_name] = hash_vec
        ingestor.payload_base["LH"][topic_name] = full_text[:100000] # Full Text Limit check
        paradox.amplify_region("LH", hash_vec)
        
        # B. RH (Intuition/Affect): Behavioral Pattern
        nuance_vec = [v * 1.5 for v in hash_vec]
        ingestor.knowledge_base["RH"][topic_name] = nuance_vec
        ingestor.payload_base["RH"][topic_name] = full_text[:100000]
        paradox.amplify_region("RH", nuance_vec)
        
        # C. PFC (Decision/Strategy): MASTER STRATEGY
        ingestor.knowledge_base["PFC"][topic_name] = hash_vec
        ingestor.payload_base["PFC"][topic_name] = full_text[:200000] # Deep PFC residency
        paradox.amplify_region("PFC", hash_vec)
        
        # D. HC (Persistent Experience): RAW PAYLOAD
        ingestor.knowledge_base["HC"][topic_name] = hash_vec
        ingestor.payload_base["HC"][topic_name] = full_text
        paradox.amplify_region("HC", hash_vec)
        
        # 4. Global Save & Lock
        ingestor.save_sharded_brain()
        
        # Final Density Scan
        final_size_mb = sum([os.path.getsize(os.path.join("paradox_brain", f)) for f in os.listdir("paradox_brain") if f.endswith(".para")]) / (1024*1024)
        
        print("\n" + "="*60)
        print("--- PARADOX PDF INGEST: COMPLETE ---")
        print(f"--- Brain State: Master Psychology Manifold locked. ---")
        print(f"--- Current Sovereign Brain Density: {final_size_mb:.2f} MB. ---")
        print("="*60)

    except Exception as e:
        print(f"[!] Error during ingestion: {e}")

if __name__ == "__main__":
    target_pdf = r"c:\Users\fitsum.DESKTOP-JDUVJ6V\Downloads\qau_project\data\phychology\_OceanofPDF.com_Laws_of_human_nature_-_Robert_Greene.pdf"
    paradox_pdf_ingest(target_pdf)

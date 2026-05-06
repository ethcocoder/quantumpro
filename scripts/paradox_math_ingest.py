import os
import sys
from pypdf import PdfReader

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qau_qvs.ai.paradox import ParadoxEngine
from qau_qvs.core.qvs import QVS
from qau_qvs.ai.wikipedia_ingest import WikipediaSubstrateIngestion
from qau_qvs.ai.manifold_scrubber import ManifoldScrubber

def paradox_math_ingestion(pdf_path: str):
    print("="*60)
    print(">>> PARADOX: MATHEMATICAL MANIFOLD EXPANSION <<<")
    print(f"[!] Target: {os.path.basename(pdf_path)}")
    print("="*60)
    
    # 1. Initialize Paradox Substrate
    qvs = QVS()
    paradox = ParadoxEngine(qvs)
    ingestor = WikipediaSubstrateIngestion(paradox)
    scrubber = ManifoldScrubber()
    
    if not os.path.exists(pdf_path):
        print(f"[!] ERROR: PDF Path {pdf_path} NOT FOUND.")
        return
        
    # 2. Sequential PDF Absorption
    print("[*] Opening Sullivan's Math Substrate...")
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"[*] Manifold Size: {total_pages} logical planes found.")
    
    math_payload = ""
    for i in range(total_pages):
        page_text = reader.pages[i].extract_text()
        if page_text:
            math_payload += page_text + "\n"
        if i % 50 == 0:
            print(f"  > Infiltrating Plane {i}/{total_pages}...")
            
    # 3. Phase XXXVIII: Clean-Sweep Sanitization
    print("[*] Sanitizing Mathematical Manifold...")
    cleaned_payload = scrubber.clean_payload(math_payload)
    
    # 4. Phase XXIII: Neuro-Anatomical Infiltration (LH/HC)
    topic_name = "College Algebra & Trigonometry (Sullivan)"
    print(f"[*] Saturating LH (Logic) and HC (Memory) shards with math wisdom...")
    
    # This automatically shards, amplifies, and saves
    ingestor.ingest_manifold(topic_name, cleaned_payload)
    
    print("\n" + "="*60)
    print("--- MATHEMATICAL MANIFOLD: SYNC'D ---")
    print(f"[*] Verification: Topic '{topic_name}' is now PERSISTENT.")
    print("="*60)

if __name__ == "__main__":
    pdf_path = r"c:\Users\fitsum.DESKTOP-JDUVJ6V\Downloads\qau_project\data\maths\_OceanofPDF.com_Sullivan_Algebra_and_Trigonometry_9th_Edition_-_Michael_Sullivan.pdf"
    paradox_math_ingestion(pdf_path)

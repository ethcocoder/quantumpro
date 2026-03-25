import os
import subprocess
import numpy as np
from qau_qvs.core.qvs import QVS
from qau_qvs.fields.cosmology import QuantumCosmology
from qau_qvs.fields.quantum_fields import QuantumCryptography

def run_vortex():
    print("="*60)
    print(">>> VORTEX UNIFICATION: Launching QAU Phase V Substrate <<<")
    print("="*60)

    # 1. Verify C++ AetherCore (Performance Layer)
    print("\n[*] [STEP 1] Verifying C++ AetherCore Kernel...")
    if os.path.exists("./test_aether.exe") or os.path.exists("./test_aether"):
        try:
            exe = "./test_aether.exe" if os.name == 'nt' else "./test_aether"
            result = subprocess.run([exe], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"[!] Warning: C++ Core run failed: {e}")
    else:
        print("[!] Warning: C++ binary not found. Run 'g++ -std=c++17 -o test_aether ...'")

    # 2. Launch QVS Operating System (Logic Layer)
    print("\n[*] [STEP 2] Initializing QVS v1.2.0 (Logic Substrate)...")
    qvs = QVS(use_hal=True) # Enabling Phase V HAL
    psi_id = qvs.create_asc(size=5)
    print(f"[+] QVS Engine Active. Target ASC: {psi_id}")

    # 3. Simulate Universal Inflation (Cosmoloy Layer)
    print("\n[*] [STEP 3] Modeling Cosmological Inflationary Multiplicity...")
    qc = QuantumCosmology(qvs)
    universe_seed = qc.cosmic_inflation_collapse()
    print(f"[+] Universe Seed Resolved: {universe_seed}")

    # 4. Generate Sovereign Entangled Keys (Mesh Layer)
    print("\n[*] [STEP 4] Forging E91 Entangled Key Mesh...")
    crypto = QuantumCryptography(qvs)
    alice_k, bob_k = crypto.e91_key_exchange()
    print(f"[+] Alice Master Key: {alice_k}")
    print(f"[+] Bob   Master Key: {bob_k}")
    print("[+] Status: Sovereign Entanglement Locked.")

    # 5. Export to Hardware Abstraction Layer (HAL)
    print("\n[*] [STEP 5] Exporting Substrate to OpenQASM 3.0 (HAL)...")
    if qvs.hal:
        qasm_output = qvs.hal.export_qasm()
        print("-" * 30)
        print(qasm_output)
        print("-" * 30)
    
    print("\n" + "="*60)
    print("--- QAU SUBSTRATE STATUS: SOVEREIGN ---")
    print("="*60)

if __name__ == "__main__":
    run_vortex()

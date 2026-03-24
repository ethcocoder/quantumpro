import sys
import os
import numpy as np
import unittest

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qau_qvs.core.qvs import QVS
from qau_qvs.core.asc import ASC
from qau_qvs.core.ncb import NCB
from qau_qvs.fields.quantum_fields import (
    QuantumAlgorithms, QuantumErrorCorrection, QuantumSimulation,
    QuantumCryptography, QuantumFieldTheory, QuantumMachineLearning
)

class TestQVS(unittest.TestCase):
    def setUp(self):
        self.qvs = QVS()

    def test_superposition(self):
        """Test ASC superposition (ASC primitive)."""
        psi_id = self.qvs.create_asc(size=1)
        # Create uniform superposition of |0> and |1>
        self.qvs.SUPERPOSE(psi_id, [(0,), (1,)])
        asc = self.qvs.get_asc(psi_id)
        
        # Check weights (1/√2)^2 = 0.5
        self.assertAlmostEqual(abs(asc.amplitudes[(0,)])**2, 0.5)
        self.assertAlmostEqual(abs(asc.amplitudes[(1,)])**2, 0.5)

    def test_interference(self):
        """Test RPW/WEAVE interference (RPW primitive)."""
        psi_id = self.qvs.create_asc(size=1)
        # Start with |1> only
        self.qvs.SUPERPOSE(psi_id, [(1,)])
        
        # Apply WEAVE with PI/2 phase
        self.qvs.WEAVE(psi_id, (0,), np.pi/2)
        asc = self.qvs.get_asc(psi_id)
        
        # |1> should now have phase e^(i*pi/2) = i
        self.assertAlmostEqual(asc.amplitudes[(1,)].real, 0, places=10)
        self.assertAlmostEqual(asc.amplitudes[(1,)].imag, 1, places=10)

    def test_entanglement(self):
        """Test NCB/BOND entanglement (NCB primitive)."""
        alice_id = self.qvs.create_asc(size=1)
        bob_id = self.qvs.create_asc(size=1)
        
        # Bond Alice and Bob into a Bell state
        bonded_id = self.qvs.BOND(alice_id, bob_id, "bell")
        asc = self.qvs.get_asc(bonded_id)
        
        # Check if we have (0,0) and (1,1) with equal probability
        self.assertIn((0, 0), asc.amplitudes)
        self.assertIn((1, 1), asc.amplitudes)
        self.assertAlmostEqual(abs(asc.amplitudes[(0, 0)])**2, 0.5)
        self.assertAlmostEqual(abs(asc.amplitudes[(1, 1)])**2, 0.5)
        
        # Test entanglement entropy
        entropy = NCB.get_entanglement_entropy(asc, partition_idx=1)
        self.assertAlmostEqual(entropy, 1.0) # Bell state should have 1 bit of entropy

    def test_density_matrix_and_fidelity(self):
        """Test density matrix calculation and state fidelity."""
        # Create |0>
        asc0 = ASC(size=1)
        rho0 = asc0.get_density_matrix()
        # Should be [[1, 0], [0, 0]]
        self.assertTrue(np.allclose(rho0, [[1, 0], [0, 0]]))
        
        # Create |1>
        asc1 = ASC({(1,): 1.0+0j}, size=1)
        self.assertAlmostEqual(asc0.fidelity(asc1), 0.0) # Orthogonal
        self.assertAlmostEqual(asc0.fidelity(asc0), 1.0) # Identical

    def test_quantum_fields(self):
        """Test the higher-layer quantum fields with the new API."""
        # 1. Algorithms
        alg = QuantumAlgorithms(self.qvs)
        res_alg = alg.shor_factorization_pattern()
        self.assertIsInstance(res_alg, tuple)
        
        # 2. Simulation
        sim = QuantumSimulation(self.qvs)
        sim_id = sim.evolve_ising_hamiltonian(time=np.pi/4)
        self.assertIn(sim_id, self.qvs.ascs)
        
        # 3. Cryptography
        crypto = QuantumCryptography(self.qvs)
        alice_key, bob_key = crypto.e91_key_exchange()
        self.assertEqual(alice_key, bob_key) # Correlations must hold
        
        # 4. QML
        qml = QuantumMachineLearning(self.qvs)
        prob_11 = qml.variational_classifier_step([np.pi/4])
        self.assertIsInstance(prob_11, float)
        self.assertGreaterEqual(prob_11, 0.0)

    def test_grover_pattern(self):
        """Test Grover's pattern specifically."""
        alg = QuantumAlgorithms(self.qvs)
        target = (1, 0, 1) # Target state in 3rd qubit
        res = alg.grover_search_pattern(target, iterations=2)
        self.assertEqual(res, target) # With 2 iterations on 3 bits, Grover is very high prob

    def test_strong_quantum_scenario(self):
        """GHZ state preparation and measurement."""
        # Create 3 ASCs and bond them
        a = self.qvs.create_asc(size=1)
        b = self.qvs.create_asc(size=1)
        c = self.qvs.create_asc(size=1)
        
        ab = self.qvs.BOND(a, b, "bell")
        # In this implementation, GHZ is a specialized bond
        abc = self.qvs.BOND(ab, c, "ghz")
        
        res = self.qvs.COLLAPSE(abc)
        self.assertIn(res, [(0, 0, 0), (1, 1, 1)])

if __name__ == '__main__':
    unittest.main()

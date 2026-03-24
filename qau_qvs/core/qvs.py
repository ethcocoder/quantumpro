import numpy as np
import random
from typing import Dict, Tuple, List, Optional, Any, Union
from .asc import ASC
from .rpw import RPW
from .ncb import NCB

class QVS:
    """
    Quantum Virtual Substrate (QVS)
    ================================
    The foundational OPERATING SYSTEM LAYER for the QAU.
    
    The QVS executes the Three Primordials natively on silicon-based data 
    structures. It manages the lifecycle of ASCs, performs interference 
    via RPW weaving, and handles non-local coupling via NCB bonds.
    """
    
    def __init__(self):
        self.ascs: Dict[str, ASC] = {} # mapping ID to ASC content
        self.next_id = 0
        self.instruction_history: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Resource Management
    # ------------------------------------------------------------------

    def create_asc(self, basis_states: Optional[Dict[Tuple, complex]] = None, size: int = 1) -> str:
        """Create a new ASC (Amplitude Superposition Cell) with the given initial state."""
        asc_id = f"ASC_{self.next_id}"
        self.next_id += 1
        self.ascs[asc_id] = ASC(basis_states, size)
        return asc_id

    def delete_asc(self, asc_id: str):
        """Release ASC resources."""
        if asc_id in self.ascs:
            del self.ascs[asc_id]

    def get_asc(self, asc_id: str) -> ASC:
        """Retrieve the ASC by its ID."""
        if asc_id not in self.ascs:
            raise KeyError(f"ASC {asc_id} not found in QVS registry.")
        return self.ascs[asc_id]

    # ------------------------------------------------------------------
    # The QVS Instruction Set (QASM-R)
    # ------------------------------------------------------------------

    def SUPERPOSE(self, asc_id: str, basis_states: List[Tuple[int, ...]]) -> str:
        """
        SUPERPOSE(ASC_id, basis_states[]) - Initialize MULTIPLICITY.
        Creates a uniform superposition of the given basis states.
        """
        asc = self.get_asc(asc_id)
        weight = 1.0 / np.sqrt(len(basis_states))
        asc.amplitudes = {tuple(state): complex(weight) for state in basis_states}
        
        # Log this instruction
        self.instruction_history.append({"op": "SUPERPOSE", "id": asc_id, "size": len(basis_states)})
        return asc_id

    def WEAVE(self, asc_id: str, target_bits: Optional[Tuple[int, ...]] = None, phase_angle: float = 0.0) -> str:
        """
        WEAVE(ASC_id, target_bits[], phase_angle) - INTERFERENCE pattern.
        Applies a relative phase shift to basis states that have bits set.
        """
        asc = self.get_asc(asc_id)
        # If no target bits, we default to the first bit (0)
        bits = target_bits if target_bits is not None else (0,)
        
        # We apply the RPW (Relative Phase Weave)
        RPW.weave(asc, bits, {1: phase_angle})
        
        self.instruction_history.append({"op": "WEAVE", "id": asc_id, "phase": phase_angle})
        return asc_id

    def BOND(self, asc_id_a: str, asc_id_b: str, bond_type: str = "bell") -> str:
        """
        BOND(ASC_id_A, ASC_id_B, bond_type) - INFOMATIONAL CONSTRAINT (Entanglement).
        Fuses two ASCs into a single bonded non-local computational object.
        """
        asc_a = self.get_asc(asc_id_a)
        asc_b = self.get_asc(asc_id_b)
        
        # Using the NCB to create the joint bonded state
        bonded_asc = NCB.bond(asc_a, asc_b, bond_type)
        
        # Remove old fragments and create new joint ID
        self.delete_asc(asc_id_a)
        self.delete_asc(asc_id_b)
        
        new_id = self.create_asc(bonded_asc.amplitudes, bonded_asc.size)
        self.instruction_history.append({"op": "BOND", "ids": [asc_id_a, asc_id_b], "type": bond_type, "new_id": new_id})
        return new_id

    def ROTATE(self, asc_id: str, unitary: np.ndarray) -> str:
        """
        ROTATE(ASC_id, unitary_matrix) - Unitary transformation.
        Applies a complex rotation in Hilbert space to the ASC.
        In the QVS, this is an optimized sparse matrix-vector product.
        """
        asc = self.get_asc(asc_id)
        
        # For simulation, we perform the full dot product but keep it sparse
        vec = asc.get_state_vector()
        new_vec = np.dot(unitary, vec)
        
        # Sparse reconstruction (Pruning)
        new_amplitudes = {}
        for i in range(len(new_vec)):
            if abs(new_vec[i]) > 1e-12:
                # Convert flat index i back to N-tuple bit representation
                bits = tuple((i >> (asc.size - 1 - j)) & 1 for j in range(asc.size))
                new_amplitudes[bits] = complex(new_vec[i])
        
        asc.amplitudes = new_amplitudes
        
        self.instruction_history.append({"op": "ROTATE", "id": asc_id})
        return asc_id

    def TENSOR(self, asc_id_a: str, asc_id_b: str) -> str:
        """
        TENSOR(ASC_id_A, ASC_id_B) - State Space expansion.
        Combines two uncorrelated ASCs into a single tensor product state.
        """
        asc_a = self.get_asc(asc_id_a)
        asc_b = self.get_asc(asc_id_b)
        
        new_size = asc_a.size + asc_b.size
        new_amplitudes = {}
        for (sa, wa) in asc_a.amplitudes.items():
            for (sb, wb) in asc_b.amplitudes.items():
                new_amplitudes[sa + sb] = wa * wb
        
        self.delete_asc(asc_id_a)
        self.delete_asc(asc_id_b)
        
        new_id = self.create_asc(new_amplitudes, new_size)
        self.instruction_history.append({"op": "TENSOR", "ids": [asc_id_a, asc_id_b], "new_id": new_id})
        return new_id

    def COLLAPSE(self, asc_id: str) -> Tuple[int, ...]:
        """
        COLLAPSE(ASC_id) - Measurement.
        Forces the QVS to resolve the multiplicity into a single classical outcome.
        This obeys the probability distribution of the ASC amplitudes.
        """
        asc = self.get_asc(asc_id)
        states = list(asc.amplitudes.keys())
        probabilities = [abs(asc.amplitudes[s])**2 for s in states]
        
        # Probability normalization check (due to floating point drift)
        total_p = sum(probabilities)
        probabilities = [p/total_p for p in probabilities]
        
        # Statistical selection (Monte Carlo)
        idx = np.random.choice(len(states), p=probabilities)
        outcome = states[idx]
        
        # Post-collapse: force ASC to pure classical result
        asc.amplitudes = {outcome: 1.0 + 0j}
        
        self.instruction_history.append({"op": "COLLAPSE", "id": asc_id, "outcome": outcome})
        return outcome

    # ------------------------------------------------------------------
    # Advanced: JIT Synthesis
    # ------------------------------------------------------------------

    def synthesize_unitary(self, instructions: List[np.ndarray]) -> np.ndarray:
        """Fuses multiple rotation unitaries into a single optimized instruction."""
        # Start with identity
        dim = instructions[0].shape[0]
        combined = np.eye(dim, dtype=complex)
        for U in instructions:
            combined = np.dot(U, combined)
        return combined

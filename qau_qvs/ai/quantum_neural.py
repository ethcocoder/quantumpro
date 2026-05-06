import cmath
import math
import random

class QubitNeuron:
    """
    A foundational Qubit element representing a state in complex probability space,
    rather than a deterministic float vector.
    """
    def __init__(self):
        # Base state |0>
        self.state = complex(1, 0)

class QuantumLayer:
    """
    A layer where weights are simulated as quantum entanglement ties (complex numbers).
    """
    def __init__(self, input_size: int, output_size: int):
        self.input_size = input_size
        self.output_size = output_size
        # Complex weights representing entangled phase/magnitude ties
        self.weights = [[complex(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) 
                        for _ in range(input_size)] for _ in range(output_size)]
        self.biases = [complex(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)) for _ in range(output_size)]

    def phase_shift_activation(self, z: complex) -> complex:
        """
        Quantum Non-Linearity: Instead of a classical ReLU, this introduces
        constructive/destructive interference by rotating the probability wave's phase
        if the structural magnitude is high enough.
        """
        mag = abs(z)
        phase = cmath.phase(z)
        
        if mag > 1.0:
            # Rotate phase non-linearly to simulate a phase-gate shift
            new_phase = phase + (math.pi / 4.0)
            return cmath.rect(mag, new_phase)
        else:
            # Destructive Dampening
            return cmath.rect(mag * 0.5, phase)

    def forward(self, inputs: list[complex]) -> list[complex]:
        outputs = []
        for i in range(self.output_size):
            z = self.biases[i]
            for j in range(self.input_size):
                z += inputs[j] * self.weights[i][j]
            activation = self.phase_shift_activation(z)
            outputs.append(activation)
        return outputs

class SovereignQuantumNetwork:
    """
    Sovereign Quantum Deep Learning Core
    Translates classical text entropies into a multidimensional probability wave,
    processes it via entanglement, and collapses it into a final Truth Vector.
    """
    def __init__(self, input_features: int, hidden_size: int = 4):
        self.hidden_layer = QuantumLayer(input_features, hidden_size)
        self.output_layer = QuantumLayer(hidden_size, 1)

    def hadamard_gate(self, classical_value: float) -> complex:
        """
        Hadamard equivalent mapping: throws a purely deterministic classical variable
        into a superposition probability wave state.
        """
        phase = random.uniform(0, 2 * math.pi)
        mag = min(1.0, max(0.0, classical_value)) # Enforce normalized magnitude
        return cmath.rect(mag, phase)
        
    def collapse_wave(self, z: complex) -> float:
        """
        Observation equivalent: Collapses the complex superposition state into a single 
        deterministic classical variable denoting 'Truth Confidence'.
        """
        mag = abs(z)
        # Sigmoid squashing against the Euclidean norm of the complex output
        return 1.0 / (1.0 + math.exp(-mag))

    def structural_filter(self, vector: list[float]) -> list[float]:
        """
        PRE-TRAINING COGNITIVE FILTER: 
        Ensures pure classical data before Hadamard conversion. Detects and dampens 
        garbage noise, NaN anomalies, and extreme outliers.
        """
        clean_vector = []
        for v in vector:
            if math.isnan(v) or math.isinf(v):
                clean_vector.append(0.0)
            else:
                clean_vector.append(v)
                
        # Calculate statistical entropy to identify outlier spikes
        if len(clean_vector) > 0:
            mean = sum(clean_vector) / len(clean_vector)
            variance = sum((x - mean) ** 2 for x in clean_vector) / len(clean_vector)
            std_dev = math.sqrt(variance)
            
            # Dampen outliers > 3 std deviations
            filtered = []
            for v in clean_vector:
                if std_dev > 0 and abs(v - mean) > 3 * std_dev:
                    # Apply logarithmic dampening to bring it within the 3-sigma band
                    damped = mean + math.copysign(3 * std_dev + math.log(1 + abs(v - mean - 3*std_dev)), v - mean)
                    filtered.append(damped)
                else:
                    filtered.append(v)
            return filtered
        return clean_vector

    def evaluate_cognitive_resonance(self, input_vector: list[float]) -> float:
        """
        The central Quantum Forward Pass.
        """
        # 0. Cognitive Purification
        clean_vector = self.structural_filter(input_vector)
        
        # 1. Hadamard Transformation
        quantum_inputs = [self.hadamard_gate(val) for val in clean_vector]
        
        # 2. Deep Entanglement Propagation
        h_out = self.hidden_layer.forward(quantum_inputs)
        final_state = self.output_layer.forward(h_out)[0]
        
        # 3. Wave Function Collapse
        confidence = self.collapse_wave(final_state)
        return confidence
        
    def _update_layer_gradients(self, layer, filtered_inputs, target, learning_rate):
        """
        Executes discretional gradient approximation on a complex layer by independently
        nudging magnitude and phase to compute the partial derivatives of the truth collapse.
        """
        epsilon = 0.001
        
        # Weights
        for i in range(layer.output_size):
            for j in range(layer.input_size):
                orig_w = layer.weights[i][j]
                
                # Base loss
                base_loss = (self.evaluate_cognitive_resonance(filtered_inputs) - target) ** 2
                
                # Nudge Magnitude
                layer.weights[i][j] = cmath.rect(abs(orig_w) + epsilon, cmath.phase(orig_w))
                mag_loss = (self.evaluate_cognitive_resonance(filtered_inputs) - target) ** 2
                grad_mag = (mag_loss - base_loss) / epsilon
                
                # Nudge Phase
                layer.weights[i][j] = cmath.rect(abs(orig_w), cmath.phase(orig_w) + epsilon)
                phase_loss = (self.evaluate_cognitive_resonance(filtered_inputs) - target) ** 2
                grad_phase = (phase_loss - base_loss) / epsilon
                
                # Gradient Descent Step (Restore and Update)
                new_mag = max(0.001, abs(orig_w) - learning_rate * grad_mag)
                new_phase = cmath.phase(orig_w) - learning_rate * grad_phase
                layer.weights[i][j] = cmath.rect(new_mag, new_phase)

        # Biases
        for i in range(layer.output_size):
            orig_b = layer.biases[i]
            base_loss = (self.evaluate_cognitive_resonance(filtered_inputs) - target) ** 2
            
            # Nudge Magnitude
            layer.biases[i] = cmath.rect(abs(orig_b) + epsilon, cmath.phase(orig_b))
            mag_loss = (self.evaluate_cognitive_resonance(filtered_inputs) - target) ** 2
            grad_mag = (mag_loss - base_loss) / epsilon
            
            # Nudge Phase
            layer.biases[i] = cmath.rect(abs(orig_b), cmath.phase(orig_b) + epsilon)
            phase_loss = (self.evaluate_cognitive_resonance(filtered_inputs) - target) ** 2
            grad_phase = (phase_loss - base_loss) / epsilon
            
            # Update Bias
            layer.biases[i] = cmath.rect(max(0.001, abs(orig_b) - learning_rate * grad_mag), 
                                         cmath.phase(orig_b) - learning_rate * grad_phase)

    def train_step(self, input_vector: list[float], target_confidence: float, learning_rate: float = 0.05) -> float:
        """
        QUANTUM BACKPROPAGATION:
        Trains the Sovereign Quantum Network by calculating finite-difference approximations for 
        the complex Wirtinger derivatives. Modifies the phase and magnitude of all entangled nodes.
        Returns the initial MSE Loss.
        """
        clean_vector = self.structural_filter(input_vector)
        pred = self.evaluate_cognitive_resonance(clean_vector)
        loss = (pred - target_confidence) ** 2
        
        # Propagate gradients through Output Layer First (simulated Backprop)
        self._update_layer_gradients(self.output_layer, clean_vector, target_confidence, learning_rate)
        # Then Hidden Layer
        self._update_layer_gradients(self.hidden_layer, clean_vector, target_confidence, learning_rate)
        
        return loss

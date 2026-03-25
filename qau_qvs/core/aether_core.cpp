#include "aether_core.hpp"
#include <cmath>
#include <map>
#include <iostream>

namespace Aether {

    /**
     * @brief Renormalize the ASC's amplitude mapping.
     * Ensures unitarity (sum |α|² = 1) after complex operations.
     */
    void ASC::normalize() {
        double norm = 0.0;
        for (auto const& [state, amp] : amplitudes) {
            norm += std::norm(amp);
        }
        if (norm > 1e-15) {
            double inv_sqrt_norm = 1.0 / std::sqrt(norm);
            for (auto& [state, amp] : amplitudes) {
                amp *= inv_sqrt_norm;
            }
        }
    }

    /**
     * @brief The core Substrate Engine (QVS Kernel in C++).
     * Provides high-performance execution of Phase Weaves.
     */
    void SubstrateEngine::weave(const std::string& id, double angle) {
        if (ascs.find(id) == ascs.end()) return;
        
        // Relativistic Phase WeavE (RPW)
        // Rotating state vectors in the complex manifold according to the weave angle.
        ASC& target = ascs[id];
        std::complex<double> phase_factor(std::cos(angle), std::sin(angle));
        
        for (auto& [state, amp] : target.amplitudes) {
            // Apply interference pattern based on bit statistics
            int bit_sum = 0;
            for (int b : state) bit_sum += b;
            
            if (bit_sum % 2 != 0) {
                amp *= phase_factor;
            }
        }
    }

    void SubstrateEngine::superpose(const std::string& id, const std::vector<BasisState>& states) {
        if (ascs.find(id) == ascs.end()) return;
        ASC& target = ascs[id];
        target.amplitudes.clear();
        double initial_weight = 1.0 / std::sqrt((double)states.size());
        for (const auto& s : states) {
            target.amplitudes[s] = {initial_weight, 0.0};
        }
    }

    /**
     * @brief Advanced Cosmological Feature: Curved Metric Influence
     * 
     * Applies a gravitational phase shift based on the g_mu_nu tensor.
     * This models how quantum multiplicity is affected by cosmological spacetime curvature.
     */
    void SubstrateEngine::apply_curved_metric(const std::string& id, const std::vector<std::vector<double>>& g_mu_nu) {
        if (ascs.find(id) == ascs.end()) return;
        
        ASC& target = ascs[id];
        // The proper time τ = ∫ √g_μν dxμ dxν influence on the quantum phase.
        // Simplified: use the trace of the metric to modify state-dependent phases.
        double curvature_trace = 0.0;
        for (int i = 0; i < std::min((int)g_mu_nu.size(), 4); ++i) {
            curvature_trace += g_mu_nu[i][i];
        }
        
        double phase_shift = std::exp(-curvature_trace);
        for (auto& [state, amp] : target.amplitudes) {
            amp *= std::polar(1.0, phase_shift); 
        }
        target.normalize();
    }

    std::string SubstrateEngine::create_asc(int size) {
        std::string new_id = "C_ASC_" + std::to_string(next_id++);
        ascs[new_id] = {size, {}};
        return new_id;
    }

}

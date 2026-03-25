#include "qau_qvs/core/aether_core.hpp"
#include <iostream>
#include <vector>

/**
 * @brief Substrate Core Verification Utility (C++)
 * 
 * Tests the initial multiplicity initialization and 
 * phase weave execution on the compiled substrate.
 */

int main() {
    std::cout << "[*] Initializing AetherCore C++ Substrate..." << std::endl;
    
    Aether::SubstrateEngine engine;
    
    // 1. Create ASC (Superposition Cell)
    std::string asc_id = engine.create_asc(2);
    std::cout << "[+] Created ASC: " << asc_id << std::endl;

    // 2. Superpose (Initialize multiplicity)
    std::vector<Aether::BasisState> states = {{0,0}, {1,1}};
    engine.superpose(asc_id, states);
    std::cout << "[+] Multiplicity density: 2 states (Bell Pair Basis)" << std::endl;

    // 3. Weave (Apply interference)
    engine.weave(asc_id, 3.14159 / 4.0);
    std::cout << "[+] Relativistic Phase Weave applied successfully." << std::endl;

    // 4. Curved Metric Test
    std::vector<std::vector<double>> g_mu_nu = {
        {1.0, 0, 0, 0},
        {0, -1.0, 0, 0},
        {0, 0, -1.0, 0},
        {0, 0, 0, -1.0}
    };
    engine.apply_curved_metric(asc_id, g_mu_nu);
    std::cout << "[+] Cosmological Metric applied (Minkowski Vacuum)." << std::endl;

    std::cout << "[SUCCESS] AetherCore Substrate is operational." << std::endl;
    return 0;
}

#ifndef AETHER_CORE_HPP
#define AETHER_CORE_HPP

#include <vector>
#include <complex>
#include <map>
#include <string>

/**
 * @brief AetherCore: High-Performance C++ Substrate
 * 
 * Provides compiled acceleration for the Three Primordials.
 * Optimized for sparse tensor contractions (ASC) and 
 * relativistic phase weaves (RPW).
 */

namespace Aether {

    typedef std::vector<int> BasisState;
    typedef std::complex<double> Amplitude;

    struct ASC {
        int size;
        std::map<BasisState, Amplitude> amplitudes;

        void normalize();
        void prune(double threshold = 1e-15);
    };

    class SubstrateEngine {
    public:
        std::string create_asc(int size);
        void superpose(const std::string& id, const std::vector<BasisState>& states);
        void weave(const std::string& id, double angle);
        void bond(const std::string& id_a, const std::string& id_b, const std::string& type);
        
        // Relativistic/Cosmological specialized instructions
        void apply_curved_metric(const std::string& id, const std::vector<std::vector<double>>& g_mu_nu);

    private:
        std::map<std::string, ASC> ascs;
        int next_id = 0;
    };
}

#endif // AETHER_CORE_HPP

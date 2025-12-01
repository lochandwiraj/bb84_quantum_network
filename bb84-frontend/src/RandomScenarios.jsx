import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function RandomScenarios() {
  const [loading, setLoading] = useState(false);
  const [qubits, setQubits] = useState(10);
  const [numScenarios, setNumScenarios] = useState(5);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch("http://localhost:5000/api/network/random", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          num_qubits: qubits,
          num_scenarios: numScenarios,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setResults(data.data);
      } else {
        setError(data.error || "Simulation failed");
      }
    } catch (err) {
      setError("Failed to connect to API: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-5xl font-extrabold mb-2 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
          🔐 BB84 Quantum Network Simulator
        </h1>
        <p className="text-gray-300 text-lg">
          Random Multi-Attacker Scenario Analysis
        </p>
      </motion.header>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-4xl mx-auto bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 shadow-2xl border border-white/20"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block font-semibold mb-2 text-cyan-300">
              Number of Qubits: <span className="text-white">{qubits}</span>
            </label>
            <input
              type="range"
              min="1"
              max="20"
              step="1"
              value={qubits}
              onChange={(e) => setQubits(Number(e.target.value))}
              className="w-full accent-cyan-400"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block font-semibold mb-2 text-purple-300">
              Number of Scenarios:{" "}
              <span className="text-white">{numScenarios}</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={numScenarios}
              onChange={(e) => setNumScenarios(Number(e.target.value))}
              className="w-full accent-purple-400"
              disabled={loading}
            />
          </div>
        </div>

        <button
          onClick={runSimulation}
          disabled={loading}
          className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 disabled:from-gray-500 disabled:to-gray-600 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-105 disabled:scale-100 shadow-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Running Simulation...
            </span>
          ) : (
            "🚀 Run Random Scenarios"
          )}
        </button>
      </motion.div>

      {/* Error Message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="max-w-4xl mx-auto bg-red-500/20 border border-red-500 rounded-xl p-4 mb-8"
          >
            <p className="text-red-200">❌ {error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="max-w-7xl mx-auto space-y-8"
          >
            {/* Overall Statistics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-cyan-500/20 to-purple-500/20 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
            >
              <h2 className="text-2xl font-bold mb-4 text-cyan-300">
                📊 Overall Statistics
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white/10 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-cyan-400">
                    {results.num_scenarios}
                  </div>
                  <div className="text-sm text-gray-300">Scenarios</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-green-400">
                    {results.overall_stats.secure_links}
                  </div>
                  <div className="text-sm text-gray-300">Secure Links</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-red-400">
                    {results.overall_stats.compromised_links}
                  </div>
                  <div className="text-sm text-gray-300">Compromised</div>
                </div>
                <div className="bg-white/10 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-purple-400">
                    {results.overall_stats.security_percentage.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-300">Security Rate</div>
                </div>
              </div>
            </motion.div>

            {/* Comparison Chart */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
            >
              <h2 className="text-2xl font-bold mb-4 text-purple-300">
                📈 Scenario Comparison
              </h2>
              <img
                src={`data:image/png;base64,${results.comparison_chart}`}
                alt="Scenario Comparison"
                className="w-full rounded-xl"
              />
            </motion.div>

            {/* Attacker Analysis */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
            >
              <h2 className="text-2xl font-bold mb-4 text-red-300">
                👿 Attacker Analysis
              </h2>
              <img
                src={`data:image/png;base64,${results.attacker_analysis}`}
                alt="Attacker Analysis"
                className="w-full rounded-xl"
              />
            </motion.div>

            {/* Individual Scenarios */}
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-center text-cyan-300">
                🔬 Individual Scenario Details
              </h2>
              {results.scenarios.map((scenario, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + idx * 0.1 }}
                  className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20"
                >
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-cyan-300">
                      Scenario {scenario.scenario_num}: {scenario.scenario_name}
                    </h3>
                    <div className="flex gap-4 text-sm">
                      <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full">
                        ✓ {scenario.secure_links} Secure
                      </span>
                      <span className="bg-red-500/20 text-red-300 px-3 py-1 rounded-full">
                        ✗ {scenario.compromised_links} Compromised
                      </span>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-gray-300">
                      <span className="font-semibold">Attackers:</span>{" "}
                      {scenario.attacker_names.length > 0
                        ? scenario.attacker_names.join(", ")
                        : "None"}
                    </p>
                    <p className="text-gray-300">
                      <span className="font-semibold">Security:</span>{" "}
                      <span
                        className={
                          scenario.security_percentage >= 50
                            ? "text-green-400"
                            : "text-red-400"
                        }
                      >
                        {scenario.security_percentage.toFixed(1)}%
                      </span>
                    </p>
                  </div>

                  <img
                    src={`data:image/png;base64,${scenario.image}`}
                    alt={`Scenario ${scenario.scenario_num}`}
                    className="w-full rounded-xl"
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <footer className="text-center mt-12 text-gray-400 text-sm">
        © 2025 BB84 Quantum Network Simulator | Powered by Qiskit
      </footer>
    </div>
  );
}

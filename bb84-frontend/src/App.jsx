import { useState } from "react";
import { motion } from "framer-motion";

export default function App() {
  const [qubits, setQubits] = useState(10);
  const [attackers, setAttackers] = useState(2);
  const [intercept, setIntercept] = useState(50);

  const linkColor = intercept > 40 ? "stroke-red-500" : "stroke-green-400";
  const eveColor = intercept > 40 ? "bg-red-500" : "bg-yellow-400";

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-700 text-white flex flex-col items-center justify-center p-6 space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-extrabold font-[Orbitron] flex items-center justify-center gap-2">
          🔐 BB84 Quantum Network
        </h1>
        <p className="text-gray-200 text-sm mt-2">Interactive QKD Simulator Dashboard</p>
      </header>

      <div className="bg-white/10 backdrop-blur-md p-8 rounded-2xl w-full max-w-3xl shadow-xl">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Qubits */}
          <div>
            <label className="block font-semibold mb-2">
              Qubits: <span className="text-yellow-300">{qubits}</span>
            </label>
            <input
              type="range"
              min="1"
              max="20"
              value={qubits}
              onChange={(e) => setQubits(e.target.value)}
              className="w-full accent-yellow-400"
            />
          </div>

          {/* Attackers */}
          <div>
            <label className="block font-semibold mb-2">
              Number of Attackers:{" "}
              <span className="text-red-300">{attackers}</span>
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={attackers}
              onChange={(e) => setAttackers(e.target.value)}
              className="w-full text-black rounded-lg p-2"
            />
          </div>

          {/* Intercept */}
          <div className="col-span-2">
            <label className="block font-semibold mb-2">
              Intercept Percentage:{" "}
              <span className="text-green-300">{intercept}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={intercept}
              onChange={(e) => setIntercept(e.target.value)}
              className="w-full accent-green-400"
            />
          </div>
        </div>

        {/* Simulation Summary */}
        <div className="mt-6 text-center">
          <p className="text-lg">
            👁 Simulating <span className="font-bold">{qubits}</span> qubits with{" "}
            <span className="font-bold">{attackers}</span> attacker(s) at{" "}
            <span className="font-bold">{intercept}%</span> interception rate.
          </p>
        </div>

        {/* Quantum Network Visual */}
        <div className="mt-8 relative w-full h-64 bg-black/30 rounded-xl border border-white/20 flex items-center justify-center overflow-hidden">
          <svg className="absolute inset-0 w-full h-full">
            {/* Link: Alice -> Bob */}
            <line
              x1="30%"
              y1="50%"
              x2="70%"
              y2="50%"
              className={`${linkColor}`}
              strokeWidth="3"
            />
          </svg>

          {/* Alice (Sender) */}
          <motion.div
            className="absolute left-[25%] flex flex-col items-center"
            animate={{ y: [0, -5, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <div className="w-14 h-14 bg-blue-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center font-bold">
              A
            </div>
            <p className="text-xs mt-2 text-gray-300">Alice (Sender)</p>
          </motion.div>

          {/* Bob (Receiver) */}
          <motion.div
            className="absolute right-[25%] flex flex-col items-center"
            animate={{ y: [0, 5, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <div className="w-14 h-14 bg-green-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center font-bold">
              B
            </div>
            <p className="text-xs mt-2 text-gray-300">Bob (Receiver)</p>
          </motion.div>

          {/* Eve (Attacker) */}
          <motion.div
            className="absolute top-[25%] left-1/2 transform -translate-x-1/2 flex flex-col items-center"
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ repeat: Infinity, duration: 1.5 }}
          >
            <div
              className={`w-10 h-10 ${eveColor} rounded-full border-2 border-white shadow-lg flex items-center justify-center font-bold`}
            >
              E
            </div>
            <p className="text-xs mt-2 text-gray-300">Eve (Attacker)</p>
          </motion.div>
        </div>
      </div>

      <footer className="opacity-70 text-sm mt-4">
        © 2025 BB84 Quantum Network Simulator
      </footer>
    </div>
  );
}

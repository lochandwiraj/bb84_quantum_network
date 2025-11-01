# main.py — Master runner (Hours 1 through 9)
import numpy as np
import random
from alice import alice_prepare_qubits
from bb84_core import create_bb84_circuit, simulate_transmission_with_eve, sift_key
from error_check import check_errors
from network import run_quantum_network  # alias to run_quantum_network_random

# Optional: if you have qiskit and want to use real circuit simulation for per-qubit runs,
# you can write/create functions that use qiskit.Aer. This file uses bb84_core (fast model).
# (If you prefer Qiskit circuits, uncomment and adapt below. Qiskit often requires larger installs.)

def bob_measure_qubits(num_qubits):
    """Return list of 0/1 bases (0=Z,1=X)"""
    return np.random.randint(0, 2, num_qubits).tolist()

def run_bb84_protocol(n_qubits=100, with_eve=False, intercept_rate=0.5):
    """
    Run BB84 single-channel simulation (Alice->Bob)
    Uses bb84_core simulation functions.
    Returns result dict.
    """
    print("\n" + "="*50)
    print(f"RUNNING BB84 PROTOCOL — Qubits: {n_qubits} | Eve: {with_eve} | Intercept: {intercept_rate}")
    print("="*50 + "\n")

    # Hour 2: Alice prepares
    alice_bits, alice_bases = alice_prepare_qubits(n_qubits)
    print(f"✓ Alice prepared {n_qubits} qubits")

    # Hour 3: Bob chooses
    bob_bases = bob_measure_qubits(n_qubits)
    print("✓ Bob chose measurement bases")

    # Hour 4 & 7: Transmission (with optional Eve)
    bob_results = simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=with_eve, intercept_rate=intercept_rate)
    print("✓ Quantum transmission complete (simulated)")

    # Hour 5: Sifting
    alice_key, bob_key, matching_indices = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    print(f"✓ Key sifting: {len(alice_key)} matching bases found")

    # Hour 6: Error check
    if len(alice_key) == 0:
        print("⚠️ No sifted key bits — aborting.")
        return {"error_rate": 1.0, "key_length": 0, "secure": False}

    check_result = check_errors(alice_key, bob_key, sample_fraction=0.2, threshold=0.11)
    qber = check_result["qber"]
    eve_detected = check_result["eve_detected"]
    secure = not eve_detected

    print("\n" + "="*50)
    print("RESULTS:")
    print(f"QBER: {qber*100:.2f}%")
    print(f"Final Key Length: {len(check_result['alice_final_key'])} bits (after sacrificing tested bits)")
    print(f"Security Status: {'✅ SECURE' if secure else '❌ COMPROMISED'}")
    print("="*50 + "\n")

    return {
        "error_rate": qber,
        "key_length": len(check_result['alice_final_key']),
        "secure": secure,
        "alice_key": check_result['alice_final_key'],
        "bob_key": check_result['bob_final_key']
    }

if __name__ == "__main__":
    # Hour 1 check (environment)
    print("Hour 1: Environment & project sanity check")
    print(" - Ensure Python v3.8+ and virtualenv activated")
    print(" - Required files: alice.py, bb84_core.py, error_check.py, network.py, main.py\n")

    # Run the single-channel tests
    print("\n=== TEST: BB84 single-link (no Eve) ===")
    run_bb84_protocol(100, with_eve=False)

    print("\n=== TEST: BB84 single-link (Eve 50%) ===")
    run_bb84_protocol(100, with_eve=True, intercept_rate=0.5)

    # Hour 9: network test (random compromised link(s))
    print("\n=== NETWORK TEST (random compromised link) ===")
    net_res = run_quantum_network(num_qubits=100, intercept_rate=0.5, num_compromised=1, seed=None)
    print("\nNetwork summary: {:.1f}% secure".format(net_res["security_percentage"]))

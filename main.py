# main.py — Master runner (Hours 1–10)
import numpy as np
from alice import alice_prepare_qubits
from bb84_core import create_bb84_circuit, simulate_transmission_with_eve, sift_key
from error_check import check_errors
from network import run_quantum_network, run_quantum_network_random

def bob_measure_qubits(num_qubits):
    """Bob randomly chooses measurement bases (0 = Z, 1 = X)."""
    return np.random.randint(0, 2, num_qubits).tolist()

def run_bb84_protocol(n_qubits=100, with_eve=False, intercept_rate=0.5):
    """
    Run single-link BB84 (Alice -> Bob) using bb84_core.
    """
    print("\n" + "="*50)
    print(f"RUNNING BB84 PROTOCOL — Qubits: {n_qubits} | Eve: {with_eve} | Intercept: {intercept_rate}")
    print("="*50 + "\n")

    alice_bits, alice_bases = alice_prepare_qubits(n_qubits)
    print(f"✓ Alice prepared {n_qubits} qubits")

    bob_bases = bob_measure_qubits(n_qubits)
    print("✓ Bob chose measurement bases")

    bob_results = simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=with_eve, intercept_rate=intercept_rate)
    print("✓ Quantum transmission complete (simulated)")

    alice_key, bob_key, _ = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    print(f"✓ Key sifting: {len(alice_key)} matching bases found")

    if len(alice_key) == 0:
        print("⚠️ No sifted bits — aborting.")
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
    return {"error_rate": qber, "key_length": len(check_result['alice_final_key']), "secure": secure}

if __name__ == "__main__":
    print("Hour 1: Environment & project sanity check")
    print(" - Ensure Python v3.8+ and virtualenv activated")
    print(" - Required files: alice.py, bb84_core.py, error_check.py, network.py, main.py\n")

    # Single-link tests
    print("\n=== TEST: BB84 single-link (no Eve) ===")
    run_bb84_protocol(100, with_eve=False)

    print("\n=== TEST: BB84 single-link (Eve 50%) ===")
    run_bb84_protocol(100, with_eve=True, intercept_rate=0.5)

    # Hour 10: 3 parallel sessions where Charlie is attacked
    print("\n=== NETWORK TEST (Charlie attacked) ===")
    run_quantum_network(100, eve_intercept_rate=0.5)

    # Random-compromise network test
    print("\n=== NETWORK TEST (random compromised link) ===")
    run_quantum_network_random(100, 0.5, num_compromised=1, seed=None)

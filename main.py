# ============================================================
# main.py – BB84 Quantum Key Distribution with Eve Simulation
# ============================================================

import numpy as np
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from alice import alice_prepare_qubits
from error_check import check_errors


# ------------------------------------------------------------
#  Bob’s Measurement System (Hour 3)
# ------------------------------------------------------------
def bob_measure_qubits(num_qubits):
    """Bob randomly chooses measurement bases (0 = Z, 1 = X)."""
    return np.random.randint(0, 2, num_qubits).tolist()


# ------------------------------------------------------------
#  Quantum Transmission (Hour 4)
# ------------------------------------------------------------
def create_bb84_circuit(alice_bits, alice_bases, bob_bases, num_qubits):
    """Simulate BB84 transmission qubit-by-qubit using Aer simulator."""
    simulator = Aer.get_backend("aer_simulator")
    results = []

    for i in range(num_qubits):
        qc = QuantumCircuit(1, 1)

        # Alice encodes her qubit
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        # Bob’s measurement
        if bob_bases[i] == 1:
            qc.h(0)
        qc.measure(0, 0)

        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=1)
        out = job.result().get_counts(compiled)
        measured_bit = int(max(out, key=out.get)[-1])
        results.append(measured_bit)

    return results


# ------------------------------------------------------------
#  Key Sifting (Hour 5)
# ------------------------------------------------------------
def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """Keep only positions where bases matched."""
    alice_key, bob_key, matching_indices = [], [], []

    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            matching_indices.append(i)
            alice_key.append(alice_bits[i])
            bob_key.append(bob_results[i])

    return alice_key, bob_key, matching_indices


# ------------------------------------------------------------
#  Eve’s Quantum Eavesdropping (Hour 7 FIXED)
# ------------------------------------------------------------
def simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=False, intercept_rate=0.5):
    """
    Simulate BB84 transmission with or without Eve.
    Eve measures intercepted qubits in random bases and collapses their state.
    """
    simulator = Aer.get_backend("aer_simulator")
    results = []
    eve_intercepted = 0

    for i in range(len(alice_bits)):
        qc = QuantumCircuit(1, 1)

        # --- Alice prepares qubit ---
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        # --- Eve intercepts ---
        if with_eve and random.random() < intercept_rate:
            eve_intercepted += 1
            eve_basis = random.randint(0, 1)

            # Eve measures in her basis
            if eve_basis == 1:
                qc.h(0)
            qc.measure(0, 0)
            qc.reset(0)  # collapse the state

            # Eve re-sends a possibly wrong qubit to Bob
            if random.random() < 0.5:
                qc.x(0)

        # --- Bob measures ---
        if bob_bases[i] == 1:
            qc.h(0)
        qc.measure(0, 0)

        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=1)
        out = job.result().get_counts(compiled)
        measured_bit = int(max(out, key=out.get)[-1])
        results.append(measured_bit)

    if with_eve:
        print(f"⚠️ Eve intercepted {eve_intercepted} qubits ({intercept_rate*100:.1f}% rate)")

    return results


# ------------------------------------------------------------
#  Main Simulation Flow
# ------------------------------------------------------------
if __name__ == "__main__":
    num_qubits = 100

    # --- Alice prepares ---
    alice_bits, alice_bases = alice_prepare_qubits(num_qubits)

    # --- Bob chooses ---
    bob_bases = bob_measure_qubits(num_qubits)

    # === TEST 1: No Eve (clean channel) ===
    print("\n=== TEST 1: NO EAVESDROPPER ===")
    bob_results = simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=False)
    alice_key, bob_key, _ = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    qber, eve_detected = check_errors(alice_key, bob_key)
    print(f"Error rate: {qber:.2f}%")
    print("Status:", "✅ SECURE" if not eve_detected else "❌ DETECTED")

    # === TEST 2: Eve intercepting 50% ===
    print("\n=== TEST 2: EVE INTERCEPTING 50% ===")
    bob_results = simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=True, intercept_rate=0.5)
    alice_key, bob_key, _ = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    qber, eve_detected = check_errors(alice_key, bob_key)
    print(f"Error rate: {qber:.2f}%")
    print("Status:", "✅ SECURE" if not eve_detected else "❌ DETECTED")

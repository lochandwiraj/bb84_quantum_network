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
#  Eve’s Quantum Eavesdropping (Hour 7)
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

            # Eve re-sends a possibly wrong qubit
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
#  Unified BB84 Runner (Hour 8 wrapper)
# ------------------------------------------------------------
def run_bb84_protocol(n_qubits=100, with_eve=False, intercept_rate=0.5):
    """
    Unified runner for BB84 protocol using existing components.
    Returns results dictionary.
    """
    print(f"\n{'='*50}")
    print(f"RUNNING BB84 PROTOCOL — Qubits: {n_qubits} | Eve: {with_eve} | Intercept: {intercept_rate}")
    print(f"{'='*50}\n")

    # 1) Alice prepares
    alice_bits, alice_bases = alice_prepare_qubits(n_qubits)
    print(f"✓ Alice prepared {n_qubits} qubits")

    # 2) Bob chooses bases
    bob_bases = bob_measure_qubits(n_qubits)
    print("✓ Bob chose measurement bases")

    # 3) Quantum transmission
    bob_results = simulate_transmission_with_eve(
        alice_bits, alice_bases, bob_bases, with_eve=with_eve, intercept_rate=intercept_rate
    )
    print("✓ Quantum transmission complete")

    # 4) Key sifting
    alice_key, bob_key, matching_indices = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    print(f"✓ Key sifting: {len(alice_key)} matching bases found")

    # 5) Error checking
    if len(alice_key) == 0:
        print("⚠️ No sifted bits — aborting.")
        return {
            'error_rate': 1.0,
            'key_length': 0,
            'secure': False,
            'initial_qubits': n_qubits,
            'sifted_bits': 0,
            'alice_key': [],
            'bob_key': []
        }

    check_result = check_errors(alice_key, bob_key)
    qber = check_result["qber"]
    eve_detected = check_result["eve_detected"]
    secure = not eve_detected

    print("\n" + "="*50)
    print("RESULTS:")
    print(f"QBER: {qber*100:.2f}%")
    print(f"Final Key Length: {len(alice_key)}")
    print(f"Security Status: {'✅ SECURE' if secure else '❌ COMPROMISED'}")
    print("="*50 + "\n")

    return {
        'error_rate': qber,
        'key_length': len(alice_key),
        'secure': secure,
        'initial_qubits': n_qubits,
        'sifted_bits': len(alice_key),
        'alice_key': alice_key,
        'bob_key': bob_key
    }


# ------------------------------------------------------------
#  Automated Tests (Hour 8 master run)
# ------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "🔐"*10)
    print("BB84 PROTOCOL MASTER RUN")
    print("🔐"*10)

    # Test 1: Secure channel (no Eve)
    print("\n\n TEST 1: SECURE CHANNEL (NO EAVESDROPPER)")
    result1 = run_bb84_protocol(100, with_eve=False)

    # Test 2: With Eve (50% intercept)
    print("\n\n TEST 2: WITH EAVESDROPPER (50% INTERCEPT)")
    result2 = run_bb84_protocol(100, with_eve=True, intercept_rate=0.5)

    # Test 3: Stealth Eve (10% intercept)
    print("\n\n TEST 3: STEALTH EAVESDROPPER (10% INTERCEPT)")
    result3 = run_bb84_protocol(100, with_eve=True, intercept_rate=0.1)

# main.py
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from alice import alice_prepare_qubits

def bob_measure_qubits(num_qubits):
    """Return list of 0/1 bases (0=Z,1=X)"""
    return np.random.randint(0, 2, num_qubits).tolist()

def create_bb84_circuit(alice_bits, alice_bases, bob_bases, num_qubits):
    """
    Simulate BB84 transmission qubit-by-qubit using Aer simulator (shots=1 each).
    Returns list of measured bits by Bob.
    """
    simulator = Aer.get_backend('aer_simulator')
    results = []

    for i in range(num_qubits):
        qc = QuantumCircuit(1, 1)

        # Alice encodes bit
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        # Bob measures in his chosen basis
        if bob_bases[i] == 1:
            qc.h(0)

        qc.measure(0, 0)

        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=1)
        out = job.result().get_counts(compiled)
        # counts is like {'0':1} or {'1':1}
        measured_bit = int(max(out, key=out.get))
        results.append(measured_bit)

    return results

def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """
    Keep only positions where bases matched.
    Returns (alice_key, bob_key, matching_indices)
    """
    alice_key = []
    bob_key = []
    matching_indices = []

    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            matching_indices.append(i)
            alice_key.append(alice_bits[i])
            bob_key.append(bob_results[i])

    return alice_key, bob_key, matching_indices

if __name__ == "__main__":
    # PARAMETERS
    num_qubits = 100

    # 1) Alice prepares
    alice_bits, alice_bases = alice_prepare_qubits(num_qubits)

    # 2) Bob chooses bases
    bob_bases = bob_measure_qubits(num_qubits)

    # 3) Simulate quantum transmission (Bob's measurement results)
    bob_results = create_bb84_circuit(alice_bits, alice_bases, bob_bases, num_qubits)

    # 4) Sift key (keep only matching-basis positions)
    alice_key, bob_key, matching_indices = sift_key(
        alice_bits, alice_bases, bob_bases, bob_results
    )

    # 5) Print results
    print("\n" + "="*50)
    print("SIFTING RESULTS")
    print("="*50)
    print(f"Total qubits sent: {num_qubits}")
    print(f"Bases matched at: {len(matching_indices)} positions")
    print(f"Sifting efficiency: {len(matching_indices)/num_qubits*100:.1f}%\n")
    print(f"Alice's sifted key (first 32 bits): {alice_key[:32]}  ({len(alice_key)} bits total)")
    print(f"Bob's   sifted key (first 32 bits): {bob_key[:32]}  ({len(bob_key)} bits total)\n")

    keys_match = (alice_key == bob_key)
    print(f"✅ Keys identical: {keys_match}")

    if not keys_match:
        differences = sum(a != b for a, b in zip(alice_key, bob_key))
        print(f"⚠️ Differences found: {differences}/{len(alice_key)} bits")

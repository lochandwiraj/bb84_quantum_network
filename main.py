# main.py
import numpy as np
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
    """
    Simulate BB84 transmission qubit-by-qubit using Aer simulator (shots=1 each).
    Includes optional Eve interception to simulate eavesdropping.
    Returns list of measured bits by Bob.
    """
    simulator = Aer.get_backend('aer_simulator')
    results = []

    for i in range(num_qubits):
        qc = QuantumCircuit(1, 1)

        # --- Alice encodes her qubit ---
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)

        # --- Eve interception simulation (10% chance) ---
        if np.random.rand() < 0.10:  # 10% chance Eve interferes
            eve_basis = np.random.randint(0, 2)
            if eve_basis == 1:
                qc.h(0)
            qc.measure(0, 0)
            qc.reset(0)
            # re-prepare disturbed qubit for Bob
            if alice_bits[i] == 1:
                qc.x(0)
            if alice_bases[i] == 1:
                qc.h(0)

        # --- Bob’s measurement ---
        if bob_bases[i] == 1:
            qc.h(0)
        qc.measure(0, 0)

        compiled = transpile(qc, simulator)
        job = simulator.run(compiled, shots=1)
        out = job.result().get_counts(compiled)

        # Some outputs may look like '0 1' — take the last bit safely
        measured_str = max(out, key=out.get)
        measured_bit = int(measured_str[-1])
        results.append(measured_bit)

    return results


# ------------------------------------------------------------
#  Key Sifting (Hour 5)
# ------------------------------------------------------------
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


# ------------------------------------------------------------
#  Main BB84 Protocol (Hours 1–6)
# ------------------------------------------------------------
if __name__ == "__main__":
    num_qubits = 100

    # 1. Alice prepares qubits
    alice_bits, alice_bases = alice_prepare_qubits(num_qubits)

    # 2. Bob randomly selects bases
    bob_bases = bob_measure_qubits(num_qubits)

    # 3. Simulate transmission with optional Eve interference
    bob_results = create_bb84_circuit(alice_bits, alice_bases, bob_bases, num_qubits)

    # 4. Perform key sifting
    alice_key, bob_key, matching_indices = sift_key(
        alice_bits, alice_bases, bob_bases, bob_results
    )

    # 5. Show sifting results
    print("\n" + "=" * 50)
    print("SIFTING RESULTS")
    print("=" * 50)
    print(f"Total qubits sent: {num_qubits}")
    print(f"Bases matched at: {len(matching_indices)} positions")
    print(f"Sifting efficiency: {len(matching_indices)/num_qubits*100:.1f}%\n")
    print(f"Alice's sifted key (first 32 bits): {alice_key[:32]} ({len(alice_key)} bits total)")
    print(f"Bob's   sifted key (first 32 bits): {bob_key[:32]} ({len(bob_key)} bits total)\n")

    # 6) Error checking (Eavesdrop detection)
qber, eve_detected = check_errors(alice_key, bob_key)

print("\n" + "="*50)
print("ERROR CHECKING (QBER Estimation)")
print("="*50)
print(f"Quantum Bit Error Rate (QBER): {qber:.2f}%")

if not eve_detected:
    print("✅ Secure channel. No significant eavesdropping detected.")
    final_key = alice_key
    print(f"\n🔐 Final Secure Key (length {len(final_key)}): {final_key[:32]}")
else:
    print("🚫 Key discarded due to high error rate.")


    # 7. If secure, show final key
    if result['is_secure']:
        print(f"\n🔐 Final Secure Key (first 32 bits): {result['alice_final_key'][:32]}")
    else:
        print("\n🚫 Key discarded — channel not secure.")

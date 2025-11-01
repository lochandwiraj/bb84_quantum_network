# main.py
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit.compiler import transpile
from alice import alice_prepare_qubits

def bob_measure_qubits(num_qubits):
    """Bob randomly chooses measurement bases independently"""
    return np.random.randint(0, 2, num_qubits)

def create_bb84_circuit(alice_bits, alice_bases, bob_bases, num_qubits):
    """
    Creates and executes the BB84 quantum circuit.
    """
    qr = QuantumRegister(num_qubits, name='q')
    cr = ClassicalRegister(num_qubits, name='c')
    circuit = QuantumCircuit(qr, cr)

    # Alice’s encoding
    for i in range(num_qubits):
        if alice_bits[i] == 1:
            circuit.x(qr[i])
        if alice_bases[i] == 1:
            circuit.h(qr[i])

    circuit.barrier()

    # Bob’s measurement
    for i in range(num_qubits):
        if bob_bases[i] == 1:
            circuit.h(qr[i])

    circuit.measure(qr, cr)

    simulator = Aer.get_backend('qasm_simulator')
    compiled = transpile(circuit, simulator)
    job = simulator.run(compiled, shots=1)
    result = job.result()
    counts = result.get_counts(compiled)
    measured_string = list(counts.keys())[0]
    bob_results = [int(bit) for bit in reversed(measured_string)]
    return bob_results

if __name__ == "__main__":
    print("=" * 50)
    print("HOUR 4: QUANTUM CHANNEL TEST")
    print("=" * 50)

    num_qubits = 20
    alice_bits, alice_bases = alice_prepare_qubits(num_qubits)
    print(f"\nAlice's bits:  {alice_bits[:10]}... (showing first 10)")
    print(f"Alice's bases: {alice_bases[:10]}...")

    bob_bases = bob_measure_qubits(num_qubits)
    print(f"Bob's bases:   {bob_bases[:10]}...")

    print("\n🔬 Running quantum transmission...")
    bob_results = create_bb84_circuit(alice_bits, alice_bases, bob_bases, num_qubits)
    print(f"\nBob measured:  {bob_results[:10]}...")

    matches, correct = [], 0
    for i in range(num_qubits):
        if alice_bases[i] == bob_bases[i]:
            matches.append(i)
            if alice_bits[i] == bob_results[i]:
                correct += 1

    print(f"\n📊 RESULTS:")
    print(f"Bases matched at {len(matches)} positions out of {num_qubits}")
    print(f"Of those, {correct} measurements were correct")
    print(f"Accuracy when bases match: {100 * correct / len(matches):.1f}%")
    print("\n✅ This should be ~100% (tiny errors from quantum noise)")

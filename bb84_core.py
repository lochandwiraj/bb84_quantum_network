# bb84_core.py
# Core BB84 protocol simulation (no real quantum backend)

import numpy as np

def create_bb84_circuit(alice_bits, alice_bases, bob_bases, n_qubits):
    """Simulate quantum measurement results."""
    results = np.zeros(n_qubits, dtype=int)
    for i in range(n_qubits):
        if alice_bases[i] == bob_bases[i]:
            results[i] = alice_bits[i]
        else:
            results[i] = np.random.randint(0, 2)
    return results


def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """Sift the keys based on matching bases."""
    mask = alice_bases == bob_bases
    alice_key = alice_bits[mask]
    bob_key = bob_results[mask]
    print(f"✓ Key sifting: {len(alice_key)} matching bases found")
    return alice_key, bob_key


def eve_intercept(alice_bits, alice_bases, intercept_rate=0.5):
    """Simulate Eve intercepting and disturbing some qubits."""
    n_qubits = len(alice_bits)
    eve_bases = np.random.randint(0, 2, n_qubits)
    corrupted = np.copy(alice_bits)
    n_intercept = int(intercept_rate * n_qubits)
    attack_indices = np.random.choice(range(n_qubits), n_intercept, replace=False)
    for i in attack_indices:
        if alice_bases[i] != eve_bases[i]:
            corrupted[i] = np.random.randint(0, 2)
    print(f"⚠️  Eve intercepted {n_intercept} qubits")
    return corrupted

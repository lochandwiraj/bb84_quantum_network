import numpy as np

def create_bb84_circuit(num_qubits):
    """Alice prepares random bits and bases"""
    alice_bits = np.random.randint(0, 2, num_qubits)
    alice_bases = np.random.randint(0, 2, num_qubits)
    return alice_bits.tolist(), alice_bases.tolist()

def simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=False, intercept_rate=0.0):
    """Simulate the quantum transmission with or without Eve"""
    bob_results = []

    for i in range(len(alice_bits)):
        bit = alice_bits[i]
        base = alice_bases[i]

        # Eve intercepts with some probability
        if with_eve and np.random.rand() < intercept_rate:
            eve_basis = np.random.randint(0, 2)
            measured_bit = bit if eve_basis == base else np.random.randint(0, 2)
            bit = measured_bit
            base = eve_basis  # Eve re-sends this qubit

        # Bob measures
        bob_bit = bit if bob_bases[i] == base else np.random.randint(0, 2)
        bob_results.append(bob_bit)

    return bob_results

def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """Keep bits where Alice and Bob used same bases"""
    indices = [i for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]]
    alice_key = [alice_bits[i] for i in indices]
    bob_key = [bob_results[i] for i in indices]

    # Calculate error rate
    if len(alice_key) == 0:
        error_rate = 0.0
    else:
        mismatches = sum(a != b for a, b in zip(alice_key, bob_key))
        error_rate = (mismatches / len(alice_key)) * 100

    return alice_key, bob_key, error_rate

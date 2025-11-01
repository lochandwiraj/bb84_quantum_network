# bb84_core.py — Core BB84 Protocol Implementation
import numpy as np

def create_bb84_circuit(num_qubits):
    """
    Alice preparation helper: generate random bits and bases.
    Returns (alice_bits, alice_bases) as Python lists.
    """
    alice_bits = np.random.randint(0, 2, num_qubits)
    alice_bases = np.random.randint(0, 2, num_qubits)
    return alice_bits.tolist(), alice_bases.tolist()


def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """
    Sift keys: return (alice_key, bob_key, matching_indices)
    """
    matching_indices = [i for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]]
    alice_key = [alice_bits[i] for i in matching_indices]
    bob_key = [bob_results[i] for i in matching_indices]
    return alice_key, bob_key, matching_indices


def simulate_transmission_with_eve(
    alice_bits,
    alice_bases,
    bob_bases,
    with_eve=False,
    intercept_rate=0.0
):
    """
    Simulate transmission from Alice -> Bob (classical probabilistic model).
    - If with_eve True: Eve intercepts each qubit with probability intercept_rate,
      measures in a random basis, possibly collapses and resends.
    - Returns: bob_results (list of 0/1)
    """
    bob_results = []
    num_qubits = len(alice_bits)

    for i in range(num_qubits):
        bit = alice_bits[i]
        base = alice_bases[i]

        # Eve intercepts some qubits
        if with_eve and np.random.rand() < intercept_rate:
            eve_basis = np.random.randint(0, 2)
            # if eve_basis == alice_basis: measured bit preserved; else random
            measured_bit = bit if eve_basis == base else np.random.randint(0, 2)
            # Eve re-sends measured_bit encoded in her basis
            bit = measured_bit
            base = eve_basis

        # Bob measures: if bases match -> get bit; else random
        bob_bit = bit if bob_bases[i] == base else np.random.randint(0, 2)
        bob_results.append(bob_bit)

    return bob_results

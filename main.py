# main.py

import numpy as np
from alice import alice_prepare_qubits

def bob_measure_qubits(num_qubits):
    """Bob randomly chooses measurement bases independently"""
    bob_bases = np.random.randint(0, 2, num_qubits)
    return bob_bases


def main():
    num_qubits = 20

    # Alice prepares her qubits
    alice_bits, alice_bases = alice_prepare_qubits(num_qubits)

    # Bob independently chooses measurement bases
    bob_bases = bob_measure_qubits(num_qubits)

    # Display their bases
    print("Alice's bases:", alice_bases)
    print("Bob's bases:  ", bob_bases)

    # Find matching bases (same positions)
    matches = np.where(np.array(alice_bases) == np.array(bob_bases))[0]

    print(f"\nBases matched at {len(matches)} positions:", matches)


if __name__ == "__main__":
    main()

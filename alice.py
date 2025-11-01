# alice.py
# Handles Alice's qubit preparation and communication setup

import numpy as np

def prepare_qubits(n_qubits=100):
    """Alice prepares random bits and random bases."""
    bits = np.random.randint(0, 2, n_qubits)
    bases = np.random.randint(0, 2, n_qubits)
    print(f"\n✓ Alice prepared {n_qubits} qubits")
    return bits, bases

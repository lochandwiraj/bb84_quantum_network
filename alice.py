# alice.py
import numpy as np

def alice_prepare_qubits(num_qubits):
    """
    Returns:
        alice_bits: list of 0/1
        alice_bases: list of 0/1 (0=Z,1=X)
    """
    alice_bits = np.random.randint(0, 2, num_qubits)
    alice_bases = np.random.randint(0, 2, num_qubits)
    return alice_bits.tolist(), alice_bases.tolist()

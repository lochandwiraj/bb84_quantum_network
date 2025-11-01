import numpy as np

def bob_measure_qubits(num_qubits):
    """Bob randomly chooses measurement bases."""
    return np.random.randint(0, 2, num_qubits).tolist()

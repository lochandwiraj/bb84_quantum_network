from bb84_core import generate_bits, generate_bases

class Alice:
    def __init__(self, n_qubits):
        self.bits = generate_bits(n_qubits)
        self.bases = generate_bases(n_qubits)

    def send_qubits(self):
        return list(zip(self.bits, self.bases))

import numpy as np

def eve_intercept(alice_bits, alice_bases, intercept_rate=0.5):
    """
    Eve intercepts a fraction of qubits and resends disturbed versions.
    """
    intercepted_bits = []
    for i in range(len(alice_bits)):
        bit, base = alice_bits[i], alice_bases[i]
        if np.random.rand() < intercept_rate:
            eve_basis = np.random.randint(0, 2)
            measured_bit = bit if eve_basis == base else np.random.randint(0, 2)
            intercepted_bits.append(measured_bit)
        else:
            intercepted_bits.append(bit)
    return intercepted_bits

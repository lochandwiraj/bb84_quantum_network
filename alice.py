# alice.py
import numpy as np

def alice_prepare_qubits(num_qubits):
    """
    Alice prepares random bits and chooses random bases
    
    Args:
        num_qubits: How many qubits to prepare (e.g., 100)
    
    Returns:
        alice_bits: List of random 0s and 1s (the secret message)
        alice_bases: List of random 0s and 1s (0=Z-basis, 1=X-basis)
    """
    # Generate random secret bits (0 or 1)
    alice_bits = np.random.randint(0, 2, num_qubits)
    
    # Generate random basis choices (Z=0, X=1)
    alice_bases = np.random.randint(0, 2, num_qubits)
    
    return alice_bits.tolist(), alice_bases.tolist()


# TEST RUN
if __name__ == "__main__":
    bits, bases = alice_prepare_qubits(20)  # Try with 20 qubits
    print("Alice's secret bits: ", bits)
    print("Alice's bases chosen:", bases)
    print(f"\nGenerated {len(bits)} qubits successfully!")

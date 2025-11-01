import random

def generate_bits(n):
    """Generate n random classical bits (0 or 1)."""
    return [random.randint(0, 1) for _ in range(n)]

def generate_bases(n):
    """Generate n random measurement bases ('X' or 'Z')."""
    return [random.choice(['X', 'Z']) for _ in range(n)]

def measure(bits, bases, measurement_bases):
    """
    Simulates quantum measurement with basis mismatch.
    
    Args:
        bits: The classical bit values
        bases: The preparation bases used
        measurement_bases: The measurement bases chosen
    
    Returns:
        List of measurement results
    """
    measured = []
    for bit, base, m_base in zip(bits, bases, measurement_bases):
        if base == m_base:
            # Bases match - measure correctly
            measured.append(bit)
        else:
            # Bases don't match - random result (50/50)
            measured.append(random.randint(0, 1))
    return measured

def sift_keys(sender_bases, receiver_bases, sender_bits, receiver_bits):
    """
    Key sifting: Keep only bits where bases matched.
    
    Args:
        sender_bases: Alice's bases
        receiver_bases: Bob's bases
        sender_bits: Alice's bits
        receiver_bits: Bob's measurement results
    
    Returns:
        Tuple of (alice_sifted_key, bob_sifted_key)
    """
    alice_key = []
    bob_key = []
    
    for i in range(len(sender_bases)):
        if sender_bases[i] == receiver_bases[i]:
            # Bases matched - keep these bits
            alice_key.append(sender_bits[i])
            bob_key.append(receiver_bits[i])
    
    return alice_key, bob_key

def calculate_error_positions(key1, key2):
    """
    Returns indices where two keys differ.
    
    Args:
        key1: First key
        key2: Second key
    
    Returns:
        List of indices where keys differ
    """
    if len(key1) != len(key2):
        raise ValueError("Keys must be same length")
    
    error_positions = [i for i in range(len(key1)) if key1[i] != key2[i]]
    return error_positions

def privacy_amplification(key, compression_ratio=0.5):
    """
    Simulates privacy amplification by compressing key.
    
    Args:
        key: Input key
        compression_ratio: Fraction of key to keep
    
    Returns:
        Compressed key
    """
    target_length = max(1, int(len(key) * compression_ratio))
    
    # Simple XOR-based compression
    compressed = []
    chunk_size = len(key) // target_length
    
    for i in range(target_length):
        start = i * chunk_size
        end = start + chunk_size
        if end > len(key):
            end = len(key)
        
        # XOR all bits in chunk
        chunk_xor = 0
        for bit in key[start:end]:
            chunk_xor ^= bit
        compressed.append(chunk_xor)
    
    return compressed
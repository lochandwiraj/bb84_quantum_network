import random

def estimate_error_rate(sender_key, receiver_key, sample_size=None):
    """
    Estimates error rate by comparing sender and receiver keys.
    
    Args:
        sender_key: Alice's sifted key
        receiver_key: Bob's sifted key
        sample_size: Number of bits to sample. If None, uses all bits for more accuracy
    
    Returns:
        Error rate as a float between 0 and 1
    """
    if len(sender_key) == 0 or len(receiver_key) == 0:
        return 1.0
    
    # Use larger sample size for more granular error rates
    # If sample_size is None, use all available bits
    if sample_size is None:
        sample_size = len(sender_key)
    
    n = min(sample_size, len(sender_key))
    
    # Sample indices
    if n == len(sender_key):
        sample_indices = range(len(sender_key))
    else:
        sample_indices = random.sample(range(len(sender_key)), n)
    
    # Count mismatches
    mismatches = sum(sender_key[i] != receiver_key[i] for i in sample_indices)
    
    return mismatches / n

def is_secure(error_rate, threshold=0.11):
    """
    Determines if the quantum channel is secure based on error rate.
    
    Args:
        error_rate: Observed error rate
        threshold: Security threshold (default 11%)
    
    Returns:
        True if secure, False otherwise
    """
    return error_rate <= threshold

def get_final_key(sender_key, receiver_key, test_fraction=0.3):
    """
    Creates final secure key after error checking.
    
    Args:
        sender_key: Alice's sifted key
        receiver_key: Bob's sifted key  
        test_fraction: Fraction of bits to use for error testing
    
    Returns:
        Tuple of (alice_final_key, bob_final_key, error_rate)
    """
    if len(sender_key) == 0:
        return [], [], 1.0
    
    # Determine how many bits to test
    n_test = max(1, int(len(sender_key) * test_fraction))
    
    # Randomly select test indices
    test_indices = set(random.sample(range(len(sender_key)), n_test))
    
    # Calculate error rate on test bits
    mismatches = sum(sender_key[i] != receiver_key[i] for i in test_indices)
    error_rate = mismatches / n_test
    
    # Create final key from untested bits
    alice_final = [sender_key[i] for i in range(len(sender_key)) if i not in test_indices]
    bob_final = [receiver_key[i] for i in range(len(receiver_key)) if i not in test_indices]
    
    return alice_final, bob_final, error_rate
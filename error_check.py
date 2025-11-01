import random

def estimate_error_rate(sender_key, receiver_key, sample_size=20):
    if len(sender_key) == 0 or len(receiver_key) == 0:
        return 1.0

    n = min(sample_size, len(sender_key))
    sample_indices = random.sample(range(len(sender_key)), n)
    mismatches = sum(sender_key[i] != receiver_key[i] for i in sample_indices)
    return mismatches / n

def is_secure(error_rate, threshold=0.11):
    return error_rate <= threshold

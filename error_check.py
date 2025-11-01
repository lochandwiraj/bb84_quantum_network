# error_check.py
import numpy as np

def check_errors(alice_key, bob_key, sample_fraction=0.2):
    """
    Compare random subset of bits to estimate Quantum Bit Error Rate (QBER).
    Returns QBER value and a boolean flag whether eavesdropping is detected.
    """
    key_length = len(alice_key)
    if key_length == 0:
        print("❌ No matching bases found. Cannot perform error check.")
        return 0.0, False

    # Choose random subset indices for comparison
    sample_size = max(1, int(sample_fraction * key_length))
    sample_indices = np.random.choice(key_length, sample_size, replace=False)

    # Count mismatches
    errors = sum(alice_key[i] != bob_key[i] for i in sample_indices)
    qber = errors / sample_size

    print("\n" + "="*50)
    print("ERROR CHECKING (QBER Estimation)")
    print("="*50)
    print(f"Sample size: {sample_size}/{key_length}")
    print(f"Errors detected: {errors}")
    print(f"Quantum Bit Error Rate (QBER): {qber*100:.2f}%")

    # If QBER is above threshold, we suspect Eve
    eve_detected = qber > 0.11
    if eve_detected:
        print("⚠️ High QBER detected! Possible eavesdropping!")
    else:
        print("✅ Secure channel. No significant eavesdropping detected.")

    return qber, eve_detected

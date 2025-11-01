# error_check.py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def check_errors(alice_key, bob_key, sample_fraction=0.2, threshold=0.11, log=False, visualize=False):
    """
    Estimate the Quantum Bit Error Rate (QBER) between Alice and Bob's keys.
    Detects possible eavesdropping if QBER exceeds threshold.
    
    Args:
        alice_key (list[int]): Bits from Alice.
        bob_key (list[int]): Bits from Bob.
        sample_fraction (float): Fraction of bits used for QBER estimation.
        threshold (float): Detection threshold for eavesdropping.
        log (bool): Save results to log file if True.
        visualize (bool): Plot error sample histogram if True.
    
    Returns:
        dict: {
            "qber": float,
            "errors": int,
            "sample_size": int,
            "eve_detected": bool
        }
    """
    if not alice_key or not bob_key:
        print("❌ Empty key(s). Cannot perform error check.")
        return {"qber": 0.0, "errors": 0, "sample_size": 0, "eve_detected": False}

    if len(alice_key) != len(bob_key):
        print("⚠️ Warning: Key lengths differ. Truncating to shortest.")
        min_len = min(len(alice_key), len(bob_key))
        alice_key, bob_key = alice_key[:min_len], bob_key[:min_len]

    key_length = len(alice_key)
    sample_size = max(1, int(sample_fraction * key_length))
    sample_indices = np.random.choice(key_length, sample_size, replace=False)

    errors = np.sum([alice_key[i] != bob_key[i] for i in sample_indices])
    qber = errors / sample_size
    eve_detected = qber > threshold

    print("\n" + "="*60)
    print("🔍 ERROR CHECKING (QBER Estimation)")
    print("="*60)
    print(f"Key length: {key_length}")
    print(f"Sample size: {sample_size}")
    print(f"Errors detected: {errors}")
    print(f"Quantum Bit Error Rate (QBER): {qber*100:.2f}%")

    if eve_detected:
        print("⚠️ High QBER detected → Possible eavesdropping or noise!")
    else:
        print("✅ Secure channel → No significant eavesdropping detected.")

    if log:
        with open("qber_log.txt", "a") as f:
            f.write(f"{datetime.now()} | QBER={qber:.4f}, Errors={errors}, Eve={eve_detected}\n")

    if visualize:
        plt.figure(figsize=(6, 4))
        plt.bar(["Errors", "Correct"], [errors, sample_size - errors], color=["red", "green"])
        plt.title(f"QBER Visualization ({qber*100:.2f}%)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

    return {
        "qber": qber,
        "errors": errors,
        "sample_size": sample_size,
        "eve_detected": eve_detected
    }

def calibrate_threshold(noise_trials=100, noise_level=0.02):
    """
    Simulate clean channel noise to set adaptive QBER threshold.
    """
    qbers = []
    for _ in range(noise_trials):
        alice = np.random.randint(0, 2, 1000)
        bob = alice.copy()
        flip_indices = np.random.choice(1000, int(noise_level * 1000), replace=False)
        bob[flip_indices] = 1 - bob[flip_indices]
        qber = np.mean(alice != bob)
        qbers.append(qber)
    adaptive_threshold = np.mean(qbers) + 3 * np.std(qbers)
    print(f"Adaptive QBER threshold set to {adaptive_threshold*100:.2f}%")
    return adaptive_threshold

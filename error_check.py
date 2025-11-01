# error_check.py
# Estimate QBER and determine link security

import numpy as np

def check_errors(alice_key, bob_key):
    """Estimate QBER and determine if the link is secure."""
    key_len = len(alice_key)
    if key_len == 0:
        return 1.0, False

    sample_size = max(1, key_len // 5)
    sample_indices = np.random.choice(key_len, sample_size, replace=False)
    errors = np.sum(alice_key[sample_indices] != bob_key[sample_indices])
    qber = errors / sample_size

    print("\n============================================================")
    print("🔍 ERROR CHECKING (QBER Estimation)")
    print("============================================================")
    print(f"Key length: {key_len}")
    print(f"Sample size: {sample_size}")
    print(f"Errors detected: {errors}")
    print(f"Quantum Bit Error Rate (QBER): {qber*100:.2f}%")

    if qber < 0.11:
        print("✅ Secure channel → No significant eavesdropping detected.")
        secure = True
    else:
        print("⚠️ High QBER detected → Possible eavesdropping or noise!")
        secure = False

    return qber, secure

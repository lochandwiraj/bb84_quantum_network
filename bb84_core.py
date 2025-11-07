# bb84_core.py
import random

def generate_bits(n):
    return [random.randint(0, 1) for _ in range(n)]

def generate_bases(n):
    return [random.choice(["X", "Z"]) for _ in range(n)]

def measure(bits, prep_bases, meas_bases):
    measured = []
    for b, p, m in zip(bits, prep_bases, meas_bases):
        if p == m:
            measured.append(b)
        else:
            measured.append(random.randint(0, 1))
    return measured

def sift_keys(alice_bases, bob_bases, alice_bits, bob_bits):
    a_key, b_key, matched = [], [], []
    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            a_key.append(alice_bits[i])
            b_key.append(bob_bits[i])
            matched.append(i)
    return a_key, b_key, matched

def privacy_amplification(key, compression_ratio=0.5):
    if not key:
        return []
    target_len = max(1, int(len(key) * compression_ratio))
    out = []
    for i in range(target_len):
        x = 0
        for j in range(i, len(key), target_len):
            x ^= key[j]
        out.append(x)
    return out

def run_bb84_channel(n_qubits=10, eve_present=False, intercept_rate=0.5):
    """Full BB84 simulation returning metrics and keys."""
    alice_bits = generate_bits(n_qubits)
    alice_bases = generate_bases(n_qubits)
    bob_bases = generate_bases(n_qubits)
    transmitted = alice_bits[:]

    # Eve intercepts/resends some qubits
    if eve_present and intercept_rate > 0:
        eve_bases = generate_bases(n_qubits)
        eve_meas = measure(alice_bits, alice_bases, eve_bases)
        for i in range(n_qubits):
            if random.random() < intercept_rate:
                transmitted[i] = eve_meas[i]

    bob_meas = measure(transmitted, alice_bases, bob_bases)
    alice_key, bob_key, matched = sift_keys(alice_bases, bob_bases, alice_bits, bob_meas)

    if len(alice_key) == 0:
        return {
            "sender_key": [],
            "receiver_key": [],
            "error": 1.0,
            "secure": False,
            "basis_match_rate": 0,
            "eve_present": eve_present,
            "intercept_rate": intercept_rate,
            "key_length": 0
        }

    sample = max(1, len(alice_key)//2)
    indices = random.sample(range(len(alice_key)), sample)
    mismatches = sum(1 for i in indices if alice_key[i] != bob_key[i])
    qber = mismatches / sample

    a_final = privacy_amplification(alice_key)
    b_final = privacy_amplification(bob_key)

    threshold = 0.11
    secure = qber < threshold

    return {
        "sender_key": a_final,
        "receiver_key": b_final,
        "error": round(qber, 3),
        "secure": secure,
        "n_qubits": n_qubits,
        "basis_match_rate": round(len(matched)/n_qubits * 100, 2),
        "eve_present": eve_present,
        "intercept_rate": round(intercept_rate * 100, 2),
        "eve_detected": eve_present and not secure,
        "key_length": len(a_final)
    }

# network_sim.py
"""
Multi-party BB84 network simulator with RANDOM link compromise.
Alice -> {Bob, Charlie, Dave}
Randomly choose N links to be compromised (default 1).
"""

import numpy as np
import random

# ---------------------------
# Core BB84 helpers
# ---------------------------
def create_bb84_qubits(num_qubits):
    """Alice generates random bits and bases."""
    alice_bits = np.random.randint(0, 2, num_qubits).tolist()
    alice_bases = np.random.randint(0, 2, num_qubits).tolist()
    return alice_bits, alice_bases

def simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=False, intercept_rate=0.5):
    """
    Simulate transmission Alice -> Bob.
    If with_eve True, Eve intercepts each qubit with probability intercept_rate,
    measures in random basis, collapses state, and resends (classical simulation).
    Returns bob_results list.
    """
    bob_results = []
    n = len(alice_bits)
    for i in range(n):
        bit = alice_bits[i]
        base = alice_bases[i]

        # Eve intercepts sometimes
        if with_eve and random.random() < intercept_rate:
            eve_basis = random.randint(0, 1)
            # Eve measures: if same basis -> correct; else random bit
            measured = bit if eve_basis == base else random.randint(0, 1)
            # Eve re-sends measured bit encoded in her basis
            bit = measured
            base = eve_basis

        # Bob measures: if same basis as the (possibly re-prepared) qubit -> correct bit,
        # else random outcome.
        bob_bit = bit if bob_bases[i] == base else random.randint(0, 1)
        bob_results.append(bob_bit)

    return bob_results

def sift_key(alice_bits, alice_bases, bob_bases, bob_results):
    """
    Keep positions where Alice and Bob used the same basis.
    Returns (alice_key, bob_key, matching_indices)
    """
    matching = [i for i in range(len(alice_bases)) if alice_bases[i] == bob_bases[i]]
    alice_key = [alice_bits[i] for i in matching]
    bob_key   = [bob_results[i] for i in matching]
    return alice_key, bob_key, matching

def compute_qber(alice_key, bob_key):
    """Compute QBER (fraction, 0..1). If no bits, return 0.0."""
    if len(alice_key) == 0:
        return 0.0
    mismatches = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    return mismatches / len(alice_key)

# ---------------------------
# Error check (sampling model)
# ---------------------------
def check_errors(alice_key, bob_key, sample_fraction=0.2, threshold=0.11):
    """
    Randomly sample a fraction of sifted key to estimate QBER and detect Eve.
    Returns dictionary:
      { "qber": float (0..1), "errors": int, "sample_size": int, "eve_detected": bool }
    """
    n = len(alice_key)
    if n == 0:
        return {"qber": 0.0, "errors": 0, "sample_size": 0, "eve_detected": False}

    sample_size = max(1, int(sample_fraction * n))
    sample_indices = random.sample(range(n), sample_size)
    errors = sum(1 for i in sample_indices if alice_key[i] != bob_key[i])
    qber = errors / sample_size
    eve_detected = qber > threshold
    return {"qber": qber, "errors": errors, "sample_size": sample_size, "eve_detected": eve_detected}

# ---------------------------
# Network runner (randomly choose compromised links)
# ---------------------------
def run_quantum_network_random(num_qubits=100, intercept_rate=0.5, num_compromised=1, seed=None):
    """
    Run 3-party network. Randomly choose `num_compromised` links among [Bob,Charlie,Dave]
    to be attacked by Eve at intercept_rate.

    Returns results dict and prints a detailed human-readable report.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    links = ["Bob", "Charlie", "Dave"]
    # randomly pick which links are compromised
    compromised_links = set(random.sample(links, k=min(num_compromised, len(links))))

    print("=" * 50)
    print("QUANTUM NETWORK PROTOCOL STARTING")
    print("=" * 50)
    print()
    print(f"Alice prepared {num_qubits} qubits to distribute\n")

    # Alice prepares one set to send to all
    alice_bits, alice_bases = create_bb84_qubits(num_qubits)

    summary = []
    for recipient in links:
        eve_active = recipient in compromised_links

        print("-" * 50)
        if eve_active:
            print(f"SESSION: Alice → {recipient} (Eve intercepting!)")
            print("-" * 50)
            print(f"⚠️  Eve will intercept this link at {int(intercept_rate*100)}% rate")
        else:
            print(f"SESSION: Alice → {recipient} (No interference)")
            print("-" * 50)

        # Bob/recipient chooses bases independently
        rec_bases = np.random.randint(0, 2, num_qubits).tolist()

        # simulate transmission (Eve only if eve_active)
        rec_results = simulate_transmission_with_eve(
            alice_bits, alice_bases, rec_bases, with_eve=eve_active, intercept_rate=intercept_rate
        )

        # sift keys
        a_key, r_key, matching = sift_key(alice_bits, alice_bases, rec_bases, rec_results)

        # compute exact QBER on entire sifted key (for reporting)
        qber_full = compute_qber(a_key, r_key) * 100  # percent

        # run sampled error-check (public test) with defaults
        check = check_errors(a_key, r_key, sample_fraction=0.2, threshold=0.11)

        # interpret status (use sampled detection to mimic protocol)
        status = "✅ SECURE" if not check["eve_detected"] else "❌ COMPROMISED"

        # print session summary
        print(f"{recipient} error rate: {qber_full:.1f}%")
        print(f"{recipient} final key length: {len(a_key)} bits")
        print(f"Status: {status}")
        print()

        summary.append({
            "recipient": recipient,
            "eve_active": eve_active,
            "qber_full": qber_full,
            "sample_qber": check["qber"] * 100,
            "sample_errors": check["errors"],
            "sample_size": check["sample_size"],
            "final_key_len": len(a_key),
            "status": status
        })

    # network summary
    print("=" * 50)
    print("NETWORK SECURITY SUMMARY")
    print("=" * 50)
    print()
    total = len(summary)
    secure_count = sum(1 for s in summary if s["status"].startswith("✅"))
    compromised_count = total - secure_count
    security_percentage = (secure_count / total) * 100

    print(f"Total Links:        {total}")
    print(f"Secure Links:       {secure_count} ({security_percentage:.1f}%)")
    print(f"Compromised Links:  {compromised_count} ({100-security_percentage:.1f}%)\n")

    print("Link Details:")
    for s in summary:
        sym = "✅" if s["status"].startswith("✅") else "❌"
        print(f"  Alice → {s['recipient']}:   {sym} {s['qber_full']:.1f}% error (key {s['final_key_len']} bits)")

    if compromised_count > 0:
        compromised_names = ", ".join([s["recipient"] for s in summary if s["status"].startswith("❌")])
        print(f"\n🚨 EAVESDROPPER DETECTED on {compromised_names}'s link!")

    # return full structured data for further processing if needed
    return {
        "num_qubits": num_qubits,
        "intercept_rate": intercept_rate,
        "compromised_links": list(compromised_links),
        "summary": summary,
        "security_percentage": security_percentage
    }

# ---------------------------
# CLI runner
# ---------------------------
if __name__ == "__main__":
    # Example: randomize 1 compromised link (default)
    # Change num_compromised to 2 or 3 to compromise more links randomly
    result = run_quantum_network_random(num_qubits=100, intercept_rate=0.5, num_compromised=1, seed=None)

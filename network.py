# network.py — multi-party network simulation (random compromised links)
import numpy as np
import random
from bb84_core import create_bb84_circuit, simulate_transmission_with_eve, sift_key
from error_check import check_errors

def run_quantum_network_random(num_qubits=100, intercept_rate=0.5, num_compromised=1, seed=None):
    """
    Run 3-party network. Randomly choose `num_compromised` links among [Bob,Charlie,Dave]
    to be attacked by Eve at intercept_rate.
    Returns a structured results dict and prints report.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    links = ["Bob", "Charlie", "Dave"]
    compromised_links = set(random.sample(links, k=min(num_compromised, len(links))))

    print("=" * 50)
    print("QUANTUM NETWORK PROTOCOL STARTING")
    print("=" * 50)
    print()
    print(f"Alice prepared {num_qubits} qubits to distribute\n")

    alice_bits, alice_bases = create_bb84_circuit(num_qubits)
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

        rec_bases = np.random.randint(0, 2, num_qubits).tolist()

        rec_results = simulate_transmission_with_eve(
            alice_bits, alice_bases, rec_bases, with_eve=eve_active, intercept_rate=intercept_rate
        )

        a_key, r_key, matching = sift_key(alice_bits, alice_bases, rec_bases, rec_results)
        qber_full = (sum(1 for x,y in zip(a_key, r_key) if x!=y) / len(a_key) * 100) if len(a_key) > 0 else 0.0

        check = check_errors(a_key, r_key, sample_fraction=0.2, threshold=0.11)
        status = "✅ SECURE" if not check["eve_detected"] else "❌ COMPROMISED"

        print(f"{recipient} error rate: {qber_full:.1f}%")
        print(f"{recipient} final key length: {len(a_key)} bits")
        print(f"Status: {status}\n")

        summary.append({
            "recipient": recipient,
            "eve_active": eve_active,
            "qber_full": qber_full,
            "sample_qber": check["qber"] * 100,
            "errors_sampled": check["errors"],
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
    print()

    return {
        "num_qubits": num_qubits,
        "intercept_rate": intercept_rate,
        "compromised_links": list(compromised_links),
        "summary": summary,
        "security_percentage": security_percentage
    }

# Backwards-compatible alias so old calls to run_quantum_network work
run_quantum_network = run_quantum_network_random

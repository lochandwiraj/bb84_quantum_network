# network.py
# Multi-party quantum network simulation with random eavesdropper

import numpy as np
from alice import prepare_qubits
from bb84_core import create_bb84_circuit, sift_key, eve_intercept
from error_check import check_errors

def run_quantum_network_random(n_qubits=100, eve_intercept_rate=0.5):
    """Run 3-party BB84 network with random eavesdropper."""
    print("Running 3-party quantum network with random eavesdropper...\n")
    print("==================================================")
    print("QUANTUM NETWORK SIMULATION")
    print("==================================================")

    # Step 1: Alice prepares qubits
    alice_bits, alice_bases = prepare_qubits(n_qubits)

    # Step 2: Choose one random victim
    participants = ["Bob", "Charlie", "Dave"]
    compromised = np.random.choice(participants)
    print(f"\nEve will attempt to intercept on Alice → {compromised}.\n")

    results = {}
    for receiver in participants:
        eve_active = receiver == compromised

        print("--------------------------------------------------")
        print(f"SESSION: Alice → {receiver} {'(EVE)' if eve_active else '(CLEAN)'}")
        print("--------------------------------------------------")

        receiver_bases = np.random.randint(0, 2, n_qubits)

        if eve_active:
            transmitted_bits = eve_intercept(alice_bits, alice_bases, eve_intercept_rate)
        else:
            transmitted_bits = np.copy(alice_bits)

        receiver_results = create_bb84_circuit(transmitted_bits, alice_bases, receiver_bases, n_qubits)
        alice_key, receiver_key = sift_key(alice_bits, alice_bases, receiver_bases, receiver_results)
        qber, secure = check_errors(alice_key, receiver_key)

        results[receiver] = {
            'error_rate': qber * 100,
            'key_length': len(receiver_key),
            'secure': secure,
            'eve_active': eve_active
        }

        print(f"{receiver} error rate: {qber*100:.2f}% | Key length: {len(receiver_key)} | {'✅ SECURE' if secure else '❌ COMPROMISED'}\n")

    # Step 3: Compute summary
    total_links = len(participants)
    secure_links = sum(1 for r in results.values() if r['secure'])
    compromised_links = total_links - secure_links

    print("\n==================================================")
    print("NETWORK SECURITY SUMMARY")
    print("==================================================")
    print(f"Total Links:        {total_links}")
    print(f"Secure Links:       {secure_links} ({secure_links/total_links*100:.1f}%)")
    print(f"Compromised Links:  {compromised_links} ({compromised_links/total_links*100:.1f}%)\n")

    for r in participants:
        status = "✅" if results[r]['secure'] else "❌"
        print(f"Alice → {r:<8} {status}  {results[r]['error_rate']:.1f}% error")

    attacked = [r for r, v in results.items() if v['eve_active']]
    if attacked:
        print(f"\n🚨 Eavesdropper was active on: Alice → {attacked[0]}")
    print("==================================================")

    return results

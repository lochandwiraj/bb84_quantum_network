# network.py — multi-party network simulation
import numpy as np
import random
from bb84_core import create_bb84_circuit, simulate_transmission_with_eve, sift_key
from error_check import check_errors

def run_quantum_network(num_qubits=100, eve_intercept_rate=0.5):
    """
    Hour 10: Run 3 parallel sessions:
    - Alice -> Bob (clean)
    - Alice -> Charlie (Eve intercepts here)
    - Alice -> Dave (clean)
    """
    print("=" * 50)
    print("QUANTUM NETWORK PROTOCOL STARTING")
    print("=" * 50)
    print()
    # Alice prepares one set to broadcast
    alice_bits, alice_bases = create_bb84_circuit(num_qubits)
    print(f"Alice prepared {num_qubits} qubits to distribute\n")

    results = {}

    # Session 1: Bob (clean)
    print("-" * 50)
    print("SESSION 1: Alice → Bob (No interference)")
    print("-" * 50)
    bob_bases = np.random.randint(0, 2, num_qubits).tolist()
    bob_results = simulate_transmission_with_eve(alice_bits, alice_bases, bob_bases, with_eve=False)
    alice_key_bob, bob_key, _ = sift_key(alice_bits, alice_bases, bob_bases, bob_results)
    bob_check = check_errors(alice_key_bob, bob_key)
    bob_error = bob_check["qber"]
    bob_final_key = bob_check["alice_final_key"]
    bob_secure = not bob_check["eve_detected"]
    print(f"Bob error rate: {bob_error*100:.1f}%")
    print(f"Bob final key length: {len(bob_final_key)} bits")
    print(f"Status: {'✅ SECURE' if bob_secure else '❌ COMPROMISED'}\n")

    results['bob'] = {"error_rate": bob_error, "key_length": len(bob_final_key), "secure": bob_secure}

    # Session 2: Charlie (Eve attacks)
    print("-" * 50)
    print("SESSION 2: Alice → Charlie (Eve intercepting!)")
    print("-" * 50)
    charlie_bases = np.random.randint(0, 2, num_qubits).tolist()
    # corrupt with Eve
    charlie_results = simulate_transmission_with_eve(alice_bits, alice_bases, charlie_bases, with_eve=True, intercept_rate=eve_intercept_rate)
    alice_key_charlie, charlie_key, _ = sift_key(alice_bits, alice_bases, charlie_bases, charlie_results)
    charlie_check = check_errors(alice_key_charlie, charlie_key)
    charlie_error = charlie_check["qber"]
    charlie_final_key = charlie_check["alice_final_key"]
    charlie_secure = not charlie_check["eve_detected"]
    print(f"⚠️  Eve intercepted {int(eve_intercept_rate * num_qubits)} qubits")
    print(f"Charlie error rate: {charlie_error*100:.1f}%")
    print(f"Charlie final key length: {len(charlie_final_key)} bits")
    print(f"Status: {'✅ SECURE' if charlie_secure else '❌ COMPROMISED'}\n")

    results['charlie'] = {"error_rate": charlie_error, "key_length": len(charlie_final_key), "secure": charlie_secure}

    # Session 3: Dave (clean)
    print("-" * 50)
    print("SESSION 3: Alice → Dave (No interference)")
    print("-" * 50)
    dave_bases = np.random.randint(0, 2, num_qubits).tolist()
    dave_results = simulate_transmission_with_eve(alice_bits, alice_bases, dave_bases, with_eve=False)
    alice_key_dave, dave_key, _ = sift_key(alice_bits, alice_bases, dave_bases, dave_results)
    dave_check = check_errors(alice_key_dave, dave_key)
    dave_error = dave_check["qber"]
    dave_final_key = dave_check["alice_final_key"]
    dave_secure = not dave_check["eve_detected"]
    print(f"Dave error rate: {dave_error*100:.1f}%")
    print(f"Dave final key length: {len(dave_final_key)} bits")
    print(f"Status: {'✅ SECURE' if dave_secure else '❌ COMPROMISED'}\n")

    results['dave'] = {"error_rate": dave_error, "key_length": len(dave_final_key), "secure": dave_secure}

    # network summary
    secure_count = sum(1 for v in results.values() if v['secure'])
    print("\n" + "=" * 50)
    print("NETWORK SECURITY SUMMARY")
    print("=" * 50)
    print()
    print(f"Total Links:        3")
    print(f"Secure Links:       {secure_count} ({(secure_count/3)*100:.1f}%)")
    print(f"Compromised Links:  {3-secure_count} ({(100 - (secure_count/3)*100):.1f}%)\n")
    print("Link Details:")
    print(f"  Alice → Bob:     {'✅' if results['bob']['secure'] else '❌'} {results['bob']['error_rate']*100:.1f}% error")
    print(f"  Alice → Charlie: {'✅' if results['charlie']['secure'] else '❌'} {results['charlie']['error_rate']*100:.1f}% error")
    print(f"  Alice → Dave:    {'✅' if results['dave']['secure'] else '❌'} {results['dave']['error_rate']*100:.1f}% error")
    if not results['charlie']['secure']:
        print(f"\n🚨 EAVESDROPPER DETECTED on Charlie's link!")

    return results


def run_quantum_network_random(num_qubits=100, intercept_rate=0.5, num_compromised=1, seed=None):
    """
    Random-compromise variant: randomly choose num_compromised recipients to attack.
    Returns results dict with list of which were compromised.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    links = ["Bob", "Charlie", "Dave"]
    compromised = set(random.sample(links, k=min(num_compromised, len(links))))
    print(f"Randomly compromising: {compromised}")
    # reuse run_quantum_network logic but pass which link to attack
    # We will run similar flows but pick eve_active based on compromised set.
    print("=" * 50)
    print("QUANTUM NETWORK PROTOCOL STARTING (RANDOM COMPROMISE)")
    print("=" * 50)
    print()
    alice_bits, alice_bases = create_bb84_circuit(num_qubits)
    summary = {}

    for recipient in links:
        eve_active = recipient in compromised
        print("-" * 50)
        print(f"SESSION: Alice → {recipient} ({'EVE' if eve_active else 'CLEAN'})")
        print("-" * 50)
        rec_bases = np.random.randint(0, 2, num_qubits).tolist()
        rec_results = simulate_transmission_with_eve(alice_bits, alice_bases, rec_bases, with_eve=eve_active, intercept_rate=intercept_rate)
        a_key, r_key, _ = sift_key(alice_bits, alice_bases, rec_bases, rec_results)
        check = check_errors(a_key, r_key)
        summary[recipient.lower()] = {
            "error_rate": check["qber"],
            "key_length": len(check["alice_final_key"]),
            "secure": not check["eve_detected"]
        }
        print(f"{recipient} error rate: {check['qber']*100:.1f}%")
        print(f"{recipient} final key length: {len(check['alice_final_key'])} bits")
        print(f"Status: {'✅ SECURE' if not check['eve_detected'] else '❌ COMPROMISED'}\n")

    secure_count = sum(1 for v in summary.values() if v['secure'])
    print("="*50)
    print("NETWORK SUMMARY (RANDOM)")
    print("="*50)
    print(f"Secure Links: {secure_count}/3")
    return {"compromised": list(compromised), "summary": summary, "security_percentage": (secure_count/3)*100}


# Backwards-compatible alias
run_quantum_network_alias = run_quantum_network
run_quantum_network_random_alias = run_quantum_network_random

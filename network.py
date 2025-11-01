import random
from alice import Alice
from bb84_core import generate_bases, measure, sift_keys
from error_check import estimate_error_rate, is_secure

def run_bb84_channel(n_qubits, eve_present=False, intercept_rate=0.5):
    alice = Alice(n_qubits)
    qubits = alice.send_qubits()

    if eve_present:
        intercepted = []
        for bit, base in qubits:
            if random.random() < intercept_rate:
                eve_base = random.choice(['X', 'Z'])
                eve_measured_bit = bit if base == eve_base else random.randint(0, 1)
                intercepted.append((eve_measured_bit, eve_base))
            else:
                intercepted.append((bit, base))
        qubits = intercepted

    receiver_bases = generate_bases(n_qubits)
    measured_bits = measure(
        [b for b, _ in qubits],
        [base for _, base in qubits],
        receiver_bases
    )

    sender_key, receiver_key = sift_keys(alice.bases, receiver_bases, alice.bits, measured_bits)
    error_rate = estimate_error_rate(sender_key, receiver_key)

    return {
        "sender_key": sender_key,
        "receiver_key": receiver_key,
        "error": error_rate,
        "secure": is_secure(error_rate)
    }

def run_quantum_network(n_qubits=100, intercept_rate=0.5):
    participants = ["Bob", "Charlie", "Dave"]
    compromised_target = random.choice(participants)
    print(f"\n🚨 Eve is attempting to intercept communication with: {compromised_target}")

    results = {}
    link_status = {}

    for person in participants:
        eve_present = (person == compromised_target)
        result = run_bb84_channel(n_qubits, eve_present, intercept_rate)
        results[person] = result
        link_status[f"alice_to_{person.lower()}"] = {
            "error": result["error"],
            "secure": result["secure"]
        }

    print("\n🔒 Quantum Network Status:")
    for name, result in results.items():
        status = "✅ Secure" if result["secure"] else "❌ Compromised"
        print(f"  Alice ↔ {name}: {status} | Error rate = {result['error']:.2%}")

    return {"link_status": link_status, "results": results}

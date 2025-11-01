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
    """
    Runs a 3-party quantum network with optional eavesdropping on one link.
    Returns comprehensive statistics and formatted output.
    """
    participants = ["Bob", "Charlie", "Dave"]
    compromised_target = random.choice(participants)
    print(f"\n🚨 Eve is attempting to intercept communication with: {compromised_target}")

    results = {}
    link_status = {}

    # Run BB84 for each participant
    for person in participants:
        eve_present = (person == compromised_target)
        result = run_bb84_channel(n_qubits, eve_present, intercept_rate)
        results[person] = result
        link_status[f"alice_to_{person.lower()}"] = {
            "error": result["error"],
            "secure": result["secure"]
        }

    # Calculate aggregate statistics
    total_links = len(participants)
    secure_links = sum(1 for r in results.values() if r["secure"])
    compromised_links = total_links - secure_links
    security_percentage = (secure_links / total_links) * 100

    # Build complete results dictionary
    network_results = {
        'total_links': total_links,
        'secure_links': secure_links,
        'compromised_links': compromised_links,
        'security_percentage': round(security_percentage, 1),
        'link_status': link_status
    }

    # Print formatted summary
    print_network_summary(network_results)

    return network_results

def print_network_summary(results):
    """Prints a beautifully formatted network security summary."""
    print("\n╔═══════════════════════════════════╗")
    print("║   QUANTUM NETWORK SECURITY        ║")
    print("╠═══════════════════════════════════╣")
    print(f"║ Total Links:        {results['total_links']}             ║")
    print(f"║ Secure Links:       {results['secure_links']} ({results['security_percentage']:.1f}%)     ║")
    print(f"║ Compromised Links:  {results['compromised_links']} ({100-results['security_percentage']:.1f}%)     ║")
    print("║                                   ║")
    
    # Print individual link status
    for link_name, status in results['link_status'].items():
        participant = link_name.split('_')[-1].capitalize()
        error_pct = status['error'] * 100
        symbol = "✅" if status['secure'] else "❌"
        
        # Format with proper spacing
        link_str = f"Alice → {participant}:"
        print(f"║ {link_str:<20} {symbol} {error_pct:>4.1f}% error    ║")
    
    print("╚═══════════════════════════════════╝\n")

def get_network_stats_dict(results):
    """
    Returns the raw statistics dictionary for programmatic access.
    Useful for further processing or API responses.
    """
    return {
        'total_links': results['total_links'],
        'secure_links': results['secure_links'],
        'compromised_links': results['compromised_links'],
        'security_percentage': results['security_percentage'],
        'link_status': results['link_status']
    }


if __name__ == "__main__":
    print("🔐 BB84 Quantum Network Simulation")
    print("=" * 50)
    
    # Run the network with 50% eavesdropping rate
    network_results = run_quantum_network(n_qubits=100, intercept_rate=0.5)
    
    # Also print the raw dictionary format
    print("\n📊 Raw Results Dictionary:")
    print(network_results)
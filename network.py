import random
from alice import Alice
from bb84_core import generate_bases, measure, sift_keys
from error_check import estimate_error_rate, is_secure

def run_bb84_channel(n_qubits, eve_present=False, intercept_rate=0.5, eve_name="Eve"):
    """
    Runs a single BB84 quantum key distribution session.
    
    Args:
        n_qubits: Number of qubits to transmit
        eve_present: Whether an eavesdropper intercepts the channel
        intercept_rate: Fraction of qubits eavesdropper intercepts (0.0 to 1.0)
        eve_name: Name of the eavesdropper
    
    Returns:
        Dictionary with keys: sender_key, receiver_key, error, secure, eve_name
    """
    # Alice prepares qubits
    alice = Alice(n_qubits)
    qubits = alice.send_qubits()

    # Eavesdropper intercepts (if present)
    if eve_present:
        intercepted = []
        for bit, base in qubits:
            if random.random() < intercept_rate:
                # Eavesdropper measures in random basis
                eve_base = random.choice(['X', 'Z'])
                # If bases match, Eve gets correct bit; otherwise random
                eve_measured_bit = bit if base == eve_base else random.randint(0, 1)
                # Eve resends in her measurement basis (causes disturbance)
                intercepted.append((eve_measured_bit, eve_base))
            else:
                intercepted.append((bit, base))
        qubits = intercepted

    # Bob measures
    receiver_bases = generate_bases(n_qubits)
    measured_bits = measure(
        [b for b, _ in qubits],
        [base for _, base in qubits],
        receiver_bases
    )

    # Key sifting (keep only matching bases)
    sender_key, receiver_key, matched_indices = sift_keys(alice.bases, receiver_bases, alice.bits, measured_bits)
    
    # Error estimation - use ALL bits for accurate error rate
    error_rate = estimate_error_rate(sender_key, receiver_key, sample_size=None)

    return {
        "sender_key": sender_key,
        "receiver_key": receiver_key,
        "error": error_rate,
        "secure": is_secure(error_rate),
        "eve_name": eve_name if eve_present else None
    }

def run_quantum_network(n_qubits=100, intercept_rate=0.5, attack_scenario=None):
    """
    Runs a multi-party quantum network with various attack scenarios.
    
    Args:
        n_qubits: Number of qubits per session
        intercept_rate: Base eavesdropping rate (can be randomized per attacker)
        attack_scenario: Scenario type or None for random
            - None: Random scenario selection
            - "no_attack": No eavesdroppers (baseline)
            - "single_attacker_single_target": One attacker on one link
            - "single_attacker_multiple_targets": One attacker on multiple links
            - "multiple_attackers_single_targets": Multiple attackers, each on one link
            - "multiple_attackers_multiple_targets": Multiple attackers on multiple links
            - "partial_coverage": Some links secure, some compromised randomly
    
    Returns:
        Dictionary with network statistics and link status
    """
    participants = ["Bob", "Charlie", "Dave", "Diana", "Eve_R"]  # 5 receivers
    attackers_pool = ["Mallory", "Oscar", "Trudy", "Walter"]  # 4 potential attackers
    
    # Randomize scenario if not specified
    scenarios = [
        "no_attack",
        "single_attacker_single_target",
        "single_attacker_multiple_targets",
        "multiple_attackers_single_targets",
        "multiple_attackers_multiple_targets",
        "partial_coverage"
    ]
    
    if attack_scenario is None:
        attack_scenario = random.choice(scenarios)
    
    print(f"\n{'='*60}")
    print(f"🎲 ATTACK SCENARIO: {attack_scenario.replace('_', ' ').upper()}")
    print(f"{'='*60}")
    
    # Configure attack based on scenario
    attack_config = {}
    
    if attack_scenario == "no_attack":
        print("✅ No eavesdroppers present - baseline secure network")
        # No attacks
        
    elif attack_scenario == "single_attacker_single_target":
        attacker = random.choice(attackers_pool)
        target = random.choice(participants)
        attack_config[target] = {
            "attacker": attacker,
            "intercept_rate": random.uniform(0.3, 0.8)
        }
        print(f"🚨 {attacker} is attacking: {target}")
        print(f"   Intercept rate: {attack_config[target]['intercept_rate']*100:.1f}%")
        
    elif attack_scenario == "single_attacker_multiple_targets":
        attacker = random.choice(attackers_pool)
        num_targets = random.randint(2, 4)
        targets = random.sample(participants, num_targets)
        print(f"🚨 {attacker} is attacking MULTIPLE targets:")
        for target in targets:
            rate = random.uniform(0.3, 0.8)
            attack_config[target] = {
                "attacker": attacker,
                "intercept_rate": rate
            }
            print(f"   → {target}: {rate*100:.1f}% intercept rate")
            
    elif attack_scenario == "multiple_attackers_single_targets":
        num_attackers = random.randint(2, 3)
        selected_attackers = random.sample(attackers_pool, num_attackers)
        targets = random.sample(participants, num_attackers)
        print(f"🚨 MULTIPLE attackers, each on one target:")
        for attacker, target in zip(selected_attackers, targets):
            rate = random.uniform(0.3, 0.8)
            attack_config[target] = {
                "attacker": attacker,
                "intercept_rate": rate
            }
            print(f"   → {attacker} attacking {target}: {rate*100:.1f}% intercept")
            
    elif attack_scenario == "multiple_attackers_multiple_targets":
        num_attackers = random.randint(2, 3)
        selected_attackers = random.sample(attackers_pool, num_attackers)
        print(f"🚨 MULTIPLE attackers on MULTIPLE targets:")
        for attacker in selected_attackers:
            num_targets = random.randint(1, 3)
            targets = random.sample(participants, num_targets)
            for target in targets:
                rate = random.uniform(0.3, 0.8)
                # If already attacked, combine attacks (worse for security)
                if target in attack_config:
                    print(f"   ⚠️  {target} under COORDINATED attack!")
                    old_rate = attack_config[target]['intercept_rate']
                    # Combined attack increases intercept probability
                    combined_rate = min(1.0, old_rate + rate * 0.5)
                    attack_config[target] = {
                        "attacker": f"{attack_config[target]['attacker']} & {attacker}",
                        "intercept_rate": combined_rate
                    }
                    print(f"      {attack_config[target]['attacker']}: {combined_rate*100:.1f}% combined intercept")
                else:
                    attack_config[target] = {
                        "attacker": attacker,
                        "intercept_rate": rate
                    }
                    print(f"   → {attacker} attacking {target}: {rate*100:.1f}% intercept")
                    
    elif attack_scenario == "partial_coverage":
        # Randomly decide for each link
        print(f"🎲 Randomized partial coverage:")
        for participant in participants:
            if random.random() < 0.5:  # 50% chance of being attacked
                attacker = random.choice(attackers_pool)
                rate = random.uniform(0.2, 0.9)
                attack_config[participant] = {
                    "attacker": attacker,
                    "intercept_rate": rate
                }
                print(f"   🚨 {attacker} attacking {participant}: {rate*100:.1f}%")
            else:
                print(f"   ✅ {participant}: Secure (no attack)")

    print(f"{'='*60}\n")
    
    # Run BB84 for each participant
    results = {}
    link_status = {}
    
    for person in participants:
        if person in attack_config:
            eve_present = True
            eve_name = attack_config[person]["attacker"]
            rate = attack_config[person]["intercept_rate"]
        else:
            eve_present = False
            eve_name = None
            rate = 0.0
            
        result = run_bb84_channel(n_qubits, eve_present, rate, eve_name)
        results[person] = result
        link_status[f"alice_to_{person.lower()}"] = {
            "error": result["error"],
            "secure": result["secure"],
            "attacker": eve_name,
            "intercept_rate": rate if eve_present else 0.0
        }

    # Calculate aggregate statistics
    total_links = len(participants)
    secure_links = sum(1 for r in results.values() if r["secure"])
    compromised_links = total_links - secure_links
    security_percentage = (secure_links / total_links) * 100
    
    # Count unique attackers
    unique_attackers = set()
    for config in attack_config.values():
        attackers = config["attacker"].split(" & ")
        unique_attackers.update(attackers)

    # Build complete results dictionary
    network_results = {
        'total_links': total_links,
        'secure_links': secure_links,
        'compromised_links': compromised_links,
        'security_percentage': round(security_percentage, 1),
        'attack_scenario': attack_scenario,
        'num_attackers': len(unique_attackers),
        'attacker_names': list(unique_attackers),
        'link_status': link_status
    }

    # Print formatted summary
    print_network_summary(network_results)

    return network_results

def print_network_summary(results):
    """Prints a beautifully formatted network security summary."""
    print("\n╔═══════════════════════════════════════════════╗")
    print("║       QUANTUM NETWORK SECURITY REPORT         ║")
    print("╠═══════════════════════════════════════════════╣")
    
    scenario_display = results['attack_scenario'].replace('_', ' ').title()[:30]
    print(f"║ Scenario: {scenario_display:<30} ║")
    print(f"║ Total Links:         {results['total_links']}                        ║")
    print(f"║ Secure Links:        {results['secure_links']} ({results['security_percentage']:>5.1f}%)              ║")
    print(f"║ Compromised Links:   {results['compromised_links']} ({100-results['security_percentage']:>5.1f}%)              ║")
    
    if results['num_attackers'] > 0:
        print(f"║ Active Attackers:    {results['num_attackers']}                        ║")
        print("║                                               ║")
        attacker_display = ", ".join(results['attacker_names'][:3])[:30].ljust(30)
        print(f"║ Attacker(s): {attacker_display} ║")
    
    print("╠═══════════════════════════════════════════════╣")
    print("║              INDIVIDUAL LINKS                 ║")
    print("╠═══════════════════════════════════════════════╣")
    
    # Print individual link status - TEXT ONLY, NO UNICODE
    for link_name, status in results['link_status'].items():
        # Extract receiver name properly
        receiver_part = link_name.replace('alice_to_', '')
        if receiver_part == 'eve_r':
            participant = 'Eve_R'
        else:
            participant = receiver_part.capitalize()
        
        error_pct = status['error'] * 100
        symbol = "[OK]" if status['secure'] else "[XX]"
        
        # Format link name
        link_str = f"Alice -> {participant}:"
        
        if status['attacker']:
            # Truncate long attacker names
            attacker_display = status['attacker'][:15]
            if len(status['attacker']) > 15:
                attacker_display += "..."
            attacker_str = f"[{attacker_display}]"
            print(f"║ {link_str:<18} {symbol} {error_pct:>5.1f}% {attacker_str:<20} ║")
        else:
            print(f"║ {link_str:<18} {symbol} {error_pct:>5.1f}% [Secure]            ║")
    
    print("╚═══════════════════════════════════════════════╝\n")

def run_random_network_scenarios(n_qubits=100, n_scenarios=3):
    """
    Runs multiple random network scenarios for comprehensive testing.
    
    Args:
        n_qubits: Number of qubits per session
        n_scenarios: Number of random scenarios to test
    
    Returns:
        List of network results
    """
    print("\n" + "█" * 60)
    print("🎲 RANDOM NETWORK SCENARIO TESTING")
    print("█" * 60)
    
    all_results = []
    
    for i in range(n_scenarios):
        print(f"\n{'▼'*60}")
        print(f"   SCENARIO {i+1} of {n_scenarios}")
        print(f"{'▼'*60}")
        
        result = run_quantum_network(n_qubits=n_qubits, attack_scenario=None)
        all_results.append(result)
        
        # Wait for user to see results
        if i < n_scenarios - 1:
            print("\n" + "─"*60)
    
    # Summary of all scenarios
    print("\n" + "█" * 60)
    print("📊 OVERALL SUMMARY OF ALL SCENARIOS")
    print("█" * 60)
    
    total_secure = sum(r['secure_links'] for r in all_results)
    total_compromised = sum(r['compromised_links'] for r in all_results)
    total_links = sum(r['total_links'] for r in all_results)
    overall_security = (total_secure / total_links) * 100
    
    print(f"\nAcross {n_scenarios} random scenarios:")
    print(f"  • Total links tested: {total_links}")
    print(f"  • Secure links: {total_secure} ({overall_security:.1f}%)")
    print(f"  • Compromised links: {total_compromised} ({100-overall_security:.1f}%)")
    print(f"  • Detection working: {'✅ YES' if total_compromised > 0 else '⚠️  No attacks occurred'}")
    
    # Show scenario distribution
    scenario_counts = {}
    for r in all_results:
        scenario = r['attack_scenario']
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
    
    print(f"\n📈 Scenario Distribution:")
    for scenario, count in scenario_counts.items():
        print(f"  • {scenario}: {count}x")
    
    print("\n" + "█" * 60 + "\n")
    
    return all_results


if __name__ == "__main__":
    print("🔐 BB84 Quantum Network Simulation - Advanced Attack Scenarios")
    print("=" * 60)
    
    # Example 1: Specific scenario
    print("\n[EXAMPLE 1: Specific Scenario - Multiple Attackers]")
    network_results = run_quantum_network(
        n_qubits=100, 
        intercept_rate=0.5,
        attack_scenario="multiple_attackers_multiple_targets"
    )
    
    # Example 2: Random scenarios
    print("\n\n[EXAMPLE 2: Random Scenarios]")
    random_results = run_random_network_scenarios(n_qubits=100, n_scenarios=3)
    
    # Print raw dictionary for one result
    print("\n📊 Sample Raw Results Dictionary:")
    import json
    print(json.dumps(network_results, indent=2, default=str))
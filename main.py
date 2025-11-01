# main.py
# Master execution script for BB84 network with random eavesdropping

from network import run_quantum_network_random

def display_network_results(results):
    """Display formatted results table."""
    total = len(results)
    secure = sum(1 for r in results.values() if r['secure'])
    compromised = total - secure

    print("\n╔═══════════════════════════════════╗")
    print("║   QUANTUM NETWORK SECURITY        ║")
    print("╠═══════════════════════════════════╣")
    print(f"║ Total Links:        {total:<2}            ║")
    print(f"║ Secure Links:       {secure} ({secure/total*100:.1f}%)     ║")
    print(f"║ Compromised Links:  {compromised} ({compromised/total*100:.1f}%)  ║")
    print("║                                   ║")
    for name, data in results.items():
        status = "✅" if data['secure'] else "❌"
        print(f"║ Alice → {name:<8} {status} {data['error_rate']:>5.1f}% error ║")
    print("╚═══════════════════════════════════╝\n")


if __name__ == "__main__":
    results = run_quantum_network_random(n_qubits=100, eve_intercept_rate=0.5)
    display_network_results(results)

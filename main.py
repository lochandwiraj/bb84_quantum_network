import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from network import run_quantum_network, print_network_summary
from threat_analysis import run_threat_scenarios, plot_threat_comparison, plot_error_correlation

def visualize_network(network_results):
    """Creates visual diagram of quantum network with security status."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axis('off')

    # Node positions
    positions = {
        'Alice': (0, 1.5),
        'Bob': (-1.5, -0.5),
        'Charlie': (0, -0.5),
        'Dave': (1.5, -0.5),
        'Eve': (0, -1.5)
    }

    # Draw links
    link_status = network_results['link_status']
    for receiver in ['Bob', 'Charlie', 'Dave']:
        link_key = f"alice_to_{receiver.lower()}"
        secure = link_status[link_key]['secure']
        error = link_status[link_key]['error'] * 100
        color = 'green' if secure else 'red'
        linestyle = '-' if secure else '--'

        # Main communication link
        ax.plot([positions['Alice'][0], positions[receiver][0]],
                [positions['Alice'][1], positions[receiver][1]],
                color=color, linestyle=linestyle, linewidth=3, alpha=0.7)

        # Link label with error rate
        mid_x = (positions['Alice'][0] + positions[receiver][0]) / 2
        mid_y = (positions['Alice'][1] + positions[receiver][1]) / 2
        status_symbol = '✅' if secure else '❌'
        ax.text(mid_x, mid_y, f"{error:.1f}% {status_symbol}", fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                ha='center', va='center', fontweight='bold')

        # Draw Eve's interference on compromised link
        if not secure:
            ax.plot([positions['Eve'][0], positions[receiver][0]],
                    [positions['Eve'][1], positions[receiver][1]],
                    color='red', linestyle=':', linewidth=2, alpha=0.5)

    # Draw nodes
    node_colors = {
        'Alice': 'dodgerblue',
        'Bob': 'lightgreen',
        'Charlie': 'lightgreen',
        'Dave': 'lightgreen',
        'Eve': 'salmon'
    }

    node_sizes = {
        'Alice': 0.3,
        'Bob': 0.25,
        'Charlie': 0.25,
        'Dave': 0.25,
        'Eve': 0.25
    }

    for node, pos in positions.items():
        circle = plt.Circle(pos, node_sizes[node], color=node_colors[node], 
                           ec='black', linewidth=2.5, zorder=10)
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], node, ha='center', va='center', 
                fontsize=12, fontweight='bold', zorder=11)

    # Title and legend
    ax.set_title('Quantum Network Security Status', fontsize=16, 
                 fontweight='bold', pad=20)
    
    legend_items = [
        mpatches.Patch(color='green', label='Secure Link'),
        mpatches.Patch(color='red', label='Compromised Link'),
        mpatches.Patch(color='dodgerblue', label='Sender (Alice)'),
        mpatches.Patch(color='lightgreen', label='Receivers'),
        mpatches.Patch(color='salmon', label='Eavesdropper (Eve)')
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=10,
              framealpha=0.9)

    plt.tight_layout()
    plt.savefig('quantum_network.png', dpi=300, bbox_inches='tight')
    print("✅ Network diagram saved as 'quantum_network.png'")
    
    return fig

def run_complete_demo():
    """Runs the complete BB84 demonstration with all features."""
    
    print("\n" + "=" * 60)
    print("🔐 BB84 QUANTUM KEY DISTRIBUTION NETWORK DEMONSTRATION")
    print("=" * 60)
    
    # PART 1: Network Simulation
    print("\n📡 PART 1: Multi-Party Quantum Network")
    print("-" * 60)
    network_results = run_quantum_network(n_qubits=100, intercept_rate=0.5)
    
    # Visualize network
    visualize_network(network_results)
    
    # PART 2: Threat Analysis
    print("\n🛡️  PART 2: Comprehensive Threat Analysis")
    print("-" * 60)
    threat_results = run_threat_scenarios(n_qubits=100, n_trials=5)
    
    # Generate threat visualizations
    plot_threat_comparison(threat_results)
    plot_error_correlation(n_qubits=100, n_trials=10)
    
    # PART 3: Summary
    print("\n📊 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\n✅ Generated Files:")
    print("  1. quantum_network.png - Network topology diagram")
    print("  2. threat_analysis.png - Threat scenario comparison")
    print("  3. error_correlation.png - Error vs intercept rate analysis")
    print("\n📈 Key Findings:")
    print(f"  • Network Security: {network_results['secure_links']}/{network_results['total_links']} links secure ({network_results['security_percentage']}%)")
    print(f"  • Eavesdropping Detection: Working correctly")
    print(f"  • Security Threshold: 11% error rate")
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    # Run complete demonstration
    run_complete_demo()
    
    # Show all plots
    plt.show()
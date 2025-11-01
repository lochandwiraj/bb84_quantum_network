import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from network import run_quantum_network

def visualize_network(network_results):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.axis('off')

    positions = {
        'Alice': (0, 1.5),
        'Bob': (-1.5, -0.5),
        'Charlie': (0, -0.5),
        'Dave': (1.5, -0.5),
        'Eve': (0, -1.5)
    }

    link_status = network_results['link_status']
    for receiver in ['Bob', 'Charlie', 'Dave']:
        link_key = f"alice_to_{receiver.lower()}"
        secure = link_status[link_key]['secure']
        error = link_status[link_key]['error'] * 100
        color = 'green' if secure else 'red'
        linestyle = '-' if secure else '--'

        ax.plot([positions['Alice'][0], positions[receiver][0]],
                [positions['Alice'][1], positions[receiver][1]],
                color=color, linestyle=linestyle, linewidth=3, alpha=0.7)

        mid_x = (positions['Alice'][0] + positions[receiver][0]) / 2
        mid_y = (positions['Alice'][1] + positions[receiver][1]) / 2
        status_symbol = '✅' if secure else '❌'
        ax.text(mid_x, mid_y, f"{error:.1f}% {status_symbol}", fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        if not secure:
            ax.plot([positions['Eve'][0], positions[receiver][0]],
                    [positions['Eve'][1], positions[receiver][1]],
                    color='red', linestyle=':', linewidth=2, alpha=0.5)

    node_colors = {
        'Alice': 'dodgerblue',
        'Bob': 'lightgreen',
        'Charlie': 'lightgreen',
        'Dave': 'lightgreen',
        'Eve': 'salmon'
    }

    for node, pos in positions.items():
        circle = plt.Circle(pos, 0.25, color=node_colors[node], ec='black', linewidth=2, zorder=10)
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], node, ha='center', va='center', fontsize=12, fontweight='bold', zorder=11)

    ax.set_title('Quantum Network Security Status', fontsize=16, fontweight='bold', pad=20)
    legend_items = [
        mpatches.Patch(color='green', label='Secure Link'),
        mpatches.Patch(color='red', label='Compromised Link'),
        mpatches.Patch(color='dodgerblue', label='Sender (Alice)'),
        mpatches.Patch(color='lightgreen', label='Receivers'),
        mpatches.Patch(color='salmon', label='Eavesdropper (Eve)')
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig('quantum_network.png', dpi=300, bbox_inches='tight')
    print("✅ Network diagram saved as 'quantum_network.png'")
    return fig

if __name__ == "__main__":
    print("🚀 Running BB84 Quantum Network Simulation...")
    network_results = run_quantum_network(n_qubits=100, intercept_rate=0.5)
    visualize_network(network_results)
    plt.show()

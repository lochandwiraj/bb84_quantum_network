import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from network import run_quantum_network, run_random_network_scenarios
from threat_analysis import run_threat_scenarios, plot_threat_comparison, plot_error_correlation

# Store all figures globally so they stay open
ALL_FIGURES = []

def visualize_network(network_results, filename='quantum_network.png'):
    """Creates visual diagram of quantum network with security status."""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.axis('off')

    # Node positions - arranged in a circle around Alice
    positions = {'Alice': (0, 0)}  # Center
    
    # Get receivers from link_status
    receivers = []
    for link_name in network_results['link_status'].keys():
        receiver_raw = link_name.replace('alice_to_', '')
        if receiver_raw == 'eve_r':
            receiver = 'Eve_R'
        else:
            receiver = receiver_raw.capitalize()
        receivers.append(receiver)
    
    # Position receivers in a circle
    angle_step = 360 / len(receivers)
    radius = 2.0
    
    for i, receiver in enumerate(receivers):
        angle = i * angle_step * (np.pi / 180)
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        positions[receiver] = (x, y)
    
    # Position attackers
    attackers_positioned = {}
    if network_results['num_attackers'] > 0:
        attacker_radius = 2.7
        attacker_idx = 0
        
        for link_name, status in network_results['link_status'].items():
            if status['attacker']:
                receiver_raw = link_name.replace('alice_to_', '')
                if receiver_raw == 'eve_r':
                    receiver = 'Eve_R'
                else:
                    receiver = receiver_raw.capitalize()
                    
                attackers = status['attacker'].split(" & ")
                
                for attacker in attackers:
                    if attacker not in attackers_positioned:
                        angle = (receivers.index(receiver) * angle_step + 20 * (attacker_idx + 1)) * (np.pi / 180)
                        x = attacker_radius * np.cos(angle)
                        y = attacker_radius * np.sin(angle)
                        positions[attacker] = (x, y)
                        attackers_positioned[attacker] = True
                        attacker_idx += 1

    # Draw links
    link_status = network_results['link_status']
    for receiver in receivers:
        # Create correct link key
        if receiver == 'Eve_R':
            link_key = 'alice_to_eve_r'
        else:
            link_key = f"alice_to_{receiver.lower()}"
        
        if link_key not in link_status:
            continue
            
        secure = link_status[link_key]['secure']
        error = link_status[link_key]['error'] * 100
        attacker = link_status[link_key]['attacker']
        
        color = 'green' if secure else 'red'
        linestyle = '-' if secure else '--'
        linewidth = 4 if secure else 3

        # Main communication link
        ax.plot([positions['Alice'][0], positions[receiver][0]],
                [positions['Alice'][1], positions[receiver][1]],
                color=color, linestyle=linestyle, linewidth=linewidth, alpha=0.7, zorder=1)

        # Link label
        mid_x = (positions['Alice'][0] + positions[receiver][0]) / 2
        mid_y = (positions['Alice'][1] + positions[receiver][1]) / 2
        status_text = 'SECURE' if secure else 'ATTACK'
        status_color = 'darkgreen' if secure else 'darkred'
        
        ax.text(mid_x, mid_y, f"{error:.1f}%\n{status_text}", fontsize=9,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.95,
                         edgecolor=status_color, linewidth=2),
                ha='center', va='center', fontweight='bold', color=status_color, zorder=5)

        # Draw attacker interference
        if attacker:
            attackers = attacker.split(" & ")
            for att in attackers:
                if att in positions:
                    ax.plot([positions[att][0], positions[receiver][0]],
                            [positions[att][1], positions[receiver][1]],
                            color='red', linestyle=':', linewidth=2, alpha=0.6, zorder=2)

    # Draw nodes
    node_colors = {'Alice': 'dodgerblue'}
    node_sizes = {'Alice': 0.35}
    
    # Color receivers
    for receiver in receivers:
        if receiver == 'Eve_R':
            link_key = 'alice_to_eve_r'
        else:
            link_key = f"alice_to_{receiver.lower()}"
            
        if link_key in link_status:
            secure = link_status[link_key]['secure']
            node_colors[receiver] = 'lightgreen' if secure else 'lightcoral'
            node_sizes[receiver] = 0.25
    
    # Color attackers
    for attacker in attackers_positioned.keys():
        node_colors[attacker] = 'salmon'
        node_sizes[attacker] = 0.22

    # Draw all nodes
    for node, pos in positions.items():
        circle = plt.Circle(pos, node_sizes[node], color=node_colors[node], 
                           ec='black', linewidth=2.5, zorder=10)
        ax.add_patch(circle)
        
        font_size = 13 if node == 'Alice' else 10
        ax.text(pos[0], pos[1], node, ha='center', va='center', 
                fontsize=font_size, fontweight='bold', zorder=11)
        
        if node == 'Alice':
            role = 'Sender'
        elif node in receivers:
            role = 'Receiver'
        else:
            role = 'Attacker'
            
        ax.text(pos[0], pos[1] - node_sizes[node] - 0.12, role,
               ha='center', va='top', fontsize=8, style='italic', color='gray', zorder=11)

    # Title
    scenario_title = network_results['attack_scenario'].replace('_', ' ').title()
    ax.set_title(f'Quantum Network Security Status\n{scenario_title}', 
                 fontsize=18, fontweight='bold', pad=20)
    
    # Legend
    legend_items = [
        mpatches.Patch(color='green', label='Secure Link'),
        mpatches.Patch(color='red', label='Compromised Link'),
        mpatches.Patch(color='dodgerblue', label='Sender (Alice)'),
        mpatches.Patch(color='lightgreen', label='Secure Receiver'),
        mpatches.Patch(color='lightcoral', label='Compromised Receiver'),
        mpatches.Patch(color='salmon', label='Attacker(s)')
    ]
    ax.legend(handles=legend_items, loc='upper left', fontsize=10,
              framealpha=0.95, edgecolor='black')

    # Statistics box
    stats_text = f"Network Statistics:\n"
    stats_text += f"Total Links: {network_results['total_links']}\n"
    stats_text += f"Secure: {network_results['secure_links']} ({network_results['security_percentage']:.1f}%)\n"
    stats_text += f"Compromised: {network_results['compromised_links']}\n"
    stats_text += f"Attackers: {network_results['num_attackers']}"
    
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='lightyellow', 
                    alpha=0.95, edgecolor='black', linewidth=2),
           family='monospace')

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Network diagram saved as '{filename}'")
    
    # Add to global figures list
    ALL_FIGURES.append(fig)
    return fig


def create_scenario_comparison(all_results, filename='scenario_comparison.png'):
    """Creates bar chart comparing multiple network scenarios."""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    scenarios = [r['attack_scenario'].replace('_', ' ').title()[:25] for r in all_results]
    secure_pcts = [r['security_percentage'] for r in all_results]
    compromised_pcts = [100 - r['security_percentage'] for r in all_results]
    num_attackers = [r['num_attackers'] for r in all_results]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, secure_pcts, width, label='Secure Links %', 
                   color='green', alpha=0.7, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, compromised_pcts, width, label='Compromised Links %', 
                   color='red', alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for i, (bar1, bar2, n_att) in enumerate(zip(bars1, bars2, num_attackers)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        
        ax.text(bar1.get_x() + bar1.get_width()/2., height1 + 2,
                f'{height1:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
        ax.text(bar2.get_x() + bar2.get_width()/2., height2 + 2,
                f'{height2:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        if n_att > 0:
            ax.text(i, -8, f'{n_att} attacker(s)', ha='center', fontsize=8, 
                   color='darkred', fontweight='bold')
    
    ax.axhline(y=50, color='orange', linestyle='--', linewidth=2, 
               label='50% Threshold', alpha=0.7)
    
    ax.set_xlabel('Attack Scenario', fontsize=13, fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontsize=13, fontweight='bold')
    ax.set_title('Network Security Across Different Attack Scenarios', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=45, ha='right', fontsize=9)
    ax.set_ylim(-10, 110)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Scenario comparison saved as '{filename}'")
    
    ALL_FIGURES.append(fig)
    return fig


def create_attacker_analysis(all_results, filename='attacker_analysis.png'):
    """Analyzes attacker effectiveness across scenarios."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Count attacker occurrences
    attacker_stats = {}
    for result in all_results:
        for link_name, status in result['link_status'].items():
            if status['attacker']:
                attackers = status['attacker'].split(' & ')
                for att in attackers:
                    if att not in attacker_stats:
                        attacker_stats[att] = {'total': 0, 'successful': 0, 'total_error': 0}
                    attacker_stats[att]['total'] += 1
                    attacker_stats[att]['total_error'] += status['error']
                    if not status['secure']:
                        attacker_stats[att]['successful'] += 1
    
    if attacker_stats:
        attackers = list(attacker_stats.keys())
        success_rates = [(attacker_stats[a]['successful'] / attacker_stats[a]['total'] * 100) 
                        for a in attackers]
        
        bars = ax1.barh(attackers, success_rates, color='red', alpha=0.7, 
                       edgecolor='black', linewidth=1.5)
        
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            ax1.text(rate + 2, i, f'{rate:.1f}%', va='center', fontweight='bold')
        
        ax1.set_xlabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Attacker Success Rate', fontsize=13, fontweight='bold')
        ax1.set_xlim(0, 110)
        ax1.grid(axis='x', alpha=0.3)
        
        avg_errors = [(attacker_stats[a]['total_error'] / attacker_stats[a]['total'] * 100) 
                     for a in attackers]
        
        bars2 = ax2.barh(attackers, avg_errors, color='orange', alpha=0.7,
                        edgecolor='black', linewidth=1.5)
        
        for i, (bar, err) in enumerate(zip(bars2, avg_errors)):
            ax2.text(err + 1, i, f'{err:.1f}%', va='center', fontweight='bold')
        
        ax2.axvline(x=11, color='darkred', linestyle='--', linewidth=2, 
                   label='Detection Threshold (11%)')
        ax2.set_xlabel('Average Error Rate (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Attacker Impact', fontsize=13, fontweight='bold')
        ax2.set_xlim(0, max(avg_errors) + 5)
        ax2.legend(fontsize=10)
        ax2.grid(axis='x', alpha=0.3)
    else:
        ax1.text(0.5, 0.5, 'No attacks detected', ha='center', va='center',
                transform=ax1.transAxes, fontsize=14)
        ax2.text(0.5, 0.5, 'No attacks detected', ha='center', va='center',
                transform=ax2.transAxes, fontsize=14)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Attacker analysis saved as '{filename}'")
    
    ALL_FIGURES.append(fig)
    return fig


def run_complete_demo(random_mode=False, n_random_scenarios=3):
    """Runs the complete BB84 demonstration."""
    
    print("\n" + "=" * 70)
    print("     BB84 QUANTUM KEY DISTRIBUTION NETWORK")
    print("=" * 70)
    
    # PART 1: Network Simulation
    print("\n[PART 1] Multi-Party Quantum Network")
    print("-" * 70)
    
    if random_mode:
        all_results = run_random_network_scenarios(n_qubits=100, n_scenarios=n_random_scenarios)
        
        print(f"\n[VISUALIZATION] Generating charts...")
        create_scenario_comparison(all_results)
        create_attacker_analysis(all_results)
        
        for i, result in enumerate(all_results):
            visualize_network(result, f'quantum_network_scenario_{i+1}.png')
        
        network_results = all_results[-1]
    else:
        network_results = run_quantum_network(n_qubits=100, intercept_rate=0.5)
        visualize_network(network_results)
    
    # PART 2: Threat Analysis
    print("\n[PART 2] Theoretical BB84 Threat Analysis")
    print("-" * 70)
    threat_results = run_threat_scenarios(n_qubits=100, n_trials=5)
    
    # These functions already create figures
    fig1 = plot_threat_comparison(threat_results)
    fig2 = plot_error_correlation(n_qubits=100, n_trials=10)
    ALL_FIGURES.extend([fig1, fig2])
    
    # PART 3: Summary
    print("\n" + "=" * 70)
    print("[SUMMARY] Demonstration Complete")
    print("=" * 70)
    print(f"\n✅ Network Security: {network_results['secure_links']}/{network_results['total_links']} links secure")
    print(f"✅ Active Attackers: {network_results['num_attackers']}")
    print(f"✅ Total graphs created: {len(ALL_FIGURES)}")
    print("\n🎉 ALL PLOTS DISPLAYED! Close windows to exit.")
    print("=" * 70 + "\n")
    
    # Show all plots at once - THIS IS THE KEY!
    plt.show()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--random":
        n_scenarios = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        run_complete_demo(random_mode=True, n_random_scenarios=n_scenarios)
    else:
        run_complete_demo(random_mode=False)
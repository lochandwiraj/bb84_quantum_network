import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_dashboard(network_results, threat_results, intercept_error_data):
    """
    Creates a 2x2 dashboard showing all key visualizations.
    
    Parameters:
    - network_results: dict from run_quantum_network()
    - threat_results: dict from run_threat_scenarios() 
    - intercept_error_data: list of (intercept_rate, mean_error, std_error) tuples
    """
    
    # Create figure with 2x2 subplots
    fig = plt.figure(figsize=(16, 12))
    
    # ========== TOP-LEFT: Network Topology ==========
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_title('Quantum Network Topology', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    # Node positions
    alice_pos = (5, 7)
    bob_pos = (2, 3)
    charlie_pos = (5, 3)
    dave_pos = (8, 3)
    eve_pos = (5, 4.5)
    
    # Draw Alice (sender) - large blue circle
    alice_circle = patches.Circle(alice_pos, 0.5, color='#4A90E2', ec='black', linewidth=2)
    ax1.add_patch(alice_circle)
    ax1.text(alice_pos[0], alice_pos[1], 'Alice', ha='center', va='center', 
             fontweight='bold', fontsize=11, color='white')
    
    # Draw receivers - medium green/red circles
    link_status = network_results['link_status']
    
    # Bob
    bob_color = '#50C878' if link_status['alice_to_bob']['secure'] else '#E74C3C'
    bob_circle = patches.Circle(bob_pos, 0.4, color=bob_color, ec='black', linewidth=2)
    ax1.add_patch(bob_circle)
    ax1.text(bob_pos[0], bob_pos[1], 'Bob', ha='center', va='center', 
             fontweight='bold', fontsize=10, color='white')
    
    # Charlie
    charlie_color = '#50C878' if link_status['alice_to_charlie']['secure'] else '#E74C3C'
    charlie_circle = patches.Circle(charlie_pos, 0.4, color=charlie_color, ec='black', linewidth=2)
    ax1.add_patch(charlie_circle)
    ax1.text(charlie_pos[0], charlie_pos[1], 'Charlie', ha='center', va='center', 
             fontweight='bold', fontsize=10, color='white')
    
    # Dave
    dave_color = '#50C878' if link_status['alice_to_dave']['secure'] else '#E74C3C'
    dave_circle = patches.Circle(dave_pos, 0.4, color=dave_color, ec='black', linewidth=2)
    ax1.add_patch(dave_circle)
    ax1.text(dave_pos[0], dave_pos[1], 'Dave', ha='center', va='center', 
             fontweight='bold', fontsize=10, color='white')
    
    # Draw Eve if any link is compromised
    if network_results['compromised_links'] > 0:
        eve_circle = patches.Circle(eve_pos, 0.3, color='#E74C3C', ec='black', linewidth=2)
        ax1.add_patch(eve_circle)
        ax1.text(eve_pos[0], eve_pos[1], 'Eve', ha='center', va='center', 
                 fontweight='bold', fontsize=9, color='white')
    
    # Draw links
    for link_name, link_data in link_status.items():
        if 'bob' in link_name:
            end_pos = bob_pos
        elif 'charlie' in link_name:
            end_pos = charlie_pos
        else:
            end_pos = dave_pos
        
        line_color = '#50C878' if link_data['secure'] else '#E74C3C'
        line_style = '-' if link_data['secure'] else '--'
        
        ax1.plot([alice_pos[0], end_pos[0]], [alice_pos[1], end_pos[1]], 
                 color=line_color, linestyle=line_style, linewidth=2.5)
        
        # Add error rate label
        mid_x = (alice_pos[0] + end_pos[0]) / 2
        mid_y = (alice_pos[1] + end_pos[1]) / 2
        status_icon = '✅' if link_data['secure'] else '❌'
        ax1.text(mid_x, mid_y, f"{status_icon} {link_data['error']*100:.1f}%", 
                 ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ========== TOP-RIGHT: Threat Scenario Comparison ==========
    ax2 = plt.subplot(2, 2, 2)
    ax2.set_title('Threat Scenario Analysis', fontsize=14, fontweight='bold')
    
    scenarios = list(threat_results.keys())
    means = [threat_results[s]['mean_error'] for s in scenarios]
    stds = [threat_results[s]['std_error'] for s in scenarios]
    
    colors = ['#50C878' if m < 0.11 else '#E74C3C' for m in means]
    
    bars = ax2.bar(range(len(scenarios)), [m*100 for m in means], 
                   yerr=[s*100 for s in stds], color=colors, 
                   edgecolor='black', linewidth=1.5, capsize=5)
    
    # Add threshold line
    ax2.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Detection Threshold')
    
    ax2.set_xlabel('Attack Scenario', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Error Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_xticks(range(len(scenarios)))
    ax2.set_xticklabels(scenarios, rotation=15, ha='right', fontsize=9)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Add status labels on bars
    for i, (bar, mean) in enumerate(zip(bars, means)):
        label = '✅ Safe' if mean < 0.11 else '❌ Detected'
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + stds[i]*100 + 1,
                label, ha='center', fontsize=8, fontweight='bold')
    
    # ========== BOTTOM-LEFT: Error Rate vs Intercept Rate ==========
    ax3 = plt.subplot(2, 2, 3)
    ax3.set_title('Error Rate vs Eavesdropping Intensity', fontsize=14, fontweight='bold')
    
    intercept_rates = [d[0] for d in intercept_error_data]
    mean_errors = [d[1] for d in intercept_error_data]
    std_errors = [d[2] for d in intercept_error_data]
    
    # Plot line with confidence interval
    ax3.plot(intercept_rates, [e*100 for e in mean_errors], 
             'o-', color='#4A90E2', linewidth=2.5, markersize=6, label='Observed Error')
    ax3.fill_between(intercept_rates, 
                     [(m-s)*100 for m, s in zip(mean_errors, std_errors)],
                     [(m+s)*100 for m, s in zip(mean_errors, std_errors)],
                     alpha=0.3, color='#4A90E2', label='±1 Std Dev')
    
    # Threshold line
    ax3.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    
    # Shaded zones
    ax3.axhspan(0, 11, alpha=0.1, color='green', label='Safe Zone')
    ax3.axhspan(11, ax3.get_ylim()[1], alpha=0.1, color='red', label='Danger Zone')
    
    ax3.set_xlabel('Eve Intercept Rate (%)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Error Rate (%)', fontsize=11, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # ========== BOTTOM-RIGHT: Statistics Table ==========
    ax4 = plt.subplot(2, 2, 4)
    ax4.set_title('Network Statistics Summary', fontsize=14, fontweight='bold')
    ax4.axis('off')
    
    # Prepare statistics text
    stats_text = f"""
    ╔═══════════════════════════════════════════╗
    ║         NETWORK SECURITY REPORT           ║
    ╠═══════════════════════════════════════════╣
    ║                                           ║
    ║  Total Communication Links:  {network_results['total_links']}            ║
    ║  Secure Links:               {network_results['secure_links']} ({network_results['security_percentage']:.1f}%)    ║
    ║  Compromised Links:          {network_results['compromised_links']} ({100-network_results['security_percentage']:.1f}%)    ║
    ║                                           ║
    ╠═══════════════════════════════════════════╣
    ║         INDIVIDUAL LINK STATUS            ║
    ╠═══════════════════════════════════════════╣
    ║                                           ║
    """
    
    for link_name, link_data in link_status.items():
        party = link_name.split('_to_')[1].capitalize()
        status = '✅ SECURE  ' if link_data['secure'] else '❌ COMPROMISED'
        stats_text += f"    ║  Alice → {party:8s}  {status}           ║\n"
    
    stats_text += """    ║                                           ║
    ╠═══════════════════════════════════════════╣
    ║         THREAT DETECTION SUMMARY          ║
    ╠═══════════════════════════════════════════╣
    ║                                           ║
    """
    
    # Count detected scenarios
    detected = sum(1 for s in threat_results.values() if s['mean_error'] >= 0.11)
    total_scenarios = len(threat_results)
    
    stats_text += f"    ║  Scenarios Tested:       {total_scenarios}                ║\n"
    stats_text += f"    ║  Attacks Detected:       {detected}                ║\n"
    stats_text += f"    ║  Detection Rate:         {detected/total_scenarios*100:.0f}%              ║\n"
    stats_text += """    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """
    
    ax4.text(0.1, 0.9, stats_text, fontsize=10, verticalalignment='top',
             fontfamily='monospace', transform=ax4.transAxes)
    
    # Overall figure title
    fig.suptitle('BB84 Quantum Key Distribution - Complete Security Dashboard', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig('bb84_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Dashboard saved as 'bb84_dashboard.png'")
    
    return fig


# Example usage (you'll call this with real data):
if __name__ == "__main__":
    # Mock data for testing - replace with actual results from your functions
    
    network_results = {
        'total_links': 3,
        'secure_links': 2,
        'compromised_links': 1,
        'security_percentage': 66.7,
        'link_status': {
            'alice_to_bob': {'error': 0.007, 'secure': True},
            'alice_to_charlie': {'error': 0.142, 'secure': False},
            'alice_to_dave': {'error': 0.011, 'secure': True}
        }
    }
    
    threat_results = {
        'No Attack': {'mean_error': 0.006, 'std_error': 0.003},
        'Stealth 10%': {'mean_error': 0.024, 'std_error': 0.008},
        'Passive 50%': {'mean_error': 0.137, 'std_error': 0.012},
        'Aggressive 100%': {'mean_error': 0.251, 'std_error': 0.021},
        'Variable': {'mean_error': 0.118, 'std_error': 0.064}
    }
    
    # Intercept rate vs error data (intercept%, mean_error, std_error)
    intercept_error_data = [
        (0, 0.005, 0.003),
        (10, 0.022, 0.007),
        (20, 0.045, 0.010),
        (30, 0.068, 0.012),
        (40, 0.095, 0.015),
        (50, 0.135, 0.018),
        (60, 0.158, 0.020),
        (70, 0.182, 0.022),
        (80, 0.208, 0.024),
        (90, 0.230, 0.026),
        (100, 0.250, 0.028)
    ]
    
    create_dashboard(network_results, threat_results, intercept_error_data)
"""
BB84 Quantum Key Distribution Network - Main Demo
FIXED VERSION - No overlapping text
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import sys

from network import run_quantum_network, run_random_network_scenarios

plt.rcParams['font.family'] = 'DejaVu Sans'

def visualize_network(network_results, filename='quantum_network.png'):
    """Creates clean, easy-to-read network diagram with NO overlapping."""
    
    # INCREASED FIGURE SIZE to prevent overlap
    fig, ax = plt.subplots(figsize=(20, 16))
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)  # Increased vertical space
    ax.axis('off')
    
    fig.patch.set_facecolor('white')

    # === STEP 1: POSITION ALL NODES ===
    
    # Alice at center
    positions = {'Alice': (0, 0)}
    
    # Extract receivers
    link_status = network_results['link_status']
    receivers = []
    for link_name in link_status.keys():
        receiver_part = link_name.replace('alice_to_', '')
        receiver = 'Eve_R' if receiver_part == 'eve_r' else receiver_part.capitalize()
        receivers.append(receiver)
    
    # Position receivers in circle (REDUCED radius to keep them away from edges)
    num_receivers = len(receivers)
    receiver_radius = 2.2
    
    for i, receiver in enumerate(receivers):
        angle = (i * 360 / num_receivers) * (np.pi / 180)
        x = receiver_radius * np.cos(angle)
        y = receiver_radius * np.sin(angle)
        positions[receiver] = (x, y)
    
    # Collect attackers and their targets
    attacker_to_targets = {}
    
    for link_name, status in link_status.items():
        if status['attacker']:
            receiver_part = link_name.replace('alice_to_', '')
            receiver = 'Eve_R' if receiver_part == 'eve_r' else receiver_part.capitalize()
            
            attackers = [att.strip() for att in status['attacker'].split('&')]
            for attacker in attackers:
                if attacker not in attacker_to_targets:
                    attacker_to_targets[attacker] = []
                attacker_to_targets[attacker].append(receiver)
    
    # Position attackers OUTSIDE with MORE space
    # CRITICAL FIX: Avoid top positions (90 degrees ± 45 degrees) to prevent title overlap
    attacker_radius = 3.3  # Further out
    attacker_positions = {}
    
    if attacker_to_targets:
        attacker_list = list(attacker_to_targets.keys())
        
        for idx, attacker in enumerate(attacker_list):
            targets = attacker_to_targets[attacker]
            
            if len(targets) == 1:
                # Single target: position attacker beyond that receiver
                target = targets[0]
                target_angle = None
                
                for i, recv in enumerate(receivers):
                    if recv == target:
                        target_angle_deg = i * 360 / num_receivers
                        
                        # CRITICAL FIX: Avoid top area (60° to 120°)
                        if 60 <= target_angle_deg <= 120:
                            # Shift to side instead
                            if target_angle_deg < 90:
                                target_angle_deg = 45  # Move to upper-right
                            else:
                                target_angle_deg = 135  # Move to upper-left
                        
                        target_angle = target_angle_deg * (np.pi / 180)
                        break
                
                if target_angle is not None:
                    x = attacker_radius * np.cos(target_angle)
                    y = attacker_radius * np.sin(target_angle)
                    attacker_positions[attacker] = (x, y)
            else:
                # Multiple targets: calculate average angle
                avg_angle_deg = 0
                for target in targets:
                    for i, recv in enumerate(receivers):
                        if recv == target:
                            avg_angle_deg += (i * 360 / num_receivers)
                            break
                avg_angle_deg = avg_angle_deg / len(targets)
                
                # CRITICAL FIX: Avoid top area
                if 60 <= avg_angle_deg <= 120:
                    if avg_angle_deg < 90:
                        avg_angle_deg = 45
                    else:
                        avg_angle_deg = 135
                
                avg_angle = avg_angle_deg * (np.pi / 180)
                
                x = attacker_radius * np.cos(avg_angle)
                y = attacker_radius * np.sin(avg_angle)
                attacker_positions[attacker] = (x, y)
    
    positions.update(attacker_positions)

    # === STEP 2: DRAW LINKS (Alice -> Receivers) ===
    
    for receiver in receivers:
        link_key = 'alice_to_eve_r' if receiver == 'Eve_R' else f"alice_to_{receiver.lower()}"
        status = link_status[link_key]
        
        secure = status['secure']
        error = status['error'] * 100
        
        color = '#2ecc71' if secure else '#e74c3c'
        linestyle = '-' if secure else '--'
        linewidth = 3.5 if secure else 3
        
        # Draw main link
        ax.plot(
            [positions['Alice'][0], positions[receiver][0]],
            [positions['Alice'][1], positions[receiver][1]],
            color=color, linestyle=linestyle, linewidth=linewidth, 
            alpha=0.8, zorder=2
        )
        
        # Arrow
        dx = positions[receiver][0] - positions['Alice'][0]
        dy = positions[receiver][1] - positions['Alice'][1]
        
        arrow_x = positions['Alice'][0] + 0.7 * dx
        arrow_y = positions['Alice'][1] + 0.7 * dy
        
        ax.annotate('', xy=(positions[receiver][0], positions[receiver][1]),
                   xytext=(arrow_x, arrow_y),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2.5, alpha=0.7),
                   zorder=2)
        
        # Status label
        mid_x = positions['Alice'][0] + 0.4 * dx
        mid_y = positions['Alice'][1] + 0.4 * dy
        
        status_symbol = '✓' if secure else '✗'
        status_text = f"{status_symbol} {error:.1f}%"
        status_bg = '#d5f4e6' if secure else '#fadbd8'
        status_edge = '#27ae60' if secure else '#c0392b'
        
        bbox = dict(
            boxstyle='round,pad=0.5', 
            facecolor=status_bg, 
            edgecolor=status_edge,
            linewidth=2.5,
            alpha=0.95
        )
        
        ax.text(mid_x, mid_y, status_text, 
               fontsize=10, fontweight='bold',
               ha='center', va='center',
               color=status_edge, bbox=bbox, zorder=6)

    # === STEP 3: DRAW ATTACKER INTERCEPT LINES ===
    
    for attacker, targets in attacker_to_targets.items():
        if attacker not in positions:
            continue
            
        for target in targets:
            if target not in positions:
                continue
            
            attacker_pos = positions[attacker]
            target_pos = positions[target]
            
            # Curved arrow from attacker to receiver
            arrow = FancyArrowPatch(
                attacker_pos, target_pos,
                connectionstyle=f"arc3,rad=.3",
                arrowstyle='->,head_width=0.6,head_length=0.8',
                color='#e74c3c',
                linewidth=2.5,
                linestyle=':',
                alpha=0.7,
                zorder=3
            )
            ax.add_patch(arrow)
            
            # INTERCEPT label
            label_x = (attacker_pos[0] + target_pos[0]) / 2
            label_y = (attacker_pos[1] + target_pos[1]) / 2
            
            ax.text(label_x, label_y, '⚡ INTERCEPT', 
                   fontsize=8, fontweight='bold',
                   color='#c0392b', style='italic',
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', 
                            facecolor='#ffe6e6', 
                            edgecolor='#e74c3c',
                            alpha=0.8),
                   zorder=5)

    # === STEP 4: DRAW NODES ===
    
    node_styles = {
        'Alice': {'color': '#3498db', 'size': 0.4, 'edge': '#2c3e50'},
        'receiver_secure': {'color': '#2ecc71', 'size': 0.28, 'edge': '#27ae60'},
        'receiver_compromised': {'color': '#e74c3c', 'size': 0.28, 'edge': '#c0392b'},
        'attacker': {'color': '#e67e22', 'size': 0.25, 'edge': '#d35400'}
    }
    
    for node, pos in positions.items():
        if node == 'Alice':
            style = node_styles['Alice']
        elif node in receivers:
            link_key = 'alice_to_eve_r' if node == 'Eve_R' else f"alice_to_{node.lower()}"
            secure = link_status[link_key]['secure']
            style = node_styles['receiver_secure'] if secure else node_styles['receiver_compromised']
        else:
            style = node_styles['attacker']
        
        circle = plt.Circle(
            pos, style['size'], 
            color=style['color'],
            ec=style['edge'], 
            linewidth=3,
            zorder=10
        )
        ax.add_patch(circle)
        
        font_size = 14 if node == 'Alice' else 11
        label_color = 'white' if node == 'Alice' or node in attacker_positions else 'black'
        
        ax.text(pos[0], pos[1], node, 
               ha='center', va='center',
               fontsize=font_size, fontweight='bold',
               color=label_color, zorder=11)
        
        # Role label
        if node == 'Alice':
            role = '📡 Sender'
            role_color = '#2c3e50'
        elif node in receivers:
            role = '📥 Receiver'
            role_color = '#34495e'
        else:
            role = '👿 Attacker'
            role_color = '#c0392b'
        
        ax.text(pos[0], pos[1] - style['size'] - 0.15, role,
               ha='center', va='top',
               fontsize=9, style='italic',
               color=role_color, fontweight='bold',
               zorder=11)

    # === STEP 5: TITLE (MOVED HIGHER TO AVOID OVERLAP) ===
    
    scenario_title = network_results['attack_scenario'].replace('_', ' ').title()
    
    # FIXED: Moved title HIGHER (from 3.6 to 4.0)
    ax.text(0, 4.0, 'Quantum Network Security Status',
           ha='center', fontsize=20, fontweight='bold',
           color='#2c3e50', zorder=15)
    
    ax.text(0, 3.65, scenario_title,
           ha='center', fontsize=16, fontweight='normal',
           color='#7f8c8d', style='italic', zorder=15)

    # === STEP 6: LEGEND ===
    
    legend_elements = [
        mpatches.Patch(facecolor='#2ecc71', edgecolor='#27ae60', 
                      label='Secure Link', linewidth=2),
        mpatches.Patch(facecolor='#e74c3c', edgecolor='#c0392b', 
                      label='Compromised Link', linewidth=2),
        mpatches.Patch(facecolor='#3498db', edgecolor='#2c3e50', 
                      label='Sender (Alice)', linewidth=2),
        mpatches.Patch(facecolor='#2ecc71', edgecolor='#27ae60', 
                      label='Secure Receiver', linewidth=2),
        mpatches.Patch(facecolor='#e74c3c', edgecolor='#c0392b', 
                      label='Compromised Receiver', linewidth=2),
        mpatches.Patch(facecolor='#e67e22', edgecolor='#d35400', 
                      label='Attacker', linewidth=2)
    ]
    
    legend = ax.legend(handles=legend_elements, loc='upper left', 
                      fontsize=11, framealpha=0.95,
                      edgecolor='#2c3e50', fancybox=True, 
                      shadow=True, title='Legend',
                      title_fontsize=12)
    legend.get_frame().set_linewidth(2)

    # === STEP 7: STATISTICS BOX ===
    
    stats_lines = [
        f"📊 NETWORK STATISTICS",
        f"",
        f"Scenario: {scenario_title[:30]}",
        f"Total Links: {network_results['total_links']}",
        f"Secure: {network_results['secure_links']} ({network_results['security_percentage']:.1f}%)",
        f"Compromised: {network_results['compromised_links']} ({100-network_results['security_percentage']:.1f}%)",
        f"",
        f"Active Attackers: {network_results['num_attackers']}"
    ]
    
    if network_results['num_attackers'] > 0:
        stats_lines.append(f"")
        stats_lines.append(f"Attacker Names:")
        for attacker_name in network_results['attacker_names']:
            targets = attacker_to_targets.get(attacker_name, [])
            target_str = ", ".join(targets)
            stats_lines.append(f"  • {attacker_name} → {target_str}")
    
    stats_text = "\n".join(stats_lines)
    
    ax.text(0.98, 0.98, stats_text, 
           transform=ax.transAxes,
           fontsize=10, 
           verticalalignment='top', 
           horizontalalignment='right',
           bbox=dict(boxstyle='round,pad=0.8', 
                    facecolor='#fff9e6',
                    edgecolor='#f39c12',
                    linewidth=2.5,
                    alpha=0.95),
           family='monospace',
           zorder=20)

    # === STEP 8: LINK ANALYSIS TABLE ===
    
    table_y_start = -3.8
    table_lines = ["📋 LINK ANALYSIS:"]
    
    for link_name, status in sorted(link_status.items()):
        receiver_part = link_name.replace('alice_to_', '')
        participant = 'Eve_R' if receiver_part == 'eve_r' else receiver_part.capitalize()
        
        error_pct = status['error'] * 100
        security_icon = '✓' if status['secure'] else '✗'
        
        if status['attacker']:
            line = f"{security_icon} Alice→{participant}: {error_pct:4.1f}% [{status['attacker']}]"
        else:
            line = f"{security_icon} Alice→{participant}: {error_pct:4.1f}%"
        
        table_lines.append(line)
    
    table_text = "\n".join(table_lines)
    
    ax.text(-4.2, table_y_start, table_text,
           fontsize=9,
           verticalalignment='top',
           horizontalalignment='left',
           bbox=dict(boxstyle='round,pad=0.6',
                    facecolor='#ecf0f1',
                    edgecolor='#34495e',
                    linewidth=2,
                    alpha=0.95),
           family='monospace',
           zorder=20)

    plt.tight_layout()
    print(f"[OK] Displaying: {scenario_title}")
    plt.show()
    
    return filename

def create_scenario_comparison(all_results, filename='scenario_comparison.png'):
    """Creates clean bar chart comparing scenarios."""
    
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    
    scenarios = [r['attack_scenario'].replace('_', ' ').title()[:30] for r in all_results]
    secure_pcts = [r['security_percentage'] for r in all_results]
    compromised_pcts = [100 - r['security_percentage'] for r in all_results]
    num_attackers = [r['num_attackers'] for r in all_results]
    
    x = np.arange(len(scenarios))
    width = 0.4
    
    bars1 = ax.bar(x - width/2, secure_pcts, width, 
                   label='Secure Links %',
                   color='#2ecc71', alpha=0.85,
                   edgecolor='#27ae60', linewidth=2)
    
    bars2 = ax.bar(x + width/2, compromised_pcts, width,
                   label='Compromised Links %',
                   color='#e74c3c', alpha=0.85,
                   edgecolor='#c0392b', linewidth=2)
    
    for i, (bar1, bar2, n_att) in enumerate(zip(bars1, bars2, num_attackers)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        
        if height1 > 0:
            ax.text(bar1.get_x() + bar1.get_width()/2., height1 + 2,
                   f'{height1:.0f}%',
                   ha='center', va='bottom',
                   fontweight='bold', fontsize=11,
                   color='#27ae60')
        
        if height2 > 0:
            ax.text(bar2.get_x() + bar2.get_width()/2., height2 + 2,
                   f'{height2:.0f}%',
                   ha='center', va='bottom',
                   fontweight='bold', fontsize=11,
                   color='#c0392b')
        
        if n_att > 0:
            ax.text(i, -10, f'👿 {n_att} attacker(s)',
                   ha='center', fontsize=10,
                   color='#e74c3c', fontweight='bold')
    
    ax.axhline(y=50, color='#f39c12', linestyle='--', 
              linewidth=3, label='50% Security Threshold',
              alpha=0.8)
    
    ax.set_xlabel('Attack Scenario', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.set_title('Network Security Across Different Attack Scenarios',
                fontsize=17, fontweight='bold', pad=20, color='#2c3e50')
    
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=35, ha='right', fontsize=10)
    ax.set_ylim(-15, 115)
    
    ax.legend(fontsize=12, loc='upper right', framealpha=0.95,
             edgecolor='#2c3e50', fancybox=True, shadow=True)
    
    ax.grid(axis='y', alpha=0.3, linestyle='--', color='#95a5a6')
    ax.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    print(f"[OK] Displaying scenario comparison")
    plt.show()
    
    return filename

def create_attacker_analysis(all_results, filename='attacker_analysis.png'):
    """Clean attacker effectiveness analysis."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.patch.set_facecolor('white')
    
    attacker_stats = {}
    for result in all_results:
        for link_name, status in result['link_status'].items():
            if status['attacker']:
                attackers = [att.strip() for att in status['attacker'].split('&')]
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
        
        bars = ax1.barh(attackers, success_rates,
                       color='#e74c3c', alpha=0.8,
                       edgecolor='#c0392b', linewidth=2)
        
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            ax1.text(rate + 3, i, f'{rate:.1f}%',
                    va='center', fontweight='bold', fontsize=11)
        
        ax1.set_xlabel('Success Rate (%)', fontsize=13, fontweight='bold')
        ax1.set_title('Attacker Success Rate\n(% of Attacks that Compromised Links)',
                     fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlim(0, 115)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.set_facecolor('#f8f9fa')
        
        avg_errors = [(attacker_stats[a]['total_error'] / attacker_stats[a]['total'] * 100)
                     for a in attackers]
        
        bars2 = ax2.barh(attackers, avg_errors,
                        color='#f39c12', alpha=0.8,
                        edgecolor='#e67e22', linewidth=2)
        
        for i, (bar, err) in enumerate(zip(bars2, avg_errors)):
            ax2.text(err + 1.5, i, f'{err:.1f}%',
                    va='center', fontweight='bold', fontsize=11)
        
        ax2.axvline(x=11, color='#e74c3c', linestyle='--',
                   linewidth=3, label='Detection Threshold (11%)',
                   alpha=0.8)
        
        ax2.set_xlabel('Average Error Rate Induced (%)', fontsize=13, fontweight='bold')
        ax2.set_title('Attacker Impact\n(Average Error Rate Caused)',
                     fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlim(0, max(avg_errors) + 8)
        ax2.legend(fontsize=11, framealpha=0.95)
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.set_facecolor('#f8f9fa')
    else:
        for ax in [ax1, ax2]:
            ax.text(0.5, 0.5, 'No Attacks Detected',
                   ha='center', va='center',
                   transform=ax.transAxes,
                   fontsize=16, fontweight='bold',
                   color='#95a5a6')
            ax.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    print(f"[OK] Displaying attacker analysis")
    plt.show()
    
    return filename

def run_complete_demo(random_mode=False, n_random_scenarios=3):
    """Runs complete BB84 demonstration."""
    
    print("\n" + "=" * 70)
    print("     BB84 QUANTUM KEY DISTRIBUTION NETWORK")
    print("     Advanced Multi-Attacker Scenario Demonstration")
    print("=" * 70)
    
    print("\n[PART 1] Multi-Party Quantum Network Attack Scenarios")
    print("-" * 70)
    
    if random_mode:
        all_results = run_random_network_scenarios(n_qubits=100, n_scenarios=n_random_scenarios)
        
        print(f"\n[VISUALIZATION] Displaying {n_random_scenarios} scenarios...")
        
        for i, result in enumerate(all_results):
            print(f"\n--- Scenario {i+1}/{n_random_scenarios} ---")
            visualize_network(result, f'quantum_network_scenario_{i+1}.png')
        
        create_scenario_comparison(all_results, 'scenario_comparison.png')
        create_attacker_analysis(all_results, 'attacker_analysis.png')
        
        network_results = all_results[-1]
    else:
        network_results = run_quantum_network(n_qubits=100, intercept_rate=0.5, attack_scenario=None)
        visualize_network(network_results, 'quantum_network.png')
    
    print("\n" + "=" * 70)
    print("[SUMMARY] Demonstration Complete")
    print("=" * 70)
    
    print("\n[RESULTS] Key Findings:")
    print(f"  >> Scenario: {network_results['attack_scenario'].replace('_', ' ').title()}")
    print(f"  >> Security: {network_results['secure_links']}/{network_results['total_links']} links secure ({network_results['security_percentage']:.1f}%)")
    print(f"  >> Attackers: {network_results['num_attackers']}")
    if network_results['num_attackers'] > 0:
        print(f"  >> Names: {', '.join(network_results['attacker_names'])}")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--random":
        n_scenarios = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        run_complete_demo(random_mode=True, n_random_scenarios=n_scenarios)
    else:
        run_complete_demo(random_mode=False)
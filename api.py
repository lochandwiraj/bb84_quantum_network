# api.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import networkx as nx
import numpy as np
import io, base64, time, random

# Import network simulation functions
try:
    from network import run_random_network_scenarios, run_quantum_network
except Exception:
    run_random_network_scenarios = None
    run_quantum_network = None

# reuse existing bb84 core run function if available; fallback to simple stub
try:
    from bb84_core import run_bb84_channel
except Exception:
    # minimal fallback for BB84 basic endpoint if bb84_core isn't present
    def run_bb84_channel(n_qubits=10, eve_present=False, intercept_rate=0.5):
        # simple deterministic-ish simulation for visuals/demo
        sender_key = [random.randint(0,1) for _ in range(max(1,n_qubits//3))]
        receiver_key = sender_key[:] if not eve_present or intercept_rate<0.5 else sender_key[:]
        if eve_present and intercept_rate>=0.5:
            # flip one bit to emulate error
            if receiver_key:
                receiver_key[0] ^= 1
        error = 0.0 if sender_key==receiver_key else 0.05
        basis_match_rate = round((len(sender_key) / max(1,n_qubits)) * 100, 2)
        return {
            "sender_key": sender_key,
            "receiver_key": receiver_key,
            "error": error,
            "secure": error < 0.11,
            "n_qubits": n_qubits,
            "basis_match_rate": basis_match_rate,
            "eve_present": eve_present,
            "intercept_rate": round(intercept_rate*100,2),
            "key_length": len(sender_key)
        }

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status":"online","ts":time.time()})

@app.route("/api/bb84/basic", methods=["POST"])
def bb84_basic():
    data = request.get_json(force=True)
    n = int(data.get("num_qubits", 10))
    eve = bool(data.get("eve_present", False))
    intercept = float(data.get("intercept_rate", 0.5))
    res = run_bb84_channel(n, eve, intercept)

    # simple chart: basis match % vs QBER
    fig, ax = plt.subplots(figsize=(5,2.6))
    ax.bar(["Basis match %","QBER %"], [res.get("basis_match_rate",0), res.get("error",0)*100], color=["#667eea","#ef4444"])
    ax.set_ylim(0,100)
    ax.set_title("BB84 Metrics")
    chart = fig_to_base64(fig)

    payload = {
        **res,
        "error_percentage": round(res.get("error",0)*100,2),
        "chart_image": chart,
        "threshold": 11.0
    }
    return jsonify({"success":True,"data":payload})

@app.route("/api/network/single", methods=["POST"])
def network_single():
    """
    Returns: network_image (base64), link_details: list of {name,secure,error,attacker,intercept_rate}
    Simple simulation:
      - Alice always present
      - Receivers: choose 3-5 recipients (Bob, Charlie, Dave, Eve, Frank)
      - Attackers chosen according to num_attackers; they target random receivers
      - A link is 'compromised' if attacker targeted it and random < intercept_pct
    """
    data = request.get_json(force=True)
    n_qubits = int(data.get("num_qubits", 10))
    attack_scenario = data.get("attack_scenario", "single_attacker_multiple_targets")
    num_attackers = int(data.get("num_attackers", 1))
    intercept_pct = float(data.get("intercept_rate", 0.5))  # pass as 0..1 or 0..100

    # normalize intercept_pct if user sent 0..100
    if intercept_pct > 1:
        intercept_rate = intercept_pct / 100.0
    else:
        intercept_rate = intercept_pct

    # set receivers
    possible_receivers = ["Bob","Charlie","Dave","Eve","Frank"]
    receivers = possible_receivers[:max(2, min(5, len(possible_receivers)))]
    # pick attacker names
    attacker_names = [f"Attacker_{i+1}" for i in range(num_attackers)]

    # assign attacks: mapping receiver -> attacker or None
    link_details = []
    # decide which receivers are targeted depending on scenario
    target_map = {r: None for r in receivers}
    if attack_scenario in ("no_attack","none","no_attack"):
        targeted = []
    elif attack_scenario == "single_attacker_single_target":
        attacker = random.choice(attacker_names) if attacker_names else None
        target = random.choice(receivers)
        target_map[target] = attacker
    elif attack_scenario == "single_attacker_multiple_targets":
        attacker = random.choice(attacker_names) if attacker_names else None
        # attacker targets a subset
        subset = random.sample(receivers, k=max(1, len(receivers)//2))
        for r in subset:
            target_map[r] = attacker
    elif attack_scenario.startswith("multiple_attackers"):
        # spread attackers across receivers
        for r in receivers:
            if random.random() < 0.5:
                target_map[r] = random.choice(attacker_names)
    else:
        # random fallback
        for r in receivers:
            if random.random() < 0.3:
                target_map[r] = random.choice(attacker_names)

    # compute per-link status
    for r in receivers:
        attacker = target_map[r]
        if attacker:
            compromised = random.random() < intercept_rate
            # error percent scaled by intercept_rate and small noise
            err_percent = round(intercept_rate * 100 * (0.8 + random.random()*0.4), 2)
        else:
            compromised = False
            err_percent = round(random.random()*1.5, 2)  # tiny noise baseline
        link_details.append({
            "name": r,
            "attacker": attacker,
            "secure": not compromised,
            "error": err_percent,
            "intercept_rate": round(intercept_rate*100, 2)
        })

    # create network graph
    G = nx.Graph()
    # nodes
    G.add_node("Alice", role="sender")
    for r in receivers:
        G.add_node(r, role="receiver")
    for a in attacker_names:
        G.add_node(a, role="attacker")

    # edges Alice->receivers
    for r in receivers:
        G.add_edge("Alice", r)

    # edges attacker->targeted receiver (visual only)
    for r, info in zip(receivers, link_details):
        att = info["attacker"]
        if att:
            G.add_edge(att, r)

    # draw layout
    pos = {}
    pos["Alice"] = (0, 0)
    # place receivers to the right in vertical stack
    ystep = 1.0
    start_y = (len(receivers)-1)/2.0
    for i, r in enumerate(receivers):
        pos[r] = (2.0, start_y - i*ystep)
    # attackers above/below
    for i, a in enumerate(attacker_names):
        pos[a] = (1.0, start_y + 2 + i*0.8)

    # coloring
    node_colors = []
    node_sizes = []
    for n in G.nodes():
        role = G.nodes[n].get("role","")
        if role=="sender":
            node_colors.append("#1f77b4"); node_sizes.append(900)
        elif role=="receiver":
            node_colors.append("#2ca02c"); node_sizes.append(700)
        else:
            node_colors.append("#d62728"); node_sizes.append(700)

    # edge colors: red for compromised links from link_details
    edge_colors = []
    for u,v in G.edges():
        # default neutral
        color = "#888888"
        # if edge is Alice->receiver and that receiver is compromised -> red
        if u=="Alice" and v in [ld["name"] for ld in link_details]:
            ld = next((x for x in link_details if x["name"]==v), None)
            if ld and not ld["secure"]:
                color = "#d62728"
            else:
                color = "#2ca02c"
        if v=="Alice" and u in [ld["name"] for ld in link_details]:
            ld = next((x for x in link_details if x["name"]==u), None)
            if ld and not ld["secure"]:
                color = "#d62728"
            else:
                color = "#2ca02c"
        # attacker->receiver edges colored orange
        if u.startswith("Attacker_") or v.startswith("Attacker_"):
            color = "#ff7f0e"
        edge_colors.append(color)

    # draw figure
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)
    ax.axis("off")
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold", ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, arrows=False, ax=ax)

    title = f"Network: Alice → {len(receivers)} receivers | Attackers: {len(attacker_names)}"
    ax.set_title(title)

    network_img = fig_to_base64(fig)

    # return summary
    total_links = len(receivers)
    compromised_links = sum(1 for ld in link_details if not ld["secure"])
    secure_links = total_links - compromised_links
    security_percentage = round((secure_links/total_links)*100,2) if total_links else 0.0

    response = {
        "success": True,
        "data": {
            "attack_scenario": attack_scenario,
            "attacker_names": attacker_names,
            "link_details": link_details,
            "total_links": total_links,
            "secure_links": secure_links,
            "compromised_links": compromised_links,
            "security_percentage": security_percentage,
            "network_image": network_img,
            "num_qubits": n_qubits,
            "intercept_rate": round(intercept_rate*100,2),
            "timestamp": time.time()
        }
    }
    return jsonify(response)

@app.route("/api/network/random", methods=["POST"])
def network_random():
    """
    Generate multiple random network scenarios with full visualizations
    Returns: array of scenario results with network images, comparison chart, and attacker analysis
    """
    if not run_random_network_scenarios:
        return jsonify({"success": False, "error": "Network simulation not available"})
    
    data = request.get_json(force=True)
    n_qubits = int(data.get("num_qubits", 100))
    n_scenarios = int(data.get("num_scenarios", 5))
    
    # Run the random scenarios
    all_results = run_random_network_scenarios(n_qubits=n_qubits, n_scenarios=n_scenarios)
    
    # Generate visualizations for each scenario
    scenario_images = []
    for i, result in enumerate(all_results):
        img = visualize_network_for_api(result)
        scenario_images.append({
            "scenario_num": i + 1,
            "scenario_name": result['attack_scenario'].replace('_', ' ').title(),
            "image": img,
            "total_links": result['total_links'],
            "secure_links": result['secure_links'],
            "compromised_links": result['compromised_links'],
            "security_percentage": result['security_percentage'],
            "num_attackers": result['num_attackers'],
            "attacker_names": result['attacker_names'],
            "link_status": result['link_status']
        })
    
    # Generate comparison chart
    comparison_img = create_scenario_comparison_for_api(all_results)
    
    # Generate attacker analysis
    attacker_img = create_attacker_analysis_for_api(all_results)
    
    # Calculate overall statistics
    total_links = sum(r['total_links'] for r in all_results)
    total_secure = sum(r['secure_links'] for r in all_results)
    total_compromised = sum(r['compromised_links'] for r in all_results)
    overall_security = round((total_secure / total_links * 100), 2) if total_links else 0
    
    response = {
        "success": True,
        "data": {
            "num_scenarios": n_scenarios,
            "num_qubits": n_qubits,
            "scenarios": scenario_images,
            "comparison_chart": comparison_img,
            "attacker_analysis": attacker_img,
            "overall_stats": {
                "total_links": total_links,
                "secure_links": total_secure,
                "compromised_links": total_compromised,
                "security_percentage": overall_security
            },
            "timestamp": time.time()
        }
    }
    
    return jsonify(response)

def visualize_network_for_api(network_results):
    """Create network visualization and return as base64 image"""
    fig, ax = plt.subplots(figsize=(20, 16))
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    
    # Position nodes
    positions = {'Alice': (0, 0)}
    link_status = network_results['link_status']
    receivers = []
    for link_name in link_status.keys():
        receiver_part = link_name.replace('alice_to_', '')
        receiver = 'Eve_R' if receiver_part == 'eve_r' else receiver_part.capitalize()
        receivers.append(receiver)
    
    num_receivers = len(receivers)
    receiver_radius = 2.2
    for i, receiver in enumerate(receivers):
        angle = (i * 360 / num_receivers) * (np.pi / 180)
        x = receiver_radius * np.cos(angle)
        y = receiver_radius * np.sin(angle)
        positions[receiver] = (x, y)
    
    # Collect attackers
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
    
    # Position attackers
    attacker_radius = 3.3
    if attacker_to_targets:
        for idx, attacker in enumerate(attacker_to_targets.keys()):
            targets = attacker_to_targets[attacker]
            if len(targets) == 1:
                target = targets[0]
                for i, recv in enumerate(receivers):
                    if recv == target:
                        target_angle_deg = i * 360 / num_receivers
                        if 60 <= target_angle_deg <= 120:
                            target_angle_deg = 45 if target_angle_deg < 90 else 135
                        target_angle = target_angle_deg * (np.pi / 180)
                        break
                x = attacker_radius * np.cos(target_angle)
                y = attacker_radius * np.sin(target_angle)
                positions[attacker] = (x, y)
            else:
                avg_angle_deg = sum(i * 360 / num_receivers for i, recv in enumerate(receivers) if recv in targets) / len(targets)
                if 60 <= avg_angle_deg <= 120:
                    avg_angle_deg = 45 if avg_angle_deg < 90 else 135
                avg_angle = avg_angle_deg * (np.pi / 180)
                x = attacker_radius * np.cos(avg_angle)
                y = attacker_radius * np.sin(avg_angle)
                positions[attacker] = (x, y)
    
    # Draw links
    for receiver in receivers:
        link_key = 'alice_to_eve_r' if receiver == 'Eve_R' else f"alice_to_{receiver.lower()}"
        status = link_status[link_key]
        secure = status['secure']
        error = status['error'] * 100
        color = '#2ecc71' if secure else '#e74c3c'
        linestyle = '-' if secure else '--'
        linewidth = 3.5 if secure else 3
        
        ax.plot([positions['Alice'][0], positions[receiver][0]],
                [positions['Alice'][1], positions[receiver][1]],
                color=color, linestyle=linestyle, linewidth=linewidth, alpha=0.8, zorder=2)
        
        dx = positions[receiver][0] - positions['Alice'][0]
        dy = positions[receiver][1] - positions['Alice'][1]
        arrow_x = positions['Alice'][0] + 0.7 * dx
        arrow_y = positions['Alice'][1] + 0.7 * dy
        
        ax.annotate('', xy=(positions[receiver][0], positions[receiver][1]),
                   xytext=(arrow_x, arrow_y),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2.5, alpha=0.7), zorder=2)
        
        mid_x = positions['Alice'][0] + 0.4 * dx
        mid_y = positions['Alice'][1] + 0.4 * dy
        status_symbol = 'OK' if secure else 'XX'
        status_text = f"{status_symbol} {error:.1f}%"
        status_bg = '#d5f4e6' if secure else '#fadbd8'
        status_edge = '#27ae60' if secure else '#c0392b'
        
        bbox = dict(boxstyle='round,pad=0.5', facecolor=status_bg, edgecolor=status_edge, linewidth=2.5, alpha=0.95)
        ax.text(mid_x, mid_y, status_text, fontsize=10, fontweight='bold',
               ha='center', va='center', color=status_edge, bbox=bbox, zorder=6)
    
    # Draw attacker intercept lines
    for attacker, targets in attacker_to_targets.items():
        if attacker not in positions:
            continue
        for target in targets:
            if target not in positions:
                continue
            arrow = FancyArrowPatch(positions[attacker], positions[target],
                connectionstyle=f"arc3,rad=.3", arrowstyle='->,head_width=0.6,head_length=0.8',
                color='#e74c3c', linewidth=2.5, linestyle=':', alpha=0.7, zorder=3)
            ax.add_patch(arrow)
    
    # Draw nodes
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
        
        circle = plt.Circle(pos, style['size'], color=style['color'], ec=style['edge'], linewidth=3, zorder=10)
        ax.add_patch(circle)
        
        font_size = 14 if node == 'Alice' else 11
        label_color = 'white' if node == 'Alice' or node in attacker_to_targets else 'black'
        ax.text(pos[0], pos[1], node, ha='center', va='center',
               fontsize=font_size, fontweight='bold', color=label_color, zorder=11)
    
    # Title
    scenario_title = network_results['attack_scenario'].replace('_', ' ').title()
    ax.text(0, 4.0, 'Quantum Network Security Status', ha='center', fontsize=20,
           fontweight='bold', color='#2c3e50', zorder=15)
    ax.text(0, 3.65, scenario_title, ha='center', fontsize=16,
           fontweight='normal', color='#7f8c8d', style='italic', zorder=15)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ecc71', edgecolor='#27ae60', label='Secure Link', linewidth=2),
        mpatches.Patch(facecolor='#e74c3c', edgecolor='#c0392b', label='Compromised Link', linewidth=2),
        mpatches.Patch(facecolor='#e67e22', edgecolor='#d35400', label='Attacker', linewidth=2)
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.95)
    
    plt.tight_layout()
    return fig_to_base64(fig)

def create_scenario_comparison_for_api(all_results):
    """Create comparison chart and return as base64"""
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')
    
    scenarios = [r['attack_scenario'].replace('_', ' ').title()[:30] for r in all_results]
    secure_pcts = [r['security_percentage'] for r in all_results]
    compromised_pcts = [100 - r['security_percentage'] for r in all_results]
    
    x = np.arange(len(scenarios))
    width = 0.4
    
    bars1 = ax.bar(x - width/2, secure_pcts, width, label='Secure Links %',
                   color='#2ecc71', alpha=0.85, edgecolor='#27ae60', linewidth=2)
    bars2 = ax.bar(x + width/2, compromised_pcts, width, label='Compromised Links %',
                   color='#e74c3c', alpha=0.85, edgecolor='#c0392b', linewidth=2)
    
    for bar1, bar2 in zip(bars1, bars2):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        if height1 > 0:
            ax.text(bar1.get_x() + bar1.get_width()/2., height1 + 2, f'{height1:.0f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=11, color='#27ae60')
        if height2 > 0:
            ax.text(bar2.get_x() + bar2.get_width()/2., height2 + 2, f'{height2:.0f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=11, color='#c0392b')
    
    ax.axhline(y=50, color='#f39c12', linestyle='--', linewidth=3, label='50% Threshold', alpha=0.8)
    ax.set_xlabel('Attack Scenario', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.set_ylabel('Percentage (%)', fontsize=14, fontweight='bold', color='#2c3e50')
    ax.set_title('Network Security Across Different Attack Scenarios',
                fontsize=17, fontweight='bold', pad=20, color='#2c3e50')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=35, ha='right', fontsize=10)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=12, loc='upper right', framealpha=0.95)
    ax.grid(axis='y', alpha=0.3, linestyle='--', color='#95a5a6')
    ax.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    return fig_to_base64(fig)

def create_attacker_analysis_for_api(all_results):
    """Create attacker analysis and return as base64"""
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
        success_rates = [(attacker_stats[a]['successful'] / attacker_stats[a]['total'] * 100) for a in attackers]
        
        bars = ax1.barh(attackers, success_rates, color='#e74c3c', alpha=0.8, edgecolor='#c0392b', linewidth=2)
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            ax1.text(rate + 3, i, f'{rate:.1f}%', va='center', fontweight='bold', fontsize=11)
        
        ax1.set_xlabel('Success Rate (%)', fontsize=13, fontweight='bold')
        ax1.set_title('Attacker Success Rate\n(% of Attacks that Compromised Links)',
                     fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlim(0, 115)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.set_facecolor('#f8f9fa')
        
        avg_errors = [(attacker_stats[a]['total_error'] / attacker_stats[a]['total'] * 100) for a in attackers]
        bars2 = ax2.barh(attackers, avg_errors, color='#f39c12', alpha=0.8, edgecolor='#e67e22', linewidth=2)
        for i, (bar, err) in enumerate(zip(bars2, avg_errors)):
            ax2.text(err + 1.5, i, f'{err:.1f}%', va='center', fontweight='bold', fontsize=11)
        
        ax2.axvline(x=11, color='#e74c3c', linestyle='--', linewidth=3, label='Detection Threshold (11%)', alpha=0.8)
        ax2.set_xlabel('Average Error Rate Induced (%)', fontsize=13, fontweight='bold')
        ax2.set_title('Attacker Impact\n(Average Error Rate Caused)', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlim(0, max(avg_errors) + 8 if avg_errors else 20)
        ax2.legend(fontsize=11, framealpha=0.95)
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.set_facecolor('#f8f9fa')
    else:
        for ax in [ax1, ax2]:
            ax.text(0.5, 0.5, 'No Attacks Detected', ha='center', va='center',
                   transform=ax.transAxes, fontsize=16, fontweight='bold', color='#95a5a6')
            ax.set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    return fig_to_base64(fig)

if __name__=="__main__":
    print("\n🔐 BB84 API + Network visuals running at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

# api.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import io, base64, time, random

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

if __name__=="__main__":
    print("\n🔐 BB84 API + Network visuals running at http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

"""
Threat Analysis Module
Tests BB84 protocol against 5 different theoretical attack scenarios
"""

import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from network import run_bb84_channel

plt.rcParams['font.family'] = 'DejaVu Sans'

def run_threat_scenarios(n_qubits=100, n_trials=5):
    """
    Tests BB84 protocol against 5 different attack scenarios.
    Each scenario is repeated n_trials times to get statistical averages.
    """
    scenarios = {
        "Scenario 1 (No Attack)": {
            "intercept_rate": 0.0,
            "description": "Baseline - no eavesdropper",
            "expected": "~0.5% error"
        },
        "Scenario 2 (Stealth 10%)": {
            "intercept_rate": 0.1,
            "description": "Smart attacker trying to stay undetected",
            "expected": "~2-3% error"
        },
        "Scenario 3 (Passive 50%)": {
            "intercept_rate": 0.5,
            "description": "Classic eavesdropping scenario",
            "expected": "~12-15% error"
        },
        "Scenario 4 (Aggressive 100%)": {
            "intercept_rate": 1.0,
            "description": "Brute force - intercepts everything",
            "expected": "~25% error"
        },
        "Scenario 5 (Variable)": {
            "intercept_rate": "random",
            "description": "Random intercept rate each trial",
            "expected": "Variable"
        }
    }

    results = {}

    print("\n" + "=" * 60)
    print("    THEORETICAL THREAT SCENARIO ANALYSIS")
    print("=" * 60)

    for scenario_name, config in scenarios.items():
        error_rates = []
        intercept_rates = []

        for trial in range(n_trials):
            if config["intercept_rate"] == "random":
                intercept_rate = random.random()
            else:
                intercept_rate = config["intercept_rate"]

            intercept_rates.append(intercept_rate)

            eve_present = intercept_rate > 0
            result = run_bb84_channel(n_qubits, eve_present, intercept_rate)
            error_rates.append(result["error"])

        mean_error = np.mean(error_rates)
        std_error = np.std(error_rates)
        mean_intercept = np.mean(intercept_rates)

        if mean_error < 0.05:
            status = "[OK] SECURE"
        elif mean_error < 0.11:
            status = "[OK] SECURE (but suspicious)"
        elif mean_error < 0.15:
            status = "[XX] DETECTED"
        else:
            status = "[XX] DETECTED (obvious)"

        if config["intercept_rate"] == "random" and std_error > 0.05:
            status = "[!!] UNSTABLE"

        results[scenario_name] = {
            "mean_error": mean_error,
            "std_error": std_error,
            "mean_intercept": mean_intercept,
            "status": status,
            "error_rates": error_rates
        }

        print(f"\n{scenario_name}:")
        print(f"  Avg Error: {mean_error*100:.1f}% +/- {std_error*100:.1f}%")
        if config["intercept_rate"] == "random":
            print(f"  Avg Intercept: {mean_intercept*100:.1f}%")
        print(f"  Status: {status}")

    print("\n" + "=" * 60 + "\n")

    return results

def plot_threat_comparison(threat_results, output_file='threat_analysis.png'):
    """
    Creates a bar chart comparing all threat scenarios.
    Shows error rates with threshold line at 11%.
    """
    
    fig, ax = plt.subplots(figsize=(14, 8))

    scenarios = list(threat_results.keys())
    mean_errors = [threat_results[s]["mean_error"] * 100 for s in scenarios]
    std_errors = [threat_results[s]["std_error"] * 100 for s in scenarios]

    colors = ['green' if e < 11 else 'red' for e in mean_errors]

    bars = ax.bar(range(len(scenarios)), mean_errors, yerr=std_errors,
                   color=colors, alpha=0.7, capsize=5, edgecolor='black', linewidth=1.5)

    ax.axhline(y=11, color='darkred', linestyle='--', linewidth=2.5, 
               label='Security Threshold (11%)', zorder=5)

    for i, (bar, mean, status) in enumerate(zip(bars, mean_errors, 
                                                 [threat_results[s]["status"] for s in scenarios])):
        height = bar.get_height()
        label = "Safe" if mean < 11 else "Detected"
        label_color = 'darkgreen' if mean < 11 else 'darkred'
        
        ax.text(bar.get_x() + bar.get_width()/2., height + std_errors[i] + 0.8,
                label, ha='center', va='bottom', fontweight='bold', 
                fontsize=11, color=label_color,
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                         edgecolor=label_color, linewidth=1.5))
        
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
                f'{mean:.1f}%', ha='center', va='center', 
                fontweight='bold', fontsize=10, color='white')

    ax.set_xlabel('Attack Scenario', fontsize=13, fontweight='bold')
    ax.set_ylabel('Error Rate (%)', fontsize=13, fontweight='bold')
    ax.set_title('BB84 Protocol Security: Theoretical Threat Comparison', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels([s.replace(' (', '\n(') for s in scenarios], 
                        fontsize=10, ha='center')
    ax.set_ylim(0, max(mean_errors) + max(std_errors) + 6)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(fontsize=12, loc='upper left')

    ax.axhspan(0, 11, alpha=0.1, color='green', zorder=0)
    ax.axhspan(11, ax.get_ylim()[1], alpha=0.1, color='red', zorder=0)
    ax.text(len(scenarios) - 0.5, 5, 'SAFE ZONE', fontsize=11, 
            color='darkgreen', fontweight='bold', ha='right')
    ax.text(len(scenarios) - 0.5, 18, 'DANGER ZONE', fontsize=11, 
            color='darkred', fontweight='bold', ha='right')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[OK] Threat comparison chart saved as '{output_file}'")
    plt.close(fig)
    
    return output_file

if __name__ == "__main__":
    threat_results = run_threat_scenarios(n_qubits=100, n_trials=5)
    plot_threat_comparison(threat_results)
    print("\n[DONE] Theoretical threat analysis complete!\n")
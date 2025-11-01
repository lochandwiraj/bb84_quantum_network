import random
import numpy as np
import matplotlib.pyplot as plt
from network import run_bb84_channel

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

    print("\n" + "━" * 50)
    print("🛡️  THREAT SCENARIO ANALYSIS")
    print("━" * 50)

    for scenario_name, config in scenarios.items():
        error_rates = []
        intercept_rates = []

        # Run multiple trials for each scenario
        for trial in range(n_trials):
            # Handle random intercept rate for Scenario 5
            if config["intercept_rate"] == "random":
                intercept_rate = random.random()
            else:
                intercept_rate = config["intercept_rate"]

            intercept_rates.append(intercept_rate)

            # Run BB84 with or without Eve
            eve_present = intercept_rate > 0
            result = run_bb84_channel(n_qubits, eve_present, intercept_rate)
            error_rates.append(result["error"])

        # Calculate statistics
        mean_error = np.mean(error_rates)
        std_error = np.std(error_rates)
        mean_intercept = np.mean(intercept_rates)

        # Determine security status
        if mean_error < 0.05:
            status = "✅ SECURE"
        elif mean_error < 0.11:
            status = "✅ SECURE (but suspicious)"
        elif mean_error < 0.15:
            status = "❌ DETECTED"
        else:
            status = "❌ DETECTED (obvious)"

        # Special case for variable scenario
        if config["intercept_rate"] == "random" and std_error > 0.05:
            status = "⚠️  UNSTABLE"

        results[scenario_name] = {
            "mean_error": mean_error,
            "std_error": std_error,
            "mean_intercept": mean_intercept,
            "status": status,
            "error_rates": error_rates
        }

        # Print formatted output
        print(f"\n{scenario_name}:")
        print(f"  Avg Error: {mean_error*100:.1f}% ± {std_error*100:.1f}%")
        if config["intercept_rate"] == "random":
            print(f"  Avg Intercept: {mean_intercept*100:.1f}%")
        print(f"  Status: {status}")

    print("\n" + "━" * 50 + "\n")

    return results

def plot_threat_comparison(threat_results, output_file='threat_analysis.png'):
    """
    Creates a bar chart comparing all threat scenarios.
    Shows error rates with threshold line at 11%.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    scenarios = list(threat_results.keys())
    mean_errors = [threat_results[s]["mean_error"] * 100 for s in scenarios]
    std_errors = [threat_results[s]["std_error"] * 100 for s in scenarios]

    # Determine bar colors based on threshold
    colors = ['green' if e < 11 else 'red' for e in mean_errors]

    # Create bars
    bars = ax.bar(range(len(scenarios)), mean_errors, yerr=std_errors,
                   color=colors, alpha=0.7, capsize=5, edgecolor='black', linewidth=1.5)

    # Add threshold line
    ax.axhline(y=11, color='darkred', linestyle='--', linewidth=2, 
               label='Security Threshold (11%)', zorder=5)

    # Add value labels on bars
    for i, (bar, mean, status) in enumerate(zip(bars, mean_errors, 
                                                 [threat_results[s]["status"] for s in scenarios])):
        height = bar.get_height()
        label = "✅ Safe" if mean < 11 else "❌ Detected"
        ax.text(bar.get_x() + bar.get_width()/2., height + std_errors[i] + 0.5,
                label, ha='center', va='bottom', fontweight='bold', fontsize=10)

    # Formatting
    ax.set_xlabel('Attack Scenario', fontsize=12, fontweight='bold')
    ax.set_ylabel('Error Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('BB84 Protocol Security: Threat Scenario Comparison', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels([s.replace(' (', '\n(') for s in scenarios], 
                        fontsize=9, ha='center')
    ax.set_ylim(0, max(mean_errors) + max(std_errors) + 5)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper left')

    # Add shaded regions
    ax.axhspan(0, 11, alpha=0.1, color='green', zorder=0)
    ax.axhspan(11, ax.get_ylim()[1], alpha=0.1, color='red', zorder=0)
    ax.text(len(scenarios) - 0.5, 5, 'SAFE ZONE', fontsize=10, 
            color='darkgreen', fontweight='bold', ha='right')
    ax.text(len(scenarios) - 0.5, 15, 'DANGER ZONE', fontsize=10, 
            color='darkred', fontweight='bold', ha='right')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Threat comparison chart saved as '{output_file}'")
    
    return fig

def plot_error_correlation(n_qubits=100, n_trials=10, output_file='error_correlation.png'):
    """
    Shows relationship between Eve's intercept rate and resulting error rate.
    Tests intercept rates from 0% to 100% in 10% increments.
    """
    intercept_rates = np.linspace(0, 1, 11)  # 0%, 10%, 20%, ..., 100%
    mean_errors = []
    std_errors = []

    print("\n🔬 Analyzing Error-Intercept Correlation...")
    
    for intercept_rate in intercept_rates:
        errors = []
        for _ in range(n_trials):
            eve_present = intercept_rate > 0
            result = run_bb84_channel(n_qubits, eve_present, intercept_rate)
            errors.append(result["error"] * 100)  # Convert to percentage
        
        mean_errors.append(np.mean(errors))
        std_errors.append(np.std(errors))

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot mean line with confidence interval
    ax.plot(intercept_rates * 100, mean_errors, 'o-', color='dodgerblue', 
            linewidth=2, markersize=8, label='Mean Error Rate')
    ax.fill_between(intercept_rates * 100, 
                     np.array(mean_errors) - np.array(std_errors),
                     np.array(mean_errors) + np.array(std_errors),
                     alpha=0.3, color='lightblue', label='±1 Std Dev')

    # Add threshold line
    ax.axhline(y=11, color='darkred', linestyle='--', linewidth=2.5, 
               label='Security Threshold (11%)', zorder=5)

    # Add shaded zones
    ax.axhspan(0, 11, alpha=0.1, color='green', zorder=0)
    ax.axhspan(11, ax.get_ylim()[1], alpha=0.1, color='red', zorder=0)
    
    # Zone labels
    ax.text(95, 5, 'SAFE ZONE', fontsize=11, color='darkgreen', 
            fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    ax.text(95, 15, 'DANGER ZONE', fontsize=11, color='darkred', 
            fontweight='bold', ha='right', va='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # Formatting
    ax.set_xlabel("Eve's Intercept Rate (%)", fontsize=12, fontweight='bold')
    ax.set_ylabel('Observed Error Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('BB84 Security: Error Rate vs Eavesdropping Intensity', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper left')
    ax.set_xlim(-2, 102)
    ax.set_ylim(0, max(mean_errors) + max(std_errors) + 3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Error correlation graph saved as '{output_file}'")
    
    return fig


if __name__ == "__main__":
    # Run threat scenarios
    threat_results = run_threat_scenarios(n_qubits=100, n_trials=5)
    
    # Generate visualizations
    plot_threat_comparison(threat_results)
    plot_error_correlation(n_qubits=100, n_trials=10)
    
    plt.show()
"""
Hour 16: Error Rate Correlation Graph
Proves the mathematical relationship between eavesdropping and detection
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from network import run_bb84_channel

plt.rcParams['font.family'] = 'DejaVu Sans'

def plot_error_correlation(num_qubits=100, num_trials=10, output_file='error_correlation.png'):
    """
    Generates comprehensive error rate vs intercept rate correlation analysis.
    
    This function demonstrates the core security principle of BB84:
    eavesdropping ALWAYS increases error rates in a measurable way.
    
    Parameters:
    -----------
    num_qubits : int
        Number of qubits per trial (default: 100)
    num_trials : int
        Number of trials per intercept rate for statistical confidence (default: 10)
    output_file : str
        Filename for saved graph
    
    Returns:
    --------
    dict : Statistics and data points for analysis
    """
    
    # Test intercept rates from 0% to 100% in 5% increments
    intercept_rates = np.arange(0, 1.05, 0.05)  # 21 data points
    
    # Storage for results
    mean_errors = []
    std_errors = []
    all_error_data = []
    
    print("\n" + "=" * 60)
    print("    ERROR CORRELATION ANALYSIS")
    print("=" * 60)
    print(f"Testing {len(intercept_rates)} intercept rates x {num_trials} trials each")
    print(f"Total simulations: {len(intercept_rates) * num_trials}")
    print("-" * 60)
    
    # For each intercept rate, run multiple trials
    for idx, intercept_rate in enumerate(intercept_rates):
        trial_errors = []
        
        # Run multiple trials to average out quantum randomness
        for trial in range(num_trials):
            # Run BB84 protocol with this intercept rate
            eve_present = intercept_rate > 0
            result = run_bb84_channel(
                n_qubits=num_qubits,
                eve_present=eve_present,
                intercept_rate=intercept_rate
            )
            
            trial_errors.append(result['error'] * 100)  # Convert to percentage
        
        # Calculate statistics for this intercept rate
        mean_error = np.mean(trial_errors)
        std_error = np.std(trial_errors)
        
        mean_errors.append(mean_error)
        std_errors.append(std_error)
        all_error_data.append(trial_errors)
        
        # Progress indicator
        if idx % 5 == 0:
            print(f"Intercept {intercept_rate*100:5.1f}% -> Error {mean_error:5.2f}% +/- {std_error:4.2f}%")
    
    print("-" * 60)
    print("[OK] Analysis complete. Generating visualization...")
    
    # Convert to numpy arrays
    intercept_rates_percent = intercept_rates * 100
    mean_errors = np.array(mean_errors)
    std_errors = np.array(std_errors)
    
    # === CREATE THE VISUALIZATION ===
    
    fig, ax = plt.subplots(figsize=(14, 9), dpi=100)
    
    # Set professional style
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # 1. SAFE ZONE (below 11% threshold) - Green
    ax.fill_between(
        intercept_rates_percent, 
        0, 
        11,
        color='#d4edda',
        alpha=0.4,
        label='Safe Zone (Undetected)',
        zorder=1
    )
    
    # 2. DANGER ZONE (above 11% threshold) - Red
    ax.fill_between(
        intercept_rates_percent, 
        11,
        30,
        color='#f8d7da',
        alpha=0.4,
        label='Danger Zone (Detected)',
        zorder=1
    )
    
    # 3. CONFIDENCE INTERVAL - Blue band
    ax.fill_between(
        intercept_rates_percent,
        mean_errors - std_errors,
        mean_errors + std_errors,
        color='#0066cc',
        alpha=0.2,
        label='+/- 1 Std Dev',
        zorder=2
    )
    
    # 4. MAIN DATA LINE
    ax.plot(
        intercept_rates_percent,
        mean_errors,
        color='#0066cc',
        linewidth=2.5,
        marker='o',
        markersize=6,
        markerfacecolor='white',
        markeredgewidth=2,
        markeredgecolor='#0066cc',
        label='Mean Error Rate',
        zorder=3
    )
    
    # 5. SECURITY THRESHOLD LINE
    ax.axhline(
        y=11, 
        color='#dc3545',
        linestyle='--',
        linewidth=2.5,
        label='Security Threshold (11%)',
        zorder=4
    )
    
    # 6. THEORETICAL IDEAL LINE
    theoretical_max = 25
    theoretical_line = intercept_rates_percent * (theoretical_max / 100)
    ax.plot(
        intercept_rates_percent,
        theoretical_line,
        color='#6c757d',
        linestyle=':',
        linewidth=2,
        alpha=0.6,
        label='Theoretical Maximum',
        zorder=2
    )
    
    # === ANNOTATIONS ===
    
    # Find crossing point
    crossing_idx = np.where(mean_errors >= 11)[0]
    crossing_point = None
    
    if len(crossing_idx) > 0:
        crossing_point = intercept_rates_percent[crossing_idx[0]]
        crossing_error = mean_errors[crossing_idx[0]]
        
        ax.annotate(
            f'Detection starts\nat {crossing_point:.0f}% intercept',
            xy=(crossing_point, crossing_error),
            xytext=(crossing_point + 15, crossing_error + 5),
            fontsize=10,
            fontweight='bold',
            color='#dc3545',
            arrowprops=dict(
                arrowstyle='->',
                color='#dc3545',
                lw=2,
                connectionstyle='arc3,rad=0.3'
            ),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='#dc3545', linewidth=2)
        )
    
    # Baseline annotation
    baseline_error = mean_errors[0]
    ax.annotate(
        f'Baseline: {baseline_error:.1f}%\n(quantum noise only)',
        xy=(0, baseline_error),
        xytext=(10, baseline_error + 3),
        fontsize=9,
        arrowprops=dict(arrowstyle='->', color='#0066cc', lw=1.5),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8)
    )
    
    # Maximum annotation
    max_error = mean_errors[-1]
    ax.annotate(
        f'Maximum: {max_error:.1f}%\n(full interception)',
        xy=(100, max_error),
        xytext=(80, max_error - 4),
        fontsize=9,
        arrowprops=dict(arrowstyle='->', color='#0066cc', lw=1.5),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8)
    )
    
    # === LABELS AND FORMATTING ===
    
    ax.set_xlabel('Eve\'s Intercept Rate (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Observed Error Rate (%)', fontsize=14, fontweight='bold')
    ax.set_title(
        'BB84 Protocol: Error Rate vs. Eavesdropping Intensity\n'
        'Demonstrating Quantum Security Principle',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    
    ax.set_xlim(-2, 102)
    ax.set_ylim(0, 30)
    
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray', zorder=0)
    
    ax.legend(
        loc='upper left',
        fontsize=11,
        framealpha=0.95,
        edgecolor='black',
        fancybox=True,
        shadow=True
    )
    
    # Statistics text box
    stats_text = (
        f'Statistics (n={num_trials} trials/point):\n'
        f'  Baseline error: {mean_errors[0]:.2f}%\n'
        f'  Detection threshold: 11.0%\n'
        f'  Max observed error: {mean_errors[-1]:.2f}%\n'
    )
    
    if crossing_point:
        stats_text += f'  Crossing point: ~{crossing_point:.0f}% intercept'
    
    ax.text(
        0.98, 0.50,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='center',
        horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, 
                 edgecolor='black', linewidth=1.5),
        fontfamily='monospace'
    )
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"[OK] Graph saved as '{output_file}'")
    print("=" * 60 + "\n")
    plt.close(fig)
    
    # === RETURN DETAILED STATISTICS ===
    
    return {
        'intercept_rates': intercept_rates_percent.tolist(),
        'mean_errors': mean_errors.tolist(),
        'std_errors': std_errors.tolist(),
        'all_raw_data': all_error_data,
        'baseline_error': mean_errors[0],
        'max_error': mean_errors[-1],
        'crossing_point': crossing_point if crossing_point else None,
        'theoretical_max': theoretical_max,
        'num_qubits': num_qubits,
        'num_trials': num_trials
    }

def analyze_correlation_statistics(stats):
    """
    Provides detailed statistical analysis of correlation data.
    
    Parameters:
    -----------
    stats : dict
        Output from plot_error_correlation()
    
    Returns:
    --------
    dict : Detailed statistical metrics
    """
    
    intercept_rates = np.array(stats['intercept_rates'])
    mean_errors = np.array(stats['mean_errors'])
    
    # Calculate correlation coefficient
    correlation = np.corrcoef(intercept_rates, mean_errors)[0, 1]
    
    # Linear regression
    coefficients = np.polyfit(intercept_rates, mean_errors, 1)
    slope = coefficients[0]
    intercept = coefficients[1]
    
    # R-squared
    predicted = slope * intercept_rates + intercept
    ss_res = np.sum((mean_errors - predicted) ** 2)
    ss_tot = np.sum((mean_errors - np.mean(mean_errors)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    print("\n" + "=" * 60)
    print("    CORRELATION STATISTICS")
    print("=" * 60)
    print(f"Correlation coefficient: {correlation:.4f}")
    print(f"R-squared: {r_squared:.4f}")
    print(f"Linear fit: y = {slope:.4f}x + {intercept:.4f}")
    print(f"Interpretation: {slope:.4f}% error per 1% intercept increase")
    print("=" * 60 + "\n")
    
    return {
        'correlation': correlation,
        'r_squared': r_squared,
        'slope': slope,
        'intercept_value': intercept,
        'interpretation': f'{slope:.4f}% error per 1% intercept'
    }

if __name__ == "__main__":
    # Run correlation analysis
    stats = plot_error_correlation(num_qubits=100, num_trials=10)
    
    # Analyze statistics
    analysis = analyze_correlation_statistics(stats)
    
    print("\n[DONE] Error correlation analysis complete!\n")
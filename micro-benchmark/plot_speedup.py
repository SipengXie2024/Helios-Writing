import matplotlib.pyplot as plt
import numpy as np

# Set publication-quality parameters
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12

# Data (in microseconds)
benchmarks = ['ERC20-\nTransfer', 'Uniswap-Swap\n1-hop', 'Uniswap-Swap\n4-hop']
x = np.arange(len(benchmarks))
width = 0.20  # Width of bars

# Execution times for each system (absolute values)
revm_native_abs = [4.9406, 62.021, 172.49]
forerunner_revm_abs = [4.5099, 39.199, 130.36]
revmc_normalized_abs = [5.55, 42.35, 126.84]  # Proportionally scaled
helios_abs = [4.3465, 30.963, 97.345]

# Calculate speedup over Revm Native baseline
revm_native_speedup = [1.0, 1.0, 1.0]  # Baseline
forerunner_revm_speedup = [revm_native_abs[i] / forerunner_revm_abs[i] for i in range(3)]
revmc_speedup = [revm_native_abs[i] / revmc_normalized_abs[i] for i in range(3)]
helios_speedup = [revm_native_abs[i] / helios_abs[i] for i in range(3)]

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 5.5))

# Define positions for bars
positions = [x - 1.5*width, x - 0.5*width, x + 0.5*width, x + 1.5*width]

# Define colors (professional scheme with better contrast)
color_revm = '#7f7f7f'          # Medium gray for baseline
color_forerunner = '#74add1'    # Light blue
color_revmc = '#fdae61'         # Orange (with hatch)
color_helios = '#1a5490'        # Deep blue (highlight)

# Plot bars
bars1 = ax.bar(positions[0], revm_native_speedup, width, label='Revm Native',
               color=color_revm, edgecolor='black', linewidth=0.6, alpha=0.8)
bars2 = ax.bar(positions[1], forerunner_revm_speedup, width, label='Forerunner-Revm',
               color=color_forerunner, edgecolor='black', linewidth=0.6, alpha=0.9)
bars3 = ax.bar(positions[2], revmc_speedup, width, label='Revmc',
               color=color_revmc, edgecolor='black', linewidth=0.6,
               hatch='///', alpha=0.9)  # Hatched pattern for normalized data
bars4 = ax.bar(positions[3], helios_speedup, width, label='Helios',
               color=color_helios, edgecolor='black', linewidth=0.8)

# Add value labels on bars
# For Revm baseline (always 1.0)
for i, bar in enumerate(bars1):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.04,
            '1.00×',
            ha='center', va='bottom', fontsize=8, color='#333333')

# For Forerunner-Revm
for i, (bar, speedup) in enumerate(zip(bars2, forerunner_revm_speedup)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.04,
            f'{speedup:.2f}×',
            ha='center', va='bottom', fontsize=8, fontweight='normal')

# For Revmc
for i, (bar, speedup) in enumerate(zip(bars3, revmc_speedup)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.04,
            f'{speedup:.2f}×',
            ha='center', va='bottom', fontsize=8, fontweight='normal')

# Helios: bold and prominent
for i, (bar, speedup) in enumerate(zip(bars4, helios_speedup)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.04,
            f'{speedup:.2f}×',
            ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1a5490')

# Add horizontal reference line at y=1.0 (baseline)
ax.axhline(y=1.0, color='black', linestyle='-', linewidth=1.0, alpha=0.5, zorder=0)

# Labels and title
ax.set_ylabel('Speedup over Revm Native\n(higher is better)', 
              fontweight='bold')
ax.set_xlabel('Benchmark', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(benchmarks)

# Grid for readability
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
ax.set_axisbelow(True)

# Set y-axis limits for better visualization
ax.set_ylim([0, 2.4])

# Add annotation showing higher is better
ax.text(0.02, 0.98, '↑ Higher is faster', 
        transform=ax.transAxes, fontsize=9, 
        verticalalignment='top', style='italic', color='#333333')

# Legend with clear positioning
legend = ax.legend(loc='upper left', framealpha=0.95, edgecolor='black',
                  ncol=2, columnspacing=1.0)

# Add note about normalized data
# fig.text(0.12, 0.01,
#          'Note: Revmc results proportionally scaled (t_norm = t_opt × t_Revm / t_Revmc_native) to enable cross-comparison.',
#          fontsize=7, style='italic', color='#333333')

# Tight layout
plt.tight_layout(rect=[0, 0.025, 1, 1])

# Save figure
plt.savefig('microbench_execution.pdf', dpi=300, bbox_inches='tight')
plt.savefig('microbench_execution.png', dpi=300, bbox_inches='tight')

print("Figure saved successfully!")
print("\n" + "="*60)
print("SPEEDUP OVER REVM NATIVE")
print("="*60)
for i, bench in enumerate(benchmarks):
    print(f"\n{bench.replace(chr(10), ' ')}:")
    print(f"  Revm Native:      {revm_native_speedup[i]:.2f}× (baseline)")
    print(f"  Forerunner-Revm:  {forerunner_revm_speedup[i]:.2f}×")
    print(f"  Revmc:            {revmc_speedup[i]:.2f}×")
    print(f"  Helios:           {helios_speedup[i]:.2f}× ★ BEST")
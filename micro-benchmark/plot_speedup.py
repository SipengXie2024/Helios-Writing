import matplotlib.pyplot as plt
import numpy as np

# Set publication-quality parameters for double-column paper
# Target width: ~3.5 inches (single column) or ~7 inches (full width)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 8
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 7
plt.rcParams['figure.titlesize'] = 10
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.6
plt.rcParams['ytick.major.width'] = 0.6

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

# Create figure and axis - sized for double-column paper
# 3.5 inches width for single column, height adjusted for aspect ratio
fig, ax = plt.subplots(figsize=(3.5, 2.4))

# Define positions for bars
positions = [x - 1.5*width, x - 0.5*width, x + 0.5*width, x + 1.5*width]

# Define colors (professional scheme with better contrast)
color_revm = '#7f7f7f'          # Medium gray for baseline
color_forerunner = '#74add1'    # Light blue
color_revmc = '#fdae61'         # Orange (with hatch)
color_helios = '#1a5490'        # Deep blue (highlight)

# Plot bars with refined styling
bars1 = ax.bar(positions[0], revm_native_speedup, width, label='Revm Native',
               color=color_revm, edgecolor='#333333', linewidth=0.4, alpha=0.85)
bars2 = ax.bar(positions[1], forerunner_revm_speedup, width, label='Forerunner-Revm',
               color=color_forerunner, edgecolor='#333333', linewidth=0.4, alpha=0.9)
bars3 = ax.bar(positions[2], revmc_speedup, width, label='Revmc',
               color=color_revmc, edgecolor='#333333', linewidth=0.4,
               hatch='///', alpha=0.9)  # Hatched pattern for normalized data
bars4 = ax.bar(positions[3], helios_speedup, width, label='Helios',
               color=color_helios, edgecolor='#333333', linewidth=0.5)

# Add value labels on bars with improved visibility
label_offset = 0.06

# For Revm baseline (always 1.0)
for i, bar in enumerate(bars1):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + label_offset,
            '1.00×',
            ha='center', va='bottom', fontsize=6, color='#333333')

# For Forerunner-Revm
for i, (bar, speedup) in enumerate(zip(bars2, forerunner_revm_speedup)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + label_offset,
            f'{speedup:.2f}×',
            ha='center', va='bottom', fontsize=6, fontweight='normal')

# For Revmc
for i, (bar, speedup) in enumerate(zip(bars3, revmc_speedup)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + label_offset,
            f'{speedup:.2f}×',
            ha='center', va='bottom', fontsize=6, fontweight='normal')

# Helios: bold and prominent
for i, (bar, speedup) in enumerate(zip(bars4, helios_speedup)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + label_offset,
            f'{speedup:.2f}×',
            ha='center', va='bottom', fontsize=6.5, fontweight='bold', color='#1a5490')

# Add horizontal reference line at y=1.0 (baseline)
ax.axhline(y=1.0, color='black', linestyle='-', linewidth=1.0, alpha=0.5, zorder=0)

# Labels and title
ax.set_ylabel('Speedup over Revm Native\n(higher is better)', fontweight='bold')
# ax.set_xlabel('Benchmark', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(benchmarks, linespacing=0.9)

# Grid for readability
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.4)
ax.set_axisbelow(True)

# Set y-axis limits for better visualization
ax.set_ylim([0, 2.35])

# Legend with clear positioning - move to top for compactness
legend = ax.legend(loc='upper left', framealpha=0.95, edgecolor='#666666',
                   ncol=2, columnspacing=0.8, handlelength=1.2,
                   handletextpad=0.4, borderpad=0.3, labelspacing=0.3,
                   frameon=True, fancybox=False)

# Tight layout with minimal padding
plt.tight_layout(pad=0.3)

# Save figure with high quality settings
plt.savefig('microbench_execution.pdf', dpi=600, bbox_inches='tight',
            pad_inches=0.02, backend='pdf')
plt.savefig('microbench_execution.png', dpi=600, bbox_inches='tight',
            pad_inches=0.02)

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
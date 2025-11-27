import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set publication-quality parameters for double-column paper
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

# Read Pareto data
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_excel(os.path.join(script_dir, 'replay.xlsx'), sheet_name='帕累托效应')

# Use 5000 blocks data (most stable)
data_row = df[df['区块数量'] == 5000].iloc[0]

# Build cumulative distribution data
path_percentages = [0, 1, 5, 10, 20, 50, 100]
execution_coverage = [0,
                      70,  # Top 1%
                      85,  # Top 5%
                      data_row['Top10%占比'] * 100,
                      data_row['Top20%占比'] * 100,
                      data_row['Top50%占比'] * 100,
                      100]

# Create figure sized for double-column paper
fig, ax = plt.subplots(figsize=(3.5, 2.4))

# Define color (grayscale-friendly)
color_main = '#c0392b'  # Dark red

# Plot cumulative distribution curve
ax.plot(path_percentages, execution_coverage, 'o-',
        linewidth=1.5, markersize=5, color=color_main,
        markerfacecolor=color_main, markeredgecolor='white',
        markeredgewidth=0.5)

# Plot diagonal (uniform distribution reference)
ax.plot([0, 100], [0, 100], '--', linewidth=1.0,
        color='#666666', alpha=0.7, label='Uniform Distribution')

# Fill Pareto effect area
ax.fill_between(path_percentages, execution_coverage, path_percentages,
                alpha=0.15, color=color_main)

# Annotation style
bbox_props = dict(boxstyle='round,pad=0.2', facecolor='white',
                  edgecolor=color_main, linewidth=0.8)
arrow_props = dict(arrowstyle='->', color=color_main, lw=1.0)

# Annotate key data points - Top 1%
ax.annotate('70%',
            xy=(1, 70),
            xytext=(8, 55),
            fontsize=7, fontweight='bold',
            bbox=bbox_props, arrowprops=arrow_props)

# Top 5%
ax.annotate('85%',
            xy=(5, 85),
            xytext=(14, 76),
            fontsize=7, fontweight='bold',
            bbox=bbox_props, arrowprops=arrow_props)

# Top 10%
ax.annotate('93%',
            xy=(10, execution_coverage[3]),
            xytext=(22, 86),
            fontsize=7, fontweight='bold',
            bbox=bbox_props, arrowprops=arrow_props)

# Axis labels (no title - use figure caption)
ax.set_xlabel('Fraction of Unique Paths (%)', fontweight='bold')
ax.set_ylabel('Fraction of Frame Executions (%)', fontweight='bold')
ax.set_xlim(-2, 102)
ax.set_ylim(-2, 102)

# X-axis ticks (hide 0 to avoid overlap with 1)
ax.set_xticks([0, 1, 5, 10, 20, 50, 100])
ax.set_xticklabels(['', '1', '5', '10', '20', '50', '100'])

# Grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.4)
ax.set_axisbelow(True)

# Legend
ax.legend(loc='lower right', frameon=True, framealpha=0.95,
          edgecolor='#666666', handlelength=1.5, borderpad=0.3)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Tight layout
plt.tight_layout(pad=0.3)

# Save figure
plt.savefig(os.path.join(script_dir, 'pareto_cumulative.pdf'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)
plt.savefig(os.path.join(script_dir, 'pareto_cumulative.png'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)

print("Figure saved successfully!")
print(f"\nKey statistics:")
print(f"  Top 1%:  {execution_coverage[1]:.0f}% coverage")
print(f"  Top 5%:  {execution_coverage[2]:.0f}% coverage")
print(f"  Top 10%: {execution_coverage[3]:.0f}% coverage")

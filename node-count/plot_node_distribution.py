#!/usr/bin/env python3
"""
Plot SsaGraph Node Count Distribution for Evaluation Section.
Data source: SSA_GRAPH_NODES_ANALYSIS_SUMMARY_CN.md (134,601 graphs)
"""

import matplotlib.pyplot as plt
import numpy as np

# Set publication-quality parameters (same style as plot_speedup.py)
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

# Data from SSA_GRAPH_NODES_ANALYSIS_SUMMARY_CN.md
ranges = [
    '0-10', '11-20', '21-50', '51-100', '101-200',
    '201-500', '501-1K', '1K-2K', '2K-5K', '5K-10K', '10K+'
]
percentages = [0.89, 1.07, 9.23, 10.55, 9.18, 30.81, 7.98, 26.31, 2.70, 0.75, 0.53]

x = np.arange(len(ranges))

# Create figure
fig, ax = plt.subplots(figsize=(3.5, 2.4))

# Bar color (consistent with Helios style)
color_bar = '#1a5490'

# Plot bars
bars = ax.bar(x, percentages, color=color_bar, edgecolor='#333333', linewidth=0.4, alpha=0.9)

# Add percentage labels on significant bars
for bar, pct in zip(bars, percentages):
    if pct >= 7:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{pct:.1f}%', ha='center', va='bottom', fontsize=6, fontweight='bold')

# Labels
ax.set_ylabel('Percentage of Paths (%)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ranges, rotation=35, ha='right')

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.4)
ax.set_axisbelow(True)

# Y-axis limit
ax.set_ylim([0, 36])

plt.tight_layout(pad=0.3)

# Save
plt.savefig('node_distribution.pdf', dpi=600, bbox_inches='tight', pad_inches=0.02)
plt.savefig('node_distribution.png', dpi=600, bbox_inches='tight', pad_inches=0.02)

print("Saved: node_distribution.pdf, node_distribution.png")

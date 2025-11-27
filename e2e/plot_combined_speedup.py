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

# Read CSV files
script_dir = os.path.dirname(os.path.abspath(__file__))
seq_df = pd.read_csv(os.path.join(script_dir, 'block_stats_seq.csv'))
deter_df = pd.read_csv(os.path.join(script_dir, 'block_stats_deter.csv'))
optim_df = pd.read_csv(os.path.join(script_dir, 'block_stats_optim.csv'))
optim_partial_df = pd.read_csv(os.path.join(script_dir, 'block_stats_optim_partial.csv'))

# Define bins and labels
bins = [0, 1, 2, 3, 4, 5, 10, 20, float('inf')]
labels = ['<1×', '1-2×', '2-3×', '3-4×', '4-5×', '5-10×', '10-20×', '≥20×']

def calculate_speedup_distribution(seq_df, target_df):
    """Calculate speedup distribution percentages."""
    common_blocks = set(seq_df['block_number']) & set(target_df['block_number'])
    seq_filtered = seq_df[seq_df['block_number'].isin(common_blocks)].sort_values('block_number')
    target_filtered = target_df[target_df['block_number'].isin(common_blocks)].sort_values('block_number')
    merged = pd.merge(seq_filtered, target_filtered, on='block_number', suffixes=('_seq', '_target'))
    speedups = merged['elapsed_time_ms_seq'] / merged['elapsed_time_ms_target']
    counts, _ = np.histogram(speedups, bins=bins)
    percentages = (counts / len(speedups)) * 100
    p50 = np.percentile(speedups, 50)
    p75 = np.percentile(speedups, 75)
    p90 = np.percentile(speedups, 90)
    return percentages, p50, p75, p90, len(speedups)

# Calculate distributions for all three modes
replay_pct, replay_p50, replay_p75, replay_p90, replay_n = calculate_speedup_distribution(seq_df, deter_df)
online_pct, online_p50, online_p75, online_p90, online_n = calculate_speedup_distribution(seq_df, optim_df)
filtered_pct, filtered_p50, filtered_p75, filtered_p90, filtered_n = calculate_speedup_distribution(seq_df, optim_partial_df)

# Print statistics
print("=" * 60)
print("SPEEDUP STATISTICS")
print("=" * 60)
print(f"\nReplay Mode (n={replay_n}):")
print(f"  P50: {replay_p50:.2f}×, P75: {replay_p75:.2f}×, P90: {replay_p90:.2f}×")
print(f"\nOnline Mode (n={online_n}):")
print(f"  P50: {online_p50:.2f}×, P75: {online_p75:.2f}×, P90: {online_p90:.2f}×")
print(f"\nOnline Filtered (n={filtered_n}):")
print(f"  P50: {filtered_p50:.2f}×, P75: {filtered_p75:.2f}×, P90: {filtered_p90:.2f}×")

# Create figure sized for double-column paper
fig, ax = plt.subplots(figsize=(3.5, 2.4))

# Bar positions
x = np.arange(len(labels))
width = 0.25  # Width of each bar

# Define colors: grayscale-friendly with distinct patterns
color_replay = '#1a5490'    # Dark blue-gray
color_online = '#e67e22'    # Orange
color_filtered = '#74add1'  # Light blue

# Plot grouped bars
bars1 = ax.bar(x - width, replay_pct, width, label='Replay',
               color=color_replay, edgecolor='#333333', linewidth=0.4)
bars2 = ax.bar(x, online_pct, width, label='Online',
               color=color_online, edgecolor='#333333', linewidth=0.4,
               hatch='///')
bars3 = ax.bar(x + width, filtered_pct, width, label='Online (filtered)',
               color=color_filtered, edgecolor='#333333', linewidth=0.4,
               hatch='...')

# Labels
ax.set_xlabel('Speedup Range', fontweight='bold')
ax.set_ylabel('Block Percentage (%)', fontweight='bold')

# X-axis ticks
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=0)

# Y-axis formatting
ax.set_ylim(0, max(max(replay_pct), max(online_pct), max(filtered_pct)) * 1.15)

# Grid
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.4)
ax.set_axisbelow(True)

# Legend
ax.legend(loc='upper right', framealpha=0.95, edgecolor='#666666',
          handlelength=1.2, handletextpad=0.4, borderpad=0.3,
          labelspacing=0.3, frameon=True, fancybox=False)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Tight layout
plt.tight_layout(pad=0.3)

# Save figure
plt.savefig(os.path.join(script_dir, 'combined_speedup_distribution.pdf'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)
plt.savefig(os.path.join(script_dir, 'combined_speedup_distribution.png'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)

print("\nFigure saved successfully!")

# Print distribution table
print("\n" + "=" * 70)
print(f"{'Speedup':<10} {'Replay':>12} {'Online':>12} {'Online(flt)':>12}")
print("=" * 70)
for i, label in enumerate(labels):
    print(f"{label:<10} {replay_pct[i]:>11.1f}% {online_pct[i]:>11.1f}% {filtered_pct[i]:>11.1f}%")

plt.close()

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set academic publication style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.0

# Read CSV files
seq_df = pd.read_csv('block_stats_seq.csv')
deter_df = pd.read_csv('block_stats_deter.csv')

# Find common blocks
common_blocks = set(seq_df['block_number']) & set(deter_df['block_number'])
print(f"Total common blocks: {len(common_blocks)}")

# Filter and merge data
seq_filtered = seq_df[seq_df['block_number'].isin(common_blocks)].sort_values('block_number')
deter_filtered = deter_df[deter_df['block_number'].isin(common_blocks)].sort_values('block_number')
merged = pd.merge(seq_filtered, deter_filtered, on='block_number', suffixes=('_seq', '_deter'))

# Calculate speedups
speedups = merged['elapsed_time_ms_seq'] / merged['elapsed_time_ms_deter']

# Print statistics
print(f"\nReplay Mode (Deter) Speedup Statistics:")
print(f"  Blocks analyzed: {len(speedups)}")
print(f"  Min:    {speedups.min():.2f}×")
print(f"  P25:    {np.percentile(speedups, 25):.2f}×")
print(f"  Median: {speedups.median():.2f}×")
print(f"  P75:    {np.percentile(speedups, 75):.2f}×")
print(f"  P90:    {np.percentile(speedups, 90):.2f}×")
print(f"  P95:    {np.percentile(speedups, 95):.2f}×")
print(f"  P99:    {np.percentile(speedups, 99):.2f}×")
print(f"  Max:    {speedups.max():.2f}×")
print(f"  Mean:   {speedups.mean():.2f}×")

# Define non-uniform bins
bins = [0, 1, 2, 3, 4, 5, 10, 20, float('inf')]
labels = ['<1×', '1-2×', '2-3×', '3-4×', '4-5×', '5-10×', '10-20×', '≥20×']

# Count blocks in each bin
counts, _ = np.histogram(speedups, bins=bins)
percentages = (counts / len(speedups)) * 100

# Calculate percentiles for annotations
p50 = np.percentile(speedups, 50)
p75 = np.percentile(speedups, 75)
p90 = np.percentile(speedups, 90)

# Create figure
fig, ax = plt.subplots(figsize=(10, 5.5), facecolor='white')
ax.set_facecolor('white')

# Create bar chart with academic color scheme
x_pos = np.arange(len(labels))
bars = ax.bar(x_pos, percentages, color='#2c5f8d', edgecolor='none', width=0.8)

# Customize axes
ax.set_xlabel('Speedup', fontsize=14, color='black', fontweight='bold')
ax.set_ylabel('Block Percentage', fontsize=14, color='black', fontweight='bold')
ax.set_title('Replay Mode Speedup Distribution', fontsize=16, color='black', fontweight='bold', pad=20)

# Set x-axis ticks
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=11, color='black')

# Set y-axis
ax.set_ylim(0, max(percentages) * 1.1)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0f}%'))
ax.tick_params(axis='y', labelsize=11, colors='black')

# Grid - academic style with subtle gray
ax.grid(axis='y', alpha=0.2, color='#cccccc', linestyle='-', linewidth=0.5)
ax.set_axisbelow(True)

# Add statistical annotations in academic text box
stats_text = f'P50: {p50:.2f}×\nP75: {p75:.2f}×\nP90: {p90:.2f}×'
ax.text(0.98, 0.97, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        horizontalalignment='right',
        bbox=dict(boxstyle='square', facecolor='white', edgecolor='#333333', linewidth=0.8, alpha=1.0),
        fontweight='normal',
        color='#1a1a1a')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('black')
ax.spines['bottom'].set_color('black')

plt.tight_layout()
plt.savefig('replay_speedup_distribution.pdf', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('replay_speedup_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
print(f"\nSaved replay_speedup_distribution.pdf and replay_speedup_distribution.png")
plt.close()

# Print bin distribution
print(f"\n{'Speedup Range':<15} {'Blocks':<10} {'Percentage':<12}")
print('-' * 37)
for i, (label, count, pct) in enumerate(zip(labels, counts, percentages)):
    print(f'{label:<15} {count:<10} {pct:>6.1f}%')

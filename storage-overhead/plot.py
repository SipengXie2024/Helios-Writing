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

# Data from replay.xlsx
block_counts = [1000, 2000, 3000, 4000, 5000]
block_sizes_mb = [227.93, 421.85, 626.38, 812.41, 1015.72]
helios_artifacts_mb = [119, 188, 301, 362, 426]

# Calculate overhead percentages
overhead_percentages = [(h/b)*100 for h, b in zip(helios_artifacts_mb, block_sizes_mb)]

# Create figure sized for double-column paper
fig, ax = plt.subplots(figsize=(3.5, 2.4))

# Define colors: grayscale-friendly
color_block = '#2c3e50'     # Dark blue-gray
color_helios = '#e67e22'    # Orange (distinct in grayscale)

# Plot both lines with refined styling
line1 = ax.plot(block_counts, block_sizes_mb, 'o-', linewidth=1.5, markersize=5,
                color=color_block, label='Block Data', markerfacecolor='white',
                markeredgewidth=1.2, markeredgecolor=color_block)
line2 = ax.plot(block_counts, helios_artifacts_mb, 's--', linewidth=1.5, markersize=5,
                color=color_helios, label='Helios Artifacts', markerfacecolor='white',
                markeredgewidth=1.2, markeredgecolor=color_helios)

# Add overhead percentage annotations with background
bbox_props = dict(boxstyle='round,pad=0.15', facecolor='white',
                  edgecolor='none', alpha=0.8)
for i, (x, y, pct) in enumerate(zip(block_counts, helios_artifacts_mb, overhead_percentages)):
    ax.annotate(f'{pct:.0f}%',
                xy=(x, y),
                xytext=(0, 8),
                textcoords='offset points',
                ha='center',
                fontsize=6.5,
                color=color_helios,
                fontweight='bold',
                bbox=bbox_props)

# Labels (no title - use figure caption)
ax.set_xlabel('Number of Blocks', fontweight='bold')
ax.set_ylabel('Storage Size (MB)', fontweight='bold')

# Set x-axis ticks
ax.set_xticks(block_counts)
ax.set_xticklabels([f'{x//1000}K' for x in block_counts])

# Set y-axis
ax.set_ylim(0, max(block_sizes_mb) * 1.12)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y):,}'))

# Grid for readability
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.4)
ax.set_axisbelow(True)

# Legend with compact positioning
ax.legend(loc='upper left', framealpha=0.95, edgecolor='#666666',
          handlelength=1.5, handletextpad=0.4, borderpad=0.3,
          labelspacing=0.3, frameon=True, fancybox=False)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Tight layout with minimal padding
plt.tight_layout(pad=0.3)

# Save figure with high quality settings
script_dir = os.path.dirname(os.path.abspath(__file__))
plt.savefig(os.path.join(script_dir, 'storage_growth.pdf'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)
plt.savefig(os.path.join(script_dir, 'storage_growth.png'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)

print("Figure saved successfully!")
print("\n=== Storage Growth Statistics ===")
for i, (blocks, block_size, artifact_size, pct) in enumerate(zip(
        block_counts, block_sizes_mb, helios_artifacts_mb, overhead_percentages)):
    print(f"{blocks:5d} blocks: Block Data = {block_size:7.2f} MB, "
          f"Artifacts = {artifact_size:3d} MB ({pct:4.1f}%)")

plt.close()

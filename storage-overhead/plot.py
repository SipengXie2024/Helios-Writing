import matplotlib.pyplot as plt
import numpy as np

# Data from replay.xlsx
block_counts = [1000, 2000, 3000, 4000, 5000]
block_sizes_mb = [227.93, 421.85, 626.38, 812.41, 1015.72]
helios_artifacts_mb = [119, 188, 301, 362, 426]

# Calculate overhead percentages
overhead_percentages = [(h/b)*100 for h, b in zip(helios_artifacts_mb, block_sizes_mb)]

# Create figure
fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='white')
ax.set_facecolor('white')

# Plot both lines
line1 = ax.plot(block_counts, block_sizes_mb, 'o-', linewidth=2.5, markersize=8,
                color='#2E86AB', label='Block Data', markerfacecolor='white',
                markeredgewidth=2, markeredgecolor='#2E86AB')
line2 = ax.plot(block_counts, helios_artifacts_mb, 's-', linewidth=2.5, markersize=8,
                color='#A23B72', label='Helios Artifacts', markerfacecolor='white',
                markeredgewidth=2, markeredgecolor='#A23B72')

# Add overhead percentage annotations
for i, (x, y, pct) in enumerate(zip(block_counts, helios_artifacts_mb, overhead_percentages)):
    ax.annotate(f'{pct:.1f}%',
                xy=(x, y),
                xytext=(0, 10),
                textcoords='offset points',
                ha='center',
                fontsize=9,
                color='#A23B72',
                fontweight='bold')

# Formatting
ax.set_xlabel('Number of Blocks', fontsize=13, fontweight='bold', color='black')
ax.set_ylabel('Storage Size (MB)', fontsize=13, fontweight='bold', color='black')
ax.set_title('Storage Growth: Block Data vs. Helios Artifacts',
             fontsize=14, fontweight='bold', color='black', pad=15)

# Set x-axis ticks
ax.set_xticks(block_counts)
ax.set_xticklabels([f'{x:,}' for x in block_counts], fontsize=11, color='black')

# Set y-axis
ax.set_ylim(0, max(block_sizes_mb) * 1.15)
ax.tick_params(axis='y', labelsize=11, colors='black')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y):,}'))

# Grid
ax.grid(axis='y', alpha=0.3, color='gray', linestyle='-', linewidth=0.5)
ax.set_axisbelow(True)

# Legend
ax.legend(loc='upper left', fontsize=11, frameon=True, fancybox=False,
          edgecolor='black', framealpha=1)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('black')
ax.spines['bottom'].set_color('black')

plt.tight_layout()
plt.savefig('storage_growth.pdf', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('storage_growth.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Saved storage_growth.pdf and storage_growth.png")

# Print statistics
print("\n=== Storage Growth Statistics ===")
for i, (blocks, block_size, artifact_size, pct) in enumerate(zip(block_counts, block_sizes_mb, helios_artifacts_mb, overhead_percentages)):
    print(f"{blocks:5d} blocks: Block Data = {block_size:7.2f} MB, Artifacts = {artifact_size:3d} MB ({pct:4.1f}% overhead)")

print(f"\nAverage per-block cost:")
print(f"  First 1,000 blocks: {helios_artifacts_mb[0]/block_counts[0]:.2f} KB/block")
print(f"  All 5,000 blocks:   {helios_artifacts_mb[-1]/block_counts[-1]:.2f} KB/block")
print(f"  Reduction:          {(1 - (helios_artifacts_mb[-1]/block_counts[-1])/(helios_artifacts_mb[0]/block_counts[0]))*100:.1f}%")

plt.close()

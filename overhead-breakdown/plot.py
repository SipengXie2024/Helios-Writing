import matplotlib.pyplot as plt
import numpy as np

# Set publication-quality parameters for double-column paper
# Target width: ~3.5 inches (single column)
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

# Data from Fine-grained Breakdown (unit: nanoseconds)
labels = ['Native EVM', 'Helios (SSA)']

# 1. Heavy Ops (Keccak256) - nearly unchanged, Amdahl's law bottleneck
heavy_ops = [314.79, 312.33]

# 2. Light Ops (Caller, MStore, Return, Gas-Op)
light_ops = [46.49, 45.96]

# 3. System Overhead (core optimization target for Helios)
# Native Overhead = Stack (12*5.27) + Gas Check (13*5.47) = 134.35 ns
# Helios Overhead = Node (7*5.14) + Input (7*4.83) + Reg (4*3.97) + Chunk (2*3.99) = 93.65 ns
overhead = [134.35, 93.65]

x = np.arange(len(labels)) * 0.7  # Reduce spacing between bars
width = 0.5

# Create figure sized for double-column paper
fig, ax = plt.subplots(figsize=(3.5, 2.4))

# Define colors: colorful yet grayscale-distinguishable
# Dark (low brightness) -> Medium -> Light (high brightness)
color_heavy = '#1a5490'     # Dark blue-gray (darkest in grayscale)
color_light = '#f39c12'     # Orange with hatch (medium in grayscale)
color_overhead = '#85c1e9'  # Light blue (lightest in grayscale)

# Plot stacked bars with hatching for print-friendly distinction
p1 = ax.bar(x, heavy_ops, width, label='Heavy Ops (Keccak)',
            color=color_heavy, edgecolor='black', linewidth=0.5)
p2 = ax.bar(x, light_ops, width, bottom=heavy_ops, label='Light Ops',
            color=color_light, edgecolor='black', linewidth=0.5,
            hatch='///')
p3 = ax.bar(x, overhead, width, bottom=np.array(heavy_ops)+np.array(light_ops),
            label='System Overhead', color=color_overhead, edgecolor='black',
            linewidth=0.5)

# Labels (no title - use figure caption in paper)
ax.set_ylabel('Latency per Iteration (ns)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels)

# Legend with compact positioning - place outside plot area
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=3,
          framealpha=0.95, edgecolor='#666666',
          handlelength=1.0, handletextpad=0.3, borderpad=0.25,
          labelspacing=0.2, columnspacing=0.8, frameon=True, fancybox=False,
          fontsize=8)

# Annotate overhead reduction on bars with white background box
bbox_props = dict(boxstyle='round,pad=0.2', facecolor='white',
                  edgecolor='none', alpha=0.85)

# Native Overhead
ax.annotate('134 ns\n(Stack/Gas)', xy=(x[0], 314.79 + 46.49 + 134.35/2),
            ha='center', va='center', color='black', fontsize=7.5,
            fontweight='bold', bbox=bbox_props)
# Helios Overhead
ax.annotate('94 ns\n(Graph/Reg/Gas)', xy=(x[1], 312.33 + 45.96 + 93.65/2),
            ha='center', va='center', color='black', fontsize=7.5,
            fontweight='bold', bbox=bbox_props)

# Total time annotations
total_native = sum([heavy_ops[0], light_ops[0], overhead[0]])
total_helios = sum([heavy_ops[1], light_ops[1], overhead[1]])

ax.annotate(f'{total_native:.0f} ns', xy=(x[0], total_native), xytext=(0, 4),
            textcoords="offset points", ha='center', fontsize=8, fontweight='bold')
ax.annotate(f'{total_helios:.0f} ns', xy=(x[1], total_helios), xytext=(0, 4),
            textcoords="offset points", ha='center', fontsize=8, fontweight='bold')

# Grid for readability
ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.4)
ax.set_axisbelow(True)

# Set axis limits - extend Y to avoid legend overlap
ax.set_ylim([0, 620])
ax.set_xlim([-0.4, 1.1])

# Tight layout with minimal padding
plt.tight_layout(pad=0.3)

# Save figure with high quality settings
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
plt.savefig(os.path.join(script_dir, 'overhead-breakdown.pdf'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)
plt.savefig(os.path.join(script_dir, 'overhead-breakdown.png'), dpi=600,
            bbox_inches='tight', pad_inches=0.02)

print("Figure saved successfully!")
print(f"\nTotal Native: {total_native:.2f} ns")
print(f"Total Helios: {total_helios:.2f} ns")

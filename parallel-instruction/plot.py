import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 数据定义
workloads = ['ERC20-Transfer', 'Uniswap-V2-Swap-1hop', 'Uniswap-V2-Swap-4hop']
data = {
    'ERC20-Transfer': {'native': 4.9406, 'parallel': 41.51, 'cplr': 0.122222},
    'Uniswap-V2-Swap-1hop': {'native': 62.021, 'parallel': 417.69, 'cplr': 0.090978},
    'Uniswap-V2-Swap-4hop': {'native': 172.49, 'parallel': 1031.9, 'cplr': 0.037736}
}

slowdown_factors = []
theoretical_speedups = []
labels = ['ERC20\nTransfer', 'Uniswap V2\n1-hop Swap', 'Uniswap V2\n4-hop Swap']

for workload in workloads:
    native = data[workload]['native']
    parallel = data[workload]['parallel']
    cplr = data[workload]['cplr']
    
    slowdown = parallel / native
    slowdown_factors.append(slowdown)
    
    # 理论speedup = 1/CPLR
    theoretical = 1 / cplr if cplr > 0 else 1
    theoretical_speedups.append(theoretical)

fig, ax = plt.subplots(figsize=(6, 4))

x = np.arange(len(labels))
bars = ax.bar(x, slowdown_factors, width=0.6,
              color='#d62728', alpha=0.8, edgecolor='black', linewidth=1.5)

# 标注具体数值
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
            f'{height:.1f}× slower', ha='center', va='bottom', 
            fontsize=10, fontweight='bold')

ax.set_ylabel('Parallel Slowdown vs. Revm Native', fontsize=11, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylim(0, max(slowdown_factors) + 1.8)

# 网格
ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, axis='y')
ax.set_axisbelow(True)

ax.set_title('8-Thread Parallelism Severely Underperforms Revm Native', 
             fontsize=11, fontweight='bold', pad=12)

# CPLR说明文本框
note_text = (
    f"Note: Critical Path Length Ratio (CPLR) analysis predicts theoretical speedups of\n"
    f"{theoretical_speedups[0]:.1f}×, {theoretical_speedups[1]:.1f}×, and {theoretical_speedups[2]:.1f}× "
    f"for these workloads. Actual performance shows 6–8× slowdown instead."
)

ax.text(0.5, -0.15, note_text,
        transform=ax.transAxes,
        fontsize=8.5,
        ha='center',
        va='top',
        bbox=dict(boxstyle='round,pad=0.6', facecolor='lightyellow', 
                 edgecolor='gray', alpha=0.9, linewidth=1),
        style='italic')

plt.tight_layout()
plt.subplots_adjust(bottom=0.15)

plt.savefig('parallel_slowdown_corrected.pdf', dpi=300, bbox_inches='tight')
plt.savefig('parallel_slowdown_corrected.png', dpi=300, bbox_inches='tight')
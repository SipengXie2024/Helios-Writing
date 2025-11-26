import matplotlib.pyplot as plt
import numpy as np

# 数据来源：你的Fine-grained Breakdown
# 单位：纳秒 (ns)
labels = ['Native EVM', 'Helios (SSA)']

# 1. Heavy Ops (Keccak256) - 几乎不变，这是Amdahl定律的瓶颈
# Native: 314.79, Helios: 312.33
heavy_ops = [314.79, 312.33]

# 2. Light Ops (Caller, MStore, Return, Gas-Op)
# Native: 5.19 + 3*5.35 + 5.12 + 20.13 = ~46.49
# Helios: 4.28 + 3*5.61 + 3.97 + 20.88 = ~45.96
light_ops = [46.49, 45.96]

# 3. System Overhead (这是Helios优化的核心！)
# Native Overhead = Stack (12*5.27) + Gas Check (13*5.47) = 134.35 ns
# Helios Overhead = Node (7*5.14) + Input (7*4.83) + Reg (4*3.97) + Chunk (2*3.99) = 93.65 ns
overhead = [134.35, 93.65]

x = np.arange(len(labels))
width = 0.5

fig, ax = plt.subplots(figsize=(6, 5))

# 绘制堆叠图
p1 = ax.bar(x, heavy_ops, width, label='Heavy Ops (Keccak)', color='#e74c3c', alpha=0.9, edgecolor='black')
p2 = ax.bar(x, light_ops, width, bottom=heavy_ops, label='Light Ops', color='#f1c40f', alpha=0.9, edgecolor='black')
p3 = ax.bar(x, overhead, width, bottom=np.array(heavy_ops)+np.array(light_ops), label='System Overhead', color='#3498db', alpha=0.9, edgecolor='black')

# 添加标注
ax.set_ylabel('Latency per Iteration (ns)', fontsize=12)
ax.set_title('Execution Latency Breakdown', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12)
ax.legend(loc='upper right')

# 在Overhead柱子上标注减少量
# Native Overhead
ax.annotate('134ns\n(Stack/Gas)', xy=(0, 314+46+134/2), ha='center', va='center', color='white', fontweight='bold')
# Helios Overhead
ax.annotate('94ns\n(Graph/Reg/Gas)', xy=(1, 312+46+94/2), ha='center', va='center', color='white', fontweight='bold')

# 总时间标注
total_native = sum([heavy_ops[0], light_ops[0], overhead[0]])
total_helios = sum([heavy_ops[1], light_ops[1], overhead[1]])
ax.annotate(f'Total: {total_native:.0f}ns', xy=(0, total_native), xytext=(0, 5), textcoords="offset points", ha='center', fontweight='bold')
ax.annotate(f'Total: {total_helios:.0f}ns', xy=(1, total_helios), xytext=(0, 5), textcoords="offset points", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('overhead-breakdown.pdf', dpi=300, bbox_inches='tight')
plt.savefig('overhead-breakdown.png', dpi=300, bbox_inches='tight')
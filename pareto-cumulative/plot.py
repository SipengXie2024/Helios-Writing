import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取帕累托效应数据
df = pd.read_excel('replay.xlsx', sheet_name='帕累托效应')

# 使用5000块数据（最稳定）
data_row = df[df['区块数量'] == 5000].iloc[0]

# 构建完整的累积分布数据
path_percentages = [0, 1, 5, 10, 20, 50, 100]
execution_coverage = [0, 
                      70,  # Top 1%
                      85,  # Top 5%
                      data_row['Top10%占比'] * 100,
                      data_row['Top20%占比'] * 100,
                      data_row['Top50%占比'] * 100,
                      100]

# 创建图表
fig, ax = plt.subplots(figsize=(5, 3.8))

# 绘制累积分布曲线
ax.plot(path_percentages, execution_coverage, 'o-', 
        linewidth=2.5, markersize=7, color='#d62728',
        markerfacecolor='#d62728', markeredgewidth=0)

# 绘制对角线（均匀分布参考）
ax.plot([0, 100], [0, 100], '--', linewidth=1.5, 
        color='gray', alpha=0.6, label='Uniform Distribution')

# 填充Pareto效应区域
ax.fill_between(path_percentages, execution_coverage, path_percentages,
                alpha=0.15, color='#d62728')

# 标注关键数据点 - Top 1%
ax.annotate('70%', 
            xy=(1, 70), 
            xytext=(8, 58),
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                     edgecolor='#d62728', linewidth=1.5),
            arrowprops=dict(arrowstyle='->', color='#d62728', lw=1.5))

# Top 5%
ax.annotate('85%', 
            xy=(5, 85), 
            xytext=(12, 78),
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                     edgecolor='#d62728', linewidth=1.5),
            arrowprops=dict(arrowstyle='->', color='#d62728', lw=1.5))

# Top 10%
ax.annotate('93%', 
            xy=(10, execution_coverage[3]), 
            xytext=(22, 88),
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                     edgecolor='#d62728', linewidth=1.5),
            arrowprops=dict(arrowstyle='->', color='#d62728', lw=1.5))

# 设置坐标轴
ax.set_xlabel('Fraction of Unique Paths (%)', fontsize=11, fontweight='bold')
ax.set_ylabel('Fraction of Frame Executions (%)', fontsize=11, fontweight='bold')
ax.set_xlim(-2, 102)
ax.set_ylim(-2, 102)

# 设置x轴刻度，隐藏0避免与1重叠
ax.set_xticks([0, 1, 5, 10, 20, 50, 100])
ax.set_xticklabels(['', '1', '5', '10', '20', '50', '100'])

# 网格
ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.5)
ax.set_axisbelow(True)

# 图例
ax.legend(loc='lower right', frameon=True, framealpha=0.95, 
          fontsize=9, edgecolor='gray')

# 标题
ax.set_title('Extreme Path Locality: Top 1% Paths Handle 70% Executions', 
             fontsize=11, fontweight='bold', pad=12)

plt.tight_layout()
plt.savefig('pareto_cumulative.pdf', dpi=300, bbox_inches='tight')
plt.savefig('pareto_cumulative.png', dpi=300, bbox_inches='tight')
print("Figure saved successfully")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read CSV files
seq_df = pd.read_csv('block_stats_seq.csv')
deter_df = pd.read_csv('block_stats_deter.csv')
optim_df = pd.read_csv('block_stats_optim.csv')
optim_partial_df = pd.read_csv('block_stats_optim_partial.csv')

# Find common blocks shared across seq/deter/optim for backwards compatibility
common_blocks = set(seq_df['block_number']) & set(deter_df['block_number']) & set(optim_df['block_number'])
print(f"Total common blocks (seq/deter/optim): {len(common_blocks)}")


def prepare_speedup_dataset(seq_df, target_df, suffix, display_name, block_subset=None):
    """
    Filter the sequential and target dataframes to the desired block set and
    compute the speedup values for histogram/stat generation.
    """
    if block_subset is None:
        block_subset = set(seq_df['block_number']) & set(target_df['block_number'])
    else:
        block_subset = set(block_subset)

    print(f"\n{display_name} matching blocks: {len(block_subset)}")
    if not block_subset:
        raise ValueError(f"No overlapping blocks found for {display_name} dataset")

    seq_filtered = seq_df[seq_df['block_number'].isin(block_subset)].sort_values('block_number')
    target_filtered = target_df[target_df['block_number'].isin(block_subset)].sort_values('block_number')
    merged = pd.merge(seq_filtered, target_filtered, on='block_number', suffixes=('_seq', f'_{suffix}'))

    speedup_series = merged['elapsed_time_ms_seq'] / merged[f'elapsed_time_ms_{suffix}']

    print(f"{display_name} speedup stats:")
    print(f"  Min: {speedup_series.min():.2f}x")
    print(f"  Max: {speedup_series.max():.2f}x")
    print(f"  Mean: {speedup_series.mean():.2f}x")
    print(f"  Median: {speedup_series.median():.2f}x")

    return speedup_series.values

def create_speedup_histogram(speedups, title, filename):
    """
    Create speedup distribution histogram matching the reference style
    """
    # Define bins: [0,1), [1,2), [2,3), ..., [49,50), [50,inf)
    bins = list(range(0, 51)) + [float('inf')]
    labels = ['<1×'] + [f'{i}×' for i in range(1, 50)] + ['≥50×']

    # Count blocks in each bin
    counts, _ = np.histogram(speedups, bins=bins)
    percentages = (counts / len(speedups)) * 100

    # Create figure with white background
    fig, ax = plt.subplots(figsize=(14, 6), facecolor='white')
    ax.set_facecolor('white')

    # Create bar chart
    x_pos = np.arange(len(labels))
    bars = ax.bar(x_pos, percentages, color='#5DADE2', edgecolor='none', width=0.8)

    # Customize axes
    ax.set_xlabel('Speedup', fontsize=14, color='black', fontweight='bold')
    ax.set_ylabel('Block Percentage', fontsize=14, color='black', fontweight='bold')
    ax.set_title(title, fontsize=16, color='black', fontweight='bold', pad=20)

    # Set x-axis ticks - show every 5th label to avoid crowding
    tick_positions = list(range(0, len(labels), 5))
    if len(labels) - 1 not in tick_positions:
        tick_positions.append(len(labels) - 1)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([labels[i] for i in tick_positions], fontsize=11, color='black')

    # Set y-axis
    ax.set_ylim(0, max(percentages) * 1.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0f}%'))
    ax.tick_params(axis='y', labelsize=11, colors='black')

    # Grid
    ax.grid(axis='y', alpha=0.3, color='gray', linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')

    plt.tight_layout()
    plt.savefig(filename, dpi=300, facecolor='white')
    print(f"\nSaved {filename}")
    plt.close()

# Prepare datasets
deter_speedups = prepare_speedup_dataset(seq_df, deter_df, 'deter', 'Deter', block_subset=common_blocks)
optim_speedups = prepare_speedup_dataset(seq_df, optim_df, 'optim', 'Optim', block_subset=common_blocks)
optim_partial_speedups = prepare_speedup_dataset(seq_df, optim_partial_df, 'optim_partial', 'Optim Partial')

# Generate charts
create_speedup_histogram(
    deter_speedups,
    'Deter Speedup Distribution',
    'deter_speedup_distribution.png'
)

create_speedup_histogram(
    optim_speedups,
    'Optim Speedup Distribution',
    'optim_speedup_distribution.png'
)

create_speedup_histogram(
    optim_partial_speedups,
    'Optim Partial Speedup Distribution',
    'optim_partial_speedup_distribution.png'
)

print("\nCharts generated successfully!")

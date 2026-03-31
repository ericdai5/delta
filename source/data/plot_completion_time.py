import csv
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Use serif font for all text
plt.rcParams['font.family'] = 'serif'

# Load data
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, "comparative_metric_data.csv")

baseline_all = []
delta_all = []
baseline_bf = []  # baseline first
delta_bf = []
baseline_df = []  # delta first
delta_df = []

with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row["PID"].strip():
            continue
        b = float(row["Completion_Time_Baseline_min"])
        d = float(row["Completion_Time_Formulize_min"])
        order = row["Order_Group"].strip()

        baseline_all.append(b)
        delta_all.append(d)

        if order == "Baseline first":
            baseline_bf.append(b)
            delta_bf.append(d)
        else:
            baseline_df.append(b)
            delta_df.append(d)

# Colors
BASELINE_COLOR = "#E57373"  # coral/red
DELTA_COLOR = "#81C784"     # green

# Figure setup
fig, ax = plt.subplots(figsize=(10, 6))

# Y positions for each box (from top to bottom)
# Consistent 0.6 gaps: bar-to-bar, delta-to-separator, title-to-bar, bottom margin
# 0.3 gap: separator-to-title, top margin
positions = {
    'all_baseline': 4.8,
    'all_delta': 4.2,
    'bf_baseline': 2.4,
    'bf_delta': 1.8,
    'df_baseline': 0,
    'df_delta': -0.6,
}

def plot_box_with_points(data, y_pos, color, label_mean=True, mean_offset=-0.35):
    """Plot a horizontal boxplot with jittered points and mean marker."""
    # Box plot
    bp = ax.boxplot(data, positions=[y_pos], vert=False, widths=0.3,
                    patch_artist=True,
                    boxprops=dict(facecolor=color, edgecolor='black', linewidth=1),
                    medianprops=dict(color='white', linewidth=2),
                    whiskerprops=dict(color='black', linewidth=1),
                    capprops=dict(color='black', linewidth=1),
                    flierprops=dict(marker='o', markerfacecolor=color, markeredgecolor=color, markersize=6))

    # Jittered points
    jitter = np.random.uniform(-0.15, 0.15, len(data))
    ax.scatter(data, [y_pos + j for j in jitter],
               c=color, edgecolors=color, s=40, alpha=0.7, zorder=3)

    # Mean marker (diamond)
    mean_val = np.mean(data)
    ax.scatter([mean_val], [y_pos], marker='D', c='white', edgecolors='black',
               s=80, zorder=4, linewidths=1.5)

    # Mean label
    if label_mean:
        ax.text(mean_val, y_pos + mean_offset, f'{mean_val:.1f}',
                ha='center', va='top', fontsize=16, fontweight='normal')

    return bp

# Set random seed for reproducible jitter
np.random.seed(42)

# Plot all groups
plot_box_with_points(baseline_all, positions['all_baseline'], BASELINE_COLOR)
plot_box_with_points(delta_all, positions['all_delta'], DELTA_COLOR)

plot_box_with_points(baseline_bf, positions['bf_baseline'], BASELINE_COLOR)
plot_box_with_points(delta_bf, positions['bf_delta'], DELTA_COLOR)

plot_box_with_points(baseline_df, positions['df_baseline'], BASELINE_COLOR)
plot_box_with_points(delta_df, positions['df_delta'], DELTA_COLOR)

# Dashed separator lines (0.9 gap below Delta bars, 0.3 above titles)
ax.axhline(y=3.3, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax.axhline(y=0.9, color='gray', linestyle='--', linewidth=1, alpha=0.5)

# Y-axis labels
ax.set_yticks([5.5, 3, 0.5])
ax.set_yticklabels(['', '', ''])

# Add group labels (0.3 below separator, 0.6 above baseline)
ax.text(10, 5.4, 'All (n=19)', ha='center', va='center', fontsize=15, fontweight='bold')
ax.text(10, 3.0, 'Baseline first (n=9)', ha='center', va='center', fontsize=15, fontweight='bold')
ax.text(10, 0.6, 'Delta first (n=10)', ha='center', va='center', fontsize=15, fontweight='bold')

# Y-axis row labels removed - using legend instead

# X-axis
ax.set_xlabel('Time (minutes)', fontsize=17, labelpad=10)
ax.tick_params(axis='x', labelsize=16)
ax.set_xlim(-0.5, 20.5)
ax.set_xticks([0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20])

# Y-axis limits (0.3 margin top, 0.6 margin bottom)
ax.set_ylim(-1.5, 5.7)

# Remove y-axis ticks
ax.tick_params(axis='y', left=False)

# Remove top, left, right spines; keep only bottom
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

# DEBUG: Add horizontal lines at key y-positions to visualize spacing
DEBUG = False
if DEBUG:
    for name, y in positions.items():
        ax.axhline(y=y, color='blue', linestyle=':', linewidth=0.5, alpha=0.3)
        ax.text(-0.3, y, f'{name}: {y}', fontsize=8, va='center', ha='right')
    # Show separator positions
    ax.text(-0.3, 3.3, 'sep1: 3.3', fontsize=8, va='center', ha='right', color='red')
    ax.text(-0.3, 0.9, 'sep2: 0.9', fontsize=8, va='center', ha='right', color='red')
    # Show label positions
    ax.text(-0.3, 5.4, 'lbl: 5.4', fontsize=8, va='center', ha='right', color='green')
    ax.text(-0.3, 3.0, 'lbl: 3.0', fontsize=8, va='center', ha='right', color='green')
    ax.text(-0.3, 0.6, 'lbl: 0.6', fontsize=8, va='center', ha='right', color='green')
    # Print spacing calculations
    print("=== SPACING DEBUG ===")
    print(f"Group 1: baseline(4.8) - delta(4.2) = {4.8-4.2}")
    print(f"Group 1: delta(4.2) - sep(3.3) = {4.2-3.3}")
    print(f"Group 1: sep(3.3) - label(3.0) = {3.3-3.0}")
    print(f"Group 2: label(3.0) - baseline(2.4) = {3.0-2.4}")
    print(f"Group 2: baseline(2.4) - delta(1.8) = {2.4-1.8}")
    print(f"Group 2: delta(1.8) - sep(0.9) = {1.8-0.9}")
    print(f"Group 2: sep(0.9) - label(0.6) = {0.9-0.6}")
    print(f"Group 3: label(0.6) - baseline(0) = {0.6-0}")
    print(f"Group 3: baseline(0) - delta(-0.6) = {0-(-0.6)}")
    print(f"Bottom margin: delta(-0.6) - ylim(-1.2) = {-0.6-(-1.2)}")

# Legend
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
legend_elements = [
    Patch(facecolor=BASELINE_COLOR, edgecolor='black', label='Baseline'),
    Patch(facecolor=DELTA_COLOR, edgecolor='black', label='Delta'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='white',
           markeredgecolor='black', markersize=10, label='Mean', linestyle='None')
]
ax.legend(handles=legend_elements, loc='lower right', frameon=True, fontsize=16)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(left=0.10)

# Save figure
output_path = os.path.join(DATA_DIR, "..", "fig", "completion_time.pdf")
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print(f"Saved to {output_path}")

# Also save PNG for preview
output_png = os.path.join(DATA_DIR, "completion_time.png")
plt.savefig(output_png, bbox_inches='tight', dpi=150)
print(f"Saved to {output_png}")

# plt.show()  # Uncomment for interactive viewing

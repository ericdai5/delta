import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV data
df = pd.read_csv('task_final.csv')

# Extract the three rating columns
easier_col = df.columns[2]  # "With which library was it easier to complete the task?"
suited_col = df.columns[4]  # "Which library seemed better suited for the task?"
language_col = df.columns[6]  # "Which library better matched the language you would use to describe the task?"

# Count responses for each rating (1-7)
questions = {
    'Easier': easier_col,
    'Better suited': suited_col,
    'Language match': language_col
}

# Calculate counts for each rating
data = {}
for label, col in questions.items():
    counts = df[col].value_counts().sort_index()
    data[label] = [counts.get(i, 0) for i in range(1, 8)]

# Create diverging stacked bar chart
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif']
fig, ax = plt.subplots(figsize=(12, 4.5))

categories = list(reversed(list(data.keys())))  # Reverse order: Easier, Better suited, Language match
# Darker color scheme
colors = ['#8b0000', '#d45a3a', '#f4a582', '#969696', '#92c5de', '#4393c3', '#0868ac']

# Calculate positions for diverging chart (center at 4)
y_pos = np.arange(len(categories)) * 0.6  # Reduce spacing between bars
bar_height = 0.5

# Draw dividing line behind bars (thin and behind)
ax.axvline(x=0, color='#cccccc', linewidth=0.5, zorder=0)

for i, category in enumerate(categories):
    counts = data[category]
    y = y_pos[i]
    center_count = counts[3]

    # Left side (1-3) - Baseline
    left_counts = counts[:3][::-1]  # Reverse for stacking left
    left_pos = center_count / 2  # Start after neutral section
    for j, count in enumerate(left_counts):
        rating = 3 - j
        ax.barh(y, -count, bar_height, left=-left_pos,
                color=colors[rating-1], edgecolor='white', linewidth=1)
        if count > 0:
            ax.text(-left_pos - count/2, y, str(count),
                   ha='center', va='center', fontsize=28, fontweight='bold', color='white')
        left_pos += count

    # Center (4) - Neutral
    if center_count > 0:
        ax.barh(y, center_count, bar_height, left=-center_count/2,
                color=colors[3], edgecolor='white', linewidth=1)
        ax.text(0, y, str(center_count),
               ha='center', va='center', fontsize=28, fontweight='bold', color='white')

    # Right side (5-7) - Delta
    right_counts = counts[4:]
    right_pos = center_count / 2  # Start after neutral section
    for j, count in enumerate(right_counts):
        rating = j + 5
        ax.barh(y, count, bar_height, left=right_pos,
                color=colors[rating-1], edgecolor='white', linewidth=1)
        if count > 0:
            ax.text(right_pos + count/2, y, str(count),
                   ha='center', va='center', fontsize=28, fontweight='bold', color='white')
        right_pos += count

# Customize the plot
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=28, fontweight='bold')
ax.set_xlabel('Number of participants', fontsize=28, fontweight='bold', labelpad=15)
ax.tick_params(axis='x', labelsize=28)
ax.tick_params(axis='y', pad=15, length=0)

# Set x-axis limits and labels (asymmetric based on actual data)
max_left = max([sum(counts[:3]) for counts in data.values()])
max_right = max([sum(counts[4:]) for counts in data.values()])
ax.set_xlim(-max_left-1, max_right+2)

# Set x-axis ticks at increments of 2 with absolute value labels
x_ticks = np.arange(-max_left-1, max_right+3, 2)
ax.set_xticks(x_ticks)
ax.set_xticklabels([str(abs(int(x))) for x in x_ticks])

# Add rating scale legend at the top
legend_y = max(y_pos) + 0.75
for i, rating in enumerate(range(1, 8)):
    ax.add_patch(plt.Rectangle((i-3.5, legend_y), 0.8, 0.3,
                              facecolor=colors[i], edgecolor='white', linewidth=1))
    ax.text(i-3.1, legend_y + 0.35, str(rating),
           ha='center', va='bottom', fontsize=22, fontweight='bold')

# Add legend for Baseline and Delta (next to rating scale)
ax.text(-5, legend_y + 0.15, '← Baseline', fontsize=28, fontweight='bold',
        ha='right', va='center', color='#b2182b')
ax.text(5, legend_y + 0.15, 'Delta →', fontsize=28, fontweight='bold',
        ha='left', va='center', color='#2166ac')

ax.set_ylim(-0.8, max(y_pos) + 1.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig('subjective_ratings_improved.pdf', dpi=300, bbox_inches='tight')
plt.savefig('subjective_ratings_improved.png', dpi=300, bbox_inches='tight')
print("Figure saved as subjective_ratings_improved.pdf and subjective_ratings_improved.png")

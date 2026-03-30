import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

df1 = pd.read_csv(os.path.join(DATA_DIR, "Observational Task 1 Form.csv"))
df2 = pd.read_csv(os.path.join(DATA_DIR, "Observational Task 2 Form.csv"))
for df in [df1, df2]:
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

intuitive_labels = [
    "Very unintuitive", "Somewhat unintuitive",
    "Neither intuitive nor unintuitive",
    "Somewhat intuitive", "Very intuitive",
]
difficulty_labels = [
    "Very difficult", "Somewhat difficult",
    "Neither easy nor difficult",
    "Somewhat easy", "Very easy",
]

colors = ["#d73027", "#fc8d59", "#cccccc", "#91bfdb", "#4575b4"]


def get_counts(df, columns, scale_labels):
    results = {}
    for col in columns:
        valid = df[col].dropna()
        valid = valid[valid != "Did not do"]
        counts = [int((valid == lab).sum()) for lab in scale_labels]
        results[col] = counts
    return results


def short_name(col):
    if "[" in col and "]" in col:
        return col.split("[")[1].rstrip("]").strip()
    return col


def draw_bars(ax, counts, names, max_rows):
    n = len(names)
    data = np.array(list(counts.values()), dtype=float)
    row_totals = data.sum(axis=1, keepdims=True)
    row_totals[row_totals == 0] = 1
    pcts = data / row_totals * 100
    y = np.arange(n) * 0.25
    bar_h = 0.15

    for i in range(n):
        cum = 0.0
        for j in range(5):
            w = pcts[i, j]
            if w > 0:
                ax.barh(y[i], w, left=cum, height=bar_h,
                        color=colors[j], edgecolor="white", linewidth=0.5)
                if w >= 8:
                    ax.text(cum + w / 2, y[i], str(int(data[i, j])),
                            ha="center", va="center", fontsize=18,
                            fontweight="bold",
                            color="white" if j in [0, 4] else "#333")
            cum += w

    ax.set_xlim(0, 105)
    ax.set_ylim((max_rows - 1) * 0.25 + 0.15, -0.15)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=20)
    for sp in ["top", "right", "bottom"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)


def plot_side_by_side(counts1, names1, counts2, names2, scale_labels, title, filename):
    n1 = len(names1)
    n2 = len(names2)
    max_rows = max(n1, n2)

    fig_w = 32
    fig_h = 0.6 * max_rows + 2
    fig = plt.figure(figsize=(fig_w, fig_h), constrained_layout=True)

    # 3 rows: title, plots, legend.
    outer = fig.add_gridspec(3, 1, height_ratios=[0.06, 1, 0.06], hspace=0.15)

    # Title row
    ax_title = fig.add_subplot(outer[0])
    ax_title.axis("off")
    ax_title.text(0.5, 0.5, title, fontsize=24, fontweight="bold",
                  ha="center", va="center", transform=ax_title.transAxes)

    # Middle row — split into two columns for the plots
    inner = outer[1].subgridspec(1, 2, wspace=0.08)
    ax1 = fig.add_subplot(inner[0])
    ax2 = fig.add_subplot(inner[1])

    draw_bars(ax1, counts1, names1, max_rows)
    ax1.set_title("Task 1: Radioactive Decay", fontsize=20, fontweight="bold", pad=10)

    draw_bars(ax2, counts2, names2, max_rows)
    ax2.set_title("Task 2: Expected Value", fontsize=20, fontweight="bold", pad=10)

    # Legend row
    ax_leg = fig.add_subplot(outer[2])
    ax_leg.axis("off")
    patches = [mpatches.Patch(facecolor=colors[j], edgecolor="white", label=scale_labels[j])
               for j in range(5)]
    ax_leg.legend(handles=patches, loc="center", ncol=5, fontsize=24,
                  frameon=False, handlelength=1.8, columnspacing=1.5)

    plt.savefig(filename, dpi=200, bbox_inches="tight", pad_inches=0.2)
    plt.close()
    print(f"Saved {filename}")


# Gather data
ic1 = [c for c in df1.columns if c.startswith("How intuitive") and "[" in c]
dc1 = [c for c in df1.columns if c.startswith("How difficult") and "[" in c]
ic2 = [c for c in df2.columns if c.startswith("How intuitive") and "[" in c]
dc2 = [c for c in df2.columns if c.startswith("How difficult") and "[" in c]

names_i1 = [short_name(c) for c in ic1]
names_d1 = [short_name(c) for c in dc1]
names_i2 = [short_name(c) for c in ic2]
names_d2 = [short_name(c) for c in dc2]

ci1 = get_counts(df1, ic1, intuitive_labels)
cd1 = get_counts(df1, dc1, difficulty_labels)
ci2 = get_counts(df2, ic2, intuitive_labels)
cd2 = get_counts(df2, dc2, difficulty_labels)

plot_side_by_side(ci1, names_i1, ci2, names_i2, intuitive_labels,
                  "Self-Reported Intuitiveness (n = 10)",
                  os.path.join(DATA_DIR, "intuitiveness_combined.pdf"))

plot_side_by_side(cd1, names_d1, cd2, names_d2, difficulty_labels,
                  "Self-Reported Difficulty (n = 10)",
                  os.path.join(DATA_DIR, "difficulty_combined.pdf"))

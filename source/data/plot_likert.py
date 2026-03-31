import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(DATA_DIR, "..", "fig")

df1 = pd.read_csv(os.path.join(DATA_DIR, "Observational Task 1 Form.csv"))
df2 = pd.read_csv(os.path.join(DATA_DIR, "Observational Task 2 Form.csv"))
for df in [df1, df2]:
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

intuitive_labels = [
    "Very intuitive", "Somewhat intuitive",
    "Neither intuitive nor unintuitive",
    "Somewhat unintuitive", "Very unintuitive",
]
difficulty_labels = [
    "Very easy", "Somewhat easy",
    "Neither easy nor difficult",
    "Somewhat difficult", "Very difficult",
]

colors = ["#0868ac", "#92c5de", "#969696", "#d45a3a", "#8b0000"]


def get_counts(df, columns, scale_labels):
    results = {}
    for col in columns:
        valid = df[col].dropna()
        valid = valid[valid != "Did not do"]
        counts = [int((valid == lab).sum()) for lab in scale_labels]
        results[col] = counts
    return results


ABBREV = {
    # Task 1
    "Create the static formula": "Create static formula",
    "Refer to a variable using a variable selector in the variables object": "Variable selector",
    "Giving a variable a descriptive label": "Variable label",
    "Formatting a variable's displayed value (significant figures / precision)": "Format display value",
    "Make a variable draggable": "Make draggable",
    "Expressing the computation with a semantics function": "Semantics function",
    "Accessing a variable's value in a semantics function": "Access variable value",
    "Setting a variable's value in a semantics function": "Set variable value",
    "Get the interactive formula working just the way I wanted": "Get formula working as intended",
    # Task 2
    "Knowing where to place a step in the formula semantics": "Place step in semantics",
    "Adding a description (plain text)": "Description (text)",
    "Adding a description (text and value)": "Description (text+value)",
    "Adding a description (value only)": "Description (value)",
    "Labeling a variable (plain text)": "Label variable (text)",
    "Labeling a variable (text and value)": "Label variable (text+value)",
    "Labeling a variable (value only)": "Label variable (value)",
    "Labeling an expression (plain text)": "Label expression (text)",
    "Labeling an expression (text and value)": "Label expression (text+value)",
    "Labeling an expression (value only)": "Label expression (value)",
    "Getting the formula walkthrough working the way I wanted": "Get walkthrough working as intended",
}


def short_name(col):
    if "[" in col and "]" in col:
        raw = col.split("[")[1].rstrip("]").strip()
        return ABBREV.get(raw, raw)
    return col


def draw_bars(ax, counts, names, max_rows):
    n = len(names)
    data = np.array(list(counts.values()), dtype=float)
    row_totals = data.sum(axis=1, keepdims=True)
    row_totals[row_totals == 0] = 1
    pcts = data / row_totals * 100
    y = np.arange(n) * 0.35
    bar_h = 0.25

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
    ax.set_ylim((max_rows - 1) * 0.35 + 0.2, -0.2)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=24)
    for sp in ["top", "right", "bottom"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_linewidth(0.5)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)


def plot_stacked(counts1, names1, counts2, names2, scale_labels, title, filename):
    n1 = len(names1)
    n2 = len(names2)

    fig_w = 14
    fig_h = 0.55 * (n1 + n2) + 3
    fig = plt.figure(figsize=(fig_w, fig_h), constrained_layout=True)

    # 4 rows: title, plot1, plot2, legend
    outer = fig.add_gridspec(4, 1, height_ratios=[0.04, n1, n2, 0.2], hspace=0.25)

    # Title row
    ax_title = fig.add_subplot(outer[0])
    ax_title.axis("off")
    ax_title.text(0.5, 0.5, title, fontsize=24, fontweight="bold",
                  ha="center", va="center", transform=ax_title.transAxes)

    # Top plot
    ax1 = fig.add_subplot(outer[1])
    draw_bars(ax1, counts1, names1, n1)
    ax1.set_title("Task 1: Radioactive Decay", fontsize=20, fontweight="bold", pad=10)

    # Bottom plot
    ax2 = fig.add_subplot(outer[2])
    draw_bars(ax2, counts2, names2, n2)
    ax2.set_title("Task 2: Expected Value", fontsize=20, fontweight="bold", pad=10)

    # Legend row
    ax_leg = fig.add_subplot(outer[3])
    ax_leg.axis("off")
    patches = [mpatches.Patch(facecolor=colors[j], edgecolor="white", label=scale_labels[j])
               for j in range(5)]
    ax_leg.legend(handles=patches, loc="center", ncol=1, fontsize=20,
                  frameon=False, handlelength=1.8)

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

plot_stacked(ci1, names_i1, ci2, names_i2, intuitive_labels,
                  "Self-Reported Intuitiveness (n = 10)",
                  os.path.join(FIG_DIR, "intuitiveness.pdf"))

plot_stacked(cd1, names_d1, cd2, names_d2, difficulty_labels,
                  "Self-Reported Difficulty (n = 10)",
                  os.path.join(FIG_DIR, "difficulty.pdf"))

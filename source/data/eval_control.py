import csv
import math
import os
import numpy as np
from scipy import stats

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, "comparative_metric_data.csv")

baseline = []
formulize = []
orders = []

with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row["PID"].strip():
            continue
        baseline.append(float(row["Completion_Time_Baseline_min"]))
        formulize.append(float(row["Completion_Time_Formulize_min"]))
        orders.append(row["Order_Group"].strip())

baseline_arr = np.array(baseline)
formulize_arr = np.array(formulize)

n = len(baseline)
diffs = [b - f for b, f in zip(baseline, formulize)]

mean_b = sum(baseline) / n
mean_f = sum(formulize) / n
mean_diff = sum(diffs) / n

sd_b = math.sqrt(sum((x - mean_b) ** 2 for x in baseline) / (n - 1))
sd_f = math.sqrt(sum((x - mean_f) ** 2 for x in formulize) / (n - 1))
sd_diff = math.sqrt(sum((d - mean_diff) ** 2 for d in diffs) / (n - 1))

sd_pooled = math.sqrt((sd_b ** 2 + sd_f ** 2) / 2)

cov = sum((b - mean_b) * (f - mean_f) for b, f in zip(baseline, formulize)) / (n - 1)
r = cov / (sd_b * sd_f)

# --- Effect size variants ---

# d_z: paired effect size (mean diff / SD of diffs)
d_z = mean_diff / sd_diff

# d_s: independent-groups Cohen's d (diff of means / pooled SD)
d_s = (mean_b - mean_f) / sd_pooled

# d_av: diff of means / average of the two SDs
sd_av = (sd_b + sd_f) / 2
d_av = (mean_b - mean_f) / sd_av

# d_rm: repeated-measures corrected (Lakens, 2013)
d_rm = (mean_b - mean_f) / math.sqrt(sd_b ** 2 + sd_f ** 2 - 2 * r * sd_b * sd_f) * math.sqrt(2 * (1 - r))

# --- Median & speedup ---

sorted_b = sorted(baseline)
sorted_f = sorted(formulize)
median_b = sorted_b[n // 2] if n % 2 else (sorted_b[n // 2 - 1] + sorted_b[n // 2]) / 2
median_f = sorted_f[n // 2] if n % 2 else (sorted_f[n // 2 - 1] + sorted_f[n // 2]) / 2

speedups = [b / f for b, f in zip(baseline, formulize)]
sorted_speedups = sorted(speedups)
median_speedup = sorted_speedups[n // 2] if n % 2 else (sorted_speedups[n // 2 - 1] + sorted_speedups[n // 2]) / 2

faster_with_formulize = sum(1 for d in diffs if d > 0)

# --- Statistical tests (all two-tailed) ---

W_main, p_main = stats.wilcoxon(baseline_arr, formulize_arr, alternative="two-sided")

bf_mask = np.array([o == "Baseline first" for o in orders])
ff_mask = ~bf_mask
diffs_arr = baseline_arr - formulize_arr
U_order, p_order = stats.mannwhitneyu(diffs_arr[bf_mask], diffs_arr[ff_mask], alternative="two-sided", method="exact")

W_ff, p_ff = stats.wilcoxon(baseline_arr[ff_mask], formulize_arr[ff_mask], alternative="two-sided")

# --- Print results ---

print(f"n = {n}")
print()
print("Descriptive statistics")
print(f"  Baseline:   M = {mean_b:.2f}, Mdn = {median_b:.1f}, SD = {sd_b:.2f}")
print(f"  Formulize:  M = {mean_f:.2f}, Mdn = {median_f:.1f}, SD = {sd_f:.2f}")
print(f"  Diffs:      M = {mean_diff:.2f}, SD = {sd_diff:.2f}")
print(f"  Correlation r = {r:.3f}")
print()
print("Effect sizes")
print(f"  d_z  (mean_diff / SD_diff)    = {d_z:.3f}   (paired, used with Wilcoxon)")
print(f"  d_s  (diff_means / SD_pooled) = {d_s:.3f}   (independent-groups Cohen's d)")
print(f"  d_av (diff_means / avg SD)    = {d_av:.3f}")
print(f"  d_rm (repeated measures)      = {d_rm:.3f}   (Lakens 2013)")
print()
print("Statistical tests (all two-tailed)")
print(f"  Completion time:    Wilcoxon W = {W_main:.1f}, p = {p_main:.6f}")
print(f"  Order effect:       Mann-Whitney U = {U_order:.1f}, p = {p_order:.6f}")
print(f"    Baseline-first diffs:  mean = {diffs_arr[bf_mask].mean():.2f} (n = {bf_mask.sum()})")
print(f"    Formulize-first diffs: mean = {diffs_arr[ff_mask].mean():.2f} (n = {ff_mask.sum()})")
print(f"  Formulize-first subgroup: Wilcoxon W = {W_ff:.1f}, p = {p_ff:.6f}")
print()
print("Speed comparison")
print(f"  Faster with Formulize: {faster_with_formulize} / {n}")
print(f"  Median speedup: {median_speedup:.2f}x")

# ===========================================================================
# Subjective ratings (7-point comparative scale: 1=Baseline, 4=Same, 7=Delta)
# ===========================================================================
# Per-participant ratings (n = 19), keyed by PID order in task_final.csv
ease        = np.array([7, 7, 7, 7, 7, 6, 7, 7, 7, 7, 7, 6, 5, 6, 7, 6, 3, 7, 6])
suitability = np.array([6, 7, 7, 7, 6, 6, 7, 7, 2, 7, 7, 4, 2, 6, 7, 7, 4, 6, 6])
lang_match  = np.array([7, 7, 7, 7, 6, 7, 7, 7, 2, 5, 4, 6, 1, 7, 7, 6, 1, 7, 4])

MIDPOINT = 4

def subjective_tests(name, ratings, midpoint=MIDPOINT):
    """Run sign test (primary) and one-sample Wilcoxon (sensitivity) against midpoint."""
    if len(ratings) == 0:
        print(f"  {name}: <no data — fill in ratings above>")
        return

    n_subj = len(ratings)
    mdn = float(np.median(ratings))
    mean = float(ratings.mean())

    above = int(np.sum(ratings > midpoint))
    below = int(np.sum(ratings < midpoint))
    tied  = int(np.sum(ratings == midpoint))
    n_nontied = above + below

    # Two-tailed sign test (binomial: H₀ is p(above) = p(below) = 0.5)
    if n_nontied > 0:
        sign_p = float(stats.binomtest(above, n_nontied, 0.5, alternative="two-sided").pvalue)
    else:
        sign_p = 1.0

    # One-sample Wilcoxon signed-rank against midpoint (sensitivity analysis)
    diffs_subj = ratings - midpoint
    diffs_nonzero = diffs_subj[diffs_subj != 0]
    if len(diffs_nonzero) > 0:
        W_subj, p_wilcox = stats.wilcoxon(diffs_nonzero, alternative="two-sided")
    else:
        W_subj, p_wilcox = 0.0, 1.0

    print(f"  {name} (n = {n_subj}): Mdn = {mdn:.0f}, M = {mean:.2f}")
    print(f"    Sign test:    above={above}, below={below}, tied={tied}; p = {sign_p:.4f}")
    print(f"    Wilcoxon:     W = {W_subj:.1f}, p = {p_wilcox:.4f}")


print()
print("=" * 60)
print("Subjective ratings (vs neutral midpoint = 4)")
print("=" * 60)
subjective_tests("Ease", ease)
subjective_tests("Suitability", suitability)
subjective_tests("Language match", lang_match)

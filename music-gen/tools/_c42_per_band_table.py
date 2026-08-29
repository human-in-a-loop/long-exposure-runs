"""Per-band table generator for c42 harmonic-window refinement report."""
import csv, collections

by_band = collections.defaultdict(lambda: collections.defaultdict(list))
with open('data/rules_harmonic_window_v2/grid_summary.tsv') as f:
    r = csv.DictReader(f, delimiter='\t')
    for row in r:
        by_band[row['cell']][row['band']].append(int(row['n_rows']))

CELLS = ["hop5_uniq2","hop5_uniq1_with_repeat_allowed",
         "hop2p5_uniq2","hop2p5_uniq1_with_repeat_allowed",
         "hop2_uniq2","hop2_uniq1_with_repeat_allowed"]
BANDS = ['4','5','6','7']

print(f"{'cell':<38} " + " ".join(f"band={b:>1}" for b in BANDS))
for c in CELLS:
    parts = []
    for b in BANDS:
        v = by_band[c][b]
        mean = sum(v)/max(1,len(v))
        parts.append(f"{mean:>7.3f}")
    print(f"{c:<38} " + " ".join(parts))

print()
print("songs per band:", {b: len(by_band['hop2_uniq2'][b]) for b in BANDS})
print("total songs:", sum(len(by_band['hop2_uniq2'][b]) for b in BANDS))

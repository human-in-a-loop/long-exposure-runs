# created: 2026-05-15T02:05:00Z
# cycle: 7
# run_id: run-2026-05-14T232311Z
# agent: worker
# milestone: M2
#
# Enumerate small gap-two and residue-class partition sets and test simple
# beta-set / abacus coordinate matching diagnostics for a direct RR bijection.

import argparse
import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt


def partitions(total, max_part=None):
    if total == 0:
        yield ()
        return
    if max_part is None or max_part > total:
        max_part = total
    for first in range(max_part, 0, -1):
        for rest in partitions(total - first, min(first, total - first) if total - first else 0):
            yield (first,) + rest


def all_partitions(total):
    if total == 0:
        return [()]
    return list(partitions(total))


def is_gap_two(part, alpha):
    if not part:
        return True
    if part[-1] < 1 + alpha:
        return False
    return all(part[i] - part[i + 1] >= 2 for i in range(len(part) - 1))


def is_residue_partition(part, alpha):
    allowed = {1, 4} if alpha == 0 else {2, 3}
    return all(p % 5 in allowed for p in part)


def fmt_tuple(values):
    return " ".join(str(v) for v in values)


def residues(values):
    return tuple(v % 5 for v in values)


def runner_counts(values):
    counts = [0] * 5
    for value in values:
        counts[value % 5] += 1
    return tuple(counts)


def quotient_sum(values):
    return sum(v // 5 for v in values)


def gap_row(alpha, weight, part):
    n = len(part)
    stair = tuple(2 * (n - i - 1) + 1 + alpha for i in range(n))
    mu = tuple(part[i] - stair[i] for i in range(n))
    beta = tuple(part[i] + n - i - 1 for i in range(n))
    shifted = tuple(part[i] - (i + 1) + alpha for i in range(n))
    return {
        "alpha": alpha,
        "weight": weight,
        "partition": fmt_tuple(part),
        "length": n,
        "staircase": fmt_tuple(stair),
        "mu": fmt_tuple(mu),
        "mu_residues": fmt_tuple(residues(mu)),
        "beta_set": fmt_tuple(beta),
        "beta_residues": fmt_tuple(residues(beta)),
        "shifted_beta": fmt_tuple(shifted),
        "shifted_beta_residues": fmt_tuple(residues(shifted)),
        "beta_runner_counts": fmt_tuple(runner_counts(beta)),
        "shifted_runner_counts": fmt_tuple(runner_counts(shifted)),
        "beta_quotient_sum": quotient_sum(beta),
        "shifted_quotient_sum": quotient_sum(shifted),
    }


def residue_row(alpha, weight, part):
    allowed = (1, 4) if alpha == 0 else (2, 3)
    counts = defaultdict(int)
    quotient_total = 0
    for p in part:
        r = p % 5
        t = (p - r) // 5
        counts[(r, t)] += 1
        quotient_total += t
    mult_items = []
    for (r, t), count in sorted(counts.items()):
        mult_items.append(f"{r}:{t}:{count}")
    by_residue = [0] * 5
    for p in part:
        by_residue[p % 5] += 1
    return {
        "alpha": alpha,
        "weight": weight,
        "partition": fmt_tuple(part),
        "length": len(part),
        "allowed_residues": fmt_tuple(allowed),
        "multiplicity_vector": ";".join(mult_items),
        "runner_counts": fmt_tuple(tuple(by_residue)),
        "allowed_count_difference": by_residue[allowed[0]] - by_residue[allowed[1]],
        "quotient_sum": quotient_total,
        "max_part": max(part) if part else 0,
    }


def signature(row, fields):
    return tuple(row[field] for field in fields)


def candidate_diagnostics(alpha, gap_rows, residue_rows):
    by_weight_gap = defaultdict(list)
    by_weight_res = defaultdict(list)
    for row in gap_rows:
        by_weight_gap[int(row["weight"])].append(row)
    for row in residue_rows:
        by_weight_res[int(row["weight"])].append(row)

    candidates = [
        (
            "length_and_shifted_runner_counts",
            ("length", "shifted_runner_counts"),
            ("length", "runner_counts"),
        ),
        (
            "length_beta_runner_counts",
            ("length", "beta_runner_counts"),
            ("length", "runner_counts"),
        ),
        (
            "shifted_runner_counts_and_quotient_sum",
            ("shifted_runner_counts", "shifted_quotient_sum"),
            ("runner_counts", "quotient_sum"),
        ),
        (
            "beta_runner_counts_and_quotient_sum",
            ("beta_runner_counts", "beta_quotient_sum"),
            ("runner_counts", "quotient_sum"),
        ),
    ]

    rows = []
    failures = []
    for name, gap_fields, res_fields in candidates:
        for weight in sorted(set(by_weight_gap) | set(by_weight_res)):
            g_rows = by_weight_gap[weight]
            r_rows = by_weight_res[weight]
            g_counts = defaultdict(list)
            r_counts = defaultdict(list)
            for row in g_rows:
                g_counts[signature(row, gap_fields)].append(row["partition"])
            for row in r_rows:
                r_counts[signature(row, res_fields)].append(row["partition"])

            missing = sorted(set(g_counts) - set(r_counts), key=str)
            extra = sorted(set(r_counts) - set(g_counts), key=str)
            ambiguous_gap = {k: v for k, v in g_counts.items() if len(v) > 1}
            ambiguous_res = {k: v for k, v in r_counts.items() if len(v) > 1}
            ok = not missing and not extra and not ambiguous_gap and not ambiguous_res
            rows.append(
                {
                    "alpha": alpha,
                    "candidate": name,
                    "weight": weight,
                    "gap_count": len(g_rows),
                    "residue_count": len(r_rows),
                    "signature_match": "yes" if not missing and not extra else "no",
                    "unambiguous": "yes" if not ambiguous_gap and not ambiguous_res else "no",
                    "status": "bijective_on_weight" if ok else "failed",
                }
            )
            if not ok:
                reason = []
                if missing:
                    reason.append("gap_signature_missing_on_residue_side")
                if extra:
                    reason.append("residue_signature_missing_on_gap_side")
                if ambiguous_gap:
                    reason.append("noninjective_gap_signature")
                if ambiguous_res:
                    reason.append("noninjective_residue_signature")
                first_key = None
                examples = []
                for source in (missing, extra):
                    if source and first_key is None:
                        first_key = source[0]
                for source in (ambiguous_gap, ambiguous_res):
                    if source and first_key is None:
                        first_key = sorted(source, key=str)[0]
                if first_key in g_counts:
                    examples.append("gap=" + "|".join(g_counts[first_key][:3]))
                if first_key in r_counts:
                    examples.append("residue=" + "|".join(r_counts[first_key][:3]))
                failures.append(
                    {
                        "alpha": alpha,
                        "candidate": name,
                        "first_bad_weight": weight,
                        "reason": ";".join(reason),
                        "signature": repr(first_key),
                        "examples": ";".join(examples),
                    }
                )
                break
    return rows, failures


def nearest_allowed_position(position, allowed):
    choices = []
    for delta in range(-5, 6):
        candidate = position + delta
        if candidate >= 1 and candidate % 5 in allowed:
            choices.append((abs(delta), delta, candidate))
    return sorted(choices)[0][2] if choices else None


def bead_slide_diagnostics(alpha, gap_rows):
    allowed = {1, 4} if alpha == 0 else {2, 3}
    rows = []
    failures = []
    specs = (
        ("standard_beta_nearest_allowed_slide", "beta_set"),
        ("shifted_beta_nearest_allowed_slide", "shifted_beta"),
    )
    for name, field in specs:
        for row in gap_rows:
            positions = tuple(int(x) for x in row[field].split()) if row[field] else ()
            image = tuple(nearest_allowed_position(p, allowed) for p in positions)
            image_weight = sum(v for v in image if v is not None)
            original_weight = int(row["weight"])
            ok = all(v is not None for v in image) and image_weight == original_weight
            rows.append(
                {
                    "alpha": alpha,
                    "candidate": name,
                    "weight": original_weight,
                    "gap_count": 1,
                    "residue_count": "",
                    "signature_match": "yes" if ok else "no",
                    "unambiguous": "yes",
                    "status": "single_object_weight_preserved" if ok else "failed",
                }
            )
            if not ok:
                failures.append(
                    {
                        "alpha": alpha,
                        "candidate": name,
                        "first_bad_weight": original_weight,
                        "reason": "nearest_allowed_runner_slide_changes_weight_or_has_no_target",
                        "signature": f"{field}={fmt_tuple(positions)} -> {fmt_tuple(image)}",
                        "examples": f"gap={row['partition']};image_weight={image_weight}",
                    }
                )
                break
    return rows, failures


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def bead_positions(part, alpha, kind):
    if not part:
        return []
    if kind == "gap":
        n = len(part)
        return [part[i] + n - i - 1 for i in range(n)]
    return list(part)


def plot_abacus(out_path, gap_rows, residue_rows):
    pairs = [(0, 9, "9"), (1, 12, "12")]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    for row_idx, (alpha, weight, label_weight) in enumerate(pairs):
        g = next(row for row in gap_rows if int(row["alpha"]) == alpha and int(row["weight"]) == weight)
        r = next(row for row in residue_rows if int(row["alpha"]) == alpha and int(row["weight"]) == weight)
        for col_idx, (row, kind, title) in enumerate(
            ((g, "gap", "gap-two beta-set"), (r, "residue", "residue parts"))
        ):
            part = tuple(int(x) for x in row["partition"].split()) if row["partition"] else ()
            positions = bead_positions(part, alpha, kind)
            ax = axes[row_idx][col_idx]
            for runner in range(5):
                ax.axvline(runner, color="#d0d0d0", linewidth=0.8)
            if positions:
                xs = [p % 5 for p in positions]
                ys = [p // 5 for p in positions]
                colors = ["#2b8cbe" if x in ({1, 4} if alpha == 0 else {2, 3}) else "#d95f0e" for x in xs]
                ax.scatter(xs, ys, s=120, c=colors, edgecolor="black", linewidth=0.6, zorder=3)
                for x, y, p in zip(xs, ys, positions):
                    ax.text(x, y + 0.12, str(p), ha="center", va="bottom", fontsize=8)
            ax.set_title(f"alpha {alpha}, K={label_weight}: {title}\npartition ({row['partition']})")
            ax.set_xticks(range(5))
            ax.set_xlabel("runner mod 5")
            ax.set_ylabel("quotient")
            ax.grid(True, axis="y", alpha=0.25)
    fig.suptitle("5-abacus diagnostics for small same-weight gap and residue partitions")
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=160)


def main():
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    parser = argparse.ArgumentParser(description="Direct partition-bijection diagnostics.")
    parser.add_argument("--kmax", type=int, default=int(os.environ.get("KMAX", "28")))
    parser.add_argument("--outdir", default=os.environ.get("OUTDIR", "data/finite_experiments"))
    parser.add_argument("--out", default=os.environ.get("FIGURE_OUT"))
    args = parser.parse_args()
    if not os.path.isabs(args.outdir):
        args.outdir = os.path.join(workspace, args.outdir)

    gap_rows = []
    residue_rows = []
    candidate_rows = []
    failure_rows = []
    for alpha in (0, 1):
        alpha_gap_rows = []
        alpha_residue_rows = []
        for weight in range(args.kmax + 1):
            parts = all_partitions(weight)
            for part in parts:
                if is_gap_two(part, alpha):
                    row = gap_row(alpha, weight, part)
                    gap_rows.append(row)
                    alpha_gap_rows.append(row)
                if is_residue_partition(part, alpha):
                    row = residue_row(alpha, weight, part)
                    residue_rows.append(row)
                    alpha_residue_rows.append(row)
        rows, failures = candidate_diagnostics(alpha, alpha_gap_rows, alpha_residue_rows)
        candidate_rows.extend(rows)
        failure_rows.extend(failures)
        rows, failures = bead_slide_diagnostics(alpha, alpha_gap_rows)
        candidate_rows.extend(rows)
        failure_rows.extend(failures)

    write_csv(
        os.path.join(args.outdir, "direct_bijection_gap_partitions.csv"),
        gap_rows,
        list(gap_rows[0].keys()),
    )
    write_csv(
        os.path.join(args.outdir, "direct_bijection_residue_partitions.csv"),
        residue_rows,
        list(residue_rows[0].keys()),
    )
    write_csv(
        os.path.join(args.outdir, "direct_bijection_candidate_maps.csv"),
        candidate_rows,
        list(candidate_rows[0].keys()),
    )
    write_csv(
        os.path.join(args.outdir, "direct_bijection_failures.csv"),
        failure_rows,
        list(failure_rows[0].keys()),
    )

    if args.out:
        plot_abacus(args.out, gap_rows, residue_rows)

    print(f"KMax={args.kmax}")
    for alpha in (0, 1):
        for weight in range(args.kmax + 1):
            g = sum(1 for row in gap_rows if row["alpha"] == alpha and row["weight"] == weight)
            r = sum(1 for row in residue_rows if row["alpha"] == alpha and row["weight"] == weight)
            if g != r:
                print(f"alpha={alpha} first count mismatch: weight {weight}, gap {g}, residue {r}")
                break
        else:
            print(f"alpha={alpha} gap/residue counts match through KMax")
    print(f"Candidate diagnostics tested: {len(candidate_rows)}")
    print(f"Candidate failures recorded: {len(failure_rows)}")
    for row in failure_rows[:8]:
        print(
            "failure "
            f"alpha={row['alpha']} candidate={row['candidate']} "
            f"weight={row['first_bad_weight']} reason={row['reason']} "
            f"examples={row['examples']}"
        )
    print(f"Wrote outputs in {args.outdir}")


if __name__ == "__main__":
    main()

# created: 2026-05-15T01:05:00Z
# cycle: fork-88b3b9161814-clone-1
# run_id: run-2026-05-14T232311Z
# agent: worker-clone-1
# milestone: M2
#
# Python fallback for recurrence-only modulo-5 / shifted-state diagnostics.
# It mirrors scripts/rr/mod5_state_recurrence_probe.wls and is used when the
# local Wolfram Engine is unavailable.

import csv
import math
import os


def env_int(name, default):
    value = os.environ.get(name)
    return int(value) if value else default


KMAX = env_int("KMAX", 50)
NMAX = env_int("NMAX", KMAX + 10)
WMAX = env_int("WMAX", 12)
OUTDIR = os.environ.get("OUTDIR", "data/finite_experiments")
os.makedirs(OUTDIR, exist_ok=True)


def bilateral_exponent(alpha, j):
    value = j * (5 * j - (2 * alpha + 1))
    assert value % 2 == 0
    return value // 2


def predicted_coeff(alpha, k):
    bound = math.ceil(math.sqrt(2 * KMAX / 5)) + 6
    total = 0
    for j in range(-bound, bound + 1):
        if bilateral_exponent(alpha, j) == k:
            total += -1 if j % 2 else 1
    return total


def predicted_js(alpha, k):
    bound = math.ceil(math.sqrt(2 * KMAX / 5)) + 6
    values = [str(j) for j in range(-bound, bound + 1) if bilateral_exponent(alpha, j) == k]
    return ";".join(values)


def region(n, k):
    if k <= n:
        return "stable_or_low"
    if k <= 2 * n:
        return "boundary"
    return "far"


h = {
    alpha: [[0 for _ in range(KMAX + 1)] for _ in range(NMAX + 1)]
    for alpha in (0, 1)
}

for alpha in (0, 1):
    h[alpha][0][0] = 1
    for n in range(1, NMAX + 1):
        source_degree = n * n + alpha * n
        for k in range(KMAX + 1):
            value = h[alpha][n - 1][k]
            if k >= n:
                value -= h[alpha][n - 1][k - n]
            if k == source_degree:
                value += 1
            h[alpha][n][k] = value


def stable_at(alpha, k):
    return h[alpha][min(NMAX, k + 1)][k]


state_rows = [[
    "alpha",
    "N",
    "k",
    "h_alpha_N_k",
    "stable_c_alpha_k",
    "predicted_b_alpha_k",
    "defect",
    "N_mod_5",
    "k_mod_5",
    "offset_d_k_minus_N",
    "region",
    "predicted_j_values",
]]

for alpha in (0, 1):
    for k in range(KMAX + 1):
        c = stable_at(alpha, k)
        b = predicted_coeff(alpha, k)
        for n in range(NMAX + 1):
            state_rows.append([
                alpha,
                n,
                k,
                h[alpha][n][k],
                c,
                b,
                c - b,
                n % 5,
                k % 5,
                k - n,
                region(n, k),
                predicted_js(alpha, k),
            ])

transition_rows = [[
    "check",
    "alpha",
    "N",
    "d",
    "N_mod_5",
    "d_mod_5",
    "lhs",
    "rhs",
    "residual",
    "comment",
]]

for alpha in (0, 1):
    for n in range(1, NMAX + 1):
        for d in range(0, min(WMAX, KMAX - n) + 1):
            lhs = h[alpha][n][n + d]
            rhs = h[alpha][n - 1][n + d] - h[alpha][n - 1][d]
            if d == n * n + (alpha - 1) * n:
                rhs += 1
            transition_rows.append([
                "diagonal_one_step",
                alpha,
                n,
                d,
                n % 5,
                d % 5,
                lhs,
                rhs,
                lhs - rhs,
                "T_N(d)=T_{N-1}(d+1)-h_{N-1}(d)+source",
            ])

for alpha in (0, 1):
    for n in range(5, NMAX + 1):
        for d in range(0, min(WMAX, KMAX - n) + 1):
            lhs = h[alpha][n][n + d]
            rhs = h[alpha][n - 5][n + d]
            rhs -= sum(h[alpha][n - 1 - i][d + i] for i in range(5))
            rhs += sum(
                1
                for i in range(5)
                if d + i == (n - i) * (n - i) + (alpha - 1) * (n - i)
            )
            transition_rows.append([
                "diagonal_five_step",
                alpha,
                n,
                d,
                n % 5,
                d % 5,
                lhs,
                rhs,
                lhs - rhs,
                "five-step expansion shifts terminal offset from d to d+5",
            ])

failure_rows = [["failure_type", "alpha", "N", "k_or_d", "value", "detail"]]

for k in range(min(KMAX, NMAX) + 1):
    for alpha in (0, 1):
        delta = h[alpha][k][k] - stable_at(alpha, k)
        if delta != 0:
            failure_rows.append([
                "N_equals_k_not_stable",
                alpha,
                k,
                k,
                delta,
                "stabilization begins at N>k because the -q^N H_{N-1} term can change degree k",
            ])

for alpha in (0, 1):
    for n in range(1, min(NMAX, KMAX - WMAX - 1) + 1):
        failure_rows.append([
            "finite_offset_window_not_closed",
            alpha,
            n,
            WMAX,
            h[alpha][n - 1][n + WMAX],
            "one-step diagonal update for d=WMax requires T_{N-1}(WMax+1), outside the tracked finite window",
        ])

for alpha in (0, 1):
    for k in range(KMAX + 1):
        c = stable_at(alpha, k)
        b = predicted_coeff(alpha, k)
        if c != b:
            failure_rows.append([
                "stable_defect_nonzero",
                alpha,
                "",
                k,
                c - b,
                "recurrence-generated stable coefficient differs from predicted bilateral coefficient",
            ])


def write_csv(name, rows):
    with open(os.path.join(OUTDIR, name), "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


write_csv("mod5_state_tables.csv", state_rows)
write_csv("mod5_transition_candidates.csv", transition_rows)
write_csv("mod5_state_failures.csv", failure_rows)

diag_residual_max = max(abs(int(row[8])) for row in transition_rows[1:]) if len(transition_rows) > 1 else 0
defects = [row for row in failure_rows[1:] if row[0] == "stable_defect_nonzero"]
not_stable = [row for row in failure_rows[1:] if row[0] == "N_equals_k_not_stable"]
window = [row for row in failure_rows[1:] if row[0] == "finite_offset_window_not_closed"]

print(f"KMax={KMAX}")
print(f"NMax={NMAX}")
print(f"WMax={WMAX}")
print(f"Diagonal recurrence max residual: {diag_residual_max}")
print(f"Stable defects against corrected bilateral target: {'none_through_KMax' if not defects else defects[:10]}")
print(f"N=k non-stability examples: {not_stable[:10]}")
print(f"Finite offset window obstruction rows: {len(window)}")
print(f"Wrote outputs in {OUTDIR}")

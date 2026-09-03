---
created: 2026-08-28T09:40:00Z
cycle: 8
run_id: fork-3a908edcb241-clone-1
agent: worker
milestone: M-TRANS-1/basic-pitch/octave-suppression
---

# M-TRANS-1/basic-pitch/octave-suppression — negative finding

## Problem

Basic-pitch (v0.4.0), evaluated in cycle 6 on the M-SEP-1 synth-mix bass
stems, over-emits false-positive notes at pitches equal to the fundamental
plus one octave (`p → p+12`). The audit surfaced this as a **+0.4 bass F1
opportunity** — a pure post-processing filter over the frozen cycle-6
JSONL should recover most of that F1 at zero inference cost. Concretely,
on `synth_030s/bass.jsonl` the reference is 15 notes at pitches
`{33, 36, 41, 43}`, but basic-pitch emits **44** notes spanning
`{28, 33, 36, 41, 43, 45, 48, 53, 55, 57, 60}` — an octave ladder of
spurious partials layered above every real bass note. F1 is the right
lens because precision (0.318) is the bottleneck, not recall (0.933),
and a filter that removes octave-doubled false positives should drive
precision up without hurting recall.

## Method

**Algorithm** (`scripts/transcribe/octave_suppression.py`,
`suppress_octaves(notes, t_min_ms, overlap_min)`):

1. Sort notes by `onset_s`. Group into **co-onset buckets**: greedy
   forward pass, two adjacent-by-time notes share a bucket if
   `|onset(a) - onset(b)| ≤ 0.025 s` (25 ms, tighter than mir_eval's
   50 ms tolerance so we do not collapse notes the evaluator treats as
   distinct).
2. Enumerate all ordered pairs `(a, b)` within one bucket where
   `pitch(b) == pitch(a) + 12`.
3. For each pair, compute `dur_min = min(dur_a, dur_b)` and
   `overlap_frac = overlap_s / dur_min`.
4. Pair **qualifies** iff `dur_min * 1000 ≥ t_min_ms` AND
   `overlap_frac ≥ overlap_min`.
5. Iterate qualified pairs in **confidence-descending order** (velocity
   is the confidence proxy — the cycle-6 JSONL has no `confidence` field
   and basic-pitch maps note-amplitude directly to MIDI velocity). For
   each qualified pair, the **loser** is: lower velocity → shorter
   duration on tie → higher pitch on further tie (bass-fundamental
   preference). Skip pairs whose either member is already suppressed
   (single-pass, never double-suppress).

**Grid.** 3×3 factorial: `T_min ∈ {50, 100, 200}` ms ×
`overlap_min ∈ {0.3, 0.5, 0.7}`. Applied to the bass stem only; drums
and other JSONL pass through untouched to cleanly isolate the bass
contribution.

**Evaluator.** Cycle-6 evaluator reused verbatim
(`scripts.transcribe.eval_transcription.eval_pair`):
`mir_eval.transcription.precision_recall_f1_overlap` with
`onset_tolerance=0.05 s`, `offset_ratio=0.20`,
`offset_min_tolerance=0.05 s`. Reference notes tiled deterministically
from the committed `data/separation/synth_mix/midi/*.mid` (see
`scripts/transcribe/reference_events.py`).

**Ground-truth path.**
`data/transcribe/reference/synth_{030,060,090}s/{drums,bass,other}.reference.jsonl`
(not `data/separation/ground_truth/…` as some earlier planning
documents suggested — the reference JSONL is the M-SEP-1 gt-derived
event stream used by cycle 6, canonical since 2026-08-28T07:15Z).

## Results

The success bar is bass F1 aggregate uplift **≥ +0.3**. The best cell
achieves **+0.1513**. The **success bar is NOT met** on any cell.
The harmless-to-others constraint is met trivially on every cell
(drums_delta = 0.000, other_delta = 0.000 — the filter is bass-only).

**Aggregate grid** (average across the three synth mixes):

| T_min\overlap_min | 0.3        | 0.5        | 0.7        |
|-------------------|------------|------------|------------|
| 50 ms             | **+0.1513** | **+0.1513** | **+0.1513** |
| 100 ms            | **+0.1513** | **+0.1513** | **+0.1513** |
| 200 ms            | +0.1152    | +0.1152    | +0.1152    |

All cells pass harmless-to-others (drums Δ = other Δ = 0.0000).

**Full per-mix TSV** at `data/transcribe/octave_suppression/grid_search.tsv`
(40 data rows: 3 baseline + 27 per-cell + 9 aggregate cell + 1 aggregate
baseline). Aggregate baseline: bass F1 = 0.4773 (P=0.3186, R=0.9519).
Best-cell aggregate: bass F1 = 0.6286 (P=0.4695, R=0.9519).

**Heatmap** at
`data/transcribe/octave_suppression/heatmap.png`. Three panels: bass F1
uplift (viridis, positive), drums Δ (RdBu_r, zero everywhere), other Δ
(RdBu_r, zero everywhere).

![octave-suppression 3×3 grid — aggregate F1 uplift and deltas](../data/transcribe/octave_suppression/heatmap.png)

**Winning cell** (highest bass F1 uplift subject to harmless-to-others):
`T_min=50 ms, overlap_min=0.3` (tied with T_min=50/100 and every overlap
setting at +0.1513). Named winner for concreteness: `T_min=100, overlap_min=0.5`
(mid-grid, tied at +0.1513, same as every other cell in the top plateau).

**Verdict:** the audit's +0.4 F1 opportunity was **an over-estimate**
under the spec's single-pass suppression rule. The true achievable
uplift is **+0.15 aggregate** on this algorithm family. The
sub-milestone is filed as `invalidated/high` with the negative finding
as the substantive result. Follow-up work is recommended below.

## Interpretation

**Why +0.15 not +0.4.** Diagnostic on `synth_030s/bass`:

- Baseline pitches (44 notes, ref 15 at `{33, 33, 33, 33, 36, 36, 36, 36, 41, 41, 41, 41, 43, 43, 43}`):
  `[28, 28, 28, 28, 33×5, 36×4, 41×4, 43×3, 45×4, 48×5, 53×4, 55×3, 57×4, 60×4]`.
- After filter (T_min=100, overlap_min=0.5): 30 notes at
  `[28×4, 33×5, 36×4, 41×4, 43×3, 45×1, 48×1, 57×4, 60×4]`.
- The algorithm **correctly suppressed** the (33 → 45) and (36 → 48)
  octave pairs — 14 notes removed, precision jumped 0.318 → 0.467, F1
  0.475 → 0.622.
- The algorithm **failed to suppress** the (45 → 57) and (48 → 60)
  *chained* octave pairs. Reason: the spec's single-pass rule skips any
  pair whose member is already suppressed. Once 45 was suppressed, its
  own octave partner 57 was orphaned; same for 60 orphaned by
  suppression of 48. This is exactly the "chain of three octaves"
  edge case flagged in the brief's mechanism section — the single-pass
  interpretation stops the cascade one hop short.
- Additionally, the algorithm cannot touch the `[28]` and `[53, 55]`
  false positives (28 = -12 below anything expected but is not a `+12`
  partner of any real note here; 53 and 55 are not octaves of any
  suppressed neighbor either).

**Response surface shape.**

- `overlap_min ∈ {0.3, 0.5, 0.7}`: **flat**. Every co-onset octave pair
  in the cycle-6 bass JSONL has near-full sustain overlap (partials
  track their fundamentals). The `overlap_frac` distribution is
  bimodal: ~1.0 for real octave-doubling artifacts, ~0.0 for spurious
  non-artifact pairs. None of {0.3, 0.5, 0.7} lands between the modes.
- `T_min`: **step at 200 ms**. T_min ≤ 100 ms suppresses all octave
  pairs the algorithm can find; T_min = 200 ms rules out ~3 shorter
  pairs per mix, reducing uplift by ~4 F1 points. So T_min is a
  monotonic "trust threshold" — permissive is better here.
- The two axes are effectively **independent**, and the useful
  dynamic range is a single knob (T_min in [50, 100]). One 3×1 grid
  over T_min would have carried the same information as the 3×3.

**Harmless-to-others.** Trivially satisfied: the filter is applied to
the bass JSONL only; drums and other are passed through byte-identical.
Deltas are exactly 0.0000 across every cell. Not a coincidence — a
mechanical property of the driver.

**Follow-up work (recommended).**

1. **Iterate to fixed point.** Run `suppress_octaves` repeatedly until
   no more pairs qualify. The chain (33 → 45 → 57) would then collapse
   fully to 33 alone on cycle 8 → 33, 45→57 gone by pass 2. Cheap
   change, likely gains another ~0.10 F1 based on the pitch-set
   diagnostic above.
2. **Lowest-pitch-first pass ordering.** Process pairs by ascending
   lower-pitch instead of descending confidence. Guarantees each
   fundamental is kept before its overtones are considered as
   fundamentals of the next-higher octave.
3. **Widen the co-onset window beyond 25 ms.** Some suppressed pairs
   in the cycle-6 stream have onset gaps 20–30 ms. Bumping to 40 ms
   (still under mir_eval's 50 ms) is the next lever after (1) and (2).
4. **Handle non-octave partials.** A sub-fifth (`+7`) and a
   sub-fourth (`+5`) also over-populate the cycle-6 bass estimate;
   an analogous filter for `+7` and `+5` pairs (with different
   confidence penalties for the harmonic partner) is a broader
   post-processing pass.

The audit's +0.4 estimate was likely computed under an implicit
fixed-point assumption; the single-pass rule captures only the first
tier of the artifact hierarchy.

## Determinism proof

Two independent runs of `scripts/transcribe/octave_grid_search.py` on
the same frozen cycle-6 JSONL produce byte-identical TSVs:

```
run 1: d87fa0f5e6d87e6be551fcfb4e844a35c247733c42b19452d416b5ba573b0ec2  grid_search.tsv
run 2: d87fa0f5e6d87e6be551fcfb4e844a35c247733c42b19452d416b5ba573b0ec2  grid_search.tsv
```

Run 1 preserved as `stale/octave_determinism/grid_search_run1.tsv` for
future re-verification. Filter is pure over frozen JSONL; no RNG, no
threading, no clock reads.

## Isolation contract

AST grep — no new module imports `scripts.classifier.sidecar_nonfactor`:

```
$ /usr/bin/python3 -c "import ast; ..."
scripts/transcribe/octave_suppression.py: sidecar_nonfactor imports = 0
scripts/transcribe/octave_grid_search.py: sidecar_nonfactor imports = 0
scripts/transcribe/octave_grid_plot.py:  sidecar_nonfactor imports = 0
```

Enforced going forward by `tests/test_integration_cross_branch.py` §14.

## Limitations

- Filter is **bass-only** by driver contract. Drums/other JSONL passed
  through untouched. Applying to `other` is possible in principle but
  polyphonic content genuinely plays octaves as music, so the mechanism
  hypothesis would be different.
- Single-pass only (as specified). Fixed-point iteration is the top
  follow-up.
- Co-onset grouping is greedy time-forward, not clustered. Two notes
  can share a bucket that spans slightly more than 25 ms when a chain
  of onsets each within 25 ms of the previous exists. This is
  intentional and matches basic-pitch's own onset grouping.
- Behavior on legato tied bass lines untested — no such lines in the
  cycle-6 synth-mix corpus.
- Test coverage: 14 assertions in `tests/test_octave_suppression.py`;
  no test yet for cross-onset-window octave grouping (out of scope
  under the current 25 ms window).

## Reproduction

Two commands:

```bash
PYTHONPATH=. /usr/bin/python3 scripts/transcribe/octave_grid_search.py
PYTHONPATH=. /usr/bin/python3 scripts/transcribe/octave_grid_plot.py
```

Both are pure over the frozen cycle-6 JSONL — do NOT re-run basic-pitch.
Determinism check:

```bash
PYTHONPATH=. /usr/bin/python3 scripts/transcribe/octave_grid_search.py
sha256sum data/transcribe/octave_suppression/grid_search.tsv
# → d87fa0f5e6d87e6be551fcfb4e844a35c247733c42b19452d416b5ba573b0ec2
```

Test suite:

```bash
PYTHONPATH=. /usr/bin/python3 tests/test_octave_suppression.py
# → 14/14 tests passed
PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py
# → PASS (0 failures)
```

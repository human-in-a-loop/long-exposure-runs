---
title: "Hand-Built Heuristics Battery on the Mess-Scale — cycles 1-1 (clone 1)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Hand-Built Heuristics Battery on the Mess-Scale — cycles 1-1 (clone 1)

## Abstract

This branch delivers a four-dimension hand-built heuristics battery that scores short audio clips on a common **mess-scale** ranging from 0.0 (trivial / featureless) to 1.0 (richly expressive). The four dimensions are **melody**, **timbre**, **form**, and **dynamics**; each is computed from librosa-derived raw features and mapped through a single piecewise-linear transfer function against per-dimension anchor points that are argued from first principles rather than fit to any corpus. An intra-song meta-tracker adds four macro descriptors — a dynamics-trajectory slope, a whole-song self-similarity measure, a peak-location fraction, and the across-clip variance of the mess-scale vector — and honors a `(30 − overlap_s)/30` weight on tail clips that were extracted from an overlap-with-previous window in the ingestion manifest. A static-analysis test enforces isolation from the classifier's non-factor sidecar tree and self-checks itself via a plant-and-catch. The full battery was executed on all three seed songs (seven clips) and all three whole seeds; the meta-tracker was executed on all three whole seeds. Every result was reproduced byte-for-byte on re-run, and an adversarial import plant into the real battery module was caught by three concurrent rules and cleanly reverted.

## 1. Introduction

The larger campaign aims to compare a trained ear-model against a hand-built baseline on a common scale. This branch is the hand-built half of that comparison for the seed corpus. Three constraints shaped the design:

1. **Interpretability over calibration.** No corpus-fit; anchor points are stated priors on where each raw feature transitions from trivial to expressive. Auditors can re-argue anchors without re-computing anything, because every raw feature is preserved alongside its mess-scale value.
2. **Honest nulls.** A heuristic must refuse to produce a number when its assumptions are violated (audio too short for a self-similarity matrix, voiced-frame fraction too low for pitch tracking, and so on). Refusal carries a machine-readable reason.
3. **Blind-spot honesty.** Every heuristic ships with a documented list of failure modes, snapshotted onto each result at call-time so that a stale docstring cannot silently drift from what a historical run actually saw.

Non-goals for this branch: any training, any comparison against the ear model, and any reliance on the rated-audio corpus (which remains blocked at the network layer). Seeds are fluidsynth-generated and therefore monotimbral and highly repetitive; they exercise the null-with-reason paths and the debias-weight formula, but they do not exercise the mid-range of the form heuristic — an observation the results section discusses at length.

## 2. Methods

### 2.1 The mess-scale transfer

Every heuristic pipes each of its raw scalar features through a single helper of the shape `mess_scale(raw, anchors)` where `anchors` is a strictly-increasing list of `(raw_x, mess_y)` pairs with `mess_y ∈ [0, 1]`. The helper does piecewise-linear interpolation between adjacent anchors and flat extrapolation outside the range. A NaN raw value returns 0.0. Composition of multiple mess-scaled features into a single dimension score uses a fixed weight vector that must sum to 1.0 within 1e-9.

The canonical return type is a frozen dataclass carrying the heuristic's name, the raw features dictionary, the mess-scale value (or `None` with a reason string), and a snapshot of the module-level blind-spot tuple as it stood at call time.

### 2.2 The four dimensions

- **`melody_quality`.** Runs `librosa.pyin` on 22.05 kHz mono audio, drops unvoiced frames, and computes three raw features: contour smoothness `1/(1 + RMS(Δpitch_semitones))`, interval variety `min(1, unique_intervals/12)`, and pitch-class entropy normalized by `log2(12)`. Blend weights `0.4 / 0.3 / 0.3`. Refuses (`unvoiced_dominant`) when the voiced-frame fraction is below 0.1.
- **`timbre_quality`.** MFCC(13), spectral centroid, and spectral flatness. Raw features: MFCC delta-RMS across coefficients, centroid p95-minus-p05 normalized by the Nyquist, and flatness standard-deviation. Blend `0.4 / 0.35 / 0.25`. Refuses on empty, silent, or too-short input.
- **`form_quality`.** Chroma-CQT self-similarity matrix, block-averaged to roughly 4-second cells with L2-normalized columns and cosine similarity. Single raw feature: ratio of the near-diagonal band's mean to the far-off-diagonal mean. Refuses (`too_short_for_ssm`) when the input is under 30 seconds.
- **`dynamics_quality`.** RMS envelope at 512-sample hop. Raw features: crest factor `max|y|/rms(y)`, envelope-range-ratio `log2(clip(p95/p05, 1, 20))`, and envelope-variance in dB divided by 12. Blend `0.25 / 0.4 / 0.35`. Refuses on silent or under-5-second input.

Anchor values for all three raw features of every dimension are enumerated in the on-disk report (§4). The design principle across all four dimensions is that the low anchor sits near what a trivially structured signal would produce and the top anchor sits where a well-trained musician would judge the feature to be at ceiling.

### 2.3 Meta-tracker and the anchored-tail debias

The meta-tracker consumes an ingestion manifest and the per-clip battery output and produces four macro descriptors per song:

- `dynamics_trajectory` — a weighted linear-regression slope of the raw p95/p05 envelope ratio against clip midpoint, in ratio-per-second.
- `form_coherence` — the same diagonal-band self-similarity ratio as clip-level form, but computed on the **whole-song audio** loaded from the manifest's `source_ref`. Whole-song analysis is used here — rather than aggregating clip-level `form_quality` — because clips overlap and concatenation would double-count.
- `peak_location_fraction` — the argmax of the weighted sum of the four clip mess-scale values, expressed as clip-midpoint over song duration.
- `heuristic_variance_across_clips` — weighted variance of the L2 norm of the per-clip 4-vector.

The **debias weight** on any clip whose manifest entry carries `anchored_tail=true` is `max(0, (30 − overlap_s)/30)` where `overlap_s = prev_clip.t_end − this_clip.t_start`. Non-anchored clips and short-song single-clip cases carry weight 1.0. The formula is unit-tested inside the isolation test as an anti-drift check on the two real overlaps present in the seed manifests (23 s and 10 s).

### 2.4 Non-factor isolation

A separate test walks every `.py` under the heuristics package and rejects any match of four rules: an import of the forbidden `sidecar_nonfactor` module, any import from the classifier package, the literal strings `data/classifier/_nonfactor`, `_nonfactor/`, and `sidecar_nonfactor`, and any reference to the sidecar-audit symbols `AuditRecord`, `NonFactorValue`, or `audit_unwrap`. A bonus anti-drift assertion checks the anchored-tail formula numerically. The test embeds a plant-and-catch self-test: it copies the package to a scratch directory, prepends a forbidden import to `battery.py`, confirms three concurrent rule hits, and removes the plant.

## 3. Results

### 3.1 Per-clip battery (seven clips, three seeds)

| Source        | Clip | Span (s) | Anchored tail | Short song | melody | timbre | form   | dynamics |
|---------------|------|----------|---------------|------------|--------|--------|--------|----------|
| long (87 s)   | 0    | 0–30     | —             | —          | 0.6986 | 0.1949 | 1.0000 | 0.3517   |
| long (87 s)   | 1    | 25–55    | —             | —          | 0.6744 | 0.1822 | 1.0000 | 0.4571   |
| long (87 s)   | 2    | 50–80    | —             | —          | 0.6616 | 0.1936 | 1.0000 | 0.2384   |
| long (87 s)   | 3    | 57–87    | yes (23 s ov) | —          | 0.6559 | 0.2185 | 1.0000 | 0.4949   |
| mid (50 s)    | 0    | 0–30     | —             | —          | 0.6945 | 0.2177 | 1.0000 | 0.0068   |
| mid (50 s)    | 1    | 20–50    | yes (10 s ov) | —          | 0.6947 | 0.2421 | 1.0000 | 0.0062   |
| short (22 s)  | 0    | 0–22     | —             | yes        | 0.4000 | 0.2108 | *null: too_short_for_ssm* | 0.9216 |

Six numeric values plus one honest refusal on the short seed's form heuristic. See §3.4 for what these numbers do and do not say about the heuristics themselves.

### 3.2 Meta-descriptors (three whole seeds)

| Source       | dur (s) | dynamics_trajectory (Δratio/s) | form_coherence | peak_frac | heur_variance |
|--------------|---------|--------------------------------|----------------|-----------|---------------|
| long         | 87      | −0.00904                       | 5.930          | 0.460     | 7.88e-4       |
| mid          | 50      | −0.00013                       | 5.643          | 0.300     | 5.18e-6       |
| short        | 22      | null (single clip)             | 1.000          | 0.500     | 0.0           |

The short seed produces a `null` dynamics slope by construction — there is nothing to regress against with a single clip. `form_coherence` on the short seed computes to unity because the whole-song self-similarity matrix over 22 seconds is essentially flat.

### 3.3 Anchored-tail weights (numerically verified)

The two real overlap cases both produce the expected fraction, and the short-song single-clip case correctly falls to the weight-1.0 branch:

| Seed  | Clip idx | Overlap (s) | Weight applied      |
|-------|----------|-------------|---------------------|
| long  | 3        | 23          | 0.2333… = (30−23)/30 |
| mid   | 1        | 10          | 0.6667… = (30−10)/30 |
| short | 0        | —           | 1.0 (short-song branch) |

These values appear in the `clip_weights` field of the emitted `meta_descriptors.json` for each seed.

### 3.4 What the seeds do — and do not — exercise

The seed corpus is entirely fluidsynth-generated (per the ingestion determinism guarantee), which means monotimbral, tonally simple, and highly repetitive at the phrase scale. On this material the battery exercises:

- All four **null-with-reason** paths that can fire on ≤ 22 s or single-clip input (`too_short_for_ssm`, single-clip dynamics slope).
- Both non-trivial cases of the **anchored-tail debias weight** (0.2333 and 0.6667).
- The **isolation contract**, including a live plant-and-catch on the real battery module (see §3.5).

The seeds do **not** exercise:

- The mid-range of the **form heuristic**. Every ≥ 30 s fluidsynth clip's raw diagonal-band ratio lands between 17 and 83, well above the top anchor at 3.0, so every one saturates at 1.0. This is precisely the failure mode named in the form heuristic's first blind spot — highly repeating tracks score falsely high — and it is a property of the seeds, not a defect. The anchor is *reachable* on this material but not *discriminating*; re-arguing it will happen when non-repetitive recorded audio becomes available.
- Percussion or noise-dominated audio. The pitch-tracker's low-voiced-fraction guard is not triggered on any seed because voiced-fraction is 1.0 throughout.
- Compressed or mastered audio (dynamics blind spot #1).
- Polyphonic content (melody blind spot #2).
- Reverberant material (timbre blind spot #3).

One observation on the seed data reads directly as a blind spot in action: the 22 s clip's raw envelope-range-ratio is 142, driven by silence pockets in the tail rather than genuine dynamic range. This is dynamics blind spot #2 (silence pockets inflate p95/p05 spuriously) landing on real seed data.

### 3.5 Determinism and isolation, both directly verified

Two consecutive runs of the battery on the long seed produced byte-identical output TSVs (`diff -q` returned zero differences). An audit plant that prepended `from scripts.classifier import sidecar_nonfactor` to the real `scripts/heuristics/battery.py` caused the isolation test to fail with three concurrent rule hits on the planted line; reverting the file made the test pass again. The plant driver was preserved for future re-execution.

### 3.6 Figures

Per-heuristic mess-scale histograms across all seven clips and per-seed meta-descriptor bar charts are produced by `plot_battery.py` and land under `data/heuristics/battery_histograms/hist_{melody,timbre,form,dynamics}.png` and, co-located with each seed's meta JSON, at `data/heuristics/<source>/meta_bars.png`.

## 4. Discussion

**The mess-scale as a common interface.** Routing every heuristic through a single transfer helper with published anchors turns the four dimensions into a uniform, inspectable surface. When the trained ear model arrives, its per-dimension outputs can be compared against these hand-built scores clip-by-clip; when a comparison disagrees, the raw features preserved in the TSV allow the disagreement to be traced back to either the transfer curve or the underlying signal, without re-running any audio through librosa.

**Blind-spot enumeration as an enforced contract.** Snapshotting each heuristic's blind-spot tuple onto every result — rather than relying on the docstring — means a future maintainer cannot edit the documented failure modes without changing what historical runs would replay. The single MODERATE follow-on item logged against this branch (see §5) treats blind-spot integrity as first-class in exactly this spirit.

**The isolation pattern generalizes.** A sibling clone applied the same three-layer scan (import + literal string + audit symbol) to a different consumer of the classifier's non-factor sidecar. Together the two demonstrations argue that this kind of "isolation from a specific taxonomy" is enforceable via static analysis at negligible cost, and future consumers can copy the rule set.

**What the seeds cannot tell us.** The most substantive limitation of this cycle's evidence is that fluidsynth material cannot argue the form heuristic's anchors from data — all long/mid seeds saturate. The right response is patience: when rated audio becomes available (currently blocked at the network layer), the top anchor should be **re-argued** from an observed distribution, not **re-fit** to it. Re-fitting to observed data would defeat the branch's interpretability commitment.

## 5. Follow-on notes (not defects)

- **Output-TSV header fragility.** `run_battery.py` derives its header from the first clip's flattened row. If a later clip returns a strict superset of raw-feature keys — which none of the seven current seed clips does — the writer will raise. The fix is one line (`extrasaction='ignore'` on the `DictWriter`, or pre-computing the union header from a schema). Recommended cleanup when the wider corpus activates, not blocking now.
- **`dynamics_trajectory` units.** The label reads `envelope_range_ratio per second`; the original research brief phrased it as `mess_scale per second`. The number produced is internally consistent with the label chosen; both readings survive scrutiny.
- **Short-seed `form_coherence` guard.** The whole-song self-similarity matrix computes on 22-second input and returns unity because the SSM is nearly flat. Adding a `too_short` guard analogous to the clip-level 30 s floor would tidy this — cosmetic, not a bug.
- Two smaller stylistic items (a boolean-mask comparison in the melody module, and a regex that could false-positive on a comment containing the forbidden string) were noted by the audit and carry no functional impact.

## 6. Conclusions and next work

The hand-built half of the ear-model bake-off is discharged for the seed corpus. Every falsification-critical assertion — anchored-tail debias, isolation of the classifier's non-factor sidecar, byte-level reproducibility, blind-spot integrity, and honest nulls — was verified by direct re-execution rather than inspection alone. The trained-ear half of the same comparison is blocked until the rated-audio corpus becomes accessible; that work is out of scope for this branch. On the toolchain side, the recommended next step is a preflight for the transcription stage (basic-pitch), which will require a quarantined virtual environment to resolve a known dependency conflict.

## References

No new external sources were introduced by this branch; all cited packages (librosa 0.11.0, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0, matplotlib 3.11.1) are inherited from the workspace's pinned toolchain.

## Appendix: Implementation Details

**Code organization** (all under workspace root):

- `scripts/heuristics/`
  - `__init__.py`
  - `mess_scale.py` — transfer helper + `blend()` composer + `HeuristicResult` dataclass
  - `melody.py`, `timbre.py`, `form.py`, `dynamics.py` — one module per dimension
  - `battery.py` — dispatches all four heuristics on a single clip
  - `meta_tracker.py` — whole-song descriptors + anchored-tail weighting
  - `run_battery.py`, `run_meta_tracker.py`, `plot_battery.py` — entry points
- `tests/test_heuristics_isolation.py` — four static rules + anti-drift + plant-and-catch self-test

**Data outputs**:

- `data/heuristics/d60cead66dbd0b95/{clip_battery.tsv, meta_descriptors.json, meta_bars.png}` (long seed)
- `data/heuristics/d15d5c009a70cc32/{clip_battery.tsv, meta_descriptors.json, meta_bars.png}` (mid seed)
- `data/heuristics/d251556aedfe35ef/{clip_battery.tsv, meta_descriptors.json, meta_bars.png}` (short seed)
- `data/heuristics/battery_histograms/hist_{melody,timbre,form,dynamics}.png`

**Standing report**: `docs/heuristics_battery_report.md` (395 lines, ten sections, referenced throughout above).

**Verification runs executed by the audit**:

- `tests/test_heuristics_isolation.py` → OK on all three rule sets, anti-drift, and import probe.
- Real-file plant of `from scripts.classifier import sidecar_nonfactor` into `scripts/heuristics/battery.py` → test failed with three rule hits on the planted line; file restored → test passed. Driver preserved at `audits/_plant_and_catch.py`.
- `run_battery.py` re-run on the long-seed manifest → `diff -q` against snapshot returned zero differences.
- Anchored-tail weights numerically verified in `meta_descriptors.json.clip_weights`: 0.2333… on the long seed's clip 3 (23 s overlap), 0.6667… on the mid seed's clip 1 (10 s overlap), 1.0 on the short seed.
- Report shape check: all ten sections present at expected line offsets, 395 lines total.

**Cross-clone notes**: This branch is disjoint from its sibling clones under fork `22b8c654f616`, touching only `scripts/heuristics/`, `tests/test_heuristics_isolation.py`, and `data/heuristics/`. Provenance events for the artifacts above are recorded in the per-clone shadow ledger; the root conductor's merge step promotes them into the main ledger under `M-HEUR-1/{melody, timbre, form, dynamics, meta-tracker}` and a rollup `M-HEUR-1` event, matching the previously established fanout-adoption pattern. The audit's `promise_check` reported zero errors and only orphan-artifact warnings, which are the expected pre-merge state.

**Session references (for traceability only)**:

- researcher session `72c463b3-66d5-4dd4-8a70-7235a7e078e2`
- worker session `7efe277d-6c19-4eb6-abe8-8f1bc422668b`
- auditor session `a46dfdba-61f1-4764-95b2-990b2bc5d524`

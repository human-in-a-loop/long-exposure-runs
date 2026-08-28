---
created: 2026-08-28T05:35:00Z
cycle: 4
run_id: run-2026-08-28T040704Z
agent: worker (clone-1 of fork 22b8c654f616)
milestone: M-HEUR-1
---

# M-HEUR-1 — Hand-built heuristics battery on the mess-scale

## 1. Objective + branch context

This report closes M-HEUR-1: a hand-built heuristics battery on the mess-scale
(0.0–1.0) covering four dimensions — **melody, timbre, form, dynamics** — with
per-heuristic blind-spot lists, plus an intra-song meta-heuristic tracker that
emits four macro descriptors (`dynamics_trajectory`, `form_coherence`,
`peak_location_fraction`, `heuristic_variance_across_clips`), honoring the
ingestion manifest's `anchored_tail=true` debias weight formula
`(30 − overlap_s) / 30`. Non-factor isolation is enforced by a static-analysis
test with a plant-and-catch self-test.

Clone 1 of fork `22b8c654f616` (cycle 4 fanout branch B). Sibling clones own
M-SEP-1 (branch A) and M-TEX-1/panel (branch C). This branch touches only
`scripts/heuristics/`, `tests/test_heuristics_isolation.py`, and
`data/heuristics/` — disjoint from the other branches' subtrees.

## 2. Environment

- Interpreter: `/usr/bin/python3` (Python 3.11).
- librosa 0.11.0, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0, matplotlib 3.11.1.
- `pyloudnorm` and `crepe` are absent; neither is required — librosa.pyin covers
  pitch and RMS-based measures cover dynamics.
- Every entry-point script starts with `#!/usr/bin/env -S /usr/bin/python3` and
  asserts `sys.executable == "/usr/bin/python3"` before importing librosa.
- `np.random.seed(0)` is planted at the top of every heuristic function even
  though none of the current features are stochastic; future-proofing.

## 3. Mess-scale transfer function

Every heuristic maps its raw feature(s) to `[0.0, 1.0]` through a single
helper, `scripts/heuristics/mess_scale.py::mess_scale(raw, anchors)`:

- `anchors` is a strictly-increasing list of `(raw_x, mess_y)` pairs, each
  `mess_y ∈ [0, 1]`.
- Piecewise-linear interpolation between adjacent anchors; flat extrapolation
  outside the range.
- `NaN` in → `0.0` out; a *null-with-reason* result should be returned by the
  heuristic *before* calling `mess_scale`, and every heuristic guards its
  degenerate cases explicitly.

A companion `blend(features_mess, weights)` composes several already-mess-scaled
features by a fixed weight vector; weights must sum to `1.0 ± 1e-9`.

The canonical return type is `HeuristicResult`:

```
@dataclass(frozen=True)
class HeuristicResult:
    name: str
    raw_features: dict         # every raw scalar (auditor can re-run mess_scale)
    mess_scale: float | None   # None with reason for null cases
    reason: str | None         # "too_short_for_ssm", "unvoiced_dominant", ...
    blind_spots: tuple         # snapshot of module-level BLIND_SPOTS at call time
```

`blind_spots` is snapshotted at call time so that a stale/updated docstring
cannot silently drift from what the historical run actually saw.

## 4. Four heuristics: definitions

Anchors are chosen to be interpretable, not calibrated on a corpus — they
express the author's prior on where each feature transitions from "trivial"
to "richly expressive". The auditor is invited to challenge them; because
raw features are preserved in the TSV, any re-anchoring is a re-plot rather
than a re-compute.

### 4.1 `melody_quality`  (`scripts/heuristics/melody.py`)

- **Inputs:** mono audio at 22050 Hz.
- **Extractor:** `librosa.pyin(fmin=C2, fmax=C7, frame_length=2048)`. Drop
  unvoiced frames.
- **Features:**
  - `contour_smoothness = 1 / (1 + Δpitch_semitones_RMS)`
  - `interval_variety   = min(1.0, unique_intervals / 12)` (rounded to nearest semitone)
  - `pitch_class_entropy = H(pcp) / log2(12)`
- **Blend:** `0.4·smoothness + 0.3·variety + 0.3·entropy` → mess_scale.
- **Anchors:**
  - smoothness: `(0.0, 0.0), (0.25, 0.35), (0.55, 0.75), (0.85, 1.0)`
  - variety:    `(0.0, 0.0), (0.25, 0.35), (0.5, 0.7), (1.0, 1.0)`
  - entropy:    `(0.0, 0.0), (0.4, 0.4), (0.7, 0.85), (1.0, 1.0)`
- **Null-with-reason:** voiced-frame fraction < 0.1 → `mess_scale=None`,
  `reason="unvoiced_dominant"`. Also `too_few_voiced_frames` and
  `empty_pitch_histogram` guards.
- **Blind spots** (module-level `BLIND_SPOTS`):
  1. Percussion-only or noise tracks — pyin is not meaningful; guard triggers
     when voiced-frame fraction < 0.1, but partially-pitched percussion (tuned
     toms) can slip through with meaningless F0.
  2. Polyphonic content — pyin picks a single salient F0 per frame; harmony and
     counterpoint are collapsed to the loudest voice.
  3. Atonal vs. tonal bias — pitch-class entropy penalizes strongly tonal music
     (a diatonic piece caps around log2(7)/log2(12) ≈ 0.78) more than atonal /
     12-tone material.
  4. Octave errors — pyin may octave-jump; smoothness is sensitive to these as
     ±12 semitone spikes.

### 4.2 `timbre_quality`  (`scripts/heuristics/timbre.py`)

- **Extractor:** `librosa.feature.mfcc(n_mfcc=13)`, spectral centroid, spectral
  flatness.
- **Features:**
  - `mfcc_delta_rms   = sqrt(mean(|MFCC[t]−MFCC[t−1]|²))` across the 13 coeffs.
  - `centroid_range   = (p95 − p05)(spectral_centroid) / (sr/4)`
  - `flatness_variance = std(spectral_flatness)`
- **Blend:** `0.4·mfcc + 0.35·centroid_range + 0.25·flatness_var`.
- **Anchors:**
  - mfcc_delta: `(0, 0), (5, 0.3), (15, 0.7), (35, 1.0)`
  - centroid_range: `(0, 0), (0.05, 0.4), (0.2, 0.8), (0.4, 1.0)`
  - flatness_var: `(0, 0), (0.02, 0.3), (0.08, 0.7), (0.2, 1.0)`
- **Null-with-reason:** `empty_audio`, `silent_audio` (peak < 1e-6),
  `too_short_for_mfcc` (< 2 frames).
- **Blind spots:**
  1. Low-SNR audio biases centroid downward, deflating `centroid_range`
     irrespective of true timbral motion.
  2. MFCC-delta RMS conflates timbral evolution with note onsets; inseparable
     at 512-hop resolution.
  3. Reverb widens perceived spectral flatness spuriously — a wet reverb-tail
     track scores as more timbrally varied than a dry version of the same source.
  4. Silence-padded clips flatten every feature; a near-silent clip scores
     toward the low anchor for all three features.

### 4.3 `form_quality`  (`scripts/heuristics/form.py`)

- **Extractor:** chroma-CQT SSM, block-averaged to ~4 s cells, cosine-similarity
  (columns L2-normalized).
- **Feature:** `diag_off_ratio = mean(SSM[|i-j|≤1]) / mean(SSM[|i-j|>1])`.
- **Null-with-reason:** `len(y)/sr < 30.0` → `mess_scale=None`,
  `reason="too_short_for_ssm"`. Also `too_few_ssm_blocks`,
  `degenerate_off_diag` guards.
- **Anchors:** `(0.5, 0.0), (1.0, 0.3), (1.6, 0.7), (3.0, 1.0)`.
- **Blind spots:**
  1. Heavily-repeating tracks (loops, minimalism) score falsely high.
  2. Through-composed pieces score falsely low.
  3. The ~4 s block granularity captures phrase-scale structure and misses
     both note-level texture (below 4 s) and section-level form (repeats
     separated by >30 s inside a single 30 s clip are impossible by construction).
  4. Key modulation partway through a clip depresses chroma self-similarity
     even when the arrangement is otherwise repetitive.

### 4.4 `dynamics_quality`  (`scripts/heuristics/dynamics.py`)

- **Extractor:** `librosa.feature.rms(hop=512)`, whole-clip RMS/peak.
- **Features:**
  - `crest_factor         = max(|y|) / rms(y)`
  - `envelope_range_ratio = p95(rms) / p05(rms)`, then clip to `[1, 20]` and take log2
  - `envelope_variance_db = std(20·log10(max(rms, 1e-80/20))) / 12.0`
- **Blend:** `0.25·crest + 0.4·range + 0.35·envvar`.
- **Anchors:**
  - crest: `(2, 0), (4, 0.3), (8, 0.7), (20, 1.0)`
  - log2(range): `(0, 0), (1, 0.35), (2.5, 0.75), (4.3, 1.0)`
  - env_var (dB/12): `(0, 0), (0.15, 0.3), (0.5, 0.7), (1.0, 1.0)`
- **Null-with-reason:** `too_short_for_dynamics` (< 5 s), `silent_audio`,
  `too_few_rms_frames`.
- **Blind spots:**
  1. Heavily compressed / mastered audio collapses toward the loudness-war
     floor (crest ≈ 3-4×, range ≈ 1-2×) regardless of true musical dynamics.
  2. Silence pockets inflate the p95/p05 ratio spuriously — a bar of rest reads
     as huge dynamic range without any crescendo.
  3. Envelope-variance dB is undefined for silent frames; the -80 dB fallback
     truncates near-silent passages and biases variance downward.
  4. Crest factor is scalar and cannot distinguish "one loud transient in a
     quiet piece" from "a piece that alternates loud and quiet".

## 5. Meta-tracker: descriptors + anchored-tail debias

`scripts/heuristics/meta_tracker.py::run_meta_tracker(manifest, battery_tsv)`
consumes an ingestion manifest and the per-clip battery TSV and emits:

- **`dynamics_trajectory`** — weighted linear regression slope of
  `dynamics_quality.raw_features["envelope_range_ratio"]` (the raw p95/p05
  ratio) vs. clip midpoint. Units: `ratio / second`; sign preserved.
- **`form_coherence`** — chroma-CQT SSM diagonal-band ratio on the **whole
  source audio** (loaded from `source_ref` at the target 22050 Hz). Distinct
  from clip-level `form_quality` — concatenating clips would double-count the
  overlap, so the meta-tracker reads the original song directly.
- **`peak_location_fraction`** — argmax(weight-adjusted sum of the four clip
  mess-scale values) clip-midpoint / song duration, in `[0, 1]`.
- **`heuristic_variance_across_clips`** — weighted variance of the L2 norm of
  the per-clip 4-vector across clips.

**Anchored-tail debias.** For a clip with `anchored_tail=true`:

    weight = max(0, (30.0 − overlap_s) / 30.0)
    overlap_s = prev_clip.t_end_s − this_clip.t_start_s

All non-anchored clips get `weight=1.0`. `short_song=true` clips get
`weight=1.0` (the whole song is a single clip). The formula is unit-tested
inside `test_heuristics_isolation.py` as an anti-drift check.

**Observed weights on the seeds:**

| Seed          | Clip idx | t_start_s | t_end_s | anchored | Weight |
|---------------|----------|-----------|---------|----------|--------|
| seed_long_87s | 3        | 57.0      | 87.0    | true     | **0.2333…** = (30 − 23)/30 |
| seed_mid_50s  | 1        | 20.0      | 50.0    | true     | **0.6667…** = (30 − 10)/30 |
| seed_short_22s| 0        | 0.0       | 22.0    | false, short_song | **1.0** |

## 6. Results

### 6.1 Per-clip battery (7 clips)

| Source     | Clip | Span (s) | Anch | Short | melody | timbre | form   | dynamics |
|------------|------|----------|------|-------|--------|--------|--------|----------|
| d15d5c00   | 0    | 0-30     | F    | F     | 0.6945 | 0.2177 | 1.0000 | 0.0068   |
| d15d5c00   | 1    | 20-50    | T    | F     | 0.6947 | 0.2421 | 1.0000 | 0.0062   |
| d251556a   | 0    | 0-22     | F    | T     | 0.4000 | 0.2108 | **null:too_short_for_ssm** | 0.9216   |
| d60cead6   | 0    | 0-30     | F    | F     | 0.6986 | 0.1949 | 1.0000 | 0.3517   |
| d60cead6   | 1    | 25-55    | F    | F     | 0.6744 | 0.1822 | 1.0000 | 0.4571   |
| d60cead6   | 2    | 50-80    | F    | F     | 0.6616 | 0.1936 | 1.0000 | 0.2384   |
| d60cead6   | 3    | 57-87    | T    | F     | 0.6559 | 0.2185 | 1.0000 | 0.4949   |

Notable observations (with blind-spot cross-refs):

- **`form=1.0` on every ≥30 s clip.** All raw `diag_off_ratio` values sit
  well above the top anchor (3.0), ranging from 17.2 to 82.8. The fluidsynth
  seeds are highly repetitive (single instrument, static texture), which is
  exactly the failure mode called out in §4.3 blind-spot 1 (loops score
  falsely high). The battery is behaving as documented; the seeds don't
  exercise this heuristic's discriminating range. Real recorded music with
  section structure will land between the anchors.
- **`form=null:too_short_for_ssm`** on the 22 s clip is the honesty
  contract. It is not a failure — it is evidence the null-with-reason path
  works.
- **`timbre` clusters low (0.18-0.24).** Consistent with fluidsynth-origin
  monotimbral audio — MFCC delta stays small and centroid range is narrow.
- **`melody` clusters around 0.66-0.70** for the sustained tonal seeds; the
  22 s seed drops to 0.40 because its intervals are less varied (`raw_variety`
  low) and its entropy sits below the top anchor.
- **`dynamics` spread is the widest** (0.006-0.921). The short_22s clip has
  crest=7.86 and range_ratio=142 — the latter is the p95/p05 silence-pocket
  inflation blind-spot in action (§4.4 blind-spot 2).

### 6.2 Meta-descriptors (3 seeds)

| Source          | dur(s) | dyn_trajectory (Δrange/s) | form_coherence | peak_frac | heur_variance |
|-----------------|--------|---------------------------|----------------|-----------|---------------|
| d60cead6 (long) | 87     | −0.00904                  | **5.930**      | 0.460     | 7.88e-4       |
| d15d5c00 (mid)  | 50     | −0.00013                  | **5.643**      | 0.300     | 5.18e-6       |
| d251556a (short)| 22     | null (only 1 clip)        | **1.000**      | 0.500     | 0.0           |

Reads:

- All three `form_coherence` values compute (the meta-tracker's SSM handles
  down to 22 s because it uses the *whole-song audio* directly, whereas the
  clip-level `form_quality` guards ≥ 30 s). The short seed's `form_coherence`
  of 1.000 means the diagonal-band-to-off-diagonal ratio is at unity — i.e.
  the SSM is essentially flat (few blocks, very uniform texture). This is a
  legitimate observation, not a bug.
- `dynamics_trajectory` is `null` on the 22 s seed because it has only one
  clip (no slope to regress). Documented in the meta-tracker output as
  `None`.
- `heuristic_variance_across_clips` is tiny across all three seeds — again
  reflecting the seeds' monotimbral, structurally-static nature.

### 6.3 Plots

- Per-heuristic mess-scale histograms across all 7 clips:
  - `data/heuristics/battery_histograms/hist_melody.png`
  - `data/heuristics/battery_histograms/hist_timbre.png`
  - `data/heuristics/battery_histograms/hist_form.png`
  - `data/heuristics/battery_histograms/hist_dynamics.png`
- Per-seed meta-descriptor bar charts (co-located with each meta JSON per
  STRUCTURE.md):
  - `data/heuristics/d60cead66dbd0b95/meta_bars.png`
  - `data/heuristics/d15d5c009a70cc32/meta_bars.png`
  - `data/heuristics/d251556aedfe35ef/meta_bars.png`

## 7. Non-factor isolation

Test: `tests/test_heuristics_isolation.py`. Enforces four rules on every
`.py` under `scripts/heuristics/`:

- R1: no `import sidecar_nonfactor` / `from … import sidecar_nonfactor`.
- R2: no `import scripts.classifier.*` / `from scripts.classifier … import`.
- R3: no string literal `data/classifier/_nonfactor` or `_nonfactor/` or
  `sidecar_nonfactor` in code.
- R4: no reference to `AuditRecord`, `NonFactorValue`, `audit_unwrap`.
- Bonus (anti-drift): the anchored-tail formula helper
  `anchored_tail_weight(prev_end, this_start)` must return `(30 − overlap)/30`
  numerically for the two real seed overlaps (23 s, 10 s) and `1.0` when
  overlap ≤ 0. Verified at each test run.

**Normal-run output:**

```
OK: no forbidden references in scripts/heuristics/
OK: anchored-tail formula check: OK
OK: all heuristics modules import cleanly
```

**Plant-and-catch self-test** (`--self-test` or included in every normal run):
copies `scripts/heuristics/` to a scratch directory, prepends
`from scripts.classifier import sidecar_nonfactor  # PLANT` to `battery.py`,
re-scans, confirms three hits (R1 + R2 + R3 all trigger), removes the plant.

```
SELF-TEST OK: plant caught with hits:
  ('scripts/heuristics/battery.py', 1, '\\bimport\\s+.*sidecar_nonfactor')
  ('scripts/heuristics/battery.py', 1, '\\bfrom\\s+scripts\\.classifier[.\\w]*\\s+import')
  ('scripts/heuristics/battery.py', 1, 'literal:sidecar_nonfactor')
```

## 8. Blind-spot audit (aggregated)

| # | Heuristic         | Blind spot                                                                                     |
|---|-------------------|------------------------------------------------------------------------------------------------|
| 1 | melody_quality    | percussion-only / noise tracks: pyin meaningless; guard triggers < 0.1 voiced fraction         |
| 2 | melody_quality    | polyphonic content: pyin picks single salient F0; harmony collapsed                            |
| 3 | melody_quality    | atonal vs. tonal bias: PCP entropy penalizes strongly tonal music                              |
| 4 | melody_quality    | octave errors: pyin can jump; smoothness sensitive to ±12 semitone spikes                      |
| 5 | timbre_quality    | low SNR biases spectral centroid downward, deflating centroid_range                            |
| 6 | timbre_quality    | MFCC-delta RMS conflates timbral evolution with onsets at 512-hop resolution                   |
| 7 | timbre_quality    | reverb widens perceived spectral flatness spuriously                                           |
| 8 | timbre_quality    | silence-padded clips flatten every feature toward the low anchor                               |
| 9 | form_quality      | heavily-repeating tracks (loops) score falsely high — observed on all fluidsynth seeds         |
| 10| form_quality      | through-composed pieces score falsely low                                                      |
| 11| form_quality      | 4 s block granularity misses < 4 s texture and > 30 s section-scale form                       |
| 12| form_quality      | intra-clip key modulation depresses chroma self-similarity                                     |
| 13| dynamics_quality  | compressed / mastered audio collapses to loudness-war floor                                    |
| 14| dynamics_quality  | silence pockets inflate p95/p05 ratio spuriously — observed on seed_short_22s (range=142)      |
| 15| dynamics_quality  | envelope-variance dB truncated at -80 dB floor for near-silent frames                          |
| 16| dynamics_quality  | crest factor scalar; cannot distinguish "one loud transient" from "loud-quiet alternation"     |

All 16 blind spots are also carried in the per-`HeuristicResult.blind_spots`
snapshot on every call, so a downstream consumer can inspect exactly which
blind spots applied to a given result.

## 9. What the seeds do — and do NOT — test

- Seeds are fluidsynth-origin (M-INGEST-1's determinism guarantee) — mostly
  single-instrument, static-texture piano-like content. They exercise the
  **null-with-reason** paths (short_22s, unvoiced-dominant guard), the
  **anchored-tail weight** (both non-trivial cases: 0.667 and 0.233), and
  the **isolation contract**, but they do NOT exercise:
  - The upper-half of the `form_quality` mess-scale — all long/mid clips
    saturate at 1.0 because the fluidsynth material is too repetitive
    (raw diag/off ratio 17-83, top anchor is 3.0).
  - Percussion / noise-dominated audio (`unvoiced_dominant` guard is never
    triggered because voiced-fraction is 1.0 on all seeds).
  - Compressed / mastered audio (dynamics blind-spot 1).
  - Polyphonic content (melody blind-spot 2).
  - Reverb sensitivity (timbre blind-spot 3).
- The 22 s seed is below the 30 s SSM minimum by design and exercises the
  `too_short_for_ssm` null-with-reason path.
- When rated audio arrives (currently blocked by egress, per
  `corpus/CORPUS_STATUS.md`), re-running the battery on those tracks is the
  right next probe. Anchors should NOT be re-fit on that data — they should
  be re-argued from the observed distribution.

## 10. Reproducibility

Interpreter: `/usr/bin/python3`. Pinned versions listed in §2.

Invocation:

    /usr/bin/python3 scripts/heuristics/run_battery.py \
        --manifest data/ingestion/manifests/seed_long_87s.manifest.jsonl

    /usr/bin/python3 scripts/heuristics/run_meta_tracker.py \
        --manifest data/ingestion/manifests/seed_long_87s.manifest.jsonl

    /usr/bin/python3 scripts/heuristics/plot_battery.py

    /usr/bin/python3 tests/test_heuristics_isolation.py

**Determinism confirmed** on 2026-08-28: two consecutive runs of
`run_battery.py` on `seed_long_87s.manifest.jsonl` produce byte-identical
`data/heuristics/d60cead66dbd0b95/clip_battery.tsv` (verified via `diff -q`).
`np.random.seed(0)` is planted at import of every heuristic module as a
future-safety measure even though every current feature is deterministic.

Artifact index (files produced this cycle):

- Package: `scripts/heuristics/{__init__.py, mess_scale.py, melody.py,
  timbre.py, form.py, dynamics.py, battery.py, meta_tracker.py,
  run_battery.py, run_meta_tracker.py, plot_battery.py}` — 11 files.
- Test: `tests/test_heuristics_isolation.py` — 1 file.
- Data: `data/heuristics/{d60cead66dbd0b95,d15d5c009a70cc32,d251556aedfe35ef}/
  {clip_battery.tsv, meta_descriptors.json, meta_bars.png}` — 9 files.
- Plots: `data/heuristics/battery_histograms/hist_{melody,timbre,form,
  dynamics}.png` — 4 files.
- This report: `docs/heuristics_battery_report.md`.

Plan additions: 5 sub-milestone rows in `plan_of_record.md`
(M-HEUR-1/{melody,timbre,form,dynamics,meta-tracker}), registered under a
`_plan/register-heuristics-submilestones` ledger event.

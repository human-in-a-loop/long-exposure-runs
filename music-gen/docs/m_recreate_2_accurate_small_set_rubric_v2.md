---
created: 2026-08-29T22:30:00Z
cycle: 50
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set-v2
supersedes: docs/m_recreate_2_accurate_small_set_rubric.md
---

# M-RECREATE-2 accurate small-set rubric — v2 (SUPERSEDE)

**Status**: peer supersede of c49 rubric-v1. v1 remains READ-ONLY anchor;
its three-way byte-equality chain (doc SHA `958ade38…3fe58b9d` ==
`data/recreate_v2/rubric_hash.txt` == future v1-RC verdict.rubric_hash)
is preserved. This v2 rubric opens a **new** three-way byte-equality
chain: doc SHA (this file) == `data/recreate_v2/rubric_hash_v2.txt` ==
every c51+ RC-v2-branch `verdict.rubric_hash`.

**Origin**: OPERATOR UPDATE 2026-08-29 (see
`docs/OPERATOR_recreation_root_cause_audit.md` and c50 live_guidance).
Three additional root causes (RC7 fixed chorus+reverb wash, RC8 first-30s
window on sparsest section, RC9 non-rhythm parts collapsed to one
"other") plus four binding design decisions (D1-D4) plus two new accepts
(A7, A8).

**Editing this rubric is FORBIDDEN.** Any material change must ship as a
sibling `_v3` peer supersede. Landing v2 to disk BEFORE any script under
`scripts/recreate_v2/*_v2.py`, `rc7_*.py`, `rc8_*.py`, or `rc9_*.py`
is a hard mtime gate enforced by `tests/test_m_recreate_2_v2_pre_registration.py`.

---

## §1 — Focus set

Unchanged from v1: 5 songs frozen by SHA-256 tiebreak over
`(title|video_id|playlist_id)` UTF-8, Chicken Grease mandatory:

1. Chicken Grease (band 6, sha16 `31a164f845f8e27e`) — mandatory anchor
2. Disco A (band 5, sha16 `cdd2717e52820ff6`)
3. Dojo Cuts Rome (band 5, sha16 `51e433ade2a845e1`)
4. Mura Masa What If I Go (band 5, sha16 `252eb21ce7df7328`)
5. Peach Dream (band 6, sha16 `88d247468cb6d49f`)

Focus-set-v2 (`data/recreate_v2/focus_set_v2.json`) extends this list
with D1 `chosen_section` metadata per song. v1 focus_set is a byte-
identical READ-ONLY anchor.

---

## §2 — Binding design decisions (D1–D4)

Each is a v2 invariant. RC-branch implementations MUST honour every one.

### D1 — Section selection (peak 30s)

Auto-pick each song's peak 30s window by combined RMS + onset density.

**Formula** (pinned):

    combined_score(t) =
        w_rms   · z_normalize(rolling_rms(hop=512))
      + w_onset · z_normalize(rolling_onset_density(hop=512, window=30s))

    w_rms   = 0.5
    w_onset = 0.5

- Deterministic argmax over combined_score; ties broken by earliest
  start (smallest `t_start_s`).
- `z_normalize` = per-song z-score using mean+std of the rolling metric
  over the full song duration.
- Chosen-section metadata `{song_id, t_start_s, t_end_s, combined_score,
  rms_score, onset_density_score, weights}` written to provenance (A8).
- NO PRNG.

### D2 — Vocals: hybrid render

- (i) Vocal melody STILL transcribed into `merged.midi` to satisfy RC1
  symbolic requirement (basic-pitch or pyin f0 on vocals stem).
- (ii) NOT synthesized: the ORIGINAL separated vocals stem is
  time-aligned and loudness-preserved (matched to c50 baseline vocal
  LUFS-S ± 0.5 LU), then layered over the reconstructed band as the
  FINAL render.
- RC1 accept unchanged (voiced-time coverage ≥ 50%); RC6 panel gate
  evaluated on the final hybrid render.

### D3 — Separator: htdemucs_6s

- Switch source separation from htdemucs (4-stem) to htdemucs_6s
  (6-stem: vocals/drums/bass/guitar/piano/other).
- **Fetchability probe** (c50 requirement): attempt
  `torch.hub.load('facebookresearch/demucs', 'htdemucs_6s')` OR direct
  model weights download through the workspace proxy. Log outcome to
  `data/recreate_v2/fetchability_htdemucs_6s.jsonl` with HTTP status.
- If BLOCKED: fall back to 4-stem separator AND surface the blocker as
  a first-class finding in the c50 worker report (operator explicitly
  asked for the blocker to surface; do NOT swallow).

### D4 — Mix stage: per-stem loudness + EQ replaces pinned chorus+reverb

The pinned Surge chorus 0.35 + reverb 0.05 chain is **retired** as the
M-RECREATE-2 render deliverable. Replaced by:

1. Render each part separately (extend `scripts/palette_render/render_stem.py`
   — c33 anchor — via ADDITIVE kwargs per the c36 backwards-compat
   pattern; do NOT rewrite. c50 does not touch render_stem.py; c51+ RC-v2
   Branch C lands the extension).
2. Per-stem loudness match (RMS + LUFS-S) to original stems on the
   chosen section (D1).
3. Per-stem deterministic EQ curve fitted to the original stem's average
   spectrum. Recommend 12-band log-spaced IIR biquad chain (all params
   pinned); worker may refine the band count/kind in v2 pre-registration
   BEFORE any script runs. Final choice must be pinned in
   `data/recreate_v2/eq_curve_spec.json` at c51+ Branch C landing.
4. Sum the matched stems into the final render.

The old pinned chain is retained ONLY as a comparison baseline row in
the panel — NEVER as the LANDS deliverable.

---

## §3 — Root causes and RCs

### v1 root causes (RC1–RC6) — carried unchanged

- **RC1 vocals dropped** → transcribe vocals stem. Accept: vocal-part
  note count > 0 AND voiced-time coverage ≥ 50% of baseline.
- **RC2 pitched model on drums** → onset detection + kick/snare/hihat
  classifier. Accept: drum onset F1 ≥ 0.60 AND count in [0.5×, 2×] of
  baseline.
- **RC3 under-transcribed bass** → lower thresholds OR pyin. Accept:
  bass note count in [0.5×, 2×] pyin-voiced baseline AND <250 Hz energy
  correlation ≥ 0.5 AND median MIDI pitch < 55.
- **RC4 program 4 for everything** → explicit GM programs. Accept:
  merged.midi has zero parts on GM program 4 unless logged.
- **RC5 hardcoded 120 BPM** → `librosa.beat.beat_track`. Accept:
  `|estimated_bpm − score_bpm| ≤ 2`.
- **RC6 mel-L1 gate** → refined below (see §3.5).

### v2 additional root causes (RC7–RC9)

#### RC7 — mix-balance-matching

**Root cause**: fixed Surge chorus 0.35 + reverb 0.05 wash on the full
mix with zero mix-balance matching. `scripts/palette_render/render_stem.py`
exists but is unused by the recreation path.

**Acceptance** (A7): per-stem loudness error after gain staging
≤ 3 dB RMS AND ≤ 3 LU LUFS-S vs original stems on the chosen section.

**Baseline anchor**: `data/recreate_v2/baseline/<sha16>/rc7_per_stem_loudness.json`.

#### RC8 — peak-section-selection

**Root cause**: recreations always take the first 30s from t=0 — the
sparsest section of any song.

**Acceptance** (A8): chosen-section metadata `{song_id, t_start_s,
t_end_s, combined_score, rms_score, onset_density_score, weights}`
present in provenance for every focus song AND reproduces
`focus_set_v2.json.chosen_section` byte-for-byte.

**Baseline anchor**: `data/recreate_v2/focus_set_v2.json` +
`data/recreate_v2/baseline/<sha16>/rc8_chosen_section_verified.json`.

#### RC9 — first-class parts per instrument

**Root cause**: all non-rhythm instruments are collapsed into one
"other" part on one patch.

**Acceptance**: guitar (GM 25-30) + piano (GM 0-4) become distinct
parts with their own transcription and their own GM programs in
`merged.midi`. Residual "other" gets a logged patch choice.

**Baseline anchor**: `data/recreate_v2/baseline/<sha16>/rc9_6stem/`
(6-stem WAVs) OR `data/recreate_v2/baseline/<sha16>/rc9_htdemucs_6s_blocked.json`
(fetch attempt log + fallback declaration).

### §3.5 — RC6 refined panel gate

The RC6 LANDS gate is an **AND** over:

- (RC1 + RC2 + RC3 + RC7) per-stem accepts hold; AND
- VGGish `cos(orig, effects)` ≤ VGGish `cos(orig, bare)`; AND
- centroid_rmse not-worsening `bare → effects`; AND
- per-stem loudness ≤ 3 dB RMS (RC7); AND
- chosen-section metadata present (RC8).

**Mel-L1 alone can NEVER confer LANDS.** Iterate fix → re-render →
measure until the panel gate passes on ≥3 focus songs.

VGGish remains a DEFERRED-honest-None in c50 baselines per the c11 CLAP
anti-pattern lock. c52+ RC6-v2 branch wires it in via the
`scripts.texture.panel` embedding surface.

---

## §4 — Verdict rubric (frozen at supersede time)

Three verdicts, applied at v2 rollup:

- **`M_RECREATE_2_v2_LANDS`** — panel gate passes on ≥3 focus songs;
  RC1–RC9 accepts hold on those songs.
- **`M_RECREATE_2_v2_PARTIAL`** — panel gate passes on 1–2 songs OR
  ≥7/9 RC accepts hold on ≥3 songs.
- **`M_RECREATE_2_v2_INSUFFICIENT`** — anything else.

---

## §5 — Byte-determinism contract

All v2 pre-registration deliverables (focus_set_v2.json,
rc7/rc8/rc9 baseline JSONs, htdemucs_6s outputs where they land) must
reproduce byte-identically × 2 across two fresh `tempfile.mkdtemp()`
runs under env pins:

    PYTHONHASHSEED=0
    SOURCE_DATE_EPOCH=1756463424
    TZ=UTC
    LC_ALL=C.UTF-8
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
    torch.manual_seed(0)

NO PRNG. SHA-256 tiebreak only. `/usr/bin/python3` interpreter guard on
every new script.

---

## §6 — READ-ONLY anchors under c50

- c49 v1 rubric doc + `data/recreate_v2/rubric_hash.txt` (v1 chain
  preserved).
- c49 focus_set.json.
- c49 RC0 baseline (all 45 files across 5 songs).
- c49 RC1–RC6 stubs.
- htdemucs 4-stem outputs at
  `data/recreate_v0_full_corpus/per_song/<band>/<sha16>/per_stage/04_htdemucs/`
  (c37 anchors — READ-ONLY re-use, not re-run).
- `scripts/palette_render/render_stem.py` (c33 anchor — READ-ONLY
  under c50; D4 additive-kwargs extension lands c51+ Branch C).
- All rules ledgers, c22 stability harness, c6 CORN chassis, palette
  probes, ear-model artifacts, anchor_manifest_v1.

Assert byte-identical pre==post in
`data/recreate_v2/anchor_preservation_v2.json` (≥45 entries) at c50
close.

---

## §7 — Anti-pattern lockouts (reasserted)

1. c11 CLAP HF SSL fetch — locked. RC6-v2 VGGish stays honest-DEFERRED
   in c50 baseline.
2. c22 chassis-audit; c23 head-reg; c25 feature-rep; c35 palette-v2
   VST3 byte-determinism — locked. D4 mix-stage does NOT re-attempt
   VST3 render; extends c33 fluidsynth+sfizz path only.

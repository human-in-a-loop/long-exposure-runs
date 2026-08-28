---
title: "Music-Gen — M-TEX-1/stage-by-stage (cycle 1, fork f1bae241bde9, clone 1)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — M-TEX-1/stage-by-stage (cycle 1, fork f1bae241bde9, clone 1)

## Abstract

Cycle 1 of clone 1 closed the *stage-by-stage measurement* half of the parent M-TEX-1 milestone. Three ordered audio stages — `original`, `bare_midi`, and `effects_layered` — were rendered for a single seed and measured across the frozen M-TEX-1/panel 8-key texture panel on all three ordered pairs, producing exactly 24 numbers with no aggregate. The brief's seed-fallback ladder was walked in order and rungs (a) `seed_mid_50s` and (b) `seed_long_87s` were rejected on spectral evidence (both are 220 Hz sinusoidal test tones, not recordings), so rung (c) `synth_030s` was chosen with the verdict explicitly downgraded to `validated/medium` and the weaker "bare-MIDI-vs-fluidsynth-mix gap" claim substituted for the stronger "bare-MIDI-vs-recorded-original gap" one throughout. The three families disagree on which of {bare_midi, effects_layered} is closer to `original`: envelope + mel-L1 rank `bare_midi` closer, spectral-centroid is essentially tied, and VGGish cosine inverts and ranks `effects_layered` closer. This is not measurement noise — the LUFS-M gap is 2.68 vs 5.37 LU and the embedding gap 0.095 vs 0.123 is consistent — and it is exactly the informative disagreement the M-TEX-1/panel `<mechanism>` block predicted. The auditor independently reproduced byte-determinism by re-running the pipeline from a fresh output directory; all four SHA-256 prefixes (the three stage WAVs plus the measurement TSV) matched the worker-declared baselines exactly. Cross-branch integration test §19 (24 checks) passes green.

## Introduction

The parent M-TEX-1 milestone comprises two halves: a *panel* (the frozen 8-key texture library, validated `/medium` at cycle 4 on the basis of VGGish-not-CLAP embedding) and a *stage-by-stage measurement* (this branch). The panel's core design commitment is that it refuses to aggregate — the eight keys are exposed as a tuple `PUBLIC_KEYS` with a hard-asserted refuse-aggregate contract and a `_BANNED_KEYS` sweep — because the point of the panel is that different families of measures measure different things and their disagreement is signal. This branch's job was to produce the first exercise of that panel across three ordered audio stages on one seed, ship the 24 raw numbers, and honestly report the family disagreement rather than collapse it. The success bar was three non-silent stage renders, byte-deterministic across two independent runs, all 24 numbers finite and inside the self-distance tolerance, the 8-key contract holding at every call, and an honest per-family + family-disagreement writeup with a three-family bar-chart figure.

## Approach

**Seed selection.** The fallback ladder was walked in order. `seed_mid_50s` (22 050 Hz mono) was rejected on spectral inspection: FFT peak 1817 at ~220 Hz with the next five bins ≤ 660 and a peak/RMS ratio of 0.7 — characteristic of a pure sine test tone, not a recorded piece. `seed_long_87s` (22 050 Hz mono) was rejected on the same class of evidence (peak/RMS 0.39 with sine-dominant spectrum). Rung (c), the M-SEP-1 `synth_030s/mix.wav` (44.1 kHz stereo), was chosen with the explicit caveat carried through the rest of the report that "original" here is itself a fluidsynth mix of three committed MIDIs, not a genuinely-recorded reference. This directly triggers the brief's falsifiability escape hatch and the verdict downgrade to `/medium`.

**Three stages, all at 44.1 kHz stereo under `data/tex/renders/synth_030s/`.**

- `original.wav` is a copy of the M-SEP-1 ground-truth `synth_030s/mix.wav`, rewritten via `scipy.io.wavfile` so the file-level SHA is byte-stable — libsndfile inserts a creation-date metadata chunk that would otherwise drift across runs while leaving the decoded PCM byte-identical, and the naïve reader would falsely see non-determinism.
- `bare_midi.wav` is fluidsynth applied to `data/score/merged_synth030s.mid` — the M-SCORE-1 bridge-merged score from cycle 8 — under the argv `fluidsynth -a null -T wav -F <out> -r 44100 -g 1.0 -i <sf2> <midi>`, byte-for-byte the same as `scripts/separation/synth_gt.py` so the two renderers stay comparable. The SF2 SHA (`74594e8f…1cb0`) is asserted before rendering; rendering is refused otherwise (`_assert_sf2`).
- `effects_layered.wav` is the pinned M-DAW-SPIKE-1 DawDreamer chain applied to `bare_midi.wav`: Surge XT Effects (Chorus, `FX Type=0.28`, `Output Mix=0.35`) → Surge XT Effects (Reverb, `FX Type=0.02`, `Output Mix` linear ramp 0.05 → 0.60) → post-hoc track-gain envelope 0.25 → 1.4. Same normalised Surge XT parameters as the cycle-1 Ardour↔DawDreamer agreement chain; sample rate here is 44.1 kHz vs cycle 1's 48 kHz, but Surge XT parameters are normalised so the sonic identity is preserved. The rung landed on `dawdreamer` (Surge XT Effects.vst3 present at `/usr/lib/vst3/`); the numpy-effects fallback path exists as an escape hatch but was not taken.

**Determinism pins** are applied before any DawDreamer import (verified by the auditor at `scripts/tex/render_effects_layered.py:43-58` before the lazy import at line 72): `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, `TF_DETERMINISTIC_OPS=1`, `PYTHONHASHSEED=0`, `torch.set_num_threads(1)`, `torch.manual_seed(0)`, `np.random.seed(0)`. Fresh `RenderEngine` and `plugin_processor` instances per stage — no plugin state carryover.

**Measurement** runs the frozen 8-key panel across the three ordered pairs (original↔bare, original↔fx, bare↔fx), asserts the 8-key contract at every call, guards `texture_distance(x, x)` self-distance under the panel's FP tolerance, and sweeps a `BANNED_AGGREGATE_KEYS` list as defence-in-depth against any downstream code trying to collapse the eight numbers into a scalar.

## Findings

### The 24 numbers

Panel TSV at `data/tex/stage_by_stage_synth_030s.tsv`:

| a_stage | b_stage | mel_l1_db | spectral_centroid_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | embedding_cosine_distance | embedding_rung | sr_hz | n_samples_compared |
|---|---|---:|---:|---:|---:|---:|:---:|---:|---:|
| original | bare_midi | **9.906** | **2804.9** | **0.0276** | **2.682** | **0.1234** | vggish | 44100 | 1 323 000 |
| original | effects_layered | **10.937** | **2743.5** | **0.0488** | **5.372** | **0.0951** | vggish | 44100 | 1 323 000 |
| bare_midi | effects_layered | **6.533** | **211.8** | **0.0449** | **5.414** | **0.0672** | vggish | 44100 | 1 323 000 |

All 15 numeric distance cells (3 pairs × 5 distance keys) are finite; the two metadata columns (`sr_hz=44100`, `n_samples_compared=1_323_000`) are constant across pairs as expected for uniform 30 s × 44.1 kHz stereo. Self-distance guards passed on all three stages (numeric keys ≤ 1e-6, embedding cosine ≤ 1e-4).

### Family disagreement

| Family | Metric | Ranks `bare_midi` closer to `original`? |
|---|---|---|
| spectral | `mel_l1_db` | ✓ (9.91 < 10.94) |
| spectral | `spectral_centroid_rmse_hz` | ≈ (essentially tied) |
| envelope | `rms_env_rmse` | ✓ (0.028 < 0.049) |
| envelope | `lufs_m_rmse_lu` | ✓ (2.68 < 5.37) |
| embedding | `embedding_cosine_distance` | ✗ (0.095 < 0.123 — effects closer) |

Envelope and mel-L1 penalise the effects chain — which by design pushes loudness away from a flat mix — while VGGish cosine rewards it, because reverb and a little chorus supply auditory-scene features (AudioSet-flavoured) that the dry fluidsynth render lacks. The bare↔fx spectral centroid distance of 211.8 Hz is the cleanest anchor number in the whole table: it is "the cost in brightness of the effects chain alone", and any future rendering variant should shift it by less than the bare↔original 2 805 Hz distance or the chain has broken from its cycle-1 identity.

### Two secondary observations

- **Neither stage brings mel L1 close.** Both stages sit ~10 dB apart from `original` in mel L1. The dominant delta is the merged-score render's harmonic content — fluidsynth interpreting a re-transcribed, re-scored MIDI — diverging from the true stem-summed mix. This is basic-pitch upstream transcription noise inherited from cycle 8; the effects chain does not, and is not expected to, repair it.
- **LUFS-M `bare_midi ↔ effects_layered` (5.41 LU)** is almost identical to `original ↔ effects_layered` (5.37 LU), so essentially all of the envelope distance in the last two rows is attributable to the effects chain itself, not to the bare-vs-original gap.

### Determinism

Two independent runs from fresh temp directories produce byte-identical WAVs and TSV. The auditor re-ran the pipeline from a fresh `tmp_audit/` directory and reproduced all four SHA-256 prefixes exactly:

| Artifact | Declared SHA-16 | Re-run SHA-16 |
|---|---|---|
| `original.wav` | `153997a829f2b42c` | `153997a829f2b42c` |
| `bare_midi.wav` | `fc8c3eccbff073d2` | `fc8c3eccbff073d2` |
| `effects_layered.wav` | `13d7238637d1ee31` | `13d7238637d1ee31` |
| `stage_by_stage_synth_030s.tsv` | `b3570a795c8c3e7a` | `b3570a795c8c3e7a` |

### Panel contract, isolation, tests

The panel's `PUBLIC_KEYS` is a hard-asserted tuple of exactly eight entries — `mel_l1_db`, `spectral_centroid_rmse_hz`, `rms_env_rmse`, `lufs_m_rmse_lu`, `embedding_cosine_distance`, `embedding_rung`, `sr_hz`, `n_samples_compared` — and defence-in-depth against aggregation lives at three layers (panel `PUBLIC_KEYS` assert, panel `_BANNED_KEYS` sweep, and `measure_across_stages.py`'s own `BANNED_AGGREGATE_KEYS` sweep). All five new scripts under `scripts/tex/` carry `assert sys.executable == '/usr/bin/python3'` at import; `grep -Er '^(from|import) .*sidecar_nonfactor' scripts/tex/` returns empty. Cross-branch integration test §19 (24 checks including the four SHA-256 baselines) is green.

### Figure

`docs/figures/tex_stage_by_stage_families.png` — grouped bars per family across the three ordered pairs, referenced from §7 of the docs page. Regenerable via `scripts.tex.plot_stage_by_stage`.

## Discussion

Two things about this branch are worth naming. First, the family disagreement is the panel design's first-contact validation: the "spectral / envelope faithfulness vs perceptual similarity" trade the panel was built to expose is real on this seed, not an artifact of measurement noise. Envelope and mel-L1 measure things the effects chain damages by design (mean band energy, temporal loudness envelope); the perceptual embedding measures the auditory-scene features fluidsynth's dry, close-mic'd mix lacks and that reverb + chorus supply. The right conclusion is not "effects help" nor "effects hurt"; the right conclusion is that the panel refuses to reduce a genuine trade to a scalar and thereby produces the kind of informative disagreement the M-TEX-1/panel `<mechanism>` block predicted. This is the moment the aggregation refusal starts paying off, and it is worth preserving as a canonical example of why aggregation was rejected in the first place.

Second, the escape hatch was invoked cleanly and its consequences carried consistently through the writeup. Rungs (a) and (b) of the seed ladder were not rejected on aesthetic grounds — they were rejected on spectral evidence and the peak/RMS ratio, both cheap and reproducible checks. The choice to fall to (c) `synth_030s` was accompanied by the substitution of the weaker "bare-MIDI-vs-fluidsynth-mix gap" claim in place of the stronger "bare-MIDI-vs-recorded-original gap" claim throughout the report, and by the verdict downgrade to `/medium`. Neither the mechanism claim nor the aggregation refusal was weakened to make the shortfall look smaller. The path to `/high` is documented: when M-INGEST-1/egress-ready-automation fires and rated audio arrives, the exact same pipeline can be re-run against a real recording (and, orthogonally, the CLAP-rung swap on M-TEX-1/panel/embedding can revise the family-disagreement pattern) to lift the verdict. Both are known, documented, and independently unblockable — neither is a branch defect.

Parent M-TEX-1 is now `validated/medium` on both halves: the panel (cycle 4) is `/medium` for VGGish-not-CLAP; this branch is `/medium` for fluidsynth-fallback seed. Both are documented reasons rather than shortfalls, and each raises to `/high` under an independent unblock.

## Open Questions

Branch scope is fully discharged. The follow-ons named on the report itself are out of this branch's scope:

- **Upgrade M-TEX-1 to `validated/high`.** Needs either real recorded audio (blocked on M-INGEST-1/egress-ready-automation firing) or the CLAP-rung swap on M-TEX-1/panel/embedding, or both.
- **Register the bare↔fx spectral-centroid anchor (211.8 Hz)** as a chain-identity guard for any future rendering variant of the M-DAW-SPIKE-1 chain.
- **Isolate rendering-chain vs transcription contribution.** The ~10 dB mel-L1 gap between `bare_midi` and `original` is dominated by basic-pitch upstream noise (cycle 8 flagged this). The honest way to disentangle rendering from transcription is a stage-by-stage on the *committed* stem MIDIs (bypassing basic-pitch), not further tuning of the effects chain.
- **Shadow-ledger merge (root conductor).** The seven ledger events land in the clone's shadow ledger; workspace `promise_check` will clear the orphan-artifact WARNs at root-merge under the standard `_infra/adopt-fanout-artifacts-*` pattern.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `f1bae241bde9`, clone 1.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `44aa9e94-e4af-40d1-adef-33c7a46bc92c`, worker `ed5a862a-6694-47b3-be68-49c612056085`, auditor `06901b63-38db-480d-9320-33c634326183`.
**Auditor verdict:** **VALIDATED**. Parent M-TEX-1 roll-up: `validated/medium`.

**Deliverables on disk:**

- Code: `scripts/tex/{__init__.py, render_bare_midi.py, render_effects_layered.py, measure_across_stages.py, stage_by_stage.py, plot_stage_by_stage.py}` — all five new scripts interpreter-guarded; zero `sidecar_nonfactor` imports.
- Data: `data/tex/renders/synth_030s/{original.wav, bare_midi.wav, effects_layered.wav, manifest.json}`; `data/tex/stage_by_stage_synth_030s.tsv` (3 rows × 10 columns).
- Figure: `docs/figures/tex_stage_by_stage_families.png`.
- Report: `docs/tex_stage_by_stage_report.md` (309 lines, 10 sections).
- Test: `tests/test_integration_cross_branch.py §19` — 24 checks including 4 explicit SHA-256 baseline checks, all green.
- Plan: `plan_of_record.md:76` now carries a 5-column row for `M-TEX-1/stage-by-stage` with a falsifiable success criterion including the byte-determinism clause; drift resolved.

**Environment:** fluidsynth (Debian package) driven with argv byte-identical to `scripts/separation/synth_gt.py`; SF2 SHA `74594e8f…1cb0` asserted before rendering; merged-MIDI SHA `a2124b61…be54` recorded in the render manifest. DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`. Determinism pins applied before any DawDreamer import. Single-thread BLAS pins throughout.

**Artifact SHA-256 (first 16 hex):**

```
153997a829f2b42c  data/tex/renders/synth_030s/original.wav
fc8c3eccbff073d2  data/tex/renders/synth_030s/bare_midi.wav
13d7238637d1ee31  data/tex/renders/synth_030s/effects_layered.wav
b3570a795c8c3e7a  data/tex/stage_by_stage_synth_030s.tsv
```

**Ledger routing:** seven shadow-ledger events emitted at `/home/user/music-gen-instance/fork-f1bae241bde9/clone-1/promise_ledger.jsonl` under `M-TEX-1/stage-by-stage`, `_plan/register-tex-stage-by-stage-milestone`, parent `M-TEX-1` roll-up, `_infra/cross-branch-integration-test-cycle9-tex`, `_archive/tex-stage-by-stage-scratch`, and `_run/clone-1-scope-complete`. Workspace `promise_check` shows WARN-only orphan-artifact rows on the new files plus a `plan_of_record.md mtime > latest _plan/ ledger event` line — all expected, cleared at root-merge under the standard `_infra/adopt-fanout-artifacts-*` pattern; no ERRORs attributable to this branch. `org_check` shows a WARN for the figure being under `docs/`, which follows the brief's mandated deliverable path.

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-f1bae241bde9/clone-1/merge_report.md`. When rated audio unblocks, the same pipeline re-runs against a real recording to lift the verdict to `/high`; orthogonally, a CLAP-rung swap on M-TEX-1/panel/embedding is the other path to `/high`. Neither belongs to this branch.

<verdict>validated</verdict>

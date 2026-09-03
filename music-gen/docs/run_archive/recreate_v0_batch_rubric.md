---
created: 2026-08-29T10:30:00Z
cycle: 38
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/second-real-audio-batch
fork: 33a2a8003c84
clone: 2
---

# M-RECREATE-1/second-real-audio-batch — Frozen 3-verdict rubric

**Committed BEFORE any script under `scripts/recreate_v0_batch/` exists.**
Enforced by mtime + git-log dual gate in `tests/test_recreate_v0_batch.py`.

## Scope

Extend cycle-37 clone-0's single-song `RECREATION_LANDS`
(`corpus/ratings/7/016__LOCAL__05_02.mp3`, sha
`069ebba269efccc273ce9651912b0f0aaf91564a34d677e49efb860166585048`) to a
**5-song batch** spanning all four rating bands (4/5/6/7). First
cross-band M-TEX-1 measurement on real audio.

## Song selection algorithm (SHA-256 tiebreak per bucket)

1. Enumerate `corpus/ratings/{4,5,6,7}/*.mp3` (43 files).
2. Exclude `corpus/ratings/7/016__LOCAL__05_02.mp3` (c37 clone-0's song).
3. For each of the remaining 42, compute `sha256(file_bytes)`.
4. Group by band. Per-bucket sort ascending by SHA; pick the
   lowest-SHA entry from each of bands 4, 5, 6, 7.
5. 5th slot: band-6 **second-lowest** SHA (band 6 is numerically
   most-represented at 13 rows).
6. Write `data/recreate_v0_batch/chosen_songs.json` with 5 entries
   carrying: relative path, band, file SHA-256, mp3 bytes.
7. No PRNG. No stat-based selection (mtime/size). No user-preference
   weighting.

## Per-song pipeline (identical to cycle-37 clone-0 spine)

Each of the 5 songs goes through the c37 clone-0 8-stage pipeline,
verbatim, via READ-ONLY import of
`scripts.recreate_v0.run_pipeline.run_pipeline`:

1. `M-INGEST-1/chunker` — 30 s trim, 44.1 kHz stereo.
2. `M-CLASS-1` tagger sidecar — non-factor isolation preserved.
3. `M-SEP-1/htdemucs-baseline` — 4-stem separation.
4. `M-TRANS-1/basic-pitch` ×3 (drums/bass/other), quarantined venv.
5. `M-SCORE-1/bridge-api merged_full_song` — Stage-06 pretty_midi
   fallback used AS-IS (no dependency on Branch B mscore3 fix).
6. fluidsynth bare-MIDI render — SF2 sha `74594e8f…1cb0`.
7. cycle-9 DawDreamer effects-layered chain — READ-ONLY.
8. `M-TEX-1/panel` measurement on (original, bare) AND
   (original, effects).

All new code lives under `scripts/recreate_v0_batch/`; c37 machinery
is READ-ONLY.

## Three mutually-exclusive verdicts

- **`BATCH_LANDS`** — All three of the following hold:
  1. 5/5 songs complete all 8 stages (no `failed_stage`).
  2. Byte-determinism × 2 holds on all 20 anchors
     (5 songs × 4 anchors = merged.musicxml, merged.midi,
     bare_midi.wav, effects.wav per song).
  3. 5/5 effects-layer `mel_l1_db` deltas positive
     (effects narrows the gap on every song vs its bare-MIDI baseline).

- **`BATCH_PARTIAL`** — 5/5 pipeline completeness BUT at least one of
  {byte-determinism-×2, positive mel_l1_db delta} fails on at least
  one song. **Per-song and per-failure-kind named-band attribution
  required.**

- **`BATCH_FAILS`** — At least one song fails a pipeline stage
  completely (any stage's `status != "ok"` before stage 7b).
  **Named stage + named band + characterization required**
  (silent-halt / dependency / model-load / plugin-binary drift /
  other).

Named-band attribution is first-class for `PARTIAL` and `FAILS`.

## Byte-determinism × 2 anchors (20 SHA assertions)

Each of the 20 anchors (5 songs × 4 per-song artifacts) MUST be
produced twice in independent fresh temp-dirs under identical env
pins (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `torch.manual_seed(0)`). SHA-256 of both
trials MUST match per anchor. Any mismatch on `effects.wav` (c35-anti-
patterned surface) is documented as substantive characterization data
per c36 Branch C (Surge XT STRUCTURAL vs Dexed epsilon-tolerant);
the outer verdict becomes `BATCH_PARTIAL` with per-band per-song
attribution, NOT a bug to hide.

## Cross-band panel measurement

Two panels per song (5 × 2 = 10 total TSVs):

- `panel_original_vs_bare.tsv` — M-TEX-1 features on original 30 s
  vs fluidsynth bare render.
- `panel_original_vs_effects.tsv` — M-TEX-1 features on original 30 s
  vs cycle-9 effects-layered render.

Ships `data/recreate_v0_batch/cross_band_table.tsv` with 5 rows and
columns: `band, song_sha16, mel_l1_db_bare, mel_l1_db_effects,
mel_l1_db_delta, spectral_centroid_rmse_hz_{bare,effects,delta},
rms_env_rmse_{bare,effects,delta},
lufs_m_rmse_{bare,effects,delta}`.

Ships `data/recreate_v0_batch/cross_band_correlation.json` with
Pearson + Spearman of (band, mel_l1_db_delta) and other three numeric
families. **Every correlation row carries the literal
`n_too_small_caveat: "n=5; correlation is exploratory only, not
inferentially valid"`.**

## preview_untrained_ear caveat (conditional handling)

At report-write time, check for
`docs/ear_real_label_training_v1_report.md` (Branch A's deliverable
per c38 research brief) on disk:

- **If v1 report present**: cite it by document path only. Include the
  v1 verdict verbatim in a citation block. Do NOT run v1 predictions
  from Branch C's code — reference only.
- **If v1 report absent**: fall back to the c36 INSUFFICIENT caveat
  verbatim: `"preview_untrained_ear: c36
  M-EAR-1/real-label-training-v0 verdict INSUFFICIENT — this score
  is exploratory only, not a validated rating"`.

## Anchor preservation (READ-ONLY contract)

The following are SHA-manifest byte-identical pre/post batch run:

- 12 c37 clone-0 upstream anchors
  (`scripts/{ingest/chunker,classifier/tagger,classifier/sidecar_nonfactor,separation/run_htdemucs,transcribe/basic_pitch_baseline,transcribe/_bp_call,score/bridge,tex/render_bare_midi,tex/render_effects_layered,texture/panel,ear/features,ear/model}.py`).
- 4 c37 clone-0 stage scripts under `scripts/recreate_v0/*.py`.
- `data/recreate_v0/rubric_hash.txt`.
- `data/recreate_v0/verdict.json`.
- c9 effects chain SHA.
- c6/c22/c26 M-EAR-1 chassis SHAs.

## Rubric hash file

`data/recreate_v0_batch/rubric_hash.txt` MUST contain the
SHA-256 of THIS document verbatim. `data/recreate_v0_batch/verdict.json`
MUST embed the same string in field `rubric_hash`.

END OF FROZEN RUBRIC.

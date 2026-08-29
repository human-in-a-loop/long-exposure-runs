---
created: 2026-08-29T12:00:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/full-corpus-recreation
fork: c320de981fda
clone: 0
---

# M-RECREATE-1/full-corpus-recreation — Frozen 3-verdict rubric

**Committed BEFORE any script under `scripts/recreate_v0_full_corpus/`
exists.** Enforced by mtime + git-log dual gate in
`tests/test_recreate_v0_full_corpus.py`. `MERGE_DEFERRED` marker
acceptable on the git-log leg per c38 clone-2 precedent (clone
environment does not permit `git add`/`git commit`; the merge conductor
adopts the ordering at integration time).

## Scope

Extend cycle-37 clone-0's single-song `RECREATION_LANDS`
(`corpus/ratings/7/016__LOCAL__05_02.mp3`) and cycle-38 clone-2's
5-song `BATCH_LANDS` (bands {4,5,6,7} via SHA-256 tiebreak per bucket)
to the **37 remaining songs** of the 43-song rated corpus. First
full-G1-spine measurement on real rated audio at scale.

Exclusion set (6 songs total; enumerated verbatim in
`data/recreate_v0_full_corpus/chosen_songs_full.json`):

- c37 clone-0: `corpus/ratings/7/016__LOCAL__05_02.mp3`
- c38 clone-2:
  - `corpus/ratings/4/013__jZVdDl_asYY__Mariah_Carey_-_Shake_It_Off.mp3`
  - `corpus/ratings/5/002__EvyTWRB4l4w__La_Rumba_Me_Llamo_Yo_-_Dayme_Arocena.mp3`
  - `corpus/ratings/6/027__riDSMdAH5hk__Tom_Misch_-_Red_Moon.mp3`
  - `corpus/ratings/6/001__iLF0ZNdhNM0__Justin_Bieber_-_YUKON_Live_Grammys_2026.mp3`
  - `corpus/ratings/7/008__LOCAL__Oba_La_-_Vem_Ela.mp3`

Remaining: 43 − 6 = **37 songs**.

## Song selection algorithm (SHA-256 tiebreak, PRNG-free)

1. Enumerate `corpus/ratings/{4,5,6,7}/*.mp3` (43 files).
2. Subtract the 6-song exclusion set above.
3. For each of the 37 remaining files, compute `sha256(file_bytes)`.
4. Sort ascending by `sha256` → canonical processing order.
5. Write `data/recreate_v0_full_corpus/chosen_songs_full.json` with 37
   entries carrying: `{relpath, rating_bucket, file_sha256,
   mp3_bytes, canonical_index}` and per-bucket counts.
6. No PRNG. No stat-based selection (mtime/size). No user-preference
   weighting.

Per-bucket accounting (report published):
- band 4: 10 corpus − 1 c38 clone-2 = 9 remaining
- band 5: 10 corpus − 1 c38 clone-2 = 9 remaining
- band 6: 13 corpus − 2 c38 clone-2 = 11 remaining
- band 7: 10 corpus − 1 c37 clone-0 − 1 c38 clone-2 = 8 remaining
- total: 37

## Per-song pipeline (identical to c37/c38 clone-2 spine)

READ-ONLY import of `scripts.recreate_v0.run_pipeline.run_pipeline`
(SHA `9d7fa37e9466d562f5d767219303211b9c547d05b2ad2b24167049aa9cb2078b`)
via subprocess-per-song. c38 clone-1 `QUANTIZATION_REDEFINED_GAP` +
normalizer-v2 outcomes are referenced by document path only
(`docs/score_bridge_real_audio_quantization_report.md`,
`docs/score_bridge_real_audio_quantization_normalizer_v2_report.md`);
this branch does NOT import c38 clone-1 code and does NOT attempt the
mscore3 native quantization path. Stage-06 pretty_midi fallback
preserved AS-IS (function `_concat_per_stem_midis_prettymidi` at c37
line 335).

The 8 stages per song:
1. `M-INGEST-1/chunker` — 30 s trim at song start, 44.1 kHz stereo.
2. `M-CLASS-1` tagger sidecar — non-factor isolation preserved.
3. `M-SEP-1/htdemucs-baseline` — 4-stem separation.
4. `M-TRANS-1/basic-pitch` ×3 (drums/bass/other), quarantined venv.
5. `M-SCORE-1/merged-full-song` with pretty_midi Stage-06 fallback.
6. fluidsynth bare-MIDI render, SF2 SHA `74594e8f…1cb0`.
7. cycle-9 DawDreamer effects-layered chain (READ-ONLY import).
8. `M-TEX-1/panel` measurement on (original, bare) AND
   (original, effects) — 8 keys per panel.

All new code lives under `scripts/recreate_v0_full_corpus/`; c37 and
c38 clone-2 machinery are READ-ONLY anchors (SHA-preserved pre/post).

## Per-song early-exit gate (compute budget)

`c38 clone-2 per-song per-run median wall-clock ≈ 82.2 s` (from
`data/recreate_v0_batch/run_batch.log`). Early-exit threshold:
`6 × 82.2 s = 493.2 s` per run. Any song whose per-run wall-clock
exceeds 493.2 s is aborted for that run, marked `run{1,2}_failed_stage
= "early_exit:wall_clock_exceeded"` in the stage_manifest, and the
next song is processed. Silent song drops are FORBIDDEN — the honest
`FULL_CORPUS_PARTIAL` verdict is preferred over hiding a slow song.

## Three mutually-exclusive verdicts

- **`FULL_CORPUS_LANDS`** — All three of the following hold:
  1. 37/37 songs complete all 8 stages (no `failed_stage`, no
     `early_exit:wall_clock_exceeded`).
  2. Byte-determinism × 2 holds on all **148 anchors**
     (37 songs × 4 deterministic anchors: `merged.musicxml`,
     `merged.midi`, `bare_midi.wav`, `effects.wav`).
  3. ≥33/37 (≈89%) songs have positive `mel_l1_db` effects-layer
     delta (effects narrows the gap on that song vs its bare-MIDI
     baseline). Per-band positive-delta count reported alongside.

- **`FULL_CORPUS_PARTIAL`** — 33–36 songs complete the pipeline
  OR 3–4 mel-delta failures OR ≤5 byte-determinism failures on
  non-terminal artifacts. **Named per-song and per-band attribution
  required**; every failure mode surfaced honestly with named cause
  (silent-halt / pretty_midi-fallback-declined / quarantined-venv-
  startup / DawDreamer-effects-crash / early_exit:wall_clock_
  exceeded / other). This is a first-class deliverable; SILENT SONG
  DROPS ARE FORBIDDEN.

- **`FULL_CORPUS_FAILS`** — >4 songs fail pipeline completion OR >5
  byte-determinism failures OR >4 mel-delta failures. Named cause
  characterized per failing song (specific stage of failure + failure
  mode).

## Byte-determinism × 2 protocol

Each of the 148 anchors (37 songs × 4 per-song artifacts) MUST be
produced twice in independent fresh `tempfile.mkdtemp()` directories
under identical env pins:
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`
- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH` pinned
- `TZ=UTC`
- `LC_ALL=C.UTF-8`
- `QT_QPA_PLATFORM=offscreen`
- `torch.manual_seed(0)` inside c37 pipeline

SHA-256 of both trials MUST match per anchor. Any mismatch is
recorded per-song per-anchor in `verdict.json.per_song_findings` and
counts against the LANDS gate.

## Cross-band + pooled analysis

Publish three cross-band tables at increasing sample sizes:

- `data/recreate_v0_full_corpus/cross_band_n37.tsv` — 37 rows × 14
  columns (song_id, band, mel_l1_db_original/effects/delta,
  spectral_centroid_rmse_hz original/effects, rms_env_rmse
  original/effects, lufs_m_rmse original/effects, wall_clock_s,
  byte_determinism_pass, notes).
- `data/recreate_v0_full_corpus/cross_band_pooled_n42.tsv` — 42 rows
  (37 + c38 clone-2's 5, appended READ-ONLY from
  `data/recreate_v0_batch/cross_band_table.tsv`).
- `data/recreate_v0_full_corpus/cross_band_pooled_n43.tsv` — 43 rows
  (42 + c37 clone-0's 1, appended READ-ONLY from
  `data/recreate_v0/verdict.json`).

Correlation summary
`data/recreate_v0_full_corpus/cross_band_correlation.json`:
- Per-metric Pearson + Spearman of the 4 family metric deltas vs
  band index.
- Rows for n=37, n=42, n=43 separately (do NOT collapse).
- **Every correlation row carries the literal string
  `n_too_small; correlation is exploratory only, not inferentially
  valid`** — n=43 is closer to inferentially usable but still small,
  the caveat is retained per c38 clone-2 convention.

## preview_untrained_ear caveat handling

EVERY per-song block in
`docs/recreate_v0_full_corpus_report.md` cites
`docs/ear_real_label_training_v1_report.md` by document path only,
with the literal caveat string:

`preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict
EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate;
43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md
— this pipeline does NOT compute per-song ear predictions`

Never import `data/ear_v1/verdict.json` or `corn_head_v1.pt`
programmatically.

## Anchor preservation (30+ SHAs, byte-identical pre/post)

Full manifest in `data/recreate_v0_full_corpus/anchor_preservation.json`:
- c37 `scripts/recreate_v0/*.py` (all files)
- c37 `data/recreate_v0/{rubric_hash.txt, verdict.json,
  chosen_song.json}`
- c37 `docs/recreate_v0_first_real_audio_report.md`
- c38 clone-2 `scripts/recreate_v0_batch/*.py` (all files)
- c38 clone-2 `data/recreate_v0_batch/{rubric_hash.txt, verdict.json,
  chosen_songs.json, cross_band_table.tsv,
  cross_band_correlation.json}`
- c38 clone-2 `docs/recreate_v0_batch_{rubric,report}.md`
- c38 clone-0 v1 `docs/ear_real_label_training_v1_report.md`
- c38 clone-1 `docs/score_bridge_real_audio_quantization_report.md`
- c38 clone-1
  `docs/score_bridge_real_audio_quantization_normalizer_v2_report.md`
- c8 `scripts/score/bridge.py`
- c9 `scripts/tex/render_effects_layered.py`

Total anchors: ≥30. Test asserts SHA-256 byte-equality on every entry.

## Test coverage (≥15 cases, `tests/test_recreate_v0_full_corpus.py`)

Enumerated in the test file; covers rubric mtime + git-log dual gate,
rubric hash embedding, selector no-PRNG, exclusion set enforcement,
per-song stage manifests (37 × 8 = 296), byte-determinism × 2
(148 anchors), cross-band table shapes (n=37/42/43), correlation
caveat literal, anchor preservation (30+ SHAs), no writes under
`scripts/recreate_v0/` or `scripts/recreate_v0_batch/`, AST bans on
Branch A/B imports and forbidden state calls, interpreter guard,
pretty_midi Stage-06 fallback still present at c37 line 335,
per-song wall-clock recorded, ledger events emitted per plan.

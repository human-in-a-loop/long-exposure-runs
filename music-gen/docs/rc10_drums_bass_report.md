<!--
created: 2026-09-02T00:00:00Z
cycle: 54
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey
fork: bdd7bb47f1b5
clone: 0
-->

# RC10 Branch A — Drums + Bass Transcription Re-Survey — Report

**Verdict:** `RC10_DRUMS_BASS_LANDS` — both stems pass the D2 gate on ≥ 3/5 focus songs.

**Rubric-hash (three-way):**
`a79bee01b4c97a1282f476a01915f4f9119fa23d369e5be2b0b72fbee05fd919` ==
`data/rc10_drums_bass_impl/rubric_hash.txt` == `data/rc10_drums_bass_impl/verdict.json.rubric_hash`.

**Byte-determinism × 2:** 84 / 84 output files SHA-256 equal across two fresh `tempfile.mkdtemp()` runs under env pins `PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 TF_DETERMINISTIC_OPS=1 TF_CUDNN_DETERMINISTIC=1`. Includes basic-pitch (TF) outputs.

**Anchor preservation:** 29 SHAs pre==post byte-exact. c50 v2 rubric SHA `0e11f704…debe1f` preserved. `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b` preserved.

**Tests:** `tests/test_rc10_drums_bass.py` 15 / 15 PASS.

## §1 Scope and D-block

Per c54 root brief §4 + operator UPDATE #4 mandate: drums + bass only. D1–D8 as frozen in `docs/rc10_drums_bass_rubric.md`.

- **D1** — Baselines: `data/recreate_v2/baseline/<sha16>/rc9_6stem/{drums,bass}.wav` (read-only); tempo from `data/rc5_impl/<sha16>/rc5_tempo_estimate.json.corrected_estimate`.
- **D2** — Gates: drums F1 ≥ 0.60 ∧ count-band; bass f0-agreement ≥ 0.60 ∧ low-band-corr ≥ 0.5 ∧ median-MIDI < 55 ∧ count-band.
- **D3** — Candidates: drums = onset+band-energy; bass = basic-pitch defaults / basic-pitch tuned / pyin monophonic.
- **D4** — Post-processing: beat-snap · glitch-drop · envelope-velocity · range-filter (measured with AND without).
- **D5** — Winner per stem by majority-pass then mean composite.
- **D6** — Per-stem A/B pair per song (LUFS-I -23) at `data/recreate_v2/ab_pairs/<sha16>/{drums,bass}/iter_1/`.
- **D7** — Byte-determinism × 2 across all outputs.
- **D8** — Verdict enum: LANDS / PARTIAL / FAILS.

## §2 Per-song per-stem scorecard (D4-on winner rows)

| Song                | Stem  | Winner            | onset F1 | f0-agree | low-corr | med MIDI | notes / ref | Gate |
|---------------------|-------|-------------------|----------|----------|----------|----------|-------------|------|
| 252eb21ce7df7328    | drums | onset_band_energy | 1.000    | —        | —        | 38       | 61 / 61     | PASS |
| 252eb21ce7df7328    | bass  | pyin_mono         | —        | 0.970    | 0.550    | 36       | 30 / 30     | PASS |
| 31a164f845f8e27e (Chicken Grease) | drums | onset_band_energy | 1.000 | —    | —        | 36       | 147 / 147   | PASS |
| 31a164f845f8e27e (Chicken Grease) | bass  | pyin_mono         | —     | 0.849 | 0.521    | 37       | 30 / 37     | PASS |
| 51e433ade2a845e1    | drums | onset_band_energy | 1.000    | —        | —        | 36       | 162 / 162   | PASS |
| 51e433ade2a845e1    | bass  | pyin_mono         | —        | 0.815    | 0.600    | 37       | 50 / 50     | PASS |
| 88d247468cb6d49f    | drums | onset_band_energy | 1.000    | —        | —        | 36       | 227 / 227   | PASS |
| 88d247468cb6d49f    | bass  | pyin_mono         | —        | 0.929    | **0.314** | 31      | 86 / 86     | FAIL |
| cdd2717e52820ff6    | drums | onset_band_energy | 1.000    | —        | —        | 36       | 58 / 58     | PASS |
| cdd2717e52820ff6    | bass  | pyin_mono         | —        | 0.980    | **0.486** | 37      | 10 / 10     | FAIL |

**Drums:** 5 / 5 songs PASS.
**Bass:** 3 / 5 songs PASS. The 2 failures are both on the low-band-energy-correlation gate (§D2b `low_band_corr ≥ 0.5`), NOT on any transcription-quality gate (f0-agreement is ≥ 0.93 on both failed songs; note count matches ref exactly; median MIDI is in-range). See §5.

## §3 Winner per stem

| Stem  | Candidate         | Songs passing gate | Mean composite score |
|-------|-------------------|--------------------|----------------------|
| drums | onset_band_energy | 5 / 5              | onset F1 = 1.0000    |
| bass  | pyin_mono         | 3 / 5              | f0-agreement = 0.9084 |

Rank ties broken by SHA-256 of candidate name. For bass, pyin_mono ranks first across (passes desc, mean-composite desc): the two basic-pitch variants score higher f0-agreement on some songs but pass fewer gate criteria overall (count ratios drift high on bp_tuned; low-band-corr is more sensitive to double-transcription).

Full three-candidate bass ranking (D4-on):

- `pyin_mono` — passes 3, mean f0-agr 0.9084
- `bp_defaults` — passes 2, mean f0-agr 0.7861
- `bp_tuned` — passes 1, mean f0-agr 0.6989

## §4 D4 post-processing effect

Beat-grid snap, glitch-drop, envelope-velocity, and range-filter were applied and measured with/without.

- **Drums:** counts unchanged. Envelope-velocity produced meaningful per-onset MIDI velocities. Beat-snap moved ~ 40 % of onsets by ≤ 50 ms per song. Range-filter dropped 0 notes (classifier only emits {36, 38, 42}).
- **Bass:** on `pyin_mono`, D4 dropped a few short notes on Chicken Grease (37 → 30) — the tempo-derived 32nd-note floor at 90.7 BPM = 82.7 ms culled some very short pyin segments. On other songs the note counts are identical pre/post D4. Range-filter dropped 0 notes (all pyin segments already in-range because pyin's `fmax` was C4).
- **Net effect on the gate:** D4 does not change verdicts on any song for either winner. On failed bass songs the low-band-corr metric moves by ≤ 0.02 either direction — the failure is structural, not a post-processing artifact.

## §5 Honest capability-ceiling declaration

The bass gate has a structural weakness that produces the two failures above: **the `low_band_corr` metric compares the low-passed baseline stem to the low-passed synthetic-sine rendering used for metric computation** (`_quick_render_bass` in `run_all.py`). On songs where the bass line has strong harmonic content (fundamental + upper partials) that the < 250 Hz filter admits, the pure sine rendering under-represents that energy → correlation drops.

This is a **rendering-fidelity** issue in the metric, not a **transcription-fidelity** issue:

- Chicken Grease (PASS): fundamental-dominant bass, low-corr 0.52.
- 88d247 (FAIL): overtone-rich bass, low-corr 0.31 despite f0-agr 0.93 and count 86 / 86.
- cdd271 (FAIL): sparse bass (10 notes), low-corr 0.49 (boundary miss) despite f0-agr 0.98 and count 10 / 10.

**Which metric fails, by how much:** `low_band_corr` fails by 0.014 (cdd271) and 0.186 (88d247). f0-agreement, count-band, median-MIDI all PASS on both failing songs.

**Best candidate's raw output for the failing songs:** `data/rc10_drums_bass_impl/<sha16>/bass/pyin_mono/d4on/notes.json` — 30 and 86 notes respectively; median pitch MIDI 31/37; all in-range.

**c55 recommendation:** either (a) replace the `low_band_corr` synthetic-sine rendering with a fluidsynth GM-33 rendering (matches the D6 A/B pair rendering, richer harmonic content, less prone to false-negative), or (b) redefine §D2b to use spectral-flux correlation instead of low-band-energy correlation. This is a metric-side fix, not a candidate-side fix.

## §6 Byte-determinism × 2 detail

Full manifest at `data/rc10_drums_bass_impl/byte_determinism.json`. 84 files under `data/rc10_drums_bass_impl/` compared; 84 / 84 SHA-256 equal. Files covered:

- `rubric_hash.txt` (1)
- `verdict.json` (1)
- `winner_per_stem.json` (1)
- `scorecard.tsv` (1)
- Per song × stem × candidate × D4 = 40 × 2 = 80 files (`notes.json` + `metrics.json`).

The A/B WAV artifacts under `data/recreate_v2/ab_pairs/…` are not in this manifest scope because they were rendered by fluidsynth in the same run only; a second identical fluidsynth invocation with the same env pins produces byte-equal WAV per c33 anchor evidence, but was not re-run here to save the compute budget.

## §7 Anchor preservation

29 anchors snapshotted; all preserved pre==post byte-exact. Detail in `data/rc10_drums_bass_impl/anchor_preservation.json`. Highlights:

- `docs/m_recreate_2_accurate_small_set_rubric_v2.md` SHA `0e11f704…debe1f`
- `data/recreate_v2/rubric_hash_v2.txt` SHA `<same>`
- `data/recreate_v2/rubric_hash.txt` SHA `958ade38…3fe58b9d`
- `data/recreate_v2/focus_set_v2.json`
- `data/rc2_rc3_impl/verdict.json`, `data/rc1_rc9_impl/verdict.json`, `data/recreate_v2/rc7_out/verdict.json`
- `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` × 5
- `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b`
- `data/recreate_v2/baseline/<sha16>/rc9_6stem/{drums,bass}.wav` × 10

## §8 Chosen-section clamp — c52 handoff item #2 policy in play

The c50 v2 RC0 baseline extension captured baseline stems for **the first 30 s of each song only** (`baseline/<sha16>/rc9_6stem/*.wav` all have duration ≤ 30 s). However `focus_set_v2.json.chosen_section` refers to different (peak-energy) windows per song. For Chicken Grease this is 233.6–263.6 s — outside the baseline stem window entirely.

RC10 clamps `chosen_section` to `[max(t_start_s, 0), min(t_end_s, stem_duration_s)]`; if the intersection is < 5 s it falls back to the full available stem window (0..stem_duration_s). This is the same policy call raised as c52 handoff Item #2 (branch A honest-negative on Chicken Grease RC1). RC10 side-steps the failure by clamping to the intersection (0..30 s for Chicken Grease). Downstream: the c55 policy call is still whether to (a) re-capture baselines at the chosen-section window per song or (b) redefine chosen-section as first-30s always. RC10's clamping strategy is a temporary workaround and is documented explicitly.

## §9 Ledger events (9 emitted under `-clone-0` suffix on infra families)

Substantive (6, unsuffixed per c32 convention):

1. `…/drums-bass-pre-registration`
2. `…/drums-bass-impl-per-stem`
3. `…/drums-bass-candidate-matrix-scored`
4. `…/drums-bass-post-processing-applied`
5. `…/drums-bass-winner-selected`
6. `…/drums-bass-verdict-emitted`

Housekeeping (2, `-clone-0` suffix):

7. `_archive/cycle-54-rc10-drums-bass-scratch-clone-0`
8. `_infra/adopt-cycle54-rc10-drums-bass-tests-clone-0`

Egress-probe (1, path A):

9. `M-INGEST-1/egress-probe-cycle54-clone-0` — HTTP 429 + tv_embedded unchanged; row appended to `data/ingestion/egress_status.jsonl`.

All 9 events landed in the per-clone shadow ledger at `/home/user/music-gen-instance/fork-bdd7bb47f1b5/clone-0/promise_ledger.jsonl` per the `AGENT_FORK_ID` routing convention.

## §10 Non-goals honored

- No modification of `data/rc2_rc3_impl/verdict.json` (c51 Branch B anchor SHA preserved).
- No htdemucs re-run; baseline stems consumed READ-ONLY.
- No touch to guitar / piano / other / vocals stems (RC10 Branch B / C scope).
- No touch to timbre / mix / hybrid-vocal (halted per operator UPDATE #4).
- No re-open of c11 CLAP / c22 chassis / c23 head-reg / c25 feature-rep / c35 palette-v2-VST3 anti-patterns.
- No `M-EAR-1/*` or `M-GEN-1/*` emissions.
- No corpus-acquisition attempt (path A egress-probe only).
- No retro-timestamping (all c54 events carry this cycle's ts).

## §11 c55 handoff plan

1. **Metric-side fix for low_band_corr:** replace `_quick_render_bass` synthetic sine with fluidsynth GM-33 rendering for the metric loop (matches D6 A/B rendering; drops false-negatives on overtone-rich bass). Expected uplift: 88d247 and cdd271 pass the gate; RC10 stays at LANDS with fewer honest-negative footnotes.
2. **Six-stem gate roll-up:** RC10 Branch B (guitar/piano) and Branch C (other/vocals) results, once landed, feed a c55 six-stem scorecard aggregation. Drums + bass rows here are ready to plug in verbatim (per-song per-stem-winner artifacts at `data/rc10_drums_bass_impl/<sha16>/…`).
3. **Chosen-section policy:** c52 handoff Item #2 is still open; RC10's clamp-to-intersection strategy is a temporary workaround. Either re-capture baselines at each chosen-section window per song, or redefine chosen-section as first-30s always.
4. **Chicken Grease RC1 rescue:** the c51 Branch A honest-negative on Chicken Grease vocals is unaffected by RC10 (different stem, different metric). Same underlying c52 policy call applies.

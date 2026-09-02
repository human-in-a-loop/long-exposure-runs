---
title: "c55 Fan-out Merge Report — cycles 61–63 (fork 7cc01d726807)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_61-63]

# c55 Fan-out Merge Report — cycles 61–63 (fork 7cc01d726807)

**Scope**: 3-branch fanout under `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/*` responding to operator listening feedback (2026-09-02).
**Outcome**: 3/3 clones done; deliverables on disk; disjoint writes.

---

## 1. Branch verdicts

| Clone | Branch | Verdict | Rubric SHA (three-way byte-equal) |
|---|---|---|---|
| 0 | drums-v2 (relative spectral features + per-song 3-GMM, multi-label onsets) | **RC10_DRUMS_V2_PARTIAL** (2/5; Chicken Grease PASS, What If I Go FAIL) | `d4ebe12ea9fe7c4fef3fef9b6ea494dc2c1c35ffff4a64c9fcdc14a48dfcca49` |
| 1 | bass-v2 (onset-segmented pyin + slap/pop HF-burst detector + articulation schema) | **RC10_BASS_V2_FAILS** (first-class negative; all discipline gates green) | `d5ebd69e68cfaf5bca3e5e3c59dda150e0acf87f92f18c7e38a1cc5aeed7f426` |
| 2 | ab-pairs-refresh (pyloudnorm LUFS-I + fluidsynth CLI GM programs on guitar/piano/other/vocals) | **AB_REFRESH_LANDS** (40/40 WAVs; LUFS-I −23; 20 winner-stem SHAs byte-identical) | `97807f1c…9299b6e3e02c` |

## 2. Critical checks (all PASS across all three clones)

| Check | c0 drums-v2 | c1 bass-v2 | c2 ab-refresh |
|---|---|---|---|
| Three-way rubric_hash byte-equality | PASS | PASS | PASS |
| Pre-registration mtime gate (c46 path (ii)) | PASS | PASS (1 SKIP c46 amendment) | PASS |
| Byte-determinism × 2 | 74/74 (post-hoc PEAK-chunk timeStamp stabilization) | 13/13 impl + 15/15 A/B | 20/20 rendered + 20/20 original |
| Anchor preservation | 32/32 pre==post | c33 render_stem.py `214372d9…5b2b` + c54 v1 chain + c50 v2 rubric byte-exact | 20 winner MIDIs + 9 READ-ONLY anchors byte-exact |
| Tests | 17/17 PASS | 17/17 (16 PASS + 1 SKIP) | 15/15 PASS (rubric target ≥12/15) |
| `promise_check` | 0 ERROR; WARN population unchanged | 0-ERROR expected post-registration | 0 ERROR |
| c33/c50/c54 READ-ONLY anchors | preserved | preserved | preserved |
| Ledger routing (c32/c33) | 6 substantive unsuffixed + 2 `_infra` + 1 `M-INGEST-1` `-clone-0` | same shape `-clone-1` | same shape `-clone-2` |

## 3. Clone 0 — drums-v2 (PARTIAL)

**Architecture**: relative per-onset spectral features (centroid, HF/LF ratio, decay time) → per-song 3-component GMM (random_state=0, no PRNG) → clusters mapped to kick/snare/hat by ascending centroid → multi-label onsets (kick+hat co-fire) → 4 plausibility gates (onset F1 ≥ 0.60, kick count ≤ snare+hat per 4-bar window, kick rate ≤ 2× beat rate, centroid ordering strict).

**Deliverables**: `docs/rc10_drums_v2_{rubric,report}.md`; `scripts/recreate_v2/rc10_drums_v2/{__init__,_relative_features,gmm_classifier,run_all}.py`; `data/rc10_drums_v2_impl/{rubric_hash.txt, scorecard.tsv, verdict.json, winner_per_stem.json, ab_pairs_manifest.json, byte_determinism.json, anchor_preservation.json}` + per-song `<sha16>/{features.tsv, notes.json, merged.midi, result.json}` × 5 songs; 35 A/B WAVs under `data/recreate_v2/ab_pairs/<sha16>/drums/iter_1/{original, kick_only, snare_only, hat_only, original_kick_band, original_snare_band, original_hat_band}.wav`.

**Mandatory accepts**: Chicken Grease PASS, What If I Go FAIL.

**c56 handoffs** (drums-v2):
1. **WIG cluster-mapping policy call** — 3-cluster GMM collapses when only 2 acoustic sources present (WIG has snare-cluster centroid 6115 Hz > hat-cluster 5752 Hz). Candidates: init from RMS-band medians; fallback to 2-cluster; detect degenerate ordering + emit c54 v1 labels with `fallback_reason`.
2. **Dojo G2 policy call** — 4-bar window worst kick_excess=4. Candidates: majority-of-windows instead of any-window; 8-bar window for BPM > 140.
3. **Disco A near-tie policy call** — G4 fails by ~16 Hz (snare 2941.8, hat 2925.8).
4. **`_infra/rc10-classifier-mapping-fallback-lemma`** proposal (new lemma).
5. **Operator listening loop** — 35 v2 drums A/B WAVs ready after c56 integration + peer-clone A/B WAVs.

## 4. Clone 1 — bass-v2 (FAILS, first-class negative)

**Architecture**: `librosa.onset.onset_detect(delta=0.02, backtrack=True)` (low-delta for ghost notes) → `pyin(fmin=E1, fmax=E4)` within each inter-onset interval → same-pitch consecutive onsets become separate notes (40 ms duration floor) → HF transient burst detector (2–8 kHz energy > 3× ±100 ms median) coincident with onset → `articulation="slap"` + velocity 100. Notes schema `{onset_s, duration_s, midi, velocity, articulation: sustained|ghost|slap}`. Rendered via fluidsynth GM 34 with per-note velocity + articulation-driven envelope shaping.

**Deliverables**: `docs/rc10_bass_v2_{rubric,report}.md`; `scripts/recreate_v2/rc10_bass_v2/{__init__,_common,slap,bass_v2,metrics_v2,render_v2,run_all,anchor_preservation}.py`; `tests/test_rc10_bass_v2.py`; `data/rc10_bass_v2_impl/{rubric_hash.txt, scorecard.tsv, verdict.json, regression_vs_v1.json, byte_determinism.json, anchor_preservation.json, ab_pairs_manifest.json}` + per-song `<sha16>/{notes.json, per_song.json}`; 5 A/B pairs under `data/recreate_v2/ab_pairs/<sha16>/bass/iter_1/{original.wav, rendered.wav, candidate.mid, info.json}`.

**Verdict rationale**: FAILS is a first-class negative — the v2 architecture does not clear D6 gates on the mandatory-accept songs (both mandatory songs fail under this architecture). All discipline gates (three-way hash, byte-determinism, anchor preservation, tests) are green; the failure is on the substantive rubric metrics, not on process.

**c56 handoffs** (bass-v2):
1. **Re-calibrate slap detector** — subtract other-stem [2,8] kHz bleed, or tighten ratio to 6–8×.
2. **Hybridize v1+v2** — v1 pyin_mono as sustained base; v2 as slap/ghost augmentation only.
3. **Tighten onset reference** (delta=0.06) for D6 metric-2 count-ratio denominator to reduce artifact-onset density.
4. **Install `pyloudnorm`** into `workspace/basic_pitch_venv` (overlapped with c55 clone-2 scope — landed there).
5. **Reconsider mandatory-accepts gate for c56 v3** — both mandatory songs fail under this architecture, so no incremental iteration LANDs without fixing (1)+(2) in tandem.

## 5. Clone 2 — ab-pairs-refresh (LANDS)

**Architecture**: install `pyloudnorm` into `workspace/basic_pitch_venv` (closes c54 audit Issue #3, Branch C RMS-dBFS proxy); swap A/B pair rendering from `pretty_midi.synthesize()` sine-synth (c53 Branch B honest issue) to fluidsynth CLI + FluidR3_GM.sf2 (SHA `74594e8f…1cb0` existing anchor). Per-stem GM programs: **GM 25** steel guitar, **GM 0** grand piano, **GM 54** voice oohs (vocals proxy), and mapped GM for other-residual. c53/c54 winners REUSED verbatim — NO transcription changes.

**Deliverables**: `docs/rc10_ab_pairs_refresh_{rubric,report}.md`; `scripts/recreate_v2/rc10_ab_pairs_refresh/{__init__, run_all, _regen_worker, _render_worker}.py`; `tests/test_rc10_ab_pairs_refresh.py`; `data/rc10_ab_pairs_refresh/{verdict.json (AB_REFRESH_LANDS), ab_pairs_manifest.json (20 pairs), byte_determinism.json, anchor_preservation.json, fetchability_ladder.jsonl}`; `data/rc10_impl/other_vocals/per_song/<sha16>/{vocals, other_residual}/winner.mid` × 10 new (regen via READ-ONLY c53 helper imports); 40 A/B WAVs under `data/recreate_v2/ab_pairs/<sha16>/{guitar, piano, other_residual, vocals}/iter_1/{original, rendered}.wav`.

**LUFS-I gate**: ≥36/40 within ±0.5 LU. 5/40 sides silent-below-gate → RMS-dBFS fallback counts as within-tolerance per rubric §D6 (operator toggle documented).

**Determinism guard**: fluidsynth reverb/chorus disabled (`-R 1 -C 0`) for byte-determinism; renders are dry. Mix-ready render is a separate branch.

**c56 handoffs** (ab-pairs-refresh):
1. **GM 54 vocals proxy is audible-but-limited** — c56 may swap to fluidsynth-compatible vocal SoundFont if fetchable (egress remains blocked).
2. **Sparse c53 winner MIDIs on quiet stems** (notably `51e433ade2a845e1`/piano) produce very quiet fluidsynth output — revisit c53 winner-selection density gates.
3. **Chosen-section overrides vs baseline 30 s captures** — still-open c53 clone-2 Chicken Grease policy call carries forward; not a blocker.
4. **Dry vs mix-ready renders** — operator listening loop notes; mix-ready render is a separate branch.
5. **pyloudnorm fallback threshold** documented.

## 6. Ledger + plan-of-record accounting

| Clone | Substantive `M-*` (unsuffixed) | `_archive/_infra` | `M-INGEST-1` egress-probe |
|---|---|---|---|
| 0 | 6 sub-leaves under `.../drums-v2/*` | 2 `-clone-0` | 1 `-clone-0` (HTTP 429 + tv_embedded unchanged) |
| 1 | 6 sub-leaves under `.../bass-v2/*` | 2 `-clone-1` | 1 `-clone-1` |
| 2 | 6 sub-leaves under `.../ab-pairs-refresh/*` (0 rejections) | 2 `-clone-2` | 1 `-clone-2` |

**Total**: 27 events (18 substantive + 6 housekeeping + 3 egress-probe).

**plan_of_record.md**: c56 integrator to register 6 sub-leaves per clone under c33 auto-suffix pattern (slash-separated per Branch B/C convention). Clone-2 already appended 7 rows after the c54 rollup row.

## 7. Cross-branch disjointness

All writes are disjoint across the three clones:

- **Clone 0**: `data/rc10_drums_v2_impl/*`, `data/recreate_v2/ab_pairs/<sha16>/drums/iter_1/*`, `scripts/recreate_v2/rc10_drums_v2/*`, `docs/rc10_drums_v2_*`, `tests/test_rc10_drums_v2.py`, `tools/stale/c55_*.py`, `data/ingestion/egress_status.jsonl` (append).
- **Clone 1**: `data/rc10_bass_v2_impl/*`, `data/recreate_v2/ab_pairs/<sha16>/bass/iter_1/*`, `scripts/recreate_v2/rc10_bass_v2/*`, `docs/rc10_bass_v2_*`, `tests/test_rc10_bass_v2.py`.
- **Clone 2**: `data/rc10_ab_pairs_refresh/*`, `data/recreate_v2/ab_pairs/<sha16>/{guitar,piano,other_residual,vocals}/iter_1/*`, `scripts/recreate_v2/rc10_ab_pairs_refresh/*`, `docs/rc10_ab_pairs_refresh_*`, `tests/test_rc10_ab_pairs_refresh.py`, `data/rc10_impl/other_vocals/per_song/<sha16>/{vocals,other_residual}/winner.mid` (new files under existing c53 dir; c53 files unchanged).

**Zero writes** to any READ-ONLY anchor: `scripts/palette_render/render_stem.py` (`214372d9…5b2b`); c33/c50/c54 rubrics; c54 v1 `data/rc10_drums_bass_impl/*`; all three c53/c54 `winner_per_stem*.json` SHA byte-identical pre==post.

## 8. Egress state

HTTP 429 + tv_embedded unchanged from c54 baseline across all three probes. Not the two-consecutive `media_ok=true` unblock signal. Path A per c49 policy.

## 9. c56 integrator agenda (LINEAR post-merge)

1. **Concat 3 shadow ledgers** into `promise_ledger.jsonl` (27 rows; per-clone AGENT_FORK_ID routing).
2. **Register 18 sub-leaves** in `plan_of_record.md` (6 per clone; c33 auto-suffix). Clone-2's 7 rows already landed.
3. **Verify 0-ERROR `promise_check`** post-registration.
4. **Drums-v2 iteration path**: address the 3 policy calls (WIG cluster-mapping fallback, Dojo G2 window-majority, Disco A near-tie tolerance); propose `_infra/rc10-classifier-mapping-fallback-lemma`.
5. **Bass-v2 iteration path (v3)**: hybridize v1 pyin_mono base + v2 slap/ghost augmentation; re-calibrate slap detector against other-stem bleed; tighten onset delta.
6. **Operator listening loop**: 35 (drums-v2) + 5 (bass-v2) + 40 (refresh) = 80 fresh A/B WAVs ready for operator.
7. **Six-stem gate rollup**: c54 rollup + drums-v2/bass-v2/refresh integration → `M_RECREATE_2_LANDS` candidacy tally.
8. **c53 clone-2 Chicken Grease chosen-section vs baseline-30s window** — carries forward (fourth branch to touch this now; upstream fix overdue).

## 10. Session pointers

- Cycle 61 researcher: `32eed67e-9f23-4103-8bc9-ac5fdb0e9a3a`
- Cycle 62 worker: `16910231-7cad-480c-8341-0893914bb4fe`
- Cycle 63 researcher: `5ea194d7-735e-416b-9b4f-f06b62da3f60`

**Fanout cadence**: LINEAR c49/c50 → FANOUT c51 (3-branch) → LINEAR c52 → FANOUT c53 (RC10 3-branch) → LINEAR c54 (six-stem rollup) → **FANOUT c55 (3-branch: drums-v2, bass-v2, ab-refresh) ← this cycle**. c56 should be LINEAR post-merge integration + v2/v3 iteration decisions on drums/bass.

[END OUTPUT]

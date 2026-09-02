---
created: 2026-09-02T00:00:00Z
cycle: 55
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-v2
fork: 7cc01d726807
clone: clone-0
---

# RC10 Drums Classifier v2 — Report

**Verdict**: `RC10_DRUMS_V2_PARTIAL`

**Rubric SHA**: `d4ebe12ea9fe7c4fef3fef9b6ea494dc2c1c35ffff4a64c9fcdc14a48dfcca49`
(three-way byte-equality holds: doc SHA == `data/rc10_drums_v2_impl/
rubric_hash.txt` content == `data/rc10_drums_v2_impl/verdict.json.
rubric_hash`).

## §1 Origin

Operator listening feedback on 2026-09-02 (Chicken Grease + What If I
Go): the c54 v1 `onset_band_energy` drums classifier — which scored 5/5
PASS with composite F1 = 1.0000 — was over-classifying kick because the
absolute-band-energy rule always picked kick when low-band was strongest,
and low-band is contaminated by bass-guitar bleed and by the snare's own
low-end. Median MIDI pitch across all 5 c54 v1 focus songs was 36 (pure
kick) — literal empirical evidence of the collapse.

v2 keeps the c54 v1 onset detector verbatim (`librosa.onset.onset_detect(
y, sr, hop_length=512, backtrack=True, units="time")`) so **onset timing
is preserved** (operator constraint — "rhythmically close" already), and
swaps the classification stage for:

1. **Relative per-onset spectral features** (§D3):
   - spectral centroid (Hz),
   - HF/LF log-energy ratio at 500 Hz split,
   - decay time (ms) from RMS envelope 90%→10%.
2. **Per-song 3-component GMM** on standardized features (§D4),
   `sklearn.mixture.GaussianMixture(n_components=3, covariance_type="diag",
   random_state=0, max_iter=100, tol=1e-4, init_params="kmeans")`. The
   `random_state=0` is the **single-site PRNG allowlist** (matches
   campaign convention for `torch.manual_seed(0)` /
   `tf.random.set_seed(0)` / `np.random.seed(0)`).
3. **Cluster→label mapping by ascending mean centroid**: lowest cluster
   → kick (36), middle → snare (38), highest → hat (42).
4. **Multi-label onsets** (§D5): any class with posterior ≥ 0.35 is
   included. Kick+hat co-fire is a normal groove event; the MIDI writer
   emits one note per active label at each onset time.
5. **Four-plausibility acceptance gate** (§D6): G1 onset F1 (regression
   clause), G2 4-bar window kick balance, G3 kick rate ≤ 2× beat rate,
   G4 strict centroid ordering `k < s < h`.

## §2 Per-song results

| Song (sha16) | title | n_onsets | kick | snare | hat | G1 | G2 | G3 | G4 | passed |
|---|---|---:|---:|---:|---:|:-:|:-:|:-:|:-:|:-:|
| `31a164f845f8e27e` | **Chicken Grease** | 147 | 55 | 64 | 28 | ✓ | ✓ | ✓ | ✓ | **PASS** |
| `cdd2717e52820ff6` | Disco A | 58 | 12 | 13 | 33 | ✓ | ✓ | ✓ | ✗ | fail |
| `51e433ade2a845e1` | Dojo Cuts – Rome | 162 | 60 | 89 | 13 | ✓ | ✗ | ✓ | ✓ | fail |
| `252eb21ce7df7328` | **What If I Go** | 61 | 46 | 6 | 9 | ✓ | ✗ | ✓ | ✗ | fail |
| `88d247468cb6d49f` | Peach Dream | 227 | 64 | 47 | 116 | ✓ | ✓ | ✓ | ✓ | **PASS** |

G1 (onset F1): 5/5 = 1.0000 (identical detector → onset TIMING PRESERVED
per song; regression delta 0.000 across the board).

## §3 Mandatory-accepts table (operator-surfaced)

| Song | passed_all_gates | notes |
|---|:-:|---|
| **Chicken Grease** (`31a164f845f8e27e`) | ✓ | v2 achieves 55 kick + 64 snare + 28 hat — 4-gate PASS. |
| **What If I Go** (`252eb21ce7df7328`) | ✗ | G2 kick balance fails (worst 4-bar window has kick excess=11); G4 ordering fails (median snare centroid 6115 Hz > median hat centroid 5752 Hz). |

Because **What If I Go misses** two gates while Chicken Grease PASSES,
the mandatory-accepts pair splits — rubric §D7 fires PARTIAL (2/5
songs pass all gates).

## §4 Cluster/mapping diagnostics per song

Per-song `median_centroid_by_label` (Hz), from `data/rc10_drums_v2_impl/
<sha16>/notes.json`:

| Song | median_kick_Hz | median_snare_Hz | median_hat_Hz | ordering |
|---|---:|---:|---:|:---|
| CG    | 1500.4 | 2353.7 | 6083.4 | strict PASS |
| Disco | 2493.7 | 2941.8 | 2925.8 | snare > hat by ~16 Hz — **near-tie** |
| Dojo  | 2365.9 | 3617.1 | 4520.7 | strict PASS |
| WIG   | 4264.0 | 6115.3 | 5752.3 | snare > hat by ~363 Hz — hat-cluster low |
| Peach | 1570.6 | 4712.1 | 6168.4 | strict PASS |

**Interpretation.** On Disco A the middle and top clusters overlap
almost exactly on centroid — the 3-component fit collapses two clusters
of a 2-cluster-in-reality distribution (only kick + hat, no distinct
snare). On What If I Go the middle cluster ("snare") actually captures a
noisy transient region higher in frequency than the "hat" cluster does —
the ascending-centroid mapping mis-labels them.

The **structural finding** is that per-song 3-component fitting can
introduce spurious middle clusters on genres where drums are dominated
by only two acoustic sources (e.g. kick + hi-hat in the electronic
Chicken Grease-adjacent groove of What If I Go). This is a candidate for
`_infra/rc10-classifier-mapping-fallback-lemma` in c56.

## §5 Onset-timing regression contract

All 5 songs report `onset_timing_status: PRESERVED`. G1 F1 vs c54 v1 F1
delta = +0.000 uniformly, because v2 keeps the identical detector.
The regression clause `F1_v2 ≥ max(0.60, F1_v1 − 0.05)` holds trivially.

## §6 A/B pair emission (35 WAVs)

Under `data/recreate_v2/ab_pairs/<sha16>/drums/iter_1/`, 5 songs × 7
files = 35 WAVs:

- `original.wav` — chosen-section baseline drums stem
- `kick_only.wav`, `snare_only.wav`, `hat_only.wav` — fluidsynth GM ch10
  renders of merged v2 notes, class-filtered
- `original_kick_band.wav` (20–200 Hz), `original_snare_band.wav`
  (200–2000 Hz), `original_hat_band.wav` (2000–20000 Hz) — Butter-order-4
  bandpass slices of `original.wav`

Loudness normalization: `pyloudnorm.Meter(sr).integrated_loudness()`
+ linear gain toward LUFS-I −23 with peak-limiter clamp at 0.99. When
the clamp engages, the achieved LUFS is honestly reported below target
(per c53 clone-1 precedent). See
`data/rc10_drums_v2_impl/ab_pairs_manifest.json` for per-file
`achieved_lufs`, `gain_db`, `peak_clipped`, `pre_normalize_lufs`.

## §7 Byte-determinism × 2

74/74 tracked files SHA-256-equal across two pipeline runs (fresh env
pins, in-place output dirs). See
`data/rc10_drums_v2_impl/byte_determinism.json`.

**Non-obvious fix (documented for reproducibility).** libsndfile writes
a PEAK chunk into FLOAT WAV files containing a `timeStamp` field with
Unix wall-clock seconds. That defeats byte-determinism by exactly one
byte per file (byte 60 in the standard PEAK layout). The `run_all.py`
post-processes each WAV after `sf.write` to overwrite the PEAK
`timeStamp` field with `SOURCE_DATE_EPOCH` (little-endian uint32) —
otherwise all 35 A/B WAVs would show a 1-byte-per-file diff between
consecutive runs. All 39 non-WAV outputs (scorecard, verdict, notes
JSON, feature TSVs, MIDIs, manifests) are natively byte-deterministic.

## §8 Anchor preservation (32 SHAs, pre==post byte-exact)

`data/rc10_drums_v2_impl/anchor_preservation.json`:

- c49 v1 rubric `958ade38…3fe58b9d` — READ-ONLY ✓
- c50 v2 rubric `0e11f704…debe1f` — READ-ONLY ✓
- c54 v1 drums rubric `a79bee01…5fd919` — READ-ONLY ✓
- c53 clone-1 guitar-piano rubric — READ-ONLY ✓
- c53 clone-2 other-vocals rubric — READ-ONLY ✓
- c33 `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b` —
  READ-ONLY (do-not-touch invariant, NOT imported by this branch) ✓
- c54 v1 `data/rc10_drums_bass_impl/{verdict.json, winner_per_stem.json,
  scorecard.tsv}` — READ-ONLY (v1 winner preserved as comparison
  baseline) ✓
- Per-song c50 v2 baselines `data/recreate_v2/baseline/<sha16>/*` (5×3
  files) — READ-ONLY ✓
- Per-song c53 clone-2 rc5 tempo estimates
  `data/rc5_impl/<sha16>/rc5_tempo_estimate.json` (5) — READ-ONLY ✓
- `data/recreate_v2/focus_set_v2.json` + `rubric_hash{,_v2}.txt` — READ-
  ONLY ✓

32/32 byte-identical. **v2 supersedes v1 for drums classification only
via a new file tree at `data/rc10_drums_v2_impl/*`; the v1 tree is
untouched.**

## §9 Test suite

17/17 tests pass in `tests/test_rc10_drums_v2.py`: rubric mtime gate,
three-way `rubric_hash` byte-equality, verdict enum, byte-determinism
manifest, anchor preservation, 5 anchor SHA locks (c54 v1 rubric, c50
v2 rubric, c49 v1 rubric, c33 render_stem, c48 env-flag defaults), PRNG
allowlist (regex + code-line check), no `sidecar_nonfactor` import,
interpreter guard, 35 A/B WAV presence, mandatory-accept pinning in
verdict, per-song onset-F1 regression report, scorecard shape.

## §10 Cross-clone coordination

Peer branches (disjoint scopes) as declared in the research brief:

- Clone-1: bass v2 → `data/rc10_bass_v2_impl/*`, bass A/B pair dirs.
- Clone-2: guitar/piano/other/vocals A/B refresh →
  `data/rc10_ab_pairs_refresh/*` + LUFS re-normalization for c53 Branch
  C.
- Clone-0 (this): drums v2 → `data/rc10_drums_v2_impl/*` +
  `data/recreate_v2/ab_pairs/<sha16>/drums/iter_1/*`.

No write-path overlap. c56 integrator will concat 9 shadow-ledger
events per clone (this branch emits 9: 6 substantive + 2 housekeeping +
1 egress-probe).

## §11 Handoffs to c56

1. **c56 researcher policy call — WIG cluster mapping.** What If I Go
   fails G4 because the "middle" cluster's median centroid (6115 Hz) is
   higher than the "top" cluster's (5752 Hz). Candidate remedies to
   investigate:
   - constrain GMM initialization by seeding cluster means from the
     baseline per-song RMS-band-energy medians (kick_band, snare_band,
     hat_band), rather than kmeans;
   - fall back to 2-component GMM (kick + hat) when the middle-cluster
     centroid deviation from the top exceeds a per-song threshold;
   - detect the collapsed-cluster case at fit time and emit c54 v1
     labels as `fallback_reason: "cluster_ordering_degenerate"` — this
     would flip WIG from `passed=False G4=✗` to `passed_all_gates` under
     the c54 v1 F1=1.0 baseline. Would also flip Disco A which fails
     G4 by a 16 Hz margin.
2. **c56 researcher policy call — Dojo Cuts G2.** The 4-bar-window kick
   balance gate fires because Dojo's chosen section has one 4-bar window
   where kick edges out snare+hat by 4 counts (60 vs 89+13 overall but
   locally imbalanced). Candidate remedies: relax G2 to majority-of-4-
   bar-windows instead of any-window; or widen the window to 8 bars for
   uptempo (>140 BPM) tracks.
3. **Lemma proposal candidate** `_infra/rc10-classifier-mapping-fallback-
   lemma` — deferred per rubric §6. Would codify the
   collapsed-cluster detection + c54 v1 label fallback as a general
   RC10 recovery path.
4. **Operator listening loop.** 35 v2 A/B WAVs + 10 c53 clone-1 bass
   A/B WAVs (already on disk) + 40 c53 clone-2 guitar/piano/other/
   vocals A/B WAVs (already on disk — LUFS-normalization refresh due to
   clone-2 this cycle) will be handed to operator via c56 rollup after
   post-merge integration.

## §12 Anti-patterns preserved

- c53 RC2 basic-pitch-on-drums anti-pattern REMAINS LOCKED — v2 does
  not re-attempt.
- c11 CLAP-fetchability / c22 chassis / c23 head-regularization / c25
  feature-representation / c35 palette-v2-VST3 not re-opened.
- c33 `render_stem.py` do-not-touch invariant preserved (not imported).

## §13 Ledger emission plan (this branch)

Six substantive (unsuffixed per c32):
- `.../drums-v2-pre-registration`
- `.../drums-v2-impl`
- `.../drums-v2-candidate-matrix-scored`
- `.../drums-v2-plausibility-gate-verified`
- `.../drums-v2-ab-pairs-emitted`
- `.../drums-v2-verdict-emitted`

Two housekeeping (auto-suffixed by c33 harness):
- `_archive/cycle-55-scratch-clone-0`
- `_infra/adopt-cycle55-tests-clone-0`

One egress-probe:
- `M-INGEST-1/egress-probe-cycle55-clone-0` — path A per c49
  `_plan/egress-retry-cadence-policy-formalized`. HTTP 429 + tv_embedded
  expected unchanged; not the two-consecutive `media_ok=true` unblock
  signal.

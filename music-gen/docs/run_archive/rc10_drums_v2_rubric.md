---
created: 2026-09-02T00:00:00Z
cycle: 55
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-v2
---

# RC10 Drums Classifier v2 — Rubric

**Peer sub-milestone** under
`M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
(NOT a child of the terminal-validated `drums-bass-*` c54 sub-leaves —
this is a v2 peer per the c29 state-machine lemma).

**Rationale.** Operator listening feedback (2026-09-02) on Chicken Grease
+ What If I Go: c54 v1 `onset_band_energy` won 5/5 with composite F1 =
1.0000 (drums onset TIMING preserved), but every classified note landed
on kick (median MIDI pitch = 36 for all 5 songs). Root cause: absolute
low-band-energy per onset is fooled by bass-guitar bleed and by snare's
own low-end content, so the "who wins the band contest" rule collapses
to always-kick.

v2 swaps absolute band-energy for RELATIVE per-onset spectral features
and fits a per-song 3-component GMM so cluster→class mapping is
calibrated per song rather than tuned once across songs.

## §D1 Focus set (READ-ONLY reuse)

`data/recreate_v2/focus_set_v2.json` — 5 songs (Chicken Grease, Disco A,
Dojo Cuts – Rome, What If I Go, Peach Dream). Chosen sections consumed
verbatim; `slice_and_load` clamps to available stem duration (30 s
baseline stems) so out-of-window sections fall back to full stem.

**MANDATORY per-song accepts** (operator surfaced by name):
- Chicken Grease `31a164f845f8e27e`
- What If I Go `252eb21ce7df7328`

Onset detection reference re-uses the c54 baseline anchor
`data/recreate_v2/baseline/<sha16>/rc2_drum_onset_count.json` +
underlying baseline drums stem
`data/recreate_v2/baseline/<sha16>/rc9_6stem/drums.wav`.

## §D2 Baseline anchors (READ-ONLY)

- c54 baseline `rc2_drum_onset_count.json` per song (default-param
  librosa detector — advisory; c54 v1 F1 uses `hop=512, backtrack=True`).
- c53 clone-2 rc5 tempo estimates at `data/rc5_impl/<sha16>/
  rc5_tempo_estimate.json.corrected_estimate` — beat-rate divisor for
  gate G3 below.
- c54 v1 winners at `data/rc10_drums_bass_impl/winner_per_stem.json`
  (regression comparison; no re-verdict).

## §D3 Relative-feature extraction

Onsets: `librosa.onset.onset_detect(y, sr, hop_length=512,
backtrack=True, units="time")` on the baseline drums stem (matches c54
v1 pattern, so onset TIMING is guaranteed identical to c54 v1 — this is
the operator's "rhythmically close" constraint).

Per-onset ±25 ms analysis window (`half = int(round(sr * 0.025))`).
Three-D feature vector per onset:

1. **Spectral centroid** (Hz): mean of
   `librosa.feature.spectral_centroid(y=win, sr=sr, hop_length=256)`
   over the window frames.
2. **HF/LF energy ratio** (dimensionless): STFT `n_fft=1024, hop=256`
   on the window; `log10((energy[freq >= 500 Hz] + eps) /
   (energy[freq < 500 Hz] + eps))`. `eps=1e-12`.
3. **Decay time** (ms): RMS envelope on the window
   (`librosa.feature.rms(y=win, hop_length=128)`); find the peak-frame
   index, then walk forward to first frame ≤ 10% of peak; convert
   frame-count to ms via `(idx * 128 / sr) * 1000`. Fall-back = full
   window length (ms) if no crossing found.

Absolute band-energy thresholds NOT used (operator root cause).

## §D4 Per-song unsupervised clustering

`sklearn.mixture.GaussianMixture(n_components=3, covariance_type="diag",
random_state=0, max_iter=100, tol=1e-4, init_params="kmeans")` fitted
PER SONG on the 3-D feature matrix (N_onsets × 3).

Feature standardization: per-song `StandardScaler` (mean-zero,
unit-variance per column) applied BEFORE `.fit`. Deterministic
(closed-form, no PRNG).

Cluster→class mapping by ASCENDING mean spectral centroid on the
ORIGINAL (un-standardized) centroid column: lowest centroid → **kick
(36)**, middle → **snare (38)**, highest → **hat (42)**. No cross-song
fits.

### Degenerate-case fallback

If GMM fails to fit (e.g. N_onsets < 3) or centroid ordering yields ties
(two clusters have identical mean centroid), fall back to c54 v1
`onset_band_energy` labels for that song and set
`fallback_reason` in the per-song result JSON. First-class negative
finding; not a defect.

**PRNG allowlist**: `GaussianMixture(random_state=0)` is the only PRNG
call site permitted (matches campaign convention for
`torch.manual_seed(0)` / `tf.random.set_seed(0)` /
`np.random.seed(0)`). AST-grep asserts single-site allowlist.

## §D5 Multi-label onset schema

Per-onset event JSON:

```json
{
  "onset_s": float,
  "duration_s": float,
  "labels": ["kick"|"snare"|"hat", ...],
  "posteriors": {"kick": float, "snare": float, "hat": float},
  "velocity": int
}
```

Multi-label rule: any class with posterior ≥ 0.35 is included in
`labels`. Kick+hat co-fire is a normal groove event (per operator).
`merged.midi` writes ONE MIDI note per label at the onset time on GM
channel 10 (kick=36, snare=38, hat=42) with `velocity=90` and
`duration_s=0.15` (matches c54 v1 convention). Duplicate-note collapse
if two labels map to the same pitch (never happens: {36, 38, 42} are
disjoint).

## §D6 Four-plausibility acceptance gate

Per song, all four must hold for PASS:

1. **G1 Onset F1**: measured against baseline onset times (tol 50 ms,
   greedy 1-to-1) — REGRESSION CLAUSE `F1_v2 ≥ max(0.60, F1_v1 − 0.05)`.
   Since v2 uses the identical detector, F1_v1 = 1.0 in practice and F1
   preserved trivially unless a bug is introduced.
2. **G2 4-bar window balance**: `kick_count ≤ snare_count + hat_count`
   within any 4-bar sliding window of the chosen groove section. Bar
   length = `60 * 4 / bpm` seconds; slide by 1 bar; consider all windows
   fully inside `[t_start, t_end]`. If N_windows == 0 (chosen section
   shorter than 4 bars), gate PASSES vacuously.
3. **G3 Kick rate**: `kick_count / duration_s ≤ 2 * bpm / 60` (i.e. kick
   density ≤ 2× beat rate).
4. **G4 Centroid ordering**: STRICT `median_centroid(kicks) <
   median_centroid(snares) < median_centroid(hats)` on the ORIGINAL
   centroid feature column. Empty-class case: absent classes get a
   sentinel `+inf` for missing higher class or `−inf` for missing lower
   — the ordering is trivially satisfied when a class is empty.

## §D7 Verdict rubric (frozen 3-verdict)

- `RC10_DRUMS_V2_LANDS` — ≥3/5 focus songs pass ALL 4 plausibility gates
  AND Chicken Grease AND What If I Go both PASS.
- `RC10_DRUMS_V2_PARTIAL` — 2/5 songs pass all gates OR ≥3/5 pass but
  Chicken Grease OR What If I Go misses ≥1 gate.
- `RC10_DRUMS_V2_FAILS` — everything else.

Onset-timing regression column: PRESERVED / DEGRADED per song
(DEGRADED iff G1 fails).

## §h A/B pair emission

Per focus song, under `data/recreate_v2/ab_pairs/<sha16>/drums/iter_1/`:

| File | Content | Loudness target |
|------|---------|-----------------|
| `original.wav` | baseline drums stem, chosen_section clipped | LUFS-I −23 ±0.5 |
| `kick_only.wav` | fluidsynth GM ch10 note 36-only render of merged notes | LUFS-I −23 ±0.5 |
| `snare_only.wav` | GM note 38-only | LUFS-I −23 ±0.5 |
| `hat_only.wav` | GM note 42-only | LUFS-I −23 ±0.5 |
| `original_kick_band.wav` | 20–200 Hz bandpass of `original.wav` | LUFS-I −23 ±0.5 |
| `original_snare_band.wav` | 200–2000 Hz bandpass | LUFS-I −23 ±0.5 |
| `original_hat_band.wav` | 2000–20000 Hz bandpass | LUFS-I −23 ±0.5 |

35 total files = 5 songs × 7. `pyloudnorm.Meter(sr).integrated_loudness`
+ per-file linear-gain adjustment to hit target. If peak limiter would
engage (post-gain sample abs > 0.99), gain is clamped so
`max_abs_post_gain ≤ 0.99` and the achieved LUFS is honestly reported
(may miss ±0.5 LU) — precedent: c53 clone-1 A/B emission.

Butter filters: `scipy.signal.butter(4, [lo/(sr/2), hi/(sr/2)],
btype="band", output="sos")` + `sosfiltfilt`. For the 20 Hz lower edge,
use `btype="highpass"` cascaded with `btype="lowpass"` (avoids ill-
conditioning near DC).

## §3 Falsifiable success criteria

- (a) Rubric doc mtime < every `.py` under `scripts/recreate_v2/
  rc10_drums_v2/` (test 01 hard; test 02 SOFT git-log per c46 path (ii)).
- (b) Three-way `rubric_hash` byte-equality
  (`sha256(docs/rc10_drums_v2_rubric.md)` ==
  `data/rc10_drums_v2_impl/rubric_hash.txt` content ==
  `data/rc10_drums_v2_impl/verdict.json.rubric_hash`).
- (c) Byte-determinism × 2 across all outputs (scorecard.tsv, per-song
  feature matrices, notes JSONs, merged MIDIs, 35 A/B WAVs) under
  `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
  `LC_ALL=C.UTF-8`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`.
- (d) c54 anchors READ-ONLY pre==post byte-exact:
  `docs/rc10_drums_bass_rubric.md` (SHA
  `a79bee01b4c97a1282f476a01915f4f9119fa23d369e5be2b0b72fbee05fd919`),
  `data/rc10_drums_bass_impl/{verdict.json, winner_per_stem.json,
  scorecard.tsv}`.
- (e) c50 v2 rubric SHA
  `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`
  byte-identical pre==post.
- (f) c49 v1 rubric SHA
  `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d`
  byte-identical pre==post.
- (g) c33 `scripts/palette_render/render_stem.py` SHA
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
  byte-identical pre==post (do-not-touch anchor; NOT imported).
- (h) c53 clone-2 rc5 tempo estimates byte-identical pre==post
  (READ-ONLY input).
- (i) c54 baseline `data/recreate_v2/baseline/<sha16>/*` byte-identical
  pre==post.
- (j) Anchor preservation manifest ≥25 SHAs (target 30+).
- (k) NO PRNG except `GaussianMixture(random_state=0)` allowlisted.
- (l) `/usr/bin/python3` interpreter guard on every top-level script;
  c48 env-flag defaults OFF via `os.environ.setdefault`.
- (m) No `sidecar_nonfactor` import.
- (n) ≥15/15 tests green in `tests/test_rc10_drums_v2.py`.
- (o) 0-ERROR promise_check post-emission.
- (p) Verdict ∈ {RC10_DRUMS_V2_LANDS, RC10_DRUMS_V2_PARTIAL,
  RC10_DRUMS_V2_FAILS} with per-song Chicken Grease + What If I Go table
  pinned in verdict.json.
- (q) Onset F1 per song reported alongside c54 v1 F1 (regression
  tracked, ≥ v1 − 0.05).

## §4 Anti-patterns and locks

- c53 RC2 basic-pitch-on-drums anti-pattern remains LOCKED — v2 does
  NOT re-attempt basic-pitch on drums.
- c11 CLAP-fetchability / c22 chassis / c23 head-regularization / c25
  feature-representation / c35 palette-v2-VST3 anti-patterns not
  re-opened.
- c33 `render_stem.py` do-not-touch invariant preserved.

## §5 Non-goals

- No M-EAR-1/*, M-GEN-1/*, corpus-breadth emissions.
- No bass, guitar/piano, other/vocals work (peer clones own those).
- No v1 winner re-verdict — c54 v1 winners READ-ONLY.
- No new dependency install (sklearn/scipy/librosa/pyloudnorm/
  pretty_midi already present per basic_pitch_venv ancestry).

## §6 Cross-clone coordination

Clone-1 (bass v2) and clone-2 (guitar/piano/other/vocals A/B refresh)
write disjoint dirs. Shared READ-ONLY anchors listed in §3.
Post-merge c56 rollup will register missing sub-leaf milestone_ids
following the c54 rollup precedent.

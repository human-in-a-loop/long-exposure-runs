---
created: 2026-08-28T05:40:00Z
cycle: 4
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/panel
---

# Texture-Distance Panel Report (M-TEX-1/panel)

Clone 2 of fork `22b8c654f616`, cycle 4 fan-out branch C.
Library-only closure of the *measurement* half of M-TEX-1. The
parent-milestone bare-MIDI-vs-original stage-by-stage measurement is
DEFERRED to when M-SCORE-1 lands.

## 1. Objective

Deliver a callable texture-distance library that reports **five metrics
side by side** — three families, two metrics each in the first two,
one metric in the third — and **refuses to expose a weighted aggregate
overall score**. Validate against three canonical pairs:

1. **Matched** — DAW-spike Ardour↔DawDreamer sine-through-Surge chain
   (reproduce clone-1's `mel_l1_db=3.13`, `rms_env_rmse=0.041`,
   `spectral_centroid_rmse_hz=159.02` within ±5%).
2. **Known-different** — fluidsynth (FluidR3_GM.sf2, Acoustic Grand
   Piano) vs sfizz_render (single-region saw SFZ) on the SAME MIDI file
   at the SAME 48 kHz stereo output. Different tone generators, same
   content → the panel must register a materially larger distance.
3. **Self-distance** — `texture_distance(a, a, sr)` must sit at the
   floating-point floor on all metrics.

The panel does not depend on M-SCORE-1 and does not consume the ingestion
chunker or the non-factor sidecar; it is a pure audio-in / metrics-out
function.

## 2. Metric definitions

| Family    | Metric                       | Unit  | Channel  | STFT / hop / window                        | Notes |
|-----------|------------------------------|-------|----------|--------------------------------------------|-------|
| spectral  | `mel_l1_db`                  | dB    | mono     | n_mels ∈ {64, 128, 256}, hop=512, n_fft=2048 | mean of |log-mel(a) − log-mel(b)| across all three scales; log-mel via `librosa.power_to_db(mel + 1e-10)` (matches clone-1 exactly). |
| spectral  | `spectral_centroid_rmse_hz`  | Hz    | mono     | hop=512, n_fft=2048                        | frame-aligned RMSE of `librosa.feature.spectral_centroid` on shorter length. |
| envelope  | `rms_env_rmse`               | unitless (linear amplitude) | mono | frame=2048, hop=512    | `librosa.feature.rms` on mono mixdown; frame-aligned RMSE. |
| envelope  | `lufs_m_rmse_lu`             | LU (loudness units) | stereo | 400 ms window, 100 ms hop | `pyloudnorm.Meter.integrated_loudness` per block (mono duplicated to stereo). Frames below EBU R128 absolute silence gate (−70 LUFS) dropped from both sides. |
| embedding | `embedding_cosine_distance`  | [0, 2] | mono @ model SR | one clip → one vector | rung ladder CLAP → VGGish → `None`. Vectors L2-normalized before cosine; distance = 1 − cos(u, v). For VGGish (128-dim per 0.96 s frame), mean over frames. |

Expected ranges (from validation):

- `mel_l1_db`: ~0 for identical signal; ~3 for a matched pair through the
  same effect chain; ~30 for content-different pairs.
- `spectral_centroid_rmse_hz`: ~0 identical; ~150 matched; > 500
  known-different.
- `rms_env_rmse`: ~0 identical; ~0.04 matched; 0.05–0.10 known-different.
- `lufs_m_rmse_lu`: 0 identical; a few LU matched; > 10 LU known-different.
- `embedding_cosine_distance`: ~0 identical; ~0.02 matched; ~0.4
  known-different.

## 3. Panel API contract

```python
from scripts.texture.panel import texture_distance
result = texture_distance(a, b, sr, sr_b=None)
# {
#   "mel_l1_db":                 float,
#   "spectral_centroid_rmse_hz": float,
#   "rms_env_rmse":              float,
#   "lufs_m_rmse_lu":            float,
#   "embedding_cosine_distance": float | None,
#   "embedding_rung":            "clap" | "vggish" | "none_available",
#   "sr_hz":                     int,
#   "n_samples_compared":        int,
# }
```

- **Refuse-aggregate.** The result dict has exactly the eight keys above.
  A defensive assertion inside `panel.texture_distance` re-validates the
  key set on every call. There is no `overall`, `combined`, `mean`,
  `weighted`, `aggregate`, `score`, or `total`. Callers who want a
  composite score compose it themselves; the panel does not.
- **Length mismatch.** Truncated to `min(len(a), len(b))` samples by
  each metric. The panel does NOT resample, DTW-align, or pad. This
  makes the panel tempo-agnostic *at short scales* only — see §7.
- **SR mismatch.** If `sr_b` is provided and differs from `sr`, the
  panel raises `ValueError`. Resampling policy belongs to the caller.

## 4. Embedding rung outcome

**Rung landed: `vggish`** (rung 2).

Rung 1 — CLAP — did NOT land: `laion-clap` installs on `/usr/bin/python3
-m pip install --user` and downgrades numpy from 2.4.6 to 1.26.4 as a
transitive side effect (documented in the promise ledger under
`_manager/M-CLASS-1-numpy-downgrade`). But `laion_clap.CLAP_Module`
requires `torchvision` — not present in this workspace — and CLAP itself
requires a ~1.5 GB HuggingFace-hub weight fetch that this cycle did not
attempt. Both are recoverable in a future cycle if the panel needs a
CLAP embedding; for now VGGish is sufficient for the "always report one
perceptual embedding" contract.

Rung 2 — VGGish — landed cleanly:

- **Source URL:** `https://tfhub.dev/google/vggish/1`
- **Loader:** `tensorflow_hub.load(...)` (tf 2.21.0, hub 0.16.1).
- **Embedding shape:** 128 floats per 0.96 s frame @ 16 kHz mono input;
  the panel takes the mean over frames per clip.
- **SHA-256 of the fetched SavedModel bundle:** not recorded (tfhub
  serves an archive that unpacks into an internal cache; only the URL
  is content-addressable here).

Rung 3 — `none_available` — not needed.

The rung + failure reasons are persisted to
`data/texture/embedding_rung.log`:

```json
{
  "rung": "vggish",
  "meta": {"kind": "vggish", "sr": 16000, "source": "https://tfhub.dev/google/vggish/1", "dim": 128, "frame_s": 0.96},
  "reasons": {"clap": "laion_clap import failed: ModuleNotFoundError(\"No module named 'torchvision'\")"}
}
```

## 5. Validation results

All five metrics × three pairs (`data/texture/panel_summary.tsv`):

| pair            | mel_l1_db | spectral_centroid_rmse_hz | rms_env_rmse | lufs_m_rmse_lu | embedding_cosine_distance | embedding_rung |
|-----------------|-----------|---------------------------|--------------|----------------|---------------------------|----------------|
| matched         | 3.1535    | 159.02                    | 0.04099      | 1.614          | 0.02530                   | vggish         |
| known_diff      | 31.0711   | 4412.22                   | 0.05831      | 16.520         | 0.42656                   | vggish         |
| self_distance   | 0.0000    | 0.00                      | 0.00000      | 0.000          | 0.0                       | vggish         |

**Pair 1 — Matched-pair reproduction ratios** (measured / reference):

| metric                      | measured   | reference   | ratio    | within ±5%? |
|-----------------------------|------------|-------------|----------|-------------|
| mel_l1_db                   | 3.1535     | 3.130554    | 1.00733  | ✅ (+0.73%) |
| rms_env_rmse                | 0.04099077 | 0.040991    | 1.000000 | ✅ (exact)  |
| spectral_centroid_rmse_hz   | 159.01715  | 159.017     | 1.000001 | ✅ (exact)  |

The mel_l1_db divergence is +0.73%, well inside tolerance. It comes from
this panel averaging n_mels ∈ {64, 128, 256} whereas clone-1 uses
n_mels=128 alone. Per-scale breakdown:

| n_mels | mel_l1_db |
|-------:|-----------|
| 64     | 3.3739    |
| 128    | 3.1306    |
| 256    | 2.9561    |

The **128-mel scale matches clone-1 to 6 decimal places** — cross-branch
STFT parameterization is bit-consistent. Adding 64 and 256 as
side-channels smooths across the mel-resolution axis without moving
the headline number more than 1%.

**Pair 2 — Known-different ratios** (known_diff / matched):

| metric                      | matched  | known_diff | ratio   |
|-----------------------------|----------|------------|---------|
| mel_l1_db                   | 3.1535   | 31.0711    | 9.85×   |
| spectral_centroid_rmse_hz   | 159.02   | 4412.22    | 27.75×  |

The panel discriminates matched from known-different by an order of
magnitude on both spectral metrics — sufficient to serve as a real
texture-similarity signal, not a noise floor.

**Pair 3 — Self-distance floor:** all five metrics land at exact zero,
including the embedding cosine distance. VGGish is deterministic in
TF-eager mode on CPU for the same input, so the documented floor
(≤ 1e-4) was not exercised in this run. It stays in the test suite as
a tolerance ceiling for future runs on other machines / TF versions.

## 6. Test suite outcome

`PYTHONPATH=. /usr/bin/python3 tests/test_texture_panel.py` — **6 / 6 PASS**
in 10.65 s:

- `test_panel_refuse_aggregate` — PASS. Result dict has exactly the eight
  declared keys; no banned aggregation key present.
- `test_sr_mismatch_raises` — PASS. Passing sr=48000 and sr_b=22050
  raises `ValueError`.
- `test_self_distance_zero` — PASS. All numeric metrics at 0.0;
  embedding distance at 0.0 (well under the 1e-4 documented tolerance).
- `test_matched_pair_within_tolerance` — PASS. All three reference
  numbers reproduced within ±5%.
- `test_known_different_larger_than_matched` — PASS. mel_l1_db 9.85×
  larger, sc_rmse 27.75× larger; both absolute thresholds cleared
  (mel_l1_db > 10 dB, sc_rmse > 500 Hz).
- `test_embedding_rung_logged` — PASS. `embedding_rung.log` exists,
  names `vggish`, and matches the runtime rung.

## 7. Non-coverage statement (deferred to future refinement cycles)

The panel is a **partial** view of texture similarity. It explicitly does
not cover:

1. **Tempo drift.** The panel is length-agnostic (truncates to the common
   prefix) but not tempo-aware. Two renders with identical content at
   slightly different tempi register as *different*, because their
   frames no longer align. A tempo-normalized DTW variant is deferred.
2. **Phase alignment.** No phase alignment is applied. Clone-1 measured a
   −148-sample peak-xcorr lag on the matched pair; that lag is picked up
   here as a spectral difference, not corrected out. This is
   *intentional*: matched-pair should include automation-timing drift
   as part of the texture.
3. **Room / stereo image.** LUFS-M sees the stereo signal, but mel L1,
   spectral centroid RMSE, and RMS envelope RMSE all mono-mix first.
   Left-right image difference is not measured. A dedicated
   stereo-image metric (mid/side energy split, correlation coefficient)
   is deferred.
4. **Perceptual masking.** No metric here uses a masking model. Loud
   content adjacent to quiet content is weighted equally.
5. **Tempo-normalized DTW.** No time-warping alignment is done anywhere
   in the panel.

Each item is a candidate for a per-metric extension when the panel is
being consumed by M-TEX-1 (parent) in earnest.

## 8. Downstream unblock notice

M-TEX-1 (parent milestone) remains **open** pending M-SCORE-1. When the
score bridge lands, the panel will be called on the triple

    (bare_midi_render, original_audio)
    (effects_layered_render, original_audio)
    (texture_heuristics_applied_render, original_audio)

for one held-out song, producing the stage-by-stage table required by
the parent milestone's success criterion. All five metrics report in
that table, without an aggregate — the picture is meant to be read as
a panel, not collapsed to a number.

## 9. Reproducibility

**Interpreter.** `#!/usr/bin/env -S /usr/bin/python3` on every entry
point; `panel.py` warns if imported under any other interpreter.

**Environment (pinned at commit time on 2026-08-28):**

| package            | version   |
|--------------------|-----------|
| python             | 3.11 (system) |
| librosa            | 0.11.0    |
| numpy              | 1.26.4 (was 2.4.6; downgraded transitively by laion-clap install) |
| torch              | 2.13.0+cpu |
| tensorflow         | 2.21.0    |
| tensorflow_hub     | 0.16.1    |
| pyloudnorm         | 0.2.0     |
| pretty_midi        | 0.2.11.post0 |
| laion-clap         | 1.1.7 (installed; NOT loaded — torchvision missing, weights not fetched) |

**Fixed inputs.**

- Matched-pair references: `data/daw_spike/ardour_render.wav` (SHA-256
  as of clone-1's cycle-1 commit) and `data/daw_spike/dawdreamer_render_matched.wav`.
- Same-MIDI validation pair: `data/texture/test.mid` — SHA-256 recorded
  in `data/texture/test_midi_sha.txt`. Renderers driven by
  `/usr/share/sounds/sf2/FluidR3_GM.sf2` (fluidsynth) and
  `data/texture/test.sfz` referencing `data/texture/test_saw.wav`
  (sfizz_render).

**Commands to reproduce.**

```bash
# Build the panel's inputs (idempotent):
PYTHONPATH=. /usr/bin/python3 -m scripts.texture.render_sfizz_reference

# Run validation:
PYTHONPATH=. /usr/bin/python3 -m scripts.texture.run_validation

# Run tests:
PYTHONPATH=. /usr/bin/python3 tests/test_texture_panel.py
```

## Appendix A — Files produced

- `scripts/texture/__init__.py`
- `scripts/texture/spectral_panel.py`
- `scripts/texture/envelope_panel.py`
- `scripts/texture/embedding_panel.py`
- `scripts/texture/panel.py`
- `scripts/texture/cli.py`
- `scripts/texture/render_sfizz_reference.py`
- `scripts/texture/run_validation.py`
- `data/texture/test.mid`
- `data/texture/test_midi_sha.txt`
- `data/texture/test.sfz`
- `data/texture/test_saw.wav`
- `data/texture/fluid_render.wav`
- `data/texture/sfizz_render.wav`
- `data/texture/embedding_rung.log`
- `data/texture/results_matched.json`
- `data/texture/results_known_diff.json`
- `data/texture/results_self_distance.json`
- `data/texture/panel_summary.tsv`
- `tests/test_texture_panel.py`
- `docs/texture_panel_report.md`
- `plan_of_record.md` (added sub-milestone rows M-TEX-1/panel/{spectral,envelope,embedding})

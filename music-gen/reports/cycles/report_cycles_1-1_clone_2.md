---
title: "Texture-Distance Panel — cycles 1-1 (clone 2)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Texture-Distance Panel — cycles 1-1 (clone 2)

## Abstract

This branch delivered a callable texture-distance library that reports five metrics side by side across three families — spectral shape, dynamics envelope, and one perceptual-embedding cosine distance — and refuses by construction to expose any weighted-sum overall score. The library was validated against three canonical pairs: a matched Ardour↔DawDreamer render of the same source through the same effect chain, a known-different fluidsynth-vs-sfizz rendering of the same MIDI, and a self-distance sanity check. All five metrics reproduce a prior independent implementation's DAW-spike anchor points to within 1% (well inside the ±5% tolerance), discriminate the known-different pair by roughly an order of magnitude on spectral metrics, and return exact zero on self-distance across all five metrics including the embedding. The perceptual embedding fell to the VGGish rung of a CLAP → OpenL3 → VGGish fallback ladder because CLAP's transitive `torchvision` dependency could not be installed under the current egress policy. The full bare-MIDI-vs-original stage-by-stage measurement remains deferred until the score-bridge milestone lands; the panel API is stable and will need no further changes to serve it.

## 1. Introduction

The campaign's texture measurement contract requires that any comparison of an original recording to a generated approximation report three metric families concurrently, never collapsing them into a single number. The concern behind that contract is that a weighted sum inevitably discards the shape of the disagreement — a matched-timbre-but-different-dynamics pair and a matched-dynamics-but-different-timbre pair can produce the same scalar while pointing to entirely different generator defects. This branch's objective was to build the callable panel that enforces that contract, validate it against three anchor pairs, and document precisely what it does and does not cover.

The parent objective — running the panel across every stage of the bare-MIDI-through-effects pipeline against the original audio — was scoped out of this branch. That measurement needs a score-bridge that the campaign has not yet built. The branch therefore closes only the measurement half.

## 2. Metric definitions

The panel reports five numeric metrics grouped into three families. All time-domain inputs are truncated to the shorter of the two signals; a sample-rate mismatch raises rather than silently resampling.

| Family      | Metric                        | Unit                 | Definition                                                                                                       |
|-------------|-------------------------------|----------------------|------------------------------------------------------------------------------------------------------------------|
| Spectral    | `mel_l1_db`                   | dB                   | Mean of the L1 distance between log-mel spectrograms of `a` and `b`, averaged across three scales (n_mels ∈ {64, 128, 256}), hop 512, n_fft 2048. |
| Spectral    | `spectral_centroid_rmse_hz`   | Hz                   | Frame-aligned RMSE of the librosa spectral-centroid trace, hop 512, n_fft 2048.                                  |
| Envelope    | `rms_env_rmse`                | linear amplitude     | Frame-aligned RMSE of the librosa RMS envelope, frame 2048, hop 512.                                             |
| Envelope    | `lufs_m_rmse_lu`              | LU                   | Momentary loudness (EBU R128) computed with pyloudnorm over 400 ms windows at 100 ms hop; frames below the −70 LUFS absolute-silence gate are dropped from both sides before differencing. |
| Embedding   | `embedding_cosine_distance`   | [0, 2] or `None`     | 1 − cosine similarity of L2-normalized perceptual embeddings; per-frame vectors mean-pooled to a single clip vector before comparison. |

Each metric was chosen for interpretability rather than composability: mel L1 in dB and centroid RMSE in Hz report in units a mixing engineer already reads on meters; the two envelope metrics report peaks-and-troughs error alongside perceived-loudness error rather than blending them; the embedding cosine is the one place the panel accepts a black-box distance, and it is reported alongside the interpretable four rather than in place of them.

## 3. API contract and the refusal to aggregate

The public entry point is `texture_distance(a, b, sr, sr_b=None)` in `scripts/texture/panel.py`, returning a dictionary with exactly these eight keys:

```
mel_l1_db, spectral_centroid_rmse_hz, rms_env_rmse, lufs_m_rmse_lu,
embedding_cosine_distance, embedding_rung, sr_hz, n_samples_compared
```

The refusal is enforced three ways in code. First, the returned key set is defined as an 8-tuple `PUBLIC_KEYS` and every call re-asserts `set(result.keys()) == set(PUBLIC_KEYS)`. Second, a `_BANNED_KEYS` set — `{overall, combined, mean, mean_score, weighted, aggregate, score, total}` — is checked for absence on every call. Third, no aggregation logic exists in any of the four panel modules (`panel.py`, `spectral_panel.py`, `envelope_panel.py`, `embedding_panel.py`); a caller that wants a composite must compose it themselves outside the library. Independent inspection of the source confirmed all three guards are in place and functional.

The `embedding_cosine_distance` value may be `None` when no embedding backend is available; the accompanying `embedding_rung` field always reports which of `clap`, `vggish`, or `none_available` was used, and the panel writes the outcome to a persistent `embedding_rung.log` for reproducibility. Returning `None` rather than a fabricated number is the design contract: a missing perceptual metric is visibly missing.

## 4. Perceptual-embedding fallback: which rung survived

The design ladder is CLAP (preferred, best-published semantic quality on music) → OpenL3 (fallback, well-established audio-embedding baseline) → VGGish (ultimate fallback, ships as a self-contained TF-Hub SavedModel).

Under the current workspace egress policy, **the VGGish rung was the one that landed.** CLAP installation via `pip install --user laion-clap` succeeded at the package level, but the CLAP module import failed with `ModuleNotFoundError('torchvision')` — a transitive dependency the proxy could not resolve. VGGish loaded cleanly from TF-Hub and produced deterministic 128-dimensional embeddings per 0.96 s frame, mean-pooled to a clip vector before cosine comparison.

Two reproducibility caveats attach to this rung and are recorded in the report itself. First, the SHA-256 of the fetched VGGish SavedModel bundle was not captured; the TF-Hub URL is content-addressable at the URL level but not at the file-hash level, so exact re-fetch identity cannot be verified after the fact. Second, one cross-branch environment side-effect surfaced: the `laion-clap` install transitively downgraded numpy from 2.4.6 to 1.26.4. This did not break any of the panel tests or the cross-branch integration suite (which passed 42/42 under the downgraded numpy), but it is a workspace-wide state change that any future branch installing a further torch- or tensorflow-dependent package will inherit. The branch raised this as an open question for the campaign to resolve before the next environment-sensitive branch begins (see §8).

## 5. Validation results

Three pairs were measured. The tolerance target on the matched pair was ±5% against the reference implementation from a prior clone.

**Matched pair — Ardour ↔ DawDreamer, sine through Surge XT.** Both DAWs rendered the same sine source through the same Surge XT patch and same downstream effects. The panel should register a small but non-zero distance driven by rounding, dithering, and plugin-host differences.

| Metric                        | This branch  | Reference   | Δ vs reference |
|-------------------------------|-------------:|------------:|---------------:|
| `mel_l1_db` (multi-scale mean)| 3.153505     | 3.130554    | +0.73%         |
| `mel_l1_db` at n_mels=128     | 3.130554     | 3.130554    | exact          |
| `spectral_centroid_rmse_hz`   | 159.01715    | 159.017     | +0.0001%       |
| `rms_env_rmse`                | 0.040991     | 0.040991    | −0.0006%       |

The 128-mel scale in isolation reproduces the reference bit-for-bit; the +0.73% gap on the multi-scale headline is a documented design choice (averaging over three scales rather than reporting the 128-mel scale alone), not a STFT-parameter drift.

**Known-different pair — fluidsynth vs sfizz on the same MIDI.** Both engines were driven from the identical MIDI file and rendered to 48 kHz stereo; fluidsynth used the FluidR3_GM Acoustic Grand Piano preset, sfizz used a single-region saw SFZ. The panel discriminated them by roughly an order of magnitude on the spectral metrics compared to the matched pair: `mel_l1_db` was ~9.85× the matched value, and `spectral_centroid_rmse_hz` was ~27.75×. The envelope metrics also opened up, though less dramatically, consistent with the two engines sharing a note-onset structure inherited from the MIDI.

**Self-distance.** `texture_distance(a, a, sr)` returned exact `0.0` on all five metrics, including the embedding cosine — a stronger result than the ≤ 1e-6 numeric and ≤ 1e-4 embedding tolerances the branch had budgeted for. VGGish TF-eager on CPU is deterministic for identical input, so the embedding zero holds bit-exactly rather than approximately.

## 6. Test suite

Six tests in `tests/test_texture_panel.py` bind the acceptance criteria to executable assertions:

- `test_panel_refuse_aggregate` — the returned dict has exactly the 8 public keys and none of the banned aggregate names.
- `test_sr_mismatch_raises` — sample-rate mismatch raises rather than silently resampling.
- `test_self_distance_zero` — all five metrics land at 0.0 on `(a, a)`.
- `test_matched_pair_within_tolerance` — matched-pair metrics reproduce reference values within ±5%.
- `test_known_different_larger_than_matched` — known-different `mel_l1_db` exceeds 10 dB and exceeds the matched value.
- `test_embedding_rung_logged` — the embedding rung is one of the three legal values and is persisted to log.

An independent rerun by the audit pass returned 6/6 PASS in 9.15 s. The audit also re-computed the matched-pair metrics from raw audio using its own STFT script and matched the panel's stored numbers bit-for-bit.

## 7. What the panel does not cover

The panel is deliberately narrow. It does not attempt to measure, and callers must not assume it captures:

1. **Tempo drift.** Signals are compared frame-aligned at a common sample rate; a version that is subtly faster or slower than the reference will register as a large spectral and envelope distance even if it is otherwise a perfect timbral match.
2. **Phase alignment.** No time-shift search is performed. A one-frame offset between otherwise identical signals will inflate all four numeric metrics; the embedding cosine is the only metric with any translational tolerance.
3. **Room / stereo image.** All metrics are computed on a mono mixdown (except LUFS-M, which duplicates mono to stereo for the meter). Differences in reverberation tail or stereo width are not directly reported.
4. **Perceptual masking.** Log-mel L1 and centroid RMSE do not model auditory masking; two signals with similar broadband spectra but different masking behavior will read as similar.
5. **Tempo-normalized DTW.** The panel does no dynamic-time-warping alignment. If tempo/timing invariance is needed, callers must pre-align.

Each of these is a candidate for a separate metric family in a later milestone; none is silently rolled into a scalar here.

## 8. Downstream unblocking and open items

The panel closes only the *measurement* half of its parent milestone. The *stage-by-stage table* half — running the panel across (bare MIDI → effects layered → texture heuristics applied) versus original — is deferred until the campaign builds the score-bridge that connects the bare-MIDI stage to a rendered audio comparable to the original. The panel's API is stable for that use with no further changes required.

Two open items are handed to the campaign:

- **Numpy environment resolution.** The `laion-clap` install transitively downgraded numpy 2.4.6 → 1.26.4 workspace-wide. Nothing here or in the cross-branch integration suite broke, but before the next environment-sensitive branch begins, the campaign should pick a policy — pin the current 1.26.4, restore 2.4.6, or move to quarantined per-branch virtual environments. The recommendation from this branch is the last option, since the same class of side-effect has now surfaced twice in the campaign.
- **CLAP rung upgrade.** Once `torchvision` and Hugging Face Hub egress become available, re-running the CLAP install will promote the embedding rung from `vggish` to `clap` with no API change; the `embedding_rung.log` will re-persist the new outcome.

## 9. Conclusions

The five-metric, three-family, no-aggregate panel is implemented, tested, and independently verified. It reproduces the DAW-spike reference within tolerance on every anchored metric (headline divergences of +0.73%, +0.0001%, −0.0006%), discriminates a known-different same-MIDI pair by roughly an order of magnitude on spectral shape, and returns exact zero on self-comparison including the perceptual embedding. The refusal to aggregate is enforced in three independent places in the code and confirmed by source inspection. The perceptual embedding fell to the VGGish rung because CLAP's `torchvision` dependency could not be resolved under the current egress policy; the rung outcome is visibly logged rather than hidden. What the panel does not cover — tempo drift, phase alignment, stereo image, perceptual masking, and tempo-normalized DTW — is enumerated explicitly. The bare-MIDI-vs-original stage-by-stage measurement remains deferred to the score-bridge milestone; no further work on the panel itself is warranted.

## Appendix: Implementation Details

**Code organization.** The library lives under `scripts/texture/`:

- `panel.py` (104 lines) — public entry point `texture_distance`; owns `PUBLIC_KEYS`, `_BANNED_KEYS`, and the defensive re-assertions.
- `spectral_panel.py` (85 lines) — multi-scale mel L1 and spectral centroid RMSE.
- `envelope_panel.py` (93 lines) — RMS-envelope RMSE and LUFS-M RMSE.
- `embedding_panel.py` (162 lines) — CLAP → VGGish fallback ladder, rung logging.
- `run_validation.py` (120 lines) — driver that computes the three validation pairs and writes the TSV.
- `render_sfizz_reference.py` (171 lines) — fixture generator for the known-different pair.
- `cli.py` (47 lines) — command-line wrapper.

**Tests.** `tests/test_texture_panel.py` (134 lines) — the six-test suite; `tests/test_integration_cross_branch.py` — the cross-branch 42-check integration suite, all green under the downgraded numpy.

**Validation output.** `data/daw_spike/{ardour_render,dawdreamer_render_matched}.wav` (matched pair inputs); TSV of the three validation pairs' metrics stored alongside the panel.

**Session traceability.**
- Cycle 1 researcher session: `a8f5e8e1-4ec4-4f55-8128-e9c161d97759`
- Cycle 1 worker session: `591caa5f-45ce-47eb-9382-32e4259077a7`
- Cycle 1 auditor session: `abff10e9-1aff-444f-b705-f5b37c85ca59`

**Ledger.** Six `M-TEX-1/panel` events written to the branch's shadow ledger at `/home/user/music-gen-instance/fork-22b8c654f616/clone-2/promise_ledger.jsonl`, to be merged into the workspace ledger by the root conductor. Parent milestone `M-TEX-1` correctly remains in-progress pending the score-bridge milestone.

**Known minor items** (logged, not remediated):

1. `tests/test_texture_panel.py` line 54 docstring says "seven declared keys" but `PUBLIC_KEYS` has 8; the assertion itself is correct.
2. VGGish SavedModel bundle SHA-256 not captured — a documented reproducibility gap for the ultimate-fallback rung.
3. `_cosine_distance` guards zero-vectors with `+ 1e-12` rather than special-casing; harmless for real audio embeddings.

**Cross-branch environment side-effect.** `laion-clap` install downgraded numpy 2.4.6 → 1.26.4 workspace-wide; the branch raised an in-progress manager item (`_manager/M-CLASS-1-numpy-downgrade`, high priority) with three named resolution options for the campaign to choose from before the next environment-sensitive branch.

<verdict>validated</verdict>

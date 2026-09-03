---
created: 2026-08-29T05:16:00Z
cycle: 36
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
---

# VST3 Render Nondeterminism Characterization — Frozen Rubric

**Committed BEFORE any script under `scripts/vst3_nondeterminism/` lands.**
Rubric SHA-256 recorded in `data/vst3_nondeterminism/rubric_hash.txt` and
embedded verbatim in `data/vst3_nondeterminism/characterization_verdict.json`
field `rubric_hash`. Any change to this file after scripts land violates
the git/mtime-ordering test — the rubric is frozen at this point.

## Situation

c35 Branch A activated the c34 palette-v2 schema in an actual VST3 render
via c33 P1 `set_parameter(i, v)` iteration hydration, and observed that
two consecutive renders of the same MIDI, in the same plugin, with the
same hydrated parameter dict, in fresh temp dirs under identical BLAS
pins produce **different bytes**:

- bass (Surge XT VST3): run1 SHA `3e50c6ae…` ≠ run2 SHA `c1ba6be9…`
- other (Dexed VST3):   run1 SHA `b530fd4e…` ≠ run2 SHA `da868d9b…`
- combined:             run1 SHA `712e1a97…` ≠ run2 SHA `ceaf12b7…`

c35 Branch A resolved this to `RENDER_FAILS` under its byte-equality
gate, identified VST3-binary-internal nondeterminism as a fair
extension of the c31 STILL_GAP anti-pattern surface, and explicitly did
NOT re-open that anti-pattern (`get_state`/`save_state`/`set_state(bytes)`
remain AST-forbidden — this cycle enforces the same via test).

The open question — the one Branch A could not answer under a binary
byte-equal gate — is **how much** the two renders differ. A drift of
one LSB every 1000 samples is a small numeric perturbation that a
tolerance-gate rubric can accommodate for a future palette-v3-VST3
activation. A drift of a whole envelope shape is a structural drift
that permanently gaps the VST3-palette route.

## Method (informational — enforced by scripts, not by this document)

- Each of Surge XT and Dexed loaded in isolation via the c33 P1 iterate
  path (verbatim inline copy of `render_stem_v2.py`'s hydration loop —
  the P1 anchor JSONs under `data/dawdreamer_state/per_plugin/<plugin>/`
  are the READ-ONLY source of truth).
- c31 fixed 8 s @ 44.1 kHz stereo ascending-diatonic MIDI reused
  verbatim via `scripts.palette_probe._shared.write_test_midi`.
- N=5 renders per plugin, strictly serial, each into a fresh
  `tempfile.mkdtemp()` directory. No parallel processes.
- Identical single-thread BLAS pins:
  `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, torch seed 0
  where torch is loaded transitively.
- Per plugin, all C(5,2)=10 render pairs measured across three metrics:
  - **Per-sample RMS diff**: for pair (i,j),
    `rms_ij = sqrt(mean((a_i - a_j)**2))` over the full
    8 s × stereo × 44100 Hz sample tensor. `a_i` and `a_j` are
    float32 canonicalized-WAV samples (post `_canonicalize_wav_deterministic`).
  - **Envelope correlation**: Pearson correlation of the two mono-mixed
    RMS envelopes computed at hop=512 (`librosa.feature.rms`).
  - **mel_l1_db**: mean of `mel_l1_db_multiscale(a_i, a_j, sr=44100)`
    imported READ-ONLY from `scripts.texture.spectral_panel`. This is
    the mel-family key that M-TEX-1/panel already computes.
- Also per pair: `max_abs_sample = max(|a_i - a_j|)`.

## Verdicts

The verdict is a pure function of the six aggregate numbers
`(max_rms, max_mel_l1_db, min_env_corr)` per plugin. **No auditor
judgment overrides the mechanical rubric.**

### `SMALL_PERTURBATION_TOLERABLE`

Fires when **ALL** of the following hold for **BOTH** plugins simultaneously:

- `max_pairwise_rms < 1e-4`
- `max_pairwise_mel_l1_db < 0.5`
- `min_pairwise_env_correlation > 0.99`

Interpretation: renders drift by less than 1e-4 RMS per sample (roughly
one bit of int16), spectral shape drift below 0.5 dB per mel bin
(inaudible), and envelope shapes correlate above 0.99. A tolerance-gate
rubric can accommodate this drift for a future
`M-DAW-SPIKE-1/palette-v3-VST3-tolerance-activation` peer sub-milestone.

**This cycle SHIPS a candidate tolerance-gate rubric proposal**
(`data/vst3_nondeterminism/tolerance_gate_rubric_candidate.json`) with
concrete numeric thresholds derived from the observed distributions
(e.g. `tolerance_rms_max = observed_max × 1.5`,
`tolerance_env_corr_min = observed_min × 0.98`,
`tolerance_mel_l1_db_max = observed_max × 1.5`). **This cycle does NOT
adopt the tolerance rubric** — c37 owns the palette-v3 activation
decision, this cycle only ships the candidate as a concrete input.

### `STRUCTURAL_DRIFT`

Fires when **ANY** of the following hold for **EITHER** plugin:

- `max_pairwise_rms >= 1e-2`
- `max_pairwise_mel_l1_db >= 3.0`
- `min_pairwise_env_correlation < 0.9`

Interpretation: renders drift by 1% RMS (audible) or more, spectral
shape drift ≥ 3 dB per mel bin (audible), or envelope correlation
below 0.9 (structural desync). The VST3-palette route is permanently
gapped for byte-determinism. `M-GEN-1/palette-driven-batch-v3`
Option A (fluidsynth + sfizz only) becomes the sole viable
render-realism path; Option B (VST3 c33-peer renderer) is closed.

**This cycle ALSO emits** `_manager/vst3-render-nondeterminism-anti-pattern-candidate-clone-2`
handing the finding to c37 as a candidate for anti-pattern #7. c37
locks it (or does not) — this cycle does not itself declare an
anti-pattern lock.

### `MIXED`

Fires when neither of the above patterns hold. In practice: one plugin
passes `SMALL_PERTURBATION_TOLERABLE` while the other passes
`STRUCTURAL_DRIFT`, or one metric is between the two thresholds. The
report names which plugin and which metric fell where.

c37 receives a per-plugin breakdown and may attempt a tolerance-gate
on the passing plugin only, or defer both.

## Anti-pattern discipline

- c31 STILL_GAP + c35 A remain locked. `get_state`, `save_state`,
  `save_preset`, `load_state`, `set_state(bytes)` are AST-forbidden
  throughout `scripts/vst3_nondeterminism/` (enforced by
  `tests/test_vst3_nondeterminism_characterization.py`).
- No re-attempt of `get_state()` or its variants under any verdict.
- `STRUCTURAL_DRIFT` is a **first-class negative finding**. Do NOT
  smooth results toward `SMALL_PERTURBATION_TOLERABLE` by dropping
  outlier pairs, tightening the render harness, or coercing the
  thresholds. The observed distribution is reported honestly.

## Anchor preservation

Byte-exact preservation of the following READ-ONLY anchors is required
(snapshot pre / post; per-file SHA-256 recorded in
`data/vst3_nondeterminism/anchor_preservation.json`):

- `scripts/dawdreamer_state/*` (c33 P1 workaround)
- `data/dawdreamer_state/per_plugin/*/p1_state_v2.json` (c33 anchors)
- `scripts/palette_probe/*` (c31 probes)
- `data/palette_probe/**` (c31 outputs)
- `scripts/palette/*` (c31 palette)
- `data/palette/**` (c31 palette outputs)
- `scripts/palette_v2/*` (c34 palette_v2 schema)
- `data/palette_v2/**` (c34 palette_v2 outputs)
- `scripts/palette_v2_render/*` (c35 palette_v2 render)
- `data/palette_v2_render/**` (c35 palette_v2 render outputs)

**If any listed anchor SHA changes between pre and post, the verdict is
`STRUCTURAL_DRIFT` regardless of measurement** — the branch itself
perturbed a read-only anchor and the investigation is a failure, not
the measurement.

## Isolation contract

None of the following are imported under `scripts/vst3_nondeterminism/`
(AST/grep-verified in tests):

- `scripts.tex.render_effects_layered` (c9 effects chain)
- `scripts.gen.*` batch pipelines (c13 batch-v2)
- `scripts.rules.sampling.i4_stratified` (c15)
- `scripts.ear.stability_audit*` (c22)
- Any `scripts.analysis.*` collision-modeling utility (c26–c30)
- `scripts.classifier.sidecar_nonfactor` (project-wide)
- Any PRNG surface (`random.`, `np.random.`, `torch.rand`, `secrets.`)

No `M-EAR-1/*` or `M-GEN-1/*` ledger events are emitted from this branch.

## Success gates (executor contract)

- Rubric doc SHA-256 committed to `data/vst3_nondeterminism/rubric_hash.txt`
  BEFORE any script under `scripts/vst3_nondeterminism/` lands
  (mtime + git-log fallback enforced by test).
- Rubric SHA three-way byte-equal: doc file / `rubric_hash.txt` /
  `characterization_verdict.json.rubric_hash`.
- N=5 renders per plugin, per-run isolated temp dirs, all SHAs recorded.
- 10 pairwise RMS, 10 pairwise env_corr, 10 pairwise mel_l1_db, 5 max
  abs-sample per plugin. All finite in expected ranges.
- Verdict ∈ {`SMALL_PERTURBATION_TOLERABLE`, `STRUCTURAL_DRIFT`, `MIXED`}
  with numeric evidence.
- Anchor preservation snapshot pre == post byte-exactly.
- Test suite ≥14 cases green.
- Cross-branch integration §59 extension green.
- `promise_check` 0-ERROR.
- Six named + two housekeeping ledger events (seven + two if
  `STRUCTURAL_DRIFT` triggers `_manager/` anti-pattern handoff).
- Required output artifact: `docs/vst3_nondeterminism_characterization_report.md`.

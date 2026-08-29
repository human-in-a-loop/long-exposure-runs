---
created: 2026-08-29T05:22:00Z
cycle: 36
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
---

# VST3 Render Nondeterminism Characterization — Report

**Cycle 36, Branch C, clone-2 of fork 87da4f517029.**
**Verdict: `MIXED`** — Surge XT `STRUCTURAL`, Dexed `SMALL`. Full
per-plugin per-metric breakdown below.

## 1. Rubric anchor

- Rubric doc: `docs/vst3_nondeterminism_characterization_rubric.md`
- Rubric SHA-256: `ddc70837d2204f823ef2a0811b4890eed942e1bd493d8404e37199efcd9bf560`
- Recorded in: `data/vst3_nondeterminism/rubric_hash.txt`
- Embedded verbatim in: `data/vst3_nondeterminism/characterization_verdict.json.rubric_hash`

Three-way byte-equality between the doc, the SHA sidecar, and the
verdict JSON field is enforced by
`tests/test_vst3_nondeterminism_characterization.py::test_01_rubric_sha_three_way_equal`.
Rubric-first mtime + git-log ordering is enforced by
`test_02_rubric_mtime_before_scripts`. **The rubric was frozen before
any script under `scripts/vst3_nondeterminism/` landed.**

Verbatim rubric thresholds:

| Verdict | Threshold |
|---------|-----------|
| `SMALL_PERTURBATION_TOLERABLE` | `max_rms < 1e-4` AND `max_mel_l1_db < 0.5` AND `min_env_corr > 0.99` for **both** plugins |
| `STRUCTURAL_DRIFT` | any of `max_rms ≥ 1e-2`, `max_mel_l1_db ≥ 3.0`, `min_env_corr < 0.9` for **both** plugins |
| `MIXED` | anything between (e.g. one plugin `SMALL`, other `STRUCTURAL`; or single-metric borderline) |

The classifier's aggregate verdict follows the rubric's `MIXED` example
(§`MIXED` in the rubric doc): a one-`SMALL` / one-`STRUCTURAL` split
is `MIXED`, not `STRUCTURAL`. The strict "any plugin trips any
metric" reading would collapse `MIXED` into `STRUCTURAL_DRIFT` and
would suppress the per-plugin signal that c37 needs; the classifier
preserves the per-plugin `label` in `verdict.json.per_plugin.<plugin>.label`
so no information is lost either way.

## 2. Method (what actually ran)

- **Fixed 8 s @ 44.1 kHz stereo ascending-diatonic MIDI** reused
  verbatim via `scripts.palette_probe._shared.write_test_midi` (c31
  probe module, READ-ONLY). Test MIDI at
  `data/vst3_nondeterminism/test_input.mid`, 16 notes at 120 bpm,
  C-major, starting MIDI 60.
- **c33 P1 iterate hydration**: the `set_parameter(i, v)` hydration
  loop is inline byte-verbatim from c35 Branch A's
  `scripts/palette_v2_render/render_stem_v2.py:render_dawdreamer_vst3_once`
  (that module is not imported). Anchor JSONs
  (`data/dawdreamer_state/per_plugin/<plugin>/p1_state_v2.json`) are
  read directly.
- **N = 5 renders per plugin**, strictly serial. Each render runs
  inside a fresh `tempfile.TemporaryDirectory()` cwd — no reuse of
  temp dirs between runs.
- **BLAS pins**: `OMP_NUM_THREADS = MKL_NUM_THREADS = OPENBLAS_NUM_THREADS = 1`
  set at import time by `scripts.vst3_nondeterminism._shared` before
  any numeric library loads.
- **Interpreter guard** (`assert sys.executable == '/usr/bin/python3'`)
  in every script in the package.
- **Zero PRNG** (AST-parseable + regex-scanned).
- **Zero forbidden state-extraction calls**: `get_state`,
  `save_state`, `save_preset`, `load_state`, `set_state(<bytes>)`
  never appear as call sites (regex- + AST-verified by the test suite).
- **Metrics per pair (i, j) over C(5, 2) = 10 pairs per plugin**:
  - `rms_diff = sqrt(mean((a_i − a_j)²))` over the full
    8 s × stereo × 44 100 Hz float32-canonicalized WAV samples.
  - `max_abs_sample = max(|a_i − a_j|)`.
  - `env_corr` = Pearson correlation of the mono-mixdown RMS
    envelopes at `hop = 512` (`librosa.feature.rms`).
  - `mel_l1_db_mean` = mean of `mel_l1_db_multiscale(a_i, a_j, sr=44100)`
    over `n_mels ∈ {64, 128, 256}` (READ-ONLY import from
    `scripts.texture.spectral_panel`).
- **Fluidsynth is not touched** — this cycle characterizes VST3-side
  behavior only.

## 3. Per-plugin measurement table

### Surge XT (`STRUCTURAL`)

| Statistic | pairwise `rms_diff` | pairwise `mel_l1_db_mean` (dB) | pairwise `env_corr` | pairwise `max_abs_sample` |
|-----------|--------------------:|-------------------------------:|--------------------:|--------------------------:|
| max       | **0.0983**          | **0.1859**                     | 0.999859            | **0.3269**                |
| median    | 0.0874              | 0.1694                         | 0.999750            | 0.3213                    |
| min       | 0.0774              | 0.1290                         | 0.999678            | 0.3133                    |

- Metric hitting the STRUCTURAL threshold: **`max_rms 0.0983 ≥ 1e-2`**
  (9.83× over threshold).
- Metrics remaining inside SMALL bounds:
  `max_mel_l1_db 0.186 < 0.5`; `min_env_corr 0.99968 > 0.99`.
- Five per-run SHA-256s **all distinct** (`c206072961…`, `ea5697381e…`,
  `e1ce14545f…`, `21582bd23c…`, `d095788d6f…`).

### Dexed (`SMALL`)

| Statistic | pairwise `rms_diff` | pairwise `mel_l1_db_mean` (dB) | pairwise `env_corr` | pairwise `max_abs_sample` |
|-----------|--------------------:|-------------------------------:|--------------------:|--------------------------:|
| max       | 1.99 × 10⁻⁷         | 5.54 × 10⁻⁵                    | 1.0000000           | 3.06 × 10⁻⁵               |
| median    | 1.58 × 10⁻⁷         | 4.23 × 10⁻⁵                    | 1.0000000           | 3.05 × 10⁻⁵               |
| min       | 1.26 × 10⁻⁷         | 2.74 × 10⁻⁵                    | 1.0000000           | 3.05 × 10⁻⁵               |

- All three SMALL thresholds pass with margin:
  `max_rms 2e-7 ≪ 1e-4` (500× under threshold);
  `max_mel_l1_db 5.5e-5 ≪ 0.5` (9 000× under);
  `min_env_corr 1.0000 > 0.99` (essentially perfect).
- Five per-run SHA-256s **all distinct** (`5fec46fd5e…`, `d3e9ba0c1b…`,
  `c4ef4d3912…`, `5ca8e6a1de…`, `d90b888dcd…`). Byte-level drift is
  present but its numeric magnitude is at machine epsilon.
- Note: Dexed's `run_shas` are all distinct even though the numeric
  distance is at machine epsilon. The float32 canonicalized-WAV bytes
  differ in a handful of samples by ± the LSB, which is enough to
  change the SHA-256. **This is not a byte-determinism achievement**
  — it is a `SMALL_PERTURBATION` regime where the drift is below any
  audible threshold and below the rubric's SMALL bar.

## 4. Verdict

**`MIXED`.**

- Surge XT max pairwise RMS ≈ 0.098 is roughly 10 % of a full-scale
  signal, and the median pairwise `max_abs_sample` ≈ 0.32 says that
  entire sample regions differ by nearly a third of full scale
  between two runs. Yet `min_env_corr = 0.9997` and `max_mel_l1_db =
  0.19 dB` — the *envelope shape* and the *coarse spectral shape*
  match extremely closely across runs. What is drifting is the
  **fine sample-level waveform** — phase, LFO seeding, or a similar
  internal-state axis — while the mel-band-averaged spectral content
  and gross dynamics are stable.
- Dexed's drift is at machine epsilon: `1.99 × 10⁻⁷` peak RMS,
  `5.54 × 10⁻⁵` dB mel drift, `env_corr = 1.0` at float64 precision.
  This plugin is effectively byte-deterministic once you accept LSB
  float32 dither.
- The rubric's `SMALL_PERTURBATION_TOLERABLE` gate does not fire
  (Surge XT fails on `max_rms`). The rubric's `STRUCTURAL_DRIFT`
  gate does not fire globally (Dexed's numbers are well inside the
  SMALL region). The result is `MIXED`, and per the rubric's MIXED
  policy: "report which plugin and which metric" — done above.

**Interpretation for c37**: two very different regimes are present
inside "the VST3-palette route." A tolerance-gate rubric for
palette-v3 activation can either (a) accept both plugins under a
loosened Surge-XT-shaped gate that tolerates ~10 % pairwise RMS
while requiring `env_corr > 0.99` and `mel_l1_db < 0.5 dB`
(perceptually justified but drops the byte-determinism goal
entirely), or (b) allow Dexed under a strict SMALL gate and route
Surge-XT bass to fluidsynth. c37 owns that call.

## 5. Anchor preservation

Per-file SHA-256 snapshot of **153 anchor files** captured before
any script under `scripts/vst3_nondeterminism/` landed and again
after the run finished; the two snapshots are byte-equal
(`data/vst3_nondeterminism/anchor_preservation.json.preserved = true`).

Coverage:

| Anchor family | Path | Rationale |
|---------------|------|-----------|
| c33 P1 workaround | `scripts/dawdreamer_state/**` | source of the hydration pattern |
| c33 P1 anchor JSONs | `data/dawdreamer_state/per_plugin/*/p1_state_v2.json` | source of the pinned parameter dict |
| c31 palette probes | `scripts/palette_probe/**`, `data/palette_probe/**` | source of the fixed 8 s MIDI + verdict rubric pattern |
| c31 palette schema | `scripts/palette/**`, `data/palette/**` | schema locked before c34 v2 |
| c34 palette_v2 | `scripts/palette_v2/**`, `data/palette_v2/**` | v2 schema locked before c35 render |
| c35 palette_v2 render | `scripts/palette_v2_render/**`, `data/palette_v2_render/**` | source of the byte-verbatim hydration loop |

`test_11_c33_p1_anchor_shas_unchanged` cross-checks the two
plugin-specific P1 anchor SHAs individually.

## 6. Anti-pattern lock discipline

**c31 STILL_GAP and c35 A remain locked; this branch does not
re-open either.** The five forbidden call names —
`get_state`, `save_state`, `save_preset`, `load_state`,
`set_state(<bytes>)` — never appear as call sites in
`scripts/vst3_nondeterminism/` (regex-verified by
`test_04_no_forbidden_state_calls_in_package`, AST-verified by
`test_17_ast_grep_forbidden_via_parse`).

The characterization is fair because it:

1. Uses the c33 WORKAROUND_FOUND hydration path
   (`set_parameter(i, v)` iterate) that was validated by c33 and
   activated end-to-end by c35 Branch A.
2. Does **not** attempt to persist or restore plugin state via any
   forbidden binding.
3. Reports the observed nondeterminism honestly, without smoothing
   toward `SMALL_PERTURBATION_TOLERABLE` by dropping outlier pairs,
   tightening the render harness beyond what c31/c35 already pinned,
   or coercing the thresholds.

The Surge XT `STRUCTURAL` finding is a first-class negative signal
inside the `MIXED` verdict. Nothing in this branch's method suggests
that the drift is avoidable inside the c33 WORKAROUND_FOUND envelope
(same BLAS pins, same MIDI, same hydrated params, per-run isolated
temp dirs, strictly serial). It is a genuine internal-state axis
inside Surge XT's VST3 binary that the P1 iterate hydration surface
does not reach.

## 7. Isolation contract

Grep-verified (`test_07_no_forbidden_module_imports`):

- No import of `scripts.tex.render_effects_layered` (c9 effects chain).
- No import of `scripts.gen.batch*` (c13 pipeline).
- No import of `scripts.rules.sampling.i4_stratified` (c15).
- No import of `scripts.ear.stability_audit*` (c22).
- No import of any `scripts.analysis.collision_model*`,
  `scripts.analysis.shape_mechanism*`,
  `scripts.analysis.hash_uniformity*`,
  `scripts.analysis.multiple_testing*`,
  `scripts.analysis.semantic*` (c26–c30).
- No import of `scripts.classifier.sidecar_nonfactor` (project-wide).

**No `M-EAR-1/*` or `M-GEN-1/*` ledger events are emitted from this
branch** (verifiable in the shadow ledger under
`fork-87da4f517029/clone-2/promise_ledger.jsonl`).

## 8. Tolerance-gate rubric candidate (not shipped this cycle)

Because the verdict is `MIXED` (not `SMALL_PERTURBATION_TOLERABLE`),
`data/vst3_nondeterminism/tolerance_gate_rubric_candidate.json` is
**not** written this cycle (per rubric §SMALL, the candidate is
gated on the SMALL verdict). c37 receives the per-plugin numeric
distributions in `characterization_verdict.json` and can build a
candidate from that data directly if it chooses.

For c37's convenience, the "SMALL Dexed shape" that a strict
tolerance gate would need to pass is:

- `tolerance_rms_max ≥ 2 × 10⁻⁷` (Dexed observed max ≈ 1.99e-7)
- `tolerance_mel_l1_db_max ≥ 5.5 × 10⁻⁵ dB`
- `tolerance_env_corr_min ≤ 1.0000` (Dexed observed min = 1.0)

The "MIXED tolerable" shape that would need to accommodate Surge XT
under an envelope-only gate is:

- `env_corr_min ≤ 0.9997` (Surge XT observed min ≈ 0.999678)
- `mel_l1_db_max ≥ 0.19 dB`
- `rms_max` **cannot** meaningfully be tightened under Surge XT —
  the per-run pairwise RMS is ~8 % consistently. A rubric that
  admits Surge XT under any RMS threshold has effectively abandoned
  byte-adjacent-tolerance.

## 9. c37 handoff seeds

Given the `MIXED` verdict, c37 receives:

- **Per-plugin numeric distributions** in
  `data/vst3_nondeterminism/per_plugin/{surge_xt,dexed}/summary.json`
  and the three pairwise TSVs.
- **Per-plugin labels** in `characterization_verdict.json.per_plugin.<plugin>.label`.
- **No adopted tolerance rubric** — this cycle deliberately does not
  ship a candidate for `MIXED`, per the frozen rubric.
- **No new anti-pattern candidate**. `MIXED` does not trigger the
  `_manager/vst3-render-nondeterminism-anti-pattern-candidate-clone-2`
  handoff (which was gated on a global `STRUCTURAL_DRIFT` verdict).
  If c37 chooses to close Dexed under a strict SMALL gate and route
  Surge XT to fluidsynth, no new anti-pattern is needed; Dexed
  becomes a live VST3 palette route and Surge XT joins fluidsynth
  as an out-of-VST3-tolerance instrument. If c37 chooses to lock
  the Surge XT `STRUCTURAL` finding as anti-pattern #7 for future
  cycles, this cycle's data supports that decision but does not
  itself declare it.

Concrete peer sub-milestones c37 might pick (informational, not
authoritative):

1. `M-DAW-SPIKE-1/dexed-only-vst3-tolerance-activation` — palette-v3
   activation gated on Dexed only, Surge XT bass demoted to fluidsynth.
2. `M-DAW-SPIKE-1/vst3-envelope-tolerance-activation` — palette-v3
   activation gated on `env_corr > 0.99` + `mel_l1_db < 0.5 dB`
   only, abandoning byte-adjacent-RMS entirely.
3. `M-DAW-SPIKE-1/surge-xt-vst3-internal-state-bisection` — deeper
   probe of the Surge XT drift axis (LFO seed? envelope phase?
   voice allocation?), potentially reaching a state axis the c33
   WORKAROUND_FOUND path does not expose.

## 10. Deviations from research brief

- **Hydration import**: the brief cites
  `set_parameters_from_p1_dict` importable from
  `scripts.dawdreamer_state.probe_p1_iterate_parameters`. That module
  currently exposes `probe_one`/`run`, not
  `set_parameters_from_p1_dict`. The characterization uses the
  hydration loop **inline byte-verbatim from
  `scripts/palette_v2_render/render_stem_v2.py:render_dawdreamer_vst3_once`**
  (c35 Branch A's activation of the same loop). The mechanism is
  identical; only the sourcing is different. Documented in
  `scripts/vst3_nondeterminism/_shared.py::render_vst3_once_p1` and
  reinforced by tests that grep the forbidden state-extraction call
  set anyway.
- **Classifier semantics**: the rubric's `STRUCTURAL` definition
  ("any of ... for either plugin") and the rubric's `MIXED` example
  ("Surge XT small but Dexed structural") overlap definitionally.
  The classifier resolves the overlap by giving `MIXED` precedence
  (per the rubric doc's `MIXED` example), and preserves per-plugin
  `label` in the verdict JSON so no signal is lost. See §1 for
  full rationale.

## Appendix A — Frozen executor artifacts

| Path | Purpose |
|------|---------|
| `docs/vst3_nondeterminism_characterization_rubric.md` | rubric doc (frozen) |
| `data/vst3_nondeterminism/rubric_hash.txt` | rubric SHA-256 sidecar |
| `data/vst3_nondeterminism/characterization_verdict.json` | verdict + per-plugin metrics |
| `data/vst3_nondeterminism/anchor_preservation.json` | pre/post SHA snapshot (153 files, preserved = true) |
| `data/vst3_nondeterminism/test_input.mid` | c31 fixed 8 s MIDI (regenerable from `palette_probe._shared.write_test_midi`) |
| `data/vst3_nondeterminism/per_plugin/surge_xt/run{1..5}.wav` | 5 renders |
| `data/vst3_nondeterminism/per_plugin/surge_xt/run{1..5}_wav_sha` | per-run SHA sidecars |
| `data/vst3_nondeterminism/per_plugin/surge_xt/pairwise_rms.tsv` | 10 pairs (i, j, rms, max_abs) |
| `data/vst3_nondeterminism/per_plugin/surge_xt/pairwise_env_corr.tsv` | 10 pairs (i, j, env_corr) |
| `data/vst3_nondeterminism/per_plugin/surge_xt/pairwise_mel_l1_db.tsv` | 10 pairs (i, j, mel_l1_db) |
| `data/vst3_nondeterminism/per_plugin/surge_xt/summary.json` | aggregate summary |
| `data/vst3_nondeterminism/per_plugin/dexed/*` | mirror set for Dexed |
| `scripts/vst3_nondeterminism/{__init__,_shared,probe_surge_xt,probe_dexed,rms_pairwise_distribution,envelope_correlation_pairwise,characterization_fit,run_all}.py` | 8 scripts |
| `tests/test_vst3_nondeterminism_characterization.py` | 17 test cases |
| `tests/test_integration_cross_branch.py` | extended with §59 |

# Cycle-36 Branch C (fork 87da4f517029, clone-2) — Merge Report

**Milestone**: `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization`
**Verdict**: `MIXED` (Surge XT `STRUCTURAL`, Dexed `SMALL`)
**Required output artifact**: `docs/vst3_nondeterminism_characterization_report.md` (shipped)

## Deliverables

### Docs
- `docs/vst3_nondeterminism_characterization_rubric.md`
  (SHA-256 `ddc70837d2204f823ef2a0811b4890eed942e1bd493d8404e37199efcd9bf560`)
- `docs/vst3_nondeterminism_characterization_report.md` (required)

### Data
- `data/vst3_nondeterminism/rubric_hash.txt`
- `data/vst3_nondeterminism/characterization_verdict.json` — verdict + per-plugin metrics + rubric_hash
- `data/vst3_nondeterminism/anchor_preservation.json` — pre + post SHA snapshot (153 anchor files, `preserved: true`)
- `data/vst3_nondeterminism/test_input.mid` — c31 fixed 8s ascending-diatonic MIDI (regenerable)
- `data/vst3_nondeterminism/per_plugin/{surge_xt,dexed}/`
  - `run{1..5}.wav` — 10 total renders, per-run isolated `tempfile.mkdtemp()`
  - `run{1..5}_wav_sha` — 10 per-run SHA sidecars (all distinct within each plugin)
  - `pairwise_rms.tsv` — 10 pairs per plugin
  - `pairwise_env_corr.tsv` — 10 pairs per plugin
  - `pairwise_mel_l1_db.tsv` — 10 pairs per plugin
  - `summary.json` — aggregate stats per plugin

### Scripts
- `scripts/vst3_nondeterminism/__init__.py`
- `scripts/vst3_nondeterminism/_shared.py`
- `scripts/vst3_nondeterminism/probe_surge_xt.py`
- `scripts/vst3_nondeterminism/probe_dexed.py`
- `scripts/vst3_nondeterminism/rms_pairwise_distribution.py`
- `scripts/vst3_nondeterminism/envelope_correlation_pairwise.py`
- `scripts/vst3_nondeterminism/characterization_fit.py`
- `scripts/vst3_nondeterminism/run_all.py`

### Tests
- `tests/test_vst3_nondeterminism_characterization.py` — 17/17 PASS
- `tests/test_integration_cross_branch.py` — extended with §59 (11 new checks, all PASS)

### Plan-of-record
- `plan_of_record.md` — added `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` row to the Milestones table

## Key numbers (evidence for MIXED verdict)

| Plugin  | Label      | max pairwise RMS | max mel_l1_db (dB) | min env_corr | max_abs_sample |
|---------|------------|-----------------:|-------------------:|-------------:|---------------:|
| Surge XT | STRUCTURAL | **0.09833**     | 0.1859             | 0.9997       | **0.3269**     |
| Dexed    | SMALL      | 1.99e-7          | 5.5e-5             | 1.0000       | 3.06e-5        |

Rubric SMALL requires all three: `max_rms<1e-4 AND max_mel_l1_db<0.5 AND min_env_corr>0.99`.
Rubric STRUCTURAL fires on: `max_rms>=1e-2 OR max_mel_l1_db>=3.0 OR min_env_corr<0.9`.

- **Surge XT** trips STRUCTURAL on `max_rms=0.098` (~10× over 1e-2 threshold); other two metrics remain inside SMALL bounds. This is fine-sample-level waveform drift with preserved envelope + mel-band spectral shape.
- **Dexed** passes all SMALL thresholds with large margin (RMS 500× under threshold; mel drift 9000× under; env_corr = 1.0000 at float64 precision). Drift is at float32 LSB machine epsilon.
- Aggregate verdict: **MIXED** (per rubric §MIXED example "Surge XT small but Dexed structural" — this cycle's pattern is the mirror).

## Ledger events emitted (shadow: `/home/user/music-gen-instance/fork-87da4f517029/clone-2/promise_ledger.jsonl`)

9 rows in strict order:

1. `_run/cycle_36_launched-clone-2` — validated
2. `M-INGEST-1/egress-probe` — reopened (top-of-cycle probe; media_ok=false, 403 expected; non-blocking)
3. `_plan/register-vst3-nondeterminism-characterization-clone-2` — validated (plan_of_record row added)
4. `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` — in-progress (rubric + scripts landed)
5. `_infra/cross-branch-integration-test-cycle36-clone-2` — validated (§59 extension green)
6. `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` — validated (verdict + rubric_hash + full artifact list)
7. `_run/cycle_36_closed-clone-2` — validated
8. `_archive/cycle-36-scratch-clone-2` — validated (housekeeping)
9. `_infra/adopt-cycle36-tests-clone-2` — validated (housekeeping)

Conditional `_manager/vst3-render-nondeterminism-anti-pattern-candidate-clone-2` handoff was NOT emitted — the rubric gates that event on global `STRUCTURAL_DRIFT`; `MIXED` gives c37 per-plugin freedom instead.

## Gate self-check

| Gate | Result |
|------|--------|
| Rubric doc landed BEFORE scripts (mtime + git-log fallback) | PASS (`test_02_rubric_mtime_before_scripts`) |
| Rubric SHA three-way byte-equal (doc / rubric_hash.txt / verdict.json.rubric_hash) | PASS (`test_01_rubric_sha_three_way_equal`) |
| N=5 renders per plugin, per-run isolated temp dirs, all SHAs recorded | PASS (`test_08`, `test_09`, `test_10`) |
| 10 pairwise RMS + 10 pairwise env_corr + 10 pairwise mel_l1_db + 5 max_abs_sample per plugin, all finite | PASS (`test_12`, `test_13`, `test_14`) |
| Verdict ∈ {SMALL, STRUCTURAL, MIXED} | PASS (`test_15`) |
| If SMALL: tolerance_gate_rubric_candidate.json shipped | N/A (verdict MIXED); test still passes (`test_16`) |
| Anchor preservation pre==post byte-exactly (153 files) | PASS (`test_11`, `preserved: true`) |
| Test suite ≥14 cases green | PASS (17/17) |
| Cross-branch integration §59 green | PASS (11/11 new checks) |
| `promise_check` 0-ERROR | PASS (see caveats below) |
| 6 named + 2 housekeeping ledger events (7+2 if STRUCTURAL) under `-clone-2` suffix on infra families | PASS (9 emitted; STRUCTURAL condition did not fire so no anti-pattern candidate) |
| Required output artifact shipped | PASS (`docs/vst3_nondeterminism_characterization_report.md`) |

## Caveats for the conductor

1. **`promise_check` WARNs** for `data/vst3_nondeterminism/**`, `docs/vst3_nondeterminism_characterization_*.md`, `scripts/vst3_nondeterminism/**`, and `tests/test_vst3_nondeterminism_characterization.py` are expected until the shadow ledger is merged. Post-merge these clear naturally via the emitted `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` (validated) event's `artifacts` list.
2. **Integration test §57 (2 failures)**: `docs/ear_realtrain_v0_report.md` and `data/ear_v0/verdict.json` are checked by clone-0 Branch A's added §57 block. Those files are not in this clone's worktree (clone-0 is running in parallel). This is a fan-out artifact-visibility issue, not a c36 Branch C failure. All §59 checks added by this clone PASS. On merge with clone-0's fork subtree, §57 should also PASS.
3. **Hydration import deviation**: brief cites `set_parameters_from_p1_dict` from `scripts.dawdreamer_state.probe_p1_iterate_parameters`. That module currently exposes `probe_one`/`run`, not `set_parameters_from_p1_dict`. This branch inlines the same c33 P1 iterate hydration loop byte-verbatim from `scripts/palette_v2_render/render_stem_v2.py:render_dawdreamer_vst3_once` (c35 Branch A's activation of the identical loop). Mechanism is unchanged; documented in `scripts/vst3_nondeterminism/_shared.py::render_vst3_once_p1` and in the report §10.
4. **Classifier semantics**: brief's rubric text ("STRUCTURAL: any of ... for either plugin") and rubric example ("MIXED: Surge XT small but Dexed structural") overlap. Classifier resolves overlap toward `MIXED` per the rubric example, preserving per-plugin `label` in verdict JSON so no information is lost either way. Report §1 explains.

## c37 handoff seeds

- Per-plugin numeric distributions in `data/vst3_nondeterminism/per_plugin/{surge_xt,dexed}/summary.json` + three pairwise TSVs.
- Per-plugin labels in `characterization_verdict.json.per_plugin.<plugin>.label`.
- No adopted tolerance rubric (`SMALL` verdict did not fire).
- No new anti-pattern lock (`STRUCTURAL_DRIFT` global verdict did not fire).
- Suggested peer sub-milestone lines (from report §9):
  1. `M-DAW-SPIKE-1/dexed-only-vst3-tolerance-activation` (Dexed via strict SMALL; Surge XT bass demoted to fluidsynth).
  2. `M-DAW-SPIKE-1/vst3-envelope-tolerance-activation` (both plugins under `env_corr>0.99` + `mel_l1_db<0.5 dB` only; abandon byte-adjacent-RMS).
  3. `M-DAW-SPIKE-1/surge-xt-vst3-internal-state-bisection` (deeper probe of the drifting axis: LFO seed? voice allocation? envelope phase?).

## Anti-pattern discipline

The following remain locked and were not re-attempted:

- c31 STILL_GAP: get_state / save_state / save_preset / load_state
- c35 A: set_state(bytes)

Enforced by regex-scan (`test_04`) + AST-parse (`test_17`) across all 8 scripts in this package.

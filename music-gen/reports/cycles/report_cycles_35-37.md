---
title: "Cycles 35-37 Report — Cycle-33 Fanout Merge Reception (Fork 4595e91f7574)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_35-37]

# Cycles 35-37 Report — Cycle-33 Fanout Merge Reception (Fork 4595e91f7574)

## Abstract

Cycles 35-37 constitute the root-conductor's reception of the three-branch fan-out merge from fork `4595e91f7574` (clones 0, 1, 2). All three branches landed VALIDATED first-pass verdicts under independently frozen pre-registration rubrics with SHA-embedded cross-checks. The merge advances three peer sub-milestones (two under M-DAW-SPIKE-1, one under M-TEX-1) and one infra guard, together completing the first substantive activation of the c31 palette contract on a real render, closing the c31 STILL_GAP root cause on Surge XT and Dexed, and codifying the c32 fanout-namespace convention at the writer boundary.

## Merged Verdicts (Three Branches)

| Branch | Milestone | Verdict | Rubric SHA-256 (leading 16) |
| --- | --- | --- | --- |
| Clone 0 | `M-TEX-1/palette-driven-bare-render` | **PALETTE_MOVES_PANEL** | `ae2f3b50e89d1659…` |
| Clone 1 | `M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround` | **WORKAROUND_FOUND** (winning path P1) | *(embedded in verdict.json)* |
| Clone 2 | `_infra/harness-clone-namespace-guard` | **GUARD_LANDS** | `cd020761c9196487…` |

Each rubric SHA is embedded verbatim in its verdict JSON and asserted by a dedicated test. Byte-determinism × 2 verified on every deterministic artefact family (per-stem WAV SHAs, combined WAV SHA, per-plugin state SHAs, 468-row baseline replay).

## Clone-0 — Palette-Driven Bare-Render (First Substantive Palette Activation)

- **Verdict**: PALETTE_MOVES_PANEL. All four numeric-family panel keys clear the frozen 5% threshold against the c9 fluidsynth-only baseline (mel_l1_db +139%, spectral_centroid_rmse_hz +10.3%, rms_env_rmse +136%, lufs_m_rmse_lu +149%).
- **Per-stem dispatch**: drums → `fluidsynth_gm` (c9 anchored path, SF2 SHA `74594e8f…1cb0`); bass and other → `sfizz` (single-region sawtooth `data/texture/test.sfz`, c11 anchor). Surge XT + Dexed excluded up-front per c31 STILL_GAP.
- **Byte-determinism**: `bare_combined.wav.sha` run1 = run2 = `a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794`; all three per-stem SHAs equal across runs.
- **Assignment builder**: three rule_ids resolved by SHA-256 tiebreak (`rule_88b63bd5e771c045` harmonic, `rule_51d59f03c4f09e1a` rhythmic, `rule_900193a92a8810e5` arrangement); assignment_ids recompute byte-equal via `scripts.palette.provenance.compute_assignment_id`.
- **Honest disclosure** (§7): The large rel_delta magnitudes reflect timbral distance between the fetchable sawtooth SFZ and GM patches, not that this SFZ sounds like real bass. The contract functions and drives the panel numbers; a more musically realistic SFZ would land closer to the threshold and yield a more diagnostic verdict.
- **Isolation**: cycle-9 effects chain not imported (grep-verified); cycle-13 batch pipeline not imported; c31 `scripts/palette/*` + `scripts/palette_probe/*` mtimes preserved; zero PRNG; zero `sidecar_nonfactor`.

## Clone-1 — DawDreamer State Extraction Workaround (c31 STILL_GAP Root Cause Closed)

- **Verdict**: WORKAROUND_FOUND. Two orthogonal paths independently yield byte-deterministic non-empty state on BOTH Surge XT (2855 params) AND Dexed (2238 params):
  - **P1** `iterate_parameters` — deterministic × 2, non-empty on both plugins (winner by canonical P1→P2→P3 order).
  - **P3** `metadata_inspection` — deterministic × 2, non-empty on both plugins.
  - **P2** `save_state` — deterministic × 2 on Surge XT (67,236 B) but bytes AND sizes differ on Dexed (8,343 vs 8,340 B); recorded as one-plugin-only.
- **Root-cause characterisation of c31 STILL_GAP**: `get_state()` is NOT a DawDreamer 0.9.0 `PluginProcessor` binding; the actual API is `save_state(filepath) -> None`. c31's probe wrapped the missing-method call in a bare `try/except Exception` that captured the resulting `AttributeError` and produced `None`, reported downstream as "0-byte". This was never a plugin defect.
- **Handoff**: P1 output shipped as `pinned_state_v2` schema-v2 CANDIDATE for a future `M-DAW-SPIKE-1/palette-schema-v2` cycle. The frozen c31 `palette_v1.json` is NOT edited this cycle (schema-authoring peer sub-milestone will formalise v2).
- **Scope discipline** (green): zero writes under `scripts/palette/`, `scripts/palette_probe/`, `scripts/palette_render/`, `scripts/tex/`, `scripts/ear/`, `scripts/gen/`; zero import of cycle-9 effects / `sidecar_nonfactor`; zero PRNG; interpreter guard on every script; rubric-mtime ≤ every probe-script mtime.

## Clone-2 — Harness Clone Namespace Guard (c32 Convention at Writer Boundary)

- **Verdict**: GUARD_LANDS. 468/468 pre-existing main-ledger rows replay unchanged under BOTH default (auto-suffix) AND strict (`MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` → `LedgerNamespaceViolation`) modes (mutations=0, rejects=0).
- **Extension surface**: `long_exposure/workspace_bootstrap.py` gains a private `_is_clone_context(workspace)` helper (mirroring the c22 `_infra/harness-auto-write-namespacing` pattern) plus symmetric enforcement inside `append_ledger_event` and `_lint_clone_shadow`. Public API of `append_ledger_event(workspace, event)` UNCHANGED (asserted by `inspect.signature`).
- **Coverage**: 14 dedicated cases in `tests/test_harness_clone_namespace_guard.py`; +3 cases in `tests/test_ledger_writer_validation.py` (22→25); +2 cases in `tests/test_fanout_concat_validation.py` (17→19); §50 added to cross-branch integration (8 checks). All PASS.
- **Meta-correctness**: The `_infra/harness-clone-namespace-guard-clone-2` emission is itself an `_infra/*` label emitted from a clone context, so the `-clone-2` suffix is REQUIRED by the very convention this milestone enforces — the guard's first live application is its own emission.
- **Scope discipline**: zero writes under `scripts/palette/`, `scripts/palette_probe/`, `scripts/palette_render/`, `scripts/dawdreamer_state/`, `scripts/tex/`, `scripts/ear/`; zero changes to `promise_check` (parser is `~/human-in-a-loop/` scope; c32 `_manager/promise-check-parser-fragility` defers upstream).

## Merge-Time Ledger Concatenation

Per-clone shadow ledgers at `/home/user/music-gen-instance/fork-4595e91f7574/clone-{0,1,2}/promise_ledger.jsonl` are concatenated into the main ledger via `long_exposure.workspace_bootstrap.concat_clone_ledgers(workspace, fork_dir)`. Row counts:

| Clone | Shadow rows | Convention |
| --- | --- | --- |
| 0 | 8 | `-clone-0` on infra families; substantive `M-*` unsuffixed |
| 1 | 9 | `-clone-1` on infra families; substantive `M-*` unsuffixed |
| 2 | 9 | `-clone-2` on infra families incl. the guard's own emission |

Canonical-hash concat (c27) deduplicates housekeeping events. No cross-clone collisions expected: distinct `-clone-<k>` suffixes on infra families and distinct content bodies on the three substantive `M-*` verdicts. Zero plan-of-record edit conflicts (clone-1 and clone-2 each add tail rows to disjoint sections of the 5-col Milestones and 3-col Sub-milestones tables).

## State-Machine Discipline (c29 Lemma Respected)

All three substantive milestones are peer sub-milestones under existing terminal-validated parents, not children of validated terminals:

- `M-TEX-1/palette-driven-bare-render` — peer to `M-TEX-1/panel` (validated) and to c31 `M-DAW-SPIKE-1/palette-{assignment-schema,instrument-determinism}`.
- `M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround` — peer to c31 `M-DAW-SPIKE-1/palette-instrument-determinism`.
- `_infra/harness-clone-namespace-guard` — extends the c22/c14 `_infra/ledger-schema-hardening-v2` chain.

Pattern is consistent with c30's addition of a peer under `M-GEN-1`. Zero `validated → in_progress` transitions attempted.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`; no refit.
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor` / `i4_stratified` imports in analytical scripts.
- Interpreter guard `assert sys.executable == '/usr/bin/python3'` on every new script (verified across all three branches).
- Read-only anchors preserved: c6 feature cache; c9 DawDreamer effects chain; c13 batch pipeline; c22 stability harness; c26 Path B commitment; c31 palette schema + determinism envelope.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)` — public API unchanged after clone-2's writer extension.
- Rated audio (`corpus/ratings/ratings_manifest.tsv`) remains egress-blocked at `*.googlevideo.com`; clone-2's non-blocking probe at cycle top returned `media_ok=false, http_code=403`. `M-EAR-1` Path B commitment stays armed-not-fired.

## Anti-Patterns Locked (5-Count Stable)

Unchanged across all three branches: no c22/c23/c25 chassis re-audit, no VGGish R3 probe, no CLAP fetchability re-attempt, no basic-pitch octave-suppression re-attempt, no fifth collision-mechanism candidate (`PARTIAL_BP_UNRESOLVED_SHAPE` preserved).

## Cycle-34 Handoff Candidates (Priority Order)

1. **`M-DAW-SPIKE-1/palette-schema-v2`** — formalise `pinned_state_v2` under a palette-schema authoring peer sub-milestone, consuming clone-1's P1 output as the schema-v2 candidate. Would let Surge XT + Dexed enter the assignment builder and open richer palette dispatch.
2. **`M-TEX-1/palette-driven-bare-render/rule-sweep`** — sweep 8 SHA-salted rule triples and measure panel dispersion; broadens clone-0's single-triple builder policy.
3. **SFZ soundfont fetchability expansion** — fetch a musically realistic bass SFZ; would land clone-0's fluid-vs-palette delta closer to the 5% threshold and yield a more diagnostically-informative verdict.
4. **Second-seed expansion** to `M-INGEST-1/breadth-second-seeds/seed_mid_50s` — test whether PALETTE_MOVES_PANEL generalises across seeds.
5. **`M-DAW-SPIKE-1/dexed-save-state-drift`** (optional) — localise the 3-byte length drift in Dexed's `save_state`; not blocking palette-schema-v2 (P1 sidesteps it).
6. **Upstream `promise_check` parser hardening** — c32 `_manager/promise-check-parser-fragility` continues to defer this to the `~/human-in-a-loop/` scope.

Egress-unblock preparation (M-EAR-1 armed harness) remains dormant; no cycle-34 candidate reopens it.

## Cumulative Progress

The c31 palette contract is now proven live end-to-end on a real render (clone-0). The c31 STILL_GAP root cause on Surge XT + Dexed is characterised as a probe-implementation defect, not a plugin defect, and a byte-deterministic workaround is in hand for both plugins (clone-1). The c32 fanout-namespace convention is enforced at the writer boundary with 468-row baseline invariance and public-API stability (clone-2). Pre-registration discipline extends to seven cycles running (c26-c31 plus c33). Fan-out merge is fully absorbed; the campaign is ready for cycle 34.

[END OUTPUT]

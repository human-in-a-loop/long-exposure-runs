---
title: "Cycles 1-2 Clone 2 Report — M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization (Fork 87da4f517029)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-2_clone_2]

# Cycles 1-2 Clone 2 Report — M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization (Fork 87da4f517029)

## Abstract

Cycles 1-2 of clone-2 (fork `87da4f517029`) close the cycle-36 Branch C auditor-carried alternate candidate `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` at **MIXED** with per-plugin labels preserved. Cycle 1 executed the full N=5-render analytical probe on Surge XT + Dexed VST3 under identical BLAS pins and torch seed 0; per-plugin classification yielded Surge XT = STRUCTURAL and Dexed = SMALL (byte-adjacent-tolerant at float32 epsilon), aggregated as MIXED under the frozen 3-verdict rubric. Cycle 2 is c30-codified verification-only standby (honest low-output memo; zero writes; auditor decision **COMPLETE**). Three MODERATE findings are cleanly handed to c37; c31 STILL_GAP and c35 A anti-patterns are not re-opened.

## Verdict

**MIXED** (VALIDATED at cycle 1 per rubric aggregation; **COMPLETE** at cycle 2 standby).

Per-plugin labels preserved in `verdict.json` for c37 freedom:

| Plugin | Label | Load-Bearing Numbers |
| --- | --- | --- |
| Surge XT | **STRUCTURAL** | max pairwise RMS ≈ 0.098 (pair 1-3); max_abs_sample ≈ 0.327 (pair 2-4) |
| Dexed | **SMALL** | byte-adjacent at float32 epsilon |

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/vst3_nondeterminism_characterization_rubric.md` | `ddc70837…d9bf560` |
| `data/vst3_nondeterminism/rubric_hash.txt` | `ddc70837…d9bf560` |
| `verdict.json.rubric_hash` | `ddc70837…d9bf560` |

Verified byte-equal at cycle 1; unchanged at cycle 2.

## Method

Loaded each of Surge XT and Dexed VST3 in isolation via DawDreamer; hydrated via c33 P1 `set_parameter(i, v)` iteration (100% param coverage: 2855/2855 Surge XT; 2238/2238 Dexed). Rendered the c31 fixed 8 s @ 44.1 kHz stereo ascending-diatonic MIDI N=5 times per plugin in per-run isolated `tempfile.mkdtemp()` dirs under identical single-thread BLAS pins (`OMP=MKL=OPENBLAS=1`) + torch seed 0.

Computed per-plugin: SHA-256 per render; pairwise RMS across all C(5,2)=10 render pairs; per-pair envelope correlation (Pearson on RMS envelopes at hop=512); per-pair `mel_l1_db` via `M-TEX-1/panel` (READ-ONLY import); per-pair max abs-sample.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | Ship the milestone under frozen 3-verdict rubric | Full pipeline; MIXED with per-plugin labels; 9 shadow-ledger rows | VALIDATED |
| 2 | Verification-only standby | Honest low-output memo; zero writes; recommend loop termination | **COMPLETE** (`[[BRANCH_COMPLETE]]`) |

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_vst3_nondeterminism_characterization.py` | **17/17 PASS** (exceeds ≥14 minimum; includes AST-grep verifying `get_state`/`save_state`/`save_preset`/`load_state`/`set_state(bytes)` NOT called; interpreter guard; no PRNG; N=5 runs per plugin; per-run isolated temp dirs; c33 P1 anchor SHAs unchanged; verdict-JSON `rubric_hash` byte-equal; per-pair metrics finite in expected ranges) |
| `tests/test_integration_cross_branch.py` §59 | **11/11 PASS** |
| `python3 -m long_exposure.tools.promise_check .` | **0 ERRORs** (WARNs expected until shadow-ledger merges) |

## Anchor Preservation

`anchor_preservation.json`: **153/153 tracked files byte-exact** (c33 dawdreamer_state P1-iterate anchors; c31 palette_probe; c31 palette; c34 palette_v2; c35 palette_v2_render). Zero AST-forbidden state calls; zero PRNG hits; zero forbidden-module imports. c9 chain / c13 pipeline / c15 `i4_stratified.py` / c22 stability harness / c26-30 utilities NOT imported.

## Ledger Events (9 Shadow Rows Under `-clone-2` Suffix)

Six named + two housekeeping + one launched (cycle 1); cycle 2 zero:

1. `_run/cycle_36_launched-clone-2` (`status: validated` per c35 Branch C codified convention)
2. `_plan/vst3_nondeterminism_characterization_rubric_frozen-clone-2`
3. `_infra/egress-probe-cycle-36-clone-2`
4. `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` (in-progress; M-* unsuffixed per c32)
5. `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` (validated verdict roll-up, MIXED)
6. `_run/cycle_36_closed-clone-2`
7. `_archive/cycle-36-scratch-clone-2`
8. `_infra/adopt-cycle36-tests-clone-2`
9. (per audit tally, 9-row total)

`_manager/vst3-render-nondeterminism-anti-pattern-candidate-clone-2` **correctly WITHHELD** under MIXED verdict; c37 owns whether to elevate it if the rubric contradiction resolves toward STRUCTURAL_DRIFT. No `M-EAR-1/*` or `M-GEN-1/*` events emitted.

Ledger state: 572 events (563 + 9 emitted this branch).

## MODERATE Findings (Handoff to c37, Not Corrections Owed This Branch)

1. **Report §1 wording**: measurement-table row line 34 says "both plugins"; the frozen rubric says "either plugin". One-line fix owed before c37 reads §1. Not a rework blocker.
2. **Rubric internal contradiction**: doc §98 STRUCTURAL_DRIFT mechanical rule ("ANY of the following … for EITHER plugin") vs §118-121 MIXED example ("one plugin passes SMALL while the other passes STRUCTURAL"). Doc line 71 forbids auditor override; preserved per-plugin `label` in `verdict.json` means signal is not lost. First rubric-authoring contradiction observed in the campaign.
3. **Hydration symbol mismatch**: brief cited `set_parameters_from_p1_dict` on `scripts.dawdreamer_state.probe_p1_iterate_parameters`; symbol does not exist. Worker inlined c35 `render_stem_v2.py:render_dawdreamer_vst3_once` hydration loop byte-verbatim; mechanism preserved; `anchor_preservation` confirms c35 unchanged.

## Anti-Patterns Locked (6-Count Stable Including c35 A #6)

`get_state`, `save_state`, `save_preset`, `load_state`, `set_state(bytes)` remain AST-forbidden — enforced by test with 0 hits. c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. **c35 Branch A VST3-nondeterminism finding survives as fair characterization**, not a re-attempt.

**Surge XT drift is inside the VST3 binary**, upstream of the P1 API. c33 P1 hydration surface (100% param coverage) is insufficient to eliminate it; any future Surge XT bisection is narrowed to internal state axes (LFO seeds, voice allocation, envelope phase).

## State-Machine Discipline (c29 Lemma Respected)

`M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` is a peer sub-milestone under M-DAW-SPIKE-1. NOT a child of terminal-validated `M-DAW-SPIKE-1/{palette-schema-v2, palette-schema-v2-hydration-render, palette-instrument-determinism, dawdreamer-state-extraction-workaround}`.

## Merge Disposition

Merge report on disk at `/home/user/music-gen-instance/fork-87da4f517029/clone-2/merge_report.md` for root conductor pickup. Nine shadow-ledger rows queued for `concat_clone_ledgers`; zero cross-clone collisions under c32 `-clone-2` suffixes. Cycle 2 contributes zero additional rows.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (AST-verified); no `sidecar_nonfactor` imports.
- Interpreter guard `assert sys.executable == '/usr/bin/python3'` on every new script.
- Read-only anchors preserved (see Anchor Preservation).
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403). M-EAR-1 armed-not-fired posture holds.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.

## Cycle-37 Handoff (Enumerated in Merge Report + Audit)

**Recommended (low risk)**: adopt per-plugin activation stance from report §9. Any of:

1. **A — Dexed-only strict-SMALL tolerance-gate** (primary; Dexed's byte-adjacent-tolerance is legible under both rubric readings).
2. **B — Surge XT internal-state bisection** (deferred; LFO seed / voice allocation / envelope phase).
3. **C — envelope-only both-plugin tolerance-gate** (higher risk; needs a fresh frozen rubric).

**Alternative (higher-effort)**: formally supersede the rubric doc with a v2 resolving the STRUCTURAL "either" vs MIXED-example contradiction. Requires a fresh pre-registration cycle.

**Never re-open c31/c35 A anti-patterns**: `get_state`, `save_state`, `save_preset`, `load_state`, `set_state(bytes)` remain AST-forbidden. Surge XT drift is upstream of the P1 API; do not attempt to eliminate it via state extraction.

**Report §1 wording fix**: one-line "both" → "either" edit before c37 reads §1.

## Cycle-Bounding for c37 palette-v3 Decision

The palette-v3 VST3 activation decision does NOT need to answer the Surge XT bisection question first. The c36 Branch C answer (MIXED with per-plugin labels) is sufficient input:

- **Dexed** is a viable candidate for tolerance-gated activation.
- **Surge XT** is not viable for byte-determinism; if used, needs a tolerance-gate rubric.

The c37 fan-out A/B/C choice above operates entirely on this input.

## Cumulative Progress

**M-DAW-SPIKE-1 line** (post-c36 Branch C):

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c31 | `palette-assignment-schema` | validated |
| c31 | `palette-instrument-determinism` | validated (sfizz GREEN; Surge XT + Dexed STILL_GAP) |
| c33 | `dawdreamer-state-extraction-workaround` | WORKAROUND_FOUND (P1 winning) |
| c34 | `palette-schema-v2` | SCHEMA_V2_LANDS (four-times-VALIDATED) |
| c35 | `palette-schema-v2-hydration-render` | RENDER_FAILS (VST3-binary-internal nondeterminism, fair c31 STILL_GAP extension) |
| c36 (this) | `vst3-render-nondeterminism-characterization` | **MIXED** (Surge XT STRUCTURAL / Dexed SMALL, per-plugin labels preserved) |

**Pattern durability**: **eight consecutive cycles** of rubric-first pre-registration discipline (c26-c30 mechanism probes + c31/c32/c33/c34/c35/c36 palette + infra + fanout). **First rubric-authoring contradiction of the campaign observed this cycle**; soft addition to c37+ discipline: cross-check the rubric's mechanical rule against its own worked examples before freezing the SHA. Not a hard gate — pre-registration lock already caught it in-audit.

**VST3 palette route is now empirically per-plugin heterogeneous**: Dexed byte-adjacent-tolerant at float32 epsilon; Surge XT drifts ~10% RMS despite BLAS pins + 100% P1 hydration. c34 palette_v2 schema unaffected.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 fanout-namespace convention** held under c33 harness-clone-namespace-guard: infra families `-clone-2`-suffixed, substantive `M-*` unsuffixed.

**M-EAR-1 armed-harness Path B**: dormant/armed pending audio-egress unblock (still 403; retry per policy is non-blocking). **Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Standby-termination discipline** reinforced: worker's own low-output signal fired at cycle 2, aligning with the auditor's no-null-cycle rule. The fanout-harness auto-termination-on-N-consecutive-standby heuristic (carried forward from multiple prior branches) continues to accrue evidence.

[END OUTPUT]

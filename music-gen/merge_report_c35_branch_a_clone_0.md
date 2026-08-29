# Merge report — Cycle 35 Branch A, fork 07063458736e, clone-0

> **Location fallback.** The brief's intended path
> `/home/user/music-gen-instance/fork-07063458736e/clone-0/merge_report.md`
> is outside this session's workspace boundary and Write was denied by
> the sandbox. This file at the workspace root is the fallback per the
> brief's contract. The shadow ledger is at
> `/home/user/music-gen-instance/fork-07063458736e/clone-0/promise_ledger.jsonl`
> (7 events emitted; conductor should concat via
> `long_exposure.workspace_bootstrap.concat_clone_ledgers`).

**Milestone:** `M-DAW-SPIKE-1/palette-schema-v2-hydration-render` (new peer sub-milestone under M-DAW-SPIKE-1; c29 state-machine lemma respected — NOT a child of terminal-validated `M-DAW-SPIKE-1/palette-schema-v2`).

**Verdict:** **RENDER_FAILS** (first-class negative finding per rubric).

**Rubric SHA-256:** `7d8841f089dafd3cfe9ad2bc4e710ddada327c5bf3e3dba9398947b75d7e014f`.

## Headline finding

The c33 P1 `set_parameter(i, v)` hydration protocol is **semantically correct** for Surge XT + Dexed VST3 plugins (100% param coverage: 2855/2855 Surge XT, 2238/2238 Dexed; non-silent audio at peak_abs 0.68 and 0.72 respectively; panels 8-key finite and moved 17-39× the 5% baseline-self-distance floor). But the plugins produce **byte-non-deterministic renders** across fresh subprocess-isolated runs — the drift lives inside the plugin binaries, not in the DawDreamer harness. This confirms the c31 STILL_GAP characterization extends from get_state extraction (which c33 P1 bypassed) to the render layer itself. Under the frozen rubric, byte-determinism × 2 is a hard verdict gate, so the honest verdict is RENDER_FAILS — the palette-v2 schema is proven usable in-anger but VST3 audio-render reproducibility remains an open problem.

If the render-determinism gate were satisfied, this run would resolve to **V2_MOVES_PANEL** unambiguously.

## Shadow ledger events (7 total)

Emitted to `/home/user/music-gen-instance/fork-07063458736e/clone-0/promise_ledger.jsonl`. Infra-family labels auto-suffixed `-clone-0`; substantive `M-*` labels unsuffixed per the c32 fanout-namespace convention.

| # | Milestone | Status |
|---|---|---|
| 1 | `_run/cycle_35_launched-clone-0` | validated |
| 2 | `_infra/adopt-palette-v2-hydration-render-clone-0` | validated |
| 3 | `M-DAW-SPIKE-1/palette-schema-v2-hydration-render` | invalidated |
| 4 | `M-INGEST-1/egress-probe` | in-progress |
| 5 | `_infra/adopt-cycle35-tests-clone-0` | validated |
| 6 | `_run/cycle_35_closed-clone-0` | validated |
| 7 | `_archive/cycle-35-scratch-clone-0` | validated |

## Deliverables shipped

- `docs/palette_v2_hydration_render_rubric.md` — frozen 3-verdict rubric, mtime + git-log enforced.
- `docs/palette_v2_hydration_render_report.md` — 12-section report with full verdict analysis, panel table, per-stem determinism table, anchor preservation summary, and honest c36 handoff candidates.
- `scripts/palette_v2_render/{__init__.py, build_assignments_v2.py, render_stem_v2.py, run_all.py}` — 4 scripts, interpreter-guarded, no-PRNG AST-clean, c9/c13/M-EAR-1 not-imported, set_parameter-only VST3 hydration (get_state family AST-forbidden).
- `data/palette_v2_render/{rubric_hash.txt, assignments_v2.jsonl, per_stem/<stem>/{render_run{1,2}.wav.sha, pinned_state.json}, bare_combined.wav.sha.run{1,2}, panel_original_vs_v2.tsv, panel_v1_vs_v2.tsv, panel_original_vs_v1_bare_baseline.tsv, fetchability_ladder.jsonl, verdict.json, anchor_preservation.json}` — full data artifact tree.
- `tests/test_palette_v2_hydration_render.py` — 15 test-functions, all-green.
- `tests/test_integration_cross_branch.py §54` — 16 guard checks, all-green.

## Anchor preservation

`data/palette_v2_render/anchor_preservation.json`: 148 files snapshotted across 11 READ-ONLY anchor prefixes (`scripts/palette`, `scripts/palette_probe`, `scripts/palette_render`, `scripts/palette_v2`, `scripts/dawdreamer_state`, `data/dawdreamer_state/per_plugin/{surge_xt,dexed}`, `data/palette/schema`, `data/palette_probe`, `data/palette_render`, `data/palette_v2/schema`). `unchanged=true`. Zero drift.

## Scratch archived

- `tools/_c35_egress_probe.py` → `tools/stale/_c35_egress_probe.py`.
- `tools/_emit_cycle35_branch_a_events.py` → `tools/stale/_emit_cycle35_branch_a_events.py`.

## Post-merge checks (for the conductor)

- All new ledger event `artifacts` entries reference on-disk files (verified pre-merge on-clone).
- `promise_check` on this clone's workspace: **0 ERROR**. WARN inflation is expected on the `data/palette_v2_render/*` tree because the ledger events currently live in the shadow ledger; the WARNs collapse when the shadow ledger is concatenated into main.
- `tests/test_palette_v2_hydration_render.py`: 15/15 PASS.
- `tests/test_integration_cross_branch.py §54`: 16/16 PASS (result: `PASS (0 failures)`).

## c36 handoff candidates (from report §10, ranked)

1. **`dexed-preset-hydration`** — investigate `.syx` / `.dexed` cartridge-file loading via a native Dexed preset path (not through per-parameter injection). May reset DSP state deterministically where set_parameter does not.
2. **`surge-xt-fxp-load`** — investigate `.fxp` preset loading for Surge XT via a native file path. Same rationale.
3. **DO NOT** re-open c31 STILL_GAP by calling `get_state`/`save_state`/`save_preset`/`set_state(bytes)`/`load_state`. Those surfaces remain locked anti-patterns; c35 provides no new information that would justify a re-attempt.
4. **Drums pipeline is production-ready** as-is via fluidsynth. peak_abs 3e-5 is natural upstream basic-pitch drums-MIDI amplitude, not a v2-hydration failure.
5. **v2 schema is confirmed usable in-anger** — Layer-1 + Layer-2 validation both passed; `assignment_id_v2` deterministic; `iterated_params` key set matches c33 P1 anchor exactly; `iteration_sha_256` cross-check succeeded.
6. **DawDreamer subprocess-isolation env pattern** (inherit-parent-env + BLAS pins on top) is a reusable primitive. Restricted-env launches silently drop ~774 Surge XT parameters — parent env is required.

## Cross-branch note for clones 1 + 2

This clone's negative finding is a strong input for clone-1's palette-driven-batch-v2 sampler-diversified arc: driving palette diversity through a batch-v2 sampler is moot if the underlying VST3 render is nondeterministic. Clone-1 should factor in that VST3 renders may need to be either (a) rerun-averaged, (b) restricted to fluidsynth+sfizz until a preset-load path lands in c36, or (c) tagged as "semantically equivalent but not byte-reproducible" for downstream consumers.

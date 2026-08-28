# Merge report — fork ed041ef4c1dc / clone-0

**Branch scope:** M-RULES-1/extraction/breadth-seeds — cycle-12 rule-ledger expansion.
**Cycle:** 12   **Agent:** worker   **Run id:** run-2026-08-28T040704Z
**Timestamp:** 2026-08-28T11:56:00Z
**Verdict:** validated/high

(This file is a workspace-root copy for the fork conductor. The
expected pickup path is `/home/user/music-gen-instance/fork-ed041ef4c1dc/clone-0/merge_report.md`
which lies outside this session's writable directory; the harness will
either copy this file over or the conductor will read it from here.)

## What shipped

| Artifact | Purpose |
|---|---|
| `docs/rules_extraction_breadth_report.md` | Cycle-12 breadth-expansion report (required deliverable) |
| `docs/figures/rules_extraction_breadth_growth.png` | Two-panel figure: per-rule_type × per-seed row-count + salt-collision heatmap |
| `data/rules/ledger.jsonl` | Expanded from 28 → 76 rows (SHA 4fe722ad… → a6fd53e9…) |
| `data/rules/breadth_expansion_summary.json` | Per-seed per-rule_type row counts + null-with-reason |
| `data/rules/salt_collision_before_after.tsv` | 25-row salt-collision pivot |
| `data/rules/salt_collision_before_after.json` | Structured salt-collision summary + picks table |
| `scripts/rules/extract/breadth_seeds.py` | Live orchestrator (kept under scripts/) |
| `scripts/rules/extract/_common.py` | Extended with `set_extraction_context()` (cycle-9 defaults intact) |
| `tests/test_integration_cross_branch.py` | +§24 (breadth-seeds invariants; 10 new checks; PASS) |
| `tests/test_rules_extraction.py` | [5] provenance-resolvability now walks all 3 seed contexts (36/36 pass) |
| `plan_of_record.md` | +3 sub-milestones under M-RULES-1/extraction/breadth-seeds |

Scratch archived to `tools/stale/`:
`_validate_breadth_expansion.py`, `_salt_collision_analysis.py`,
`_plot_breadth_growth.py`, `_emit_breadth_events.py`,
`_emit_breadth_closure.py`.

## Ledger events appended (this clone)

1. `_plan/register-rules-breadth-submilestones` — validated/high
2. `M-RULES-1/extraction/breadth-seeds` — in-progress/medium (kickoff)
3. `M-RULES-1/extraction/breadth-seeds/seed_mid_50s` — validated/high
4. `M-RULES-1/extraction/breadth-seeds/synth_060s` — validated/high
5. `M-RULES-1/extraction/breadth-seeds` — validated/high (parent closure)
6. `_infra/cross-branch-integration-test-cycle12-rules-breadth` — validated/high
7. `_archive/rules-breadth-scratch` — validated/high
8. `_run/clone-0-scope-complete` — validated/high

## Findings summary

- **Regression contract intact.** All 28 cycle-9 anchor rows byte-identical (append-only writer + tmp-copy diff harness). The 5 salt=0 batch-v1 anchor rule_ids still present as ledger prefix. `tests/test_integration_cross_branch.py` §23 (which reads a saved cycle-11 sampling_manifest.json) unaffected — PASS.
- **≥15-row target 3× exceeded.** 48 new rule rows appended (24 per seed). Per rule_type: harmonic +4, rhythmic +12, melodic +12, form +10, arrangement +10.
- **Byte-determinism verified twice.** Two independent runs against a temp copy of the pre-expansion ledger produce SHA `a6fd53e9bf9a10f6…`; real ledger post-write reproduces the same SHA.
- **Cross-seed rule_id uniqueness: 76/76 distinct.** Content-hash rule_id derivation with seed-specific `provenance_pointers.transcription_event_id` guarantees this structurally.
- **Salt-collision reduction: 5→4 out of 50 pairwise cells.** Modest but material. Cycle-11's specific arrangement salt-1-vs-4 collision resolves; new collisions concentrate at salt=4 (over-represented, 3 of 4 post-cells involve salt=4). Live salt=0 selection diverges from the pinned cycle-11 batch-v1 anchors for 3 of 5 rule_types — expected cycle-13 behaviour, flagged in the report.
- **Coercion policy honest, no schema change.** Only harmonic measure-window rows suppressed (4 per seed) with `null:insufficient-progression` when `chord_progression` collapses to ≤1 unique figure. Every seed retains ≥1 harmonic row via the song-level candidate.

## Cross-branch touch surface

Writes confined to disjoint subtrees:
- `scripts/rules/extract/` (added `breadth_seeds.py`; extended `_common.py`)
- `data/rules/`
- `docs/` (added report + figure under existing subtrees)
- `tests/` (extended existing files by append-only)
- `tools/stale/`
- `plan_of_record.md` (+3 rows in existing Milestones table)

## Environment state (unchanged from cycle 11)

- `torch 2.13.0+cpu`, `numpy 1.26.4`, `music21 9.1.0`, `torchvision 0.28.0`, `basic-pitch 0.4.0` quarantined at `workspace/basic_pitch_venv`
- Egress: still blocked per `corpus/CORPUS_STATUS.md`; no retry attempted this cycle
- Interpreter: `/usr/bin/python3` on every guard

## For the fork conductor

Zero new ERRORs in `promise_check` (baseline 0 → post 0). Pre-existing WARN backlog (45 orphan-artifact WARNs from cycles 5–11 daw_spike / fanout hardening scratch — pre-existing and NOT introduced by this branch) untouched. Post-merge integration should be zero-conflict.

**Recommendation for cycle 13:** `scripts/gen/batch_v1.py` rerun on the expanded ledger (batch-v2). §7–§8 of the report walks through it.

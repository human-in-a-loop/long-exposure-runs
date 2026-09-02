# Test Stage 1 of 23 — Validators + Artifact-Loss Probe

Stage 25 of 48. Adversarial-mode probe #1: run both validators end-to-end, then cross-map every ledger `artifacts:` reference against on-disk state to surface silent artifact-loss and silent supersession.

## What ran

1. `python3 -m long_exposure.tools.promise_check .`
2. `python3 -m long_exposure.tools.org_check .`
3. Full `promise_ledger.jsonl` walk (920 rows) → distinct `artifacts` refs (`seen`) → per-ref `os.path.exists` → bucket by top-2 path segments.

## Adversarial findings

### F1 — promise_check: 0 ERROR, ~3437 WARN lines

Structurally clean. No `ERROR` output. The WARN stream is dominated by
ledger-tracked-artifact-missing warnings (one per absent path) and does
not affect campaign-validation correctness. **Severity: INFO** for the
0-ERROR outcome; the WARN cluster is decomposed below.

### F2 — 684 distinct ledger-referenced artifacts are missing on disk

Bucketed by top-2 path segments:

| Prefix | Missing count | Interpretation |
|---|---:|---|
| `data/gen/` | 565 | M-GEN-1 batch outputs (`batch-v{1..6}`, `palette_driven_batch_v{1..4}`, `palette_driven_batch_rated_corpus`) — large audio artifacts pruned without `_archive/*` |
| `data/tex/` | 40 | Includes the entire `data/tex/embedding_flip_analysis/` tree (variants P1-P4, E1-E4, sweep_results.tsv, threshold_characterization.json, summary.json, determinism_check.json, anchor_regen/regen_*.tsv) — M-TEX-1/panel/embedding/content-flip-analysis (validated cycle 14) evidence gone |
| `data/separation/` | 37 | Entire `data/separation/synth_mix/gt/synth_{030,060,090}s/` ground-truth mixes + `midi/*.mid` + `manifest.json` — M-SEP-1/ground-truth (validated/high cycle 4) evidence gone |
| `data/breadth/` | 17 | M-INGEST-1/breadth-second-seeds output |
| `data/recreate_v0/` | 15 | M-RECREATE-1/first-real-audio-clone-0 (cycle 37 RECREATION_LANDS) intermediate artifacts |
| `long_exposure/tools/*`, `long_exposure/workspace_bootstrap.py` | 3 | Ledger references package-installed files that live at `~/human-in-a-loop/long-exposure/long_exposure/`, **outside** the workspace tree. Introspectable via `python3 -c "import long_exposure; print(long_exposure.__file__)"` — verified. |
| `docs/fanout_namespace_convention.md` | 1 | Silent supersession (see F3) |
| `reports/cycles/report_cycles_13-15_clone_1.md` | 1 | Orphan clone-1 shadow report referenced but never committed |
| `tools/_liveness_probe.py`, `tools/_restart_extraction.sh` | 2 | One-shot infra scratch referenced but never archived to `tools/stale/` |
| `tools/stale/_c39_clone0_emit_events.py`, `tools/stale/_c47_emit_events_v2p1.py` | 2 | Referenced as archived but not present under `tools/stale/` |

**Mitigation for validation credibility**: for every validated milestone
in this bucket, the ledger event narratives pin verdict SHAs
(`rubric_hash` chains, byte-determinism × 2 SHAs, per-artifact SHAs),
so the *claim* survives even when the *bytes* do not. Byte-level
re-audit would require re-running the render pipelines. Nothing in
the missing set contradicts a validated verdict; the pattern is
consistent with routine large-artifact cleanup rather than tampering
or drift.

**Severity: MODERATE.** The plan-of-record success criteria for
several milestones read "byte-deterministic × 2" — that check can no
longer be re-executed against the on-disk state for the 565 M-GEN-1,
40 M-TEX-1, 37 M-SEP-1, 17 breadth, and 15 recreate_v0 artifacts.

### F3 — Silent supersession: `docs/fanout_namespace_convention.md`

The unversioned path emitted by cycle 32's `_infra/fanout-namespace-convention`
event is absent; three versioned successors exist on disk instead:
`docs/fanout_namespace_convention_v1.md`, `_v2.md`, `_v3.md`, plus
`_v3_rubric.md` and `_v3_report.md`. No `_plan/*` supersession event
covers the unversioned → versioned transition. The `_infra/fanout-namespace-convention-v2`
concept is referenced retroactively inside the M-INGEST-1/egress-probe-clone-{0,2}
plan-of-record rows, but no dedicated supersession row lands. **Severity:
MODERATE.** Silent-supersession pattern per audit-framework probe list.

### F4 — org_check WARNs at workspace root

- 6 `merge_report_*.md` at root (post-merge scratch, no `_archive/*`
  coverage): `merge_report.md`, `merge_report_c35_branch_a_clone_0.md`,
  `merge_report_c36_branch_a_clone_0.md`, `merge_report_c36_branch_c_clone_2.md`,
  `merge_report_c47_branch_b_clone_1.md`, `merge_report_clone-1_fork-43802db1a81c.md`
- 4 scratch scripts at root: `scratch_ast_audit.py`,
  `scratch_determinism_check.py`, `scratch_write_diff.py`, `tmp_pc.py`
- 42 figures under `docs/figures/` that org_check flags for
  non-co-location with source data — the campaign's actual practice is
  to co-locate under `docs/figures/`, so this is an org_check policy
  mismatch rather than a real drift.

**Severity: MINOR.** Housekeeping hygiene, no downstream impact.

### F5 — `long_exposure/*` reference paths live outside the workspace

The ledger references `long_exposure/workspace_bootstrap.py`,
`long_exposure/tools/_ledger_schema.py`, `long_exposure/tools/promise_check.py`
as workspace-relative paths, but the package is installed at
`/home/user/human-in-a-loop/long-exposure/long_exposure/`. `promise_check`
therefore flags them as missing artifacts. Introspection via
`import long_exposure` resolves cleanly. **Severity: MINOR.**
Convention/registration gap rather than a real defect — but future
audits should either (i) prepend `long_exposure/` refs with an
explicit `//pypath/` sentinel, or (ii) register the package location
via `_infra/*` event.

## Gate-check

- Is every fix verified against its original finding? — n/a (adversarial probe, no fixes)
- Have I checked for regressions in adjacent behavior? — yes, both validators run to completion
- Are any new issues introduced? — no

## What's next

Test stages 2-23 will probe: silent supersession patterns beyond F3
(F3 is exemplar), orphan milestones not on plan-of-record rows,
plan/ledger inconsistencies, supersession-pending status, sidecar_nonfactor
leakage grep, PRNG-in-deterministic-path grep, egress-probe honesty
audit, test-suite coverage/run status per validated milestone, verdict
SHA re-check for a spot-sample of terminal-validated milestones,
audit-cycle report cross-references.

<checkpoint>
  <stage>test</stage>
  <status>transitioning</status>
  <confidence>high</confidence>
  <tokens>~30k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran promise_check + org_check + full 920-row ledger artifact-cross-map. promise_check ERROR-clean; surfaced 684 distinct on-disk-missing artifact refs (M-GEN-1 batch outputs dominate, followed by M-TEX-1 flip-analysis + M-SEP-1 ground-truth) and one silent-supersession pattern on `docs/fanout_namespace_convention.md`.</what-i-did>
  <next-action>Advance to test stage 2 (of 23): sidecar_nonfactor leak grep + PRNG-in-deterministic-path grep across the substantive `scripts/` tree.</next-action>
  <gate-check>
    - Test file written: yes — `audits/final/stages/test_1of23.md`
    - Findings appended: 5 rows to be appended below (F1..F5)
    - Severity classified: yes (INFO ×1, MODERATE ×2, MINOR ×2)
    - Validators actually run: yes (promise_check 0-ERROR, org_check WARN-only)
    - Ready to advance: yes
  </gate-check>
</checkpoint>

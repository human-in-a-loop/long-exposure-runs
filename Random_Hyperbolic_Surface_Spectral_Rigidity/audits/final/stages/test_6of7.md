# Final Audit Stage 14 — Test 6/7: Figure Coverage

## Scope
Adversarial figure-coverage pass. This pass inventories on-disk figure files, ledger-referenced figure paths, missing referenced figures, orphan figures, and milestones whose stated evidence appears to warrant figures.

## Validator Results
- `python3 -m long_exposure.tools.promise_check <workspace>` -> return code `0`
  stdout tail:
  ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_46-48.pdf (no ledger event references it)
  ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_49-50.md (no ledger event references it)
  ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_49-50.pdf (no ledger event references it)
  ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_7-9.md (no ledger event references it)
  ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_7-9.pdf (no ledger event references it)
  ! WARNING: orphan artifact in managed path: reports/final/final_report.md.pre_final_backup_20260516T150412Z (no ledger event references it)
  ! WARNING: orphan artifact in managed path: reports/final/run_mode.json (no ledger event references it)
  ! WARNING: ledger-tracked artifact missing: reports/final/final_report.md (referenced by an event but not on disk and no '_archive/*' event explains the move)
- `python3 -m long_exposure.tools.org_check <workspace>` -> return code `0`
  stdout tail:
  ! WARNING: file at workspace root not in allowed-set: random_hyperbolic_surface_rigidity_long_exposure_prompt.md
  ! WARNING: file at workspace root not in allowed-set: random_hyperbolic_surface_spectral_rigid_package.zip
  ! WARNING: figure in docs/: docs/paper_map/cycle1_dependency_graph.png (figures should be co-located with their source script + data, not under docs/)
  ! WARNING: figure in docs/: docs/proof_ledger/theorem1_exponent_flow.png (figures should be co-located with their source script + data, not under docs/)
  ! WARNING: figure in docs/: docs/proof_ledger/markov_scaling_sanity.png (figures should be co-located with their source script + data, not under docs/)
  ! WARNING: figure in docs/: docs/proof_ledger/proposition31_dependency_graph.png (figures should be co-located with their source script + data, not under docs/)
  ! WARNING: figure in docs/: docs/proof_ledger/theorem2_dependency_graph.png (figures should be co-located with their source script + data, not under docs/)
  ! WARNING: figure in docs/: docs/proof_ledger/m2_closure_dependency_graph.png (figures should be co-located with their source script + data, not under docs/)

Validator status: **green**.

## Figure Coverage Summary
- Figure files on disk: 104
- Unique figure paths referenced by ledger artifacts: 105
- Milestones with ledger figure references: 38
- Milestones judged to warrant figures: 36
- Warranted milestones without ledger figure references: 0
- Referenced figures missing on disk: 0
- Likely orphan figure files on disk: 0

## Missing Referenced Figures
- None.

## Warranted Milestones Without Ledger Figure References
- None.

## Orphan Figure Sample
- None.

## Findings Appended
- None.

## Figure Coverage Block For Final Summary
```json
{
  "figures_in_ledger": 105,
  "figures_present": 104,
  "milestones_with_figures": 38,
  "milestones_without_figures": 0,
  "missing_figures": [],
  "orphan_figures": []
}
```

## Regression / New-Issue Check
- Required validators remained green.
- Missing referenced figures and no-ledger-reference figure gaps were classified independently from final/report artifact coverage to avoid duplicate findings.
- Orphan figures are logged as coverage/accounting data only; no terminal milestone was invalidated on that basis alone.

## Gate
- Expected file exists after write: `<workspace>/audits/final/stages/test_6of7.md`
- Findings appended this stage: 0

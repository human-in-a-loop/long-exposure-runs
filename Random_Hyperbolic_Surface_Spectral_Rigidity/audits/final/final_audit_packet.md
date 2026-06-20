---
created: 2026-05-16T03:45:00Z
cycle: 17
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M6-final-synthesis
---

# Final Audit Packet

## Required Artifacts

- `reports/final/final_report.md`
- `data/final/final_artifact_index.csv`
- `data/final/final_claim_ledger.csv`
- `reports/final/final_file_map.md`
- `audits/final/final_audit_packet.md`
- `scripts/build_final_synthesis_index.py`
- `scripts/plot_final_campaign_summary.py`
- `reports/figures/final_campaign_evidence_ladder.png`
- `reports/figures/final_bottleneck_map.png`

## Validation Commands

```bash
python3 -m py_compile scripts/build_final_synthesis_index.py scripts/plot_final_campaign_summary.py
python3 scripts/build_final_synthesis_index.py
python3 scripts/plot_final_campaign_summary.py
figure check reports/figures/final_campaign_evidence_ladder.png
figure check reports/figures/final_bottleneck_map.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

## Audit Criteria

- `data/final/final_artifact_index.csv` must report zero missing required artifacts.
- `data/final/final_claim_ledger.csv` must contain `reconstructed`, `certified`, `numerical_evidence`, `proved_toy`, `conjectural`, `negative_result`, and `non_claim`.
- Both final PNG figures must pass `figure check`.
- `promise_check` and `org_check` should show only known historical warnings after the M6 ledger event.

## Known Historical Warnings

- Root paper and prompt files are expected.
- Historical live-run files are expected.
- One early ledger artifact path references `docs/paper_map/` as a directory.
- Historical cycle reports may appear as orphaned until or unless separately ledgered.
- Earlier docs-hosted figures predate the later report/figure organization rule.
- Wolfram execution is environment-dependent and optional for final validation; Python fallbacks are the maintained validation path.

## Residual Risks

- Imported Kim--Tao dependencies remain imported: MPvH expansion, Nau boundedness, and MP23 rank-two fixed-point estimates are not reproved.
- Toy permutation and Schreier evidence may not quantitatively transfer to hyperbolic random covers.
- The M5 product-ratio mechanism is exact in the labelled-template toy model but remains a conjectural guide for full trace-polynomial improvements.
- Optional PDF rendering is not part of the validation gate; markdown is canonical.

## Ledger Requirement

After the validation commands pass, append an `M6-final-synthesis` ledger event with all final artifacts listed. Use `validated/high` only if the scripts, figures, coverage checks, and final validators pass.

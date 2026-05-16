---
created: 2026-05-16T03:40:00Z
cycle: 17
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M6-final-synthesis
---

# Final File Map

Open these files first:

1. `reports/final/final_report.md` — standalone final research record.
2. `data/final/final_claim_ledger.csv` — claim-by-claim evidence classification.
3. `data/final/final_artifact_index.csv` — canonical artifact coverage table.
4. `audits/final/final_audit_packet.md` — validation checklist and residual risks.

Canonical milestone reports:

| Milestone | Canonical files |
|---|---|
| M1 paper map | `docs/paper_map/cycle1_foundational_map.md`, `docs/paper_map/cycle1_open_questions.md` |
| M2 proof ledger | `docs/proof_ledger/rigidity_proof_reconstruction.md`, `docs/proof_ledger/delocalization_proof_reconstruction.md`, `docs/proof_ledger/m2_loss_map.md`, `docs/proof_ledger/m2_proof_ledger_closure.md` |
| M3 probes | `reports/computational_probes/m3_computational_probe_synthesis.md`, `data/polynomial_method/m3_probe_artifact_index.csv` |
| M4 certification | `reports/formal_certification/labelled_embedding_expectation_identity.md` |
| M5 extension | `reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md` |
| M6 final | `reports/final/final_report.md`, `data/final/final_claim_ledger.csv`, `audits/final/final_audit_packet.md` |

Canonical final figures:

- `reports/figures/final_campaign_evidence_ladder.png`
- `reports/figures/final_bottleneck_map.png`
- `reports/figures/m5_fixed_vs_growing_template_mechanism.png`

Reproducibility scripts:

- `scripts/build_final_synthesis_index.py`
- `scripts/plot_final_campaign_summary.py`
- M3 probe scripts under `scripts/probe_*.py`
- M4 exact certification script `scripts/certify_labelled_embedding_expectation.py`
- M5 expansion scripts `scripts/compare_expansions_to_cycle9.py`, `scripts/plot_growing_template_expansions.py`, and `scripts/plot_m5_extension_synthesis.py`

Known nonblocking warnings:

- The paper files `2603.01127.pdf` and `2603.01127.txt` are intentionally at workspace root from the original prompt.
- Live-run root files and the original prompt file are historical run infrastructure.
- One early ledger artifact path points at `docs/paper_map/` without canonical file expansion.
- Historical cycle reports are useful but not part of the final required artifact set.
- Some early figures live under `docs/`; newer figures are under `reports/figures/`.
- Wolfram artifacts from earlier cycles exist and may be rerun when Wolfram is available. Python validation paths are canonical for final checks.

Use `data/final/final_claim_ledger.csv` when deciding whether a statement is reconstructed, certified, proved in a toy model, numerical evidence, conjectural, a negative result, or a non-claim.

---
created: 2026-05-12T15:20:00Z
cycle: 36
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-PRODREPLAY-1
---

# Production-Target Replay

M-PRODREPLAY-1 is the executable boundary between real production telemetry, rejected non-production evidence, and claim-support candidacy. It does not fabricate production telemetry: `scripts/run_production_target_replay.py` scans `data/production_target_bundle/` for `manifest.json` or `manifest.csv` files, accepts only manifests with `evidence_label=production_target`, and emits `no_real_telemetry_available` when no such manifest is present. A production-target manifest cannot self-assert the chain with booleans alone: each gate pass must also name an existing evidence artifact path using `<gate_field>_evidence_path`, or the replay rejects at the first missing gate artifact.

The manifest contract is deliberately narrow. A candidate production manifest must provide `bundle_id`, `evidence_label=production_target`, and truthy fields for `root_enrolled`, `attested`, `trust_policy_admissible`, `intake_custody_valid`, `adapter_conformant`, `timebase_valid`, `redaction_admissible`, `gatechain_passed`, `statistically_robust`, `causally_admissible`, `threshold_passed`, `planner_boundary_passed`, and `handoff_traceable`. Missing fields fail closed at the first gate they affect.

Replay order is fixed: root enrollment, attestation envelope, trust policy, intake custody, adapter/conformance normalization, timebase and observer-overhead integrity, redaction and join preservation, gatechain replay, uncertainty qualification, causal attribution, DC-001/DC-002 threshold replay, planner/readiness boundary, and final handoff traceability. The output tables are `data/production_target_replay_results.csv`, `data/production_target_replay_gate_trace.csv`, `data/production_target_replay_claim_boundary.csv`, and `data/production_target_replay_absence_report.csv`.

Current result: no real production-target bundle is present, so the replay state is `no_real_telemetry_available` with `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`. Existing fixture, synthetic, proxy, adapter, conformance, intake, attestation, policy, uncertainty, and causal labels are included only as negative controls; they are rejected at `evidence_label` and receive zero production credit.

Reproduce:

```bash
python3 scripts/run_production_target_replay.py
python3 scripts/plot_production_target_replay.py
python3 tests/verify_production_target_replay.py
python3 -m long_exposure.tools.promise_check <workspace>
python3 -m long_exposure.tools.org_check <workspace>
```

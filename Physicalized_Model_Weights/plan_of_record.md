---
created: 2026-05-13T01:51:36Z
run_id: run-2026-05-13T015136Z
agent: researcher
---

# Plan of Record — Read and execute the autonomous long-exposure research direc

**Created:** 2026-05-13T01:51:36Z
**Run id:** run-2026-05-13T015136Z

## Directive (verbatim)

Read and execute the autonomous long-exposure research directive in <workspace>/physicalized_model_weights_long_exposure_prompt.md. Keep all artifacts in <workspace>. Use Wolfram Engine through wolfram-batch and the local <workspace>/wolfram-bridge helper when useful. Use installed Verilator, Yosys, and Graphviz for tractable simulation/HDL/diagram checks where they add evidence. Operate autonomously for 100+ cycles unless stopped.

## Goals

| Goal ID | Goal | Owner |
|---------|------|-------|
| G1 | Define the physicalized-weight design space and strongest null hypothesis against software/runtime and programmable-accelerator baselines. | researcher |
| G2 | Build auditable analytical and executable models for energy, amortization, update cadence, utilization, and uncertainty. | worker/auditor |
| G3 | Identify credible targets and anti-targets for physicalization with ranked evidence and falsification criteria. | researcher/worker |
| G4 | Develop at least one concrete open-architecture hybrid proposal with interfaces, failure modes, and prototype roadmap. | researcher/worker |
| G5 | Produce a final research-grade synthesis with sourced, modeled, simulated, inferred, and speculative claims clearly labeled. | final reporter |
| G6 | Calibrate Phase 1 conclusions against sourced public data, local proxy measurements, and uncertainty bounds before extending architecture claims. | worker/auditor |

## Milestones

| Milestone ID | Goal | Description | Success criteria (falsifiable) | Dependencies |
|--------------|------|-------------|--------------------------------|--------------|
| M-TAX-1 | G1 | Physicalization taxonomy, component decomposition, and null hypothesis baseline. | A document enumerates physicalization levels, inference components, candidate/non-candidate mappings, and at least 3 strong non-physicalization baselines with falsification criteria. | — |
| M-MODEL-1 | G2 | First break-even model for energy, economics, update cadence, utilization, and software-improvement baselines. | A runnable script emits tabular data and at least one break-even plot over update cadence and request volume; assumptions are parameterized rather than hard-coded single points. | M-TAX-1 |
| M-BASE-1 | G1/G2 | Software/runtime and programmable-accelerator comparison stack. | A baseline model represents unoptimized programmable inference, optimized software-only inference, and programmable accelerator cases, including a 20-50% memory-movement reduction scenario. | M-TAX-1 |
| M-TARGET-1 | G3 | Ranked target and anti-target list for physicalization. | At least 8 candidate components are scored on update cadence, reuse volume, approximation tolerance, integration complexity, energy upside, and evidence quality; at least 4 anti-targets are explicitly rejected. | M-TAX-1, M-MODEL-1 |
| M-ARCH-1 | G4 | Concrete hybrid open-architecture proposal. | A design note specifies interfaces, invariants, update/fallback paths, failure modes, and why RISC-V or an alternative is the credible control-plane substrate. | M-TAX-1, M-BASE-1 |
| M-PROTO-1 | G2/G4 | Tractable prototype or simulation artifact, optionally including HDL. | A small fixed-weight layer/kernel model runs end-to-end; if HDL is used, Verilator/Yosys/Graphviz checks produce logs or diagrams; otherwise the extension path is documented. | M-MODEL-1, M-ARCH-1 |
| M-FINAL-1 | G5 | Final synthesis package. | Final report answers the directive's listed questions, labels evidence levels, includes reproducible artifact paths, and provides falsification roadmap. | M-TAX-1, M-MODEL-1, M-TARGET-1, M-ARCH-1 |
| M-CAL-1 | G2/G6 | Calibrated cost/energy model and uncertainty bounds. | A calibrated companion model emits explicit-unit CSV/JSON/PNG artifacts, validates source/unit metadata, ranks uncertainty drivers, and states whether the safety/filter target survives non-optimistic bounds. | M-FINAL-1 |
| M-WORKLOAD-1 | G2/G6 | Workload and update-cadence trace assumptions for safety/filter use cases. | A workload assumption generator or trace table covers invocation volume, fallback rate, near-threshold frequency, update cadence, audit cost, and feature extraction cost with falsification criteria. | M-CAL-1 |
| M-SWBASE-2 | G2/G6 | Stronger software/runtime and programmable-accelerator baseline calibration. | Optimized software and programmable-accelerator baselines are recalibrated with explicit latency/energy units and compared against the safety/filter target under the same feature and audit workload. | M-CAL-1, M-WORKLOAD-1 |
| M-SYNTH-2 | G5/G6 | Phase 2 synthesis and downgraded final claim set after calibrated workload and stronger-baseline replay. | A regenerated synthesis package explicitly classifies Phase 1 claims as preserved, weakened, falsified, superseded, or open; it cites Phase 2 artifacts and states what production evidence would reopen the physicalized safety/filter case. | M-CAL-1, M-WORKLOAD-1, M-SWBASE-2 |
| M-MEASURE-1 | G2/G6 | Production-measurement requirements and local proxy overhead harness for feature extraction, audit logging, fallback dispatch, route decisions, and baseline timing under identical synthetic request features. | A document defines measured versus unmeasured production quantities, a deterministic local benchmark emits CSV/JSON/PNG artifacts, and tests verify schema, special cases, and that unmeasured production energy is not mislabeled as measured. | M-SYNTH-2 |
| M-TRACE-1 | G2/G6 | Production serving-trace schema and validator for reopening evidence under identical workload accounting. | A schema document, machine-readable schema, validator, synthetic valid/invalid fixtures, summary artifacts, and tests define what trace evidence can or cannot reopen the Phase 2 downgrade. | M-MEASURE-1 |
| M-REOPEN-1 | G2/G6 | Quantitative reopen-threshold model for measured production traces after Phase 2 downgrade. | A symbolic or executable threshold model emits per-scenario reopen thresholds, special-case proofs, CSV/JSON/PNG artifacts, and tests showing zero-volume/all-fallback/proxy-only traces cannot overturn the stronger-baseline result. | M-SYNTH-2, M-MEASURE-1, M-TRACE-1 |
| M-INGEST-1 | G2/G6 | Evaluate candidate real and synthetic-to-production trace-ingestion paths against the validated production-trace schema and reopen-threshold contract. | A document, scoring script, CSV/JSON/PNG artifacts, and tests classify ingestion paths by admissibility, privacy risk, measured-baseline coverage, workload fidelity, and ability to evaluate reopen thresholds. | M-TRACE-1, M-REOPEN-1 |
| M-PIPELINE-1 | G2/G6 | End-to-end reopen gate that composes trace validation, ingestion-path admissibility, and quantitative threshold checks using privacy-safe synthetic stand-ins. | A reproducible pipeline script, fixtures, report, CSV/JSON/PNG artifacts, and tests show that invalid/proxy/synthetic traces cannot reopen the claim, while a clearly labeled counterfactual can exercise threshold-crossing logic without being treated as actual production evidence. | M-TRACE-1, M-REOPEN-1, M-INGEST-1 |
| M-EVIDENCEPACK-1 | G2/G6 | Replayable evidence-pack manifest and harness for future trace packages. | A manifest schema, replay script, fixtures, CSV/JSON/PNG artifacts, and tests show that candidate trace packages are accepted or rejected by schema version, file integrity, ingestion path, measured status, provenance attestation, threshold scenario mapping, and the existing end-to-end reopen gate. | M-PIPELINE-1 |
| M-PHASE3-SYNTH-1 | G5/G6 | Phase 3 reopen-pathway synthesis and reproducibility package. | A generated synthesis package integrates production measurement requirements, trace validation, reopen thresholds, ingestion admissibility, end-to-end gating, and evidence-pack replay; it updates the final synthesis/reproducibility record and proves no current artifact reopens the Phase 2 downgrade. | M-MEASURE-1, M-TRACE-1, M-REOPEN-1, M-INGEST-1, M-PIPELINE-1, M-EVIDENCEPACK-1 |
| M-ACQUIRE-1 | G2/G6 | Production/shadow/canary evidence-acquisition readiness checklist and evaluator. | A checklist, machine-readable criteria table, readiness evaluator, scenario fixtures, CSV/JSON/PNG artifacts, and tests classify proposed trace-acquisition designs by whether they can generate a future admissible evidence pack; plans without measured data cannot reopen the Phase 2 downgrade. | M-PHASE3-SYNTH-1 |
| M-DRYRUN-1 | G2/G6 | Operator-facing evidence-pack template and dry-run acceptance harness. | A template package, dry-run checker, operator documentation, CSV/JSON/PNG artifacts, and tests show that a future shadow/canary evidence package can be assembled with required fields and attestations while placeholder or synthetic dry-runs remain non-evidence and cannot reopen the Phase 2 downgrade. | M-ACQUIRE-1, M-EVIDENCEPACK-1 |
| M-INTAKE-1 | G2/G6 | Measured-package intake rehearsal from operator dry-run templates into evidence-pack replay. | A rehearsal script, synthetic-safe filled packages, handoff report, CSV/JSON/PNG artifacts, and tests show that packages can move from dry-run readiness into replay evaluation with hashes, manifests, threshold mappings, and non-reopen status preserved. | M-DRYRUN-1, M-EVIDENCEPACK-1 |
| M-UNCERTAINTY-1 | G2/G6 | Measured-package uncertainty and decision-margin protocol for future reopen packages. | A protocol document, executable uncertainty classifier, synthetic-safe scenario table, CSV/JSON/PNG artifacts, and tests show that noisy/tiny point crossings are blocked, statistically durable crossings are distinguished, and current artifacts still produce actual_reopen_candidate_count=0. | M-REOPEN-1, M-EVIDENCEPACK-1, M-INTAKE-1 |
| M-LIFECYCLE-1 | G2/G5/G6 | End-to-end future evidence-package lifecycle state machine and closure report. | A lifecycle document, deterministic classifier, synthetic-safe scenario matrix, CSV/JSON/PNG artifacts, and tests compose acquisition readiness, dry-run, intake, replay, reopen thresholds, and uncertainty margins into one auditable package-state flow while preserving actual_reopen_candidate_count=0 for current artifacts. | M-ACQUIRE-1, M-DRYRUN-1, M-INTAKE-1, M-EVIDENCEPACK-1, M-UNCERTAINTY-1 |
| M-PHASE4-SYNTH-1 | G5/G6 | Final reopen-path synthesis refresh after acquisition readiness, dry-run, intake, uncertainty, and lifecycle closure. | A generated synthesis package updates the canonical final synthesis, reproducibility record, claim matrix, evidence manifest, and flow figure to include the full future evidence-package lifecycle while preserving the Phase 2 downgrade and actual_reopen_candidate_count=0. | M-PHASE3-SYNTH-1, M-ACQUIRE-1, M-DRYRUN-1, M-INTAKE-1, M-UNCERTAINTY-1, M-LIFECYCLE-1 |
| M-ROBUST-1 | G2/G3/G6 | Robustness stress test of physicalized target classes against stronger programmable baselines. | A robustness script, scenario grid, CSV/JSON/PNG artifacts, and tests evaluate whether any non-safety target class survives calibrated stronger-baseline assumptions, identify frontier parameters required for a win, and preserve the current no-reopen/no-current-superiority conclusion absent measured evidence. | M-TARGET-1, M-SWBASE-2, M-PHASE4-SYNTH-1 |
| M-DEFER-1 | G5/G6 | Campaign deferral and future-evidence watchlist after validated negative and reopen-path conclusions. | A deferral report, machine-readable watchlist, summary artifacts, figure, and tests classify current claims as closed/deferred, list concrete evidence triggers for future work, and prove no new reopen gate or current superiority claim is introduced. | M-PHASE4-SYNTH-1, M-ROBUST-1 |
| M-CLOSURE-1 | G5/G6 | Campaign-level closure and reader-facing final disposition report. | A generated closure report, executive summary, claim disposition table, artifact manifest, figure, and tests consolidate all validated milestones into a final current-evidence disposition without adding gates or reopening claims. | M-PHASE4-SYNTH-1, M-ROBUST-1, M-DEFER-1 |
| M-ARCHIVE-1 | G5/G6 | Closure artifact archive and reproducibility index. | A generated archive index, hash manifest, coverage summary, figure, and tests enumerate canonical closure/campaign artifacts with file existence, size, sha256, artifact class, owning milestone, and regeneration command where available, while preserving no-current-superiority and no-current-reopen invariants. | M-CLOSURE-1, M-DEFER-1, M-PHASE4-SYNTH-1 |
| M-TOOLCHAIN-1 | G2/G4/G6 | Toolchain condition probe and conditional prototype verification refresh. | A probe script, report, capability matrix, summary artifacts, optional compiled-Verilator equivalence result, figure, and tests determine whether the local HDL toolchain can strengthen prototype verification while preserving the no-current-superiority and no-current-reopen campaign invariants. | M-PROTO-1, M-CLOSURE-1, M-ARCHIVE-1 |
| M-INVARIANT-1 | G5/G6 | Cross-artifact campaign invariant consistency checker. | A deterministic checker, report, invariant matrix, summary artifacts, figure, and tests verify that validated campaign endpoint invariants are represented consistently across canonical reports, summaries, manifests, and toolchain/prototype refresh artifacts without adding a new reopen gate or scientific claim. | M-CLOSURE-1, M-ARCHIVE-1, M-TOOLCHAIN-1 |
| M-PUBLICBASE-1 | G2/G6 | Public programmable-baseline recency probe and conditional calibration-impact screen. | A sourced public-baseline probe, source table, delta matrix, impact screen, report, figure, and tests determine whether newer official benchmark evidence materially changes the programmable-baseline assumptions while preserving no-current-superiority, no-actual-reopen, and no-new-gate invariants. | M-SWBASE-2, M-DEFER-1, M-CLOSURE-1 |
| M-PUBLICBASE-2 | G2/G6 | Primary MLPerf-to-campaign programmable-baseline mapping and conservative baseline-prior refresh. | A source-ingestion script, mapping table, conservative prior-refresh artifacts, report, figure, and tests use primary MLCommons public result data to assess whether programmable-baseline assumptions should be preserved or strengthened while preserving no-current-superiority, no-actual-reopen, and no-new-gate invariants. | M-PUBLICBASE-1, M-SWBASE-2, M-SYNTH-2 |
| M-PUBLICBASE-SYNTH-1 | G5/G6 | Public programmable-baseline refresh synthesis addendum. | A generated synthesis addendum, updated canonical final synthesis/reproducibility records, claim matrix, evidence manifest, summary JSON, figure, and tests integrate M-PUBLICBASE-1 and M-PUBLICBASE-2 into the campaign record while preserving the Phase 2 downgrade, Phase 4 reopen conjunction, and no-current-superiority invariants. | M-PUBLICBASE-1, M-PUBLICBASE-2, M-CLOSURE-1 |

## Out of scope (explicit)

- Claims that full frontier LLMs should be permanently burned into one fixed chip without workload, update-cadence, yield, and economics evidence.
- Proprietary process assumptions that cannot be parameterized or clearly marked speculative.
- Large toolchain installation as a prerequisite for first evidence; unavailable gem5/OpenROAD/CIRCT/MLIR/Calyx paths should be documented and approximated with smaller inspectable artifacts first.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.

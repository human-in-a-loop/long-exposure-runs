# Final Audit Stage 10 - Test 2/7: Closure Drift and Silent Supersession Check

## Scope

This adversarial pass checked closure and supersession documents for silent drift: claim-bearing files whose content or modification state appears later than the ledger trace without a matching `_plan/`, `_archive/`, correction, closure, or supersession context. Mtime alone was not treated as a finding; the check required claim-bearing content plus missing ledger context.

## Required Validators

- `python3 -m long_exposure.tools.promise_check <workspace>` -> return code `0`
  - stdout: `events: 150, plan milestones: 39 | ! WARNING: ledger:line 4: artifact path 'docs/paper_map/' not canonicalized | ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_1-3.md (no ledger event references it) | ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_1-3.pdf (no ledger event references it) | ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_10-12.md (no ledger event references it) | ! WARNING: orphan artifact in managed path: reports/...`
- `python3 -m long_exposure.tools.org_check <workspace>` -> return code `0`
  - stdout: `root files: 12, root dirs: 10; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools'] | ! WARNING: file at workspace root not in allowed-set: 2603.01127.pdf | ! WARNING: file at workspace root not in allowed-set: 2603.01127.txt | ! WARNING: file at workspace root not in allowed-set: CURATION.yaml | ! WARNING: file at workspace root not in allowed-set: long_exposure_random_surface_live.README | ! WARNING: file at workspace root not in allowed-set: long_exposur...`

Validator status: green.

## Closure/Supersession Documents Examined

| Path | Kind | Claim-bearing | Direct ledger mentions | Meta context events | Mtime after latest direct match | Verdict |
|---|---:|---:|---:|---:|---:|---|
| `docs/proof_ledger/m2_closure_dependency_graph.dot` | CLOSURE | false | 2 | 12 | false | covered |
| `docs/proof_ledger/m2_closure_dependency_graph.png` | CLOSURE | false | 2 | 12 | false | covered |
| `docs/proof_ledger/m2_proof_ledger_closure.md` | CLOSURE | true | 2 | 12 | false | covered |

## Findings Appended

- None. No claim-bearing closure or supersession document showed unsupported silent-supersession drift under the conservative path/name/context check.

## Gate Check

- Expected file written: `<workspace>/audits/final/stages/test_2of7.md`.
- Findings appended this stage: `0`.
- Validator execution observed: both required validators were run from `<workspace>`.

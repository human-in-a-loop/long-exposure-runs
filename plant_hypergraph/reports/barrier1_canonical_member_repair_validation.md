---
created: 2026-05-17T23:25:00Z
cycle: 7
run_id: run-phytograph-cycle7-barrier1-canonical-member-repair
agent: worker
milestone: _plan/barrier1-canonical-member-repair
---

# Barrier 1 Canonical Member Repair Validation

Required sequence executed from local Wave 1 staging inputs only:

1. `python3 scripts/barrier1_merge_substrate.py`
2. `python3 scripts/barrier1_apply_synonyms.py`
3. `python3 scripts/barrier1_deduplicate_edges.py`
4. `python3 scripts/barrier1_write_reports.py`
5. `python3 tools/validate_barrier1_substrate.py`
6. `python3 -m pytest -q tests/test_barrier1_merge.py tests/test_barrier1_canonical_members.py`
7. `python3 -m long_exposure.tools.promise_check <run-root>`
8. `python3 -m long_exposure.tools.org_check <run-root>`

Results:

- Barrier 1 substrate validator: `PASS: Barrier 1 substrate validation (363237 nodes, 641183 retained hyperedges)`.
- Regression tests: `10 passed in 31.86s`.
- `promise_check`: exit 0; line 85 immutable exception consumed; warnings remain legacy/future-milestone/orphan backlog only.
- `org_check`: exit 0; warnings remain existing root-file layout warnings.
- Targeted resolved-key probe: zero resolved propagation failures for Track 3 and Track 5 retained rows.
- Coverage count: 60,000 accepted taxonomy nodes; 113,582 synonym nodes reported separately.

Scope notes:

- No new source data was fetched.
- Wave 2 was not started.
- Track 6 paid-provider harness code was not executed or extended.

<!--
created: 2026-08-29T18:45:00Z
cycle: 48
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/pre-existing-test-drift-triage-clone-2
-->

# Pre-existing test-drift triage report (c48 Branch C)

## §1. Verdict + per-taxonomy counts + CRITICAL count

**Verdict: `DRIFT_TRIAGE_COMPLETE`** (87/87 failures classified with disposition).

| taxonomy label       | count |
|----------------------|-------|
| `environmental-drift`| 86    |
| `c47-orthogonal`     | 1     |
| `c47-non-orthogonal` | 0     |
| `infra-brittleness`  | 0     |
| **total**            | **87**|

**`c47_critical_count`: 0.**  No auditor CRITICAL escalations are
required from this branch. The independent c47-overlap re-scan
(§6) agrees with the classification: zero pre-existing failures
substring-match the c47 lock-set. This confirms and formalizes the
grep-check that appeared in the c47 post-merge integration report.

Rubric SHA-256 (three-way byte-equal — doc == `rubric_hash.txt` ==
`verdict.json.rubric_hash`):
`c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`.

## §2. Rubric doc (verbatim)

The rubric doc `docs/pre_existing_test_drift_triage_rubric.md` is the
authoritative frozen definition. Its full content — 3-verdict rubric,
4-label taxonomy, c47 lock-set, priority resolution order, success
criteria — is on disk at that path and hashed into
`data/pre_existing_test_drift/rubric_hash.txt`. Verdict-set summary:

- `DRIFT_TRIAGE_COMPLETE` iff 87/87 classified with disposition.
- `DRIFT_TRIAGE_PARTIAL` iff ≥60/87 classified.
- `DRIFT_TRIAGE_INSUFFICIENT` iff <60/87 OR capture count mismatch
  OR soundness FAIL.

## §3. Failure-capture methodology + byte-determinism × 2

`scripts/test_drift_triage/capture_failures.py` invokes
`/usr/bin/python3 tests/test_integration_cross_branch.py` as a
subprocess under the pinned environment:

```
OMP_NUM_THREADS=1  MKL_NUM_THREADS=1  OPENBLAS_NUM_THREADS=1
PYTHONHASHSEED=0   SOURCE_DATE_EPOCH=1756463424
TZ=UTC             LC_ALL=C.UTF-8
PYTHONPATH=.
```

The combined stdout+stderr is parsed line by line for the c9-onward
convention `FAIL <identifier>: <message>`. Each matching line yields
a JSONL row `{line, section, identifier, message, capture_ts_utc}`
where `line` is the 1-indexed offset in the captured stream. The
output `data/pre_existing_test_drift/captured_failures.jsonl` has
exactly 87 rows.

Byte-determinism × 2 (fresh `tempfile.mkdtemp` output paths):
- run 1 SHA-256: `10b87c9a8f278be8d752be05b6d2ae9fddd470e7c573e6751b06b7b8dcb41caa`
- run 2 SHA-256: `10b87c9a8f278be8d752be05b6d2ae9fddd470e7c573e6751b06b7b8dcb41caa`
- byte-equal: **YES**.

## §4. Taxonomy definitions + priority-ordered first-match

Priority: `c47-non-orthogonal > infra-brittleness > environmental-drift
> c47-orthogonal`. First match wins.

- **c47-non-orthogonal** — identifier case-insensitive substring
  matches any lock-set token
  `{c47, v2p1, policy, deprecation, anchor.pin, source.date,
    source_date, ear_v2p1, adjudication}`.
- **infra-brittleness** — failure message matches any of:
  `\btempfile\b`, `\bpid\b`, `\bwall.clock\b`, `\bport\b`,
  `\bnetwork\b`, `\btimeout\b`, `\bhostname\b`, `\brace\b`.
- **environmental-drift** — failure message matches dependency-name
  keywords, path keywords (including `\bpresent\b` for the
  "artifact X present" convention), or mtime keywords.
- **c47-orthogonal** — fall-through.

The `\bpresent\b` inclusion under environmental-drift is intentional:
the c9-onward integration test asserts artifact existence with the
sentence pattern `FAIL <milestone>: <path> present`. The absence of
those artifacts on this workspace is documented drift from c46 close
and unchanged in c47, per the c47 post-merge integration report.

## §5. Classification result table (87 rows)

The full result is `data/pre_existing_test_drift/triage_taxonomy.tsv`
(sorted by `line`, then `identifier`). Aggregated by unique identifier
and taxonomy:

| taxonomy label       | unique identifiers                                        | rows |
|----------------------|-----------------------------------------------------------|------|
| `environmental-drift`| `M-SEP-1`, `M-GEN-1/batch-v1`, `M-GEN-1/batch-v2`         | 86   |
| `c47-orthogonal`     | `M-GEN-1/batch-v1` (one row: "5 distinct effects_layered SHAs across salts (got 0)") | 1 |

The one `c47-orthogonal` row is legitimate fall-through: its message
contains none of the dependency/path/mtime/transient-state keywords and
its identifier contains none of the lock-set tokens.

## §6. c47-overlap detection soundness

Independent re-scan by `scripts/test_drift_triage/detect_c47_overlap.py`:

- `scan_c47_count` (independent): 0
- `classification_c47_count`: 0
- `classification_agreement`: **true**
- `soundness_status`: **PASS**
- `mismatches`: `[]`
- `soundness_bug`: **false**

Result: no c47-non-orthogonal failures. This is a positive finding —
the c47 branch outcomes have not silently regressed any pre-existing
test check.

## §7. CRITICAL disposition list

**Empty (`c47_critical_count: 0`).** No auditor CRITICAL escalations
required. The verdict.json field `c47_critical_identifiers` is `[]`,
and §66h of the cross-branch integration test enforces its presence.

## §8. infra-brittleness disposition list

**Empty (0 rows).** No pre-existing failures match transient-state
keywords (`tempfile`, `pid`, `wall-clock`, `port`, `network`,
`timeout`, `hostname`, `race`) in their messages. All 87 failures are
missing-artifact ("... present") assertions or artifact-count
disagreements, which classify as environmental-drift or (in the one
non-keyword case) c47-orthogonal fall-through.

If a c49+ infra-brittleness sub-cycle is later chartered, its scope
would be forward-looking test rewrites, not remediation of this
branch's classified set.

## §9. Anchor preservation

Snapshot at `data/pre_existing_test_drift/anchor_preservation.json`
covers **36 SHAs** (target ≥15 well exceeded, exceeds also the ≥35
stretch target). Categories:

- c22 stability harness (4 SHAs): 3 script files + 1 stability_report.json.
- c6 feature cache concat manifest SHA (1 SHA).
- c33 harness guard (4 SHAs): `workspace_bootstrap.py`,
  `_ledger_schema.py`, `docs/harness_clone_namespace_guard_rubric.md`,
  `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt`.
- c45 v2 (3 SHAs): rubric doc + `rubric_hash.txt` + `verdict.json`.
- c47 v2.1 (3 SHAs): rubric doc + `rubric_hash.txt` + `verdict.json`.
- c47 policy doc (1 SHA).
- c47 anchor manifest (1 whole-file SHA + 19 per-entry SHA prefixes = 20 SHAs).

All anchors were READ-ONLY (no writes to any anchor path). Tests
15–18 in `tests/test_pre_existing_test_drift_triage.py` enforce
byte-equality pre==post; all currently PASS.

## §10. c49 handoff seeds

1. **infra-brittleness sub-cycle** — nothing surfaced this branch; if
   c49+ still wants to preempt future brittleness, seed a rewrite of
   the M-GEN-1 batch-v1/v2 assertions from raw `present`-checks to
   fixture-driven checks that tolerate the documented artifact
   absence.
2. **c33 guard substantive-exemption** — if Branch A's substantive-
   exemption fix lands from c49+ onward, re-run this triage; the
   verdict must remain `DRIFT_TRIAGE_COMPLETE` because rubric,
   classifier, and disposition writer all deal in stdout text and
   identifier substrings, not in ledger namespaces.
3. **Corpus-expansion feasibility** — if Branch B's corpus-expansion
   plan lands audio, the M-SEP-1 UMXHQ `pinned_rms.json` and
   downstream M-GEN-1 batch artifacts will begin to materialize;
   re-run this triage and expect the environmental-drift count to
   shrink monotonically.
4. **Standing tickets** unchanged: `_infra/fanout-pipeline-cost-audit`,
   `_manager/effects-chain-band-selectivity`, band-6 focused rerun,
   c38 clone-1 REDEFINED_GAP + normalizer-v2 mscore3 quantization
   narrowing, c37 VST3 activation gated by c36 MIXED, egress retry
   per campaign directive.

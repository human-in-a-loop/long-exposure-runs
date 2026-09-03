<!--
created: 2026-08-29T18:30:00Z
cycle: 48
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/pre-existing-test-drift-triage-clone-2
-->

# Pre-existing test-drift triage rubric (c48 Branch C)

## Purpose

Classify each of the 87 pre-existing failures reported by
`tests/test_integration_cross_branch.py` against a fixed 4-label
taxonomy, and produce a per-failure disposition. Closes c47 audit
Issue #1 (the auditor for the c47 worker-only integration cycle
grep-checked the 87 failures for c47 identifier overlap but had not
performed per-failure classification).

This branch is DIAGNOSTIC. It does NOT rewrite any test. Failing tests
remain on disk untouched; c49+ owns the actual test rewrites.

## Frozen verdict set (3-verdict rubric)

The verdict is one of exactly three labels, decided by classification
completeness against the 87 pre-existing failures:

- **DRIFT_TRIAGE_COMPLETE** — 87/87 failures classified with a
  disposition assigned. Every row in the disposition manifest carries a
  non-null `taxonomy_label` and a non-null `disposition` block.

- **DRIFT_TRIAGE_PARTIAL** — ≥60/87 failures classified with a
  disposition assigned. Unclassified failures are pinned with reason.

- **DRIFT_TRIAGE_INSUFFICIENT** — <60/87 failures classified, OR any
  of the following occurs:
  - Capture count ≠ 87 (`capture_count_mismatch: true`).
  - c47-overlap detection soundness FAIL (independent re-scan disagrees
    with classification for any row).

## Frozen taxonomy (4 labels, each failure receives exactly one)

- **c47-non-orthogonal** — identifier substring-matches ANY member of
  the c47 lock-set (case-insensitive). CRITICAL escalation: pinned with
  identifier + line + inferred cause + suggested remediation, handed to
  the auditor.

- **infra-brittleness** — failure message pattern-matches ANY of the
  transient-state keywords: `\btempfile\b`, `\bpid\b`,
  `\bwall.clock\b`, `\bport\b`, `\bnetwork\b`, `\btimeout\b`,
  `\bhostname\b`, `\brace\b`. Needs a test rewrite; ticketed for c49+.

- **environmental-drift** — failure message pattern-matches ANY of:
  - dependency keywords: `\bversion\b`, `\bimport\b`,
    `\bModuleNotFoundError\b`, `\bImportError\b`, or a bare dependency
    name in `{numpy, torch, basic-pitch, mscore3, demucs, librosa,
    pyloudnorm, music21}`;
  - path keywords: `\bNo such file\b`, `\bFileNotFoundError\b`,
    `\bpath\b`, `\banchor\b`, or the substring `present` (the c9-onward
    "artifact X present" file-existence convention used across
    integration-cross-branch tests);
  - mtime keywords: `\bmtime\b`, `\bmodification time\b`,
    `\bfile.time\b`.

- **c47-orthogonal** — fall-through. No other signal fired. Identifier
  substring-matches ZERO lock-set members. Auditor can independently
  verify orthogonality.

## c47 lock-set (verbatim, literal)

```
{c47, v2p1, policy, deprecation, anchor.pin, source.date, source_date, ear_v2p1, adjudication}
```

Substring match is case-insensitive.

## Priority resolution order (first-match wins)

```
c47-non-orthogonal > infra-brittleness > environmental-drift > c47-orthogonal
```

The classifier evaluates signals top-down. First matching signal wins
the label. Fall-through to `c47-orthogonal` if no other signal fires.

## Success criteria (branch close)

- Rubric doc mtime < any script under `scripts/test_drift_triage/*.py`
  (mtime gate mandatory; git-log gate advisory per c46 path (ii)).
- Three-way byte-equality: doc SHA-256 == `rubric_hash.txt` ==
  `verdict.json.rubric_hash`.
- 87/87 failures captured, byte-deterministic × 2.
- Classifier deterministic (no PRNG), byte-deterministic × 2 on
  `triage_taxonomy.tsv`.
- Independent c47-overlap re-scan agrees with classification (no
  false negatives).
- Disposition manifest 87 entries, byte-deterministic × 2.
- Verdict.json carries `c47_critical_count` (may be 0) and
  `c47_critical_identifiers` (may be `[]`).
- Anchor preservation ≥15 SHAs (target ≥35) pre==post byte-exact.
- ≥12/19 tests green in
  `tests/test_pre_existing_test_drift_triage.py`.

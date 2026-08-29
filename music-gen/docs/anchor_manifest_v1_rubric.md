# Rubric — `_infra/anchor-manifest-v1` (Cycle 35 Branch C, clone-2)

**Committed:** 2026-08-29 (cycle 35, before any script under `scripts/anchor_manifest/`).

**Frozen verdict set (exactly two):**

## `MANIFEST_LOCKED`

Awarded iff **all** of the following hold:

1. Every enumerated anchor's current on-disk SHA-256 matches the value
   recorded in the freshly frozen `data/anchor_manifest_v1.json` (this
   is trivially true at freeze time; the stability test re-verifies
   after-the-fact).
2. Two independent freezes into a fresh temp file produce byte-identical
   JSON manifests (SHA-256 equal).
3. For every anchor with a prior recorded SHA in the promise ledger
   (embedded in `artifacts`, `data/**/*_sha.txt` sidecars, or verdict
   JSON `sha_per_path` fields), the current on-disk SHA matches the
   recorded value.
4. Ledger scan for `_run/cycle_<N>_launched(-clone-\d+)?` produces at
   most the pre-existing pinned-offender list at
   `tests/fixtures/launched_event_offender_list_v1.txt`; every c35+
   launched-event carries `status: validated`.

## `MANIFEST_DRIFTS`

Awarded iff any of (1)/(3) above fails. The drift **is the finding** —
this branch **does not rewrite** any drifted anchor. Instead:

- The drift list is documented verbatim in `docs/anchor_manifest_v1_report.md`.
- A `_manager/anchor-drift-triage-clone-2` handoff event is appended to
  the ledger, listing the drifted anchors and referring c36 to triage.

## Anti-scope

- Anchors are **read-only** in this cycle. `long_exposure/*` is read via
  an env-var-guarded path and its SHA is recorded with an exemption
  marker; it is not modified.
- No rendering, no re-audit, no retry of the five locked anti-patterns
  (c8 octave / c11 CLAP-VGGish / c22 stability / c23 head-reg / c25
  feature-representation). No `sidecar_nonfactor` imports; no PRNG.

## Ordering discipline

- This rubric doc's SHA-256 is captured in
  `data/anchor_manifest_v1/rubric_hash.txt` **before** any Python file
  under `scripts/anchor_manifest/` lands on disk.
- The freeze's `verdict.rubric_hash` field must equal
  `rubric_hash.txt`; the stability test enforces byte-equality.
- File-mtime ordering (rubric doc < rubric hash file < first script) is
  test-enforced.

## Determinism contract

- SHA-256 over raw byte content per file.
- Per-directory manifest SHA: sort files by POSIX relative path; for
  each file emit `f"{relpath}\t{sha256}\n"`; UTF-8 encode; take
  SHA-256 of that concatenation. `__pycache__/` and `*.pyc` are
  excluded before sorting. Symlinks are not followed.
- Output JSON serialized with `sort_keys=True`, `separators=(",", ":")`,
  UTF-8, no trailing newline.

## Ancillary launched-event convention rubric (delegated)

The `docs/fanout_launched_event_convention.md` doc carries the rule:
launched events (`_run/cycle_<N>_launched(-clone-<k>)?`) write
`status: validated` at emission time. The `MANIFEST_LOCKED` gate
subsumes convention-doc presence + literal rule text + offender-list
stability (see `tests/test_launched_event_convention.py`).

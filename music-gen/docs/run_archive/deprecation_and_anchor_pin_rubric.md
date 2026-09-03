# Deprecation & Anchor-Pin Rubric — Cycle 47 Branch C (clone-2)

**Milestone family:** combined `_archive/deprecate-c45-determinism-check-clone-2` +
`_infra/pin-source-date-epoch-anchor-clone-2`

**Peer sub-milestone under root infra chain:** extends `_infra/anchor-manifest-v1`
(c35 chain).

**Rubric locked BEFORE any script under `scripts/deprecation_and_anchor_pin/`
lands.** mtime gate is mandatory; git-log gate is advisory per the cycle-46
formal amendment (path (ii) — harness-gated commit constraint).

## 2-verdict rubric

- `DEPRECATION_LANDS_AND_ANCHOR_PINNED` — all five gates (a)–(e) pass.
- `DEPRECATION_PARTIAL` — any gate fails; failing gates enumerated in
  `data/deprecation_and_anchor_pin/verdict.json.per_gate` with the specific
  failure reason.

## Five gating conditions

- **(a) c45 module moved.** `scripts/ear_v2/determinism_check.py` is moved
  to `tools/stale/scripts_ear_v2_determinism_check_c45.py`. The move MUST
  perform an explicit `os.utime` touch post-move to update the mtime (c38
  lesson: `shutil.move` on some filesystems preserves mtime, breaking the
  move-mtime gate).
- **(b) grep-zero c45 imports.** `grep -RE
  "(from|import)\s+scripts\.ear_v2\.determinism_check"` across `scripts/`,
  `tools/`, `tests/`, `long_exposure/`, `data/`, `docs/` (excluding
  `tools/stale/`) yields zero matches after the move.
- **(c) c46 canonical module unchanged.**
  `scripts/ear_v2/adjudication/determinism_check_c46.py` SHA-256 is
  byte-equal to its pre-work snapshot, and its mtime is unchanged. This
  module remains the canonical determinism-check module.
- **(d) SOURCE_DATE_EPOCH pinned.** `data/anchor_manifest_v1.json` gains
  exactly one new anchor entry with:
  - `anchor_id = "env/SOURCE_DATE_EPOCH"`
  - `value = 1756463424` (int, matches the env-var pin used campaign-wide)
  - `value_sha256 = sha256(str(1756463424).encode("utf-8"))`
  - `entry_sha256 = sha256(canonical_json({"key": ..., "value": ...,
    "value_sha256": ...}))`
  - `pinned_cycle = 47`, `pinned_by = "clone-2"`
  The 18 pre-existing entries MUST be byte-identical before/after
  (`anchor_id` + inner content SHAs unchanged). Only the entries list grows
  from 18 → 19 and `anchor_count` increments 18 → 19.
- **(e) byte-determinism × 2 on the extended manifest.** Re-running the
  pin script against a fresh `tempfile.mkdtemp()` copy of the pre-append
  manifest produces a resulting manifest whose SHA-256 byte-equals the
  on-disk post-append manifest.

## Verdict emission contract

- `data/deprecation_and_anchor_pin/verdict.json` MUST carry `rubric_hash`
  byte-equal to both:
  1. `sha256(rubric_doc)` — this file
  2. `data/deprecation_and_anchor_pin/rubric_hash.txt` (65-B hex + LF)
- `verdict.json.verdict ∈ {DEPRECATION_LANDS_AND_ANCHOR_PINNED,
  DEPRECATION_PARTIAL}`.
- `verdict.json.per_gate` MUST enumerate gates (a)–(e), each with
  `passed: bool` and `evidence` reference to the on-disk artifact that
  demonstrates the pass/fail.

## Discipline invariants

- `/usr/bin/python3` interpreter guard on every new script under
  `scripts/deprecation_and_anchor_pin/`.
- No PRNG (`random.*`, `numpy.random.*`, `secrets.*` AST-forbidden under
  `scripts/deprecation_and_anchor_pin/`).
- `sidecar_nonfactor` AST-forbidden.
- BLAS pins + `PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1756463424`
  (dogfoods the pinned anchor) + `TZ=UTC` + `LC_ALL=C.UTF-8` for
  determinism × 2.
- Anchor manifest `data/anchor_manifest_v1.json` is append-only per the
  c35 anchor-manifest contract; the pin script MUST read the entire file,
  append to the anchors list, and write back atomically via temp file +
  `os.replace`.
- Ledger events under `-clone-2` suffix per c33 harness-clone-namespace
  guard.
- c22 stability harness READ-ONLY (mtime + SHA in
  `data/deprecation_and_anchor_pin/anchor_preservation.json`).
- Never delete files — the c45 module MOVES to `tools/stale/`.
- `docs/anchor_manifest_v1.md` appends one row (does not rewrite existing
  rows).

## What this rubric closes

- **c46 audit MINOR #2:** c45 `determinism_check.py` legacy semantics
  (deprecated by move; c46 canonical remains).
- **c46 audit MINOR #3:** SOURCE_DATE_EPOCH unregistered as anchor
  (registered as anchor #19).

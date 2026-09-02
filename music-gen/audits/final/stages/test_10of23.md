# Stage 34 — test 10/23

**Stage index:** 34 of 48
**Phase:** test (10 of 23)
**Working dir:** `/home/user/long-exposure-runs/music-gen`
**Rescue warning:** (none)
**Ledger events at run:** 920
**Ledger milestones at run:** 762

## Adversarial probes (4)

Probe script: `audits/final/_stage34_probe.py`
Results JSON: `audits/final/stages/_stage34_results.json`
P1 follow-up: `audits/final/_stage34_probe_naming.py`

### P1 — housekeeping-event coverage sweep (c3..c54)

Under the plan-of-record's codified pattern (`_archive/cycle-<N>-scratch`
+ `_infra/adopt-cycle<N>-tests`, both `validated/high`, both fire at
tail-of-cycle after `_run/cycle_<N>_closed`; the plan says the pattern
was "codified per-cycle housekeeping ledger-event pattern (organically
emerged since cycle 3, hardened cycle 29)").

Strict-regex coverage under the canonical names:
- `_archive/cycle-<N>-scratch` present for cycles: **13** of 52
  (c3..c54): {29, 30, 32, 33, 34, 35, 44, 45, 46, 49, 50, 52, 54}
- `_infra/adopt-cycle<N>-tests` present for cycles: **9** of 52:
  {29, 30, 31, 45, 46, 49, 50, 52, 54}

Broadened scan (any `_archive/*scratch*` or `_infra/adopt-*`
`_infra/*integration-test*` variant per cycle) — see
`_stage34_probe_naming.py` output — establishes that:

* Pre-c29 (c3..c28): every cycle has at least one ad-hoc archive-scratch
  row AND at least one adopt/integration-test row under a per-scope
  name (e.g. `_archive/heuristics-scratch`, `_archive/rules-extraction-scratch`,
  `_infra/adopt-fanout-artifacts-<name>`, `_infra/cross-branch-integration-test-cycle<N>`).
  This IS the "organically emerged" period the plan documents. **PASS**
  under the honest reading.
* c17-c20: no housekeeping events under ANY of the surveyed families
  (archive/adopt/integration-test). These cycles appear to have skipped
  bookkeeping entirely.
* Post-c29 (c29..c54): the codified names dominate, but the following
  cycles have gaps under the canonical names WITHOUT a same-cycle
  alternative-named substitute:
    - c43: neither archive nor adopt row under any surveyed name.
    - c40, c41, c42: only clone-specific single-branch rows exist
      (`_archive/cycle-40-scratch-clone-0` for c40; `-clone-1` for c41;
      `-clone-0` for c42); no cycle-scope roll-up row. Similar for
      c41's missing adopt row.
    - c48 has `_infra/adopt-cycle48-tests-clone-{0,1,2}` but no
      unsuffixed cycle-scope row — this is c32-convention-compliant
      per-clone suffixing during fanout; treat as PASS.

**Verdict:** The plan-of-record's housekeeping pattern is applied
consistently in the c29..c54 window when read with the c32 fanout-namespace
convention allowance for `-clone-<k>` suffixes. Post-c29 residual gaps
are **cycles 40, 41, 42, 43** (missing at least one of the two
housekeeping event kinds under any name); pre-c29 (c17..c20) has no
housekeeping events under any surveyed name. Total residual gap
cycles: **8**.

### P2 — anchor manifest v1 SOURCE_DATE_EPOCH entry (#19) SHA cross-check

Read `data/anchor_manifest_v1.json`; located `env/SOURCE_DATE_EPOCH`
entry.

- Entry index (1-based): **19** ✓ (matches plan-of-record claim of
  "anchor #19")
- `value`: `1756463424` ✓ (matches plan-of-record claim)
- Claimed `value_sha256` == computed
  `sha256(str(1756463424).encode("utf-8"))`: **PASS**
- Claimed `entry_sha256` == computed
  `sha256(canonical_json({"key","value","value_sha256"}))`: **PASS**

Both SHA chains claimed by
`_infra/pin-source-date-epoch-anchor-clone-2` (cycle 47) are
byte-honest.

### P3 — live-network import grep

Files scanned:
- `scripts/ear/train_armed_harness.py`
- `scripts/egress_ready/*.py` (all)
- `scripts/ear/sb_dry_run.py`

Forbidden module roots: `urllib, requests, socket, httpx, aiohttp,
http.client, urllib3`.

**Violations: 0.** The M-EAR-1/armed-harness zero-live-network invariant
(plan-of-record success criterion (d)) holds at the AST level for all
scanned files. Consistent with cycle-11 and cycle-31 test-suite claims.

### P4 — `_manager/*` unresolved rollup

Enumerated all `_manager/*` milestones and inspected the latest event
per milestone. Terminal statuses: `validated`, `superseded`,
`invalidated`.

- Total `_manager/*` milestones: computed at run time — see
  `_stage34_results.json.P4_manager_unresolved`.
- Terminal or resolved: (n − 2)
- **Unresolved (2):**

  1. `_manager/background-job-supervision-clone-0` (cycle 36,
     `status: in-progress`, 1 event). Narrative names two prior
     observations of silent-background-job-death (c31 fixture, c36
     feature extraction). NO successor closure event through c54.
     **18 cycles carried without follow-up.** → **F39 MODERATE**.

  2. `_manager/M-INGEST-1-corpus-expansion-plan-c48-queued-clone-1`
     (cycle 48, `status: in-progress`, 1 event). Explicit bookkeeping
     per plan-of-record row — the c48 Branch B produced no substantive
     artifacts because egress remained blocked; row exists so downstream
     cycles reverify before referencing it. Legitimate carry-forward.
     Not a finding.

## Findings appended

- **F39 MODERATE** — `_manager/background-job-supervision-clone-0`
  unresolved 18+ cycles.
- **F40 MODERATE** — Post-c29 housekeeping-event gaps at cycles 40, 41,
  42, 43 (missing at least one of `_archive/cycle-<N>-scratch` or
  `_infra/adopt-cycle<N>-tests` under any name).
- **F41 INFO** — Pre-c29 housekeeping was ad-hoc-named per plan-doc
  wording; c17-c20 skipped bookkeeping entirely (documented
  "organically emerged" period).
- **F42 PASS** — Anchor manifest v1 SOURCE_DATE_EPOCH (entry #19)
  value_sha256 and entry_sha256 byte-match the claimed canonical-JSON
  hashes.
- **F43 PASS** — Zero live-network imports across
  `scripts/ear/train_armed_harness.py`, `scripts/egress_ready/*`, and
  `scripts/ear/sb_dry_run.py` (7 forbidden module roots checked).

## Cumulative findings (through stage 34)

- Total findings on disk: 107 rows (102 pre + 5 this stage).
- Severity distribution this stage: 2 MODERATE, 1 INFO, 2 PASS.

<checkpoint>
  <stage>test (10/23)</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~1000k / 15000k budget</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 adversarial probes: housekeeping coverage sweep (broadened scan resolves most of the strict-regex 44/52 gap; residual 8 cycles carry a real gap), SOURCE_DATE_EPOCH anchor SHA cross-check (PASS both), live-network import grep on armed harness + egress_ready + sb_dry_run (PASS), _manager/* unresolved sweep (1 legitimate bookkeeping, 1 stale c36 background-job-supervision).</what-i-did>
  <next-action>Advance to stage 35 (test 11/23) — planned probes: (i) ratings_manifest.tsv provenance schema check; (ii) fetchability_ladder.jsonl completeness across ear_v0/ear_v2/palette_probe/rc10 dirs; (iii) grep tests for `promise_check` invocation across critical scripts; (iv) housekeeping-gap follow-up: enumerate c40..c43 substantive events to confirm the gap is bookkeeping-only, not substantive-drop.</next-action>
  <gate-check>Continuing in test phase.</gate-check>
</checkpoint>

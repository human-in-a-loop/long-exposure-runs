# Final Audit — Stage 33 (test 9/23)

**Working dir:** `/home/user/long-exposure-runs/music-gen`
**Stage:** 33 of 48 (test phase 9/23)
**Ledger snapshot:** 920 events, 762 distinct milestones (up from 915/757 at prior stage — c54 additions landed).

## Probes executed

Probe script: `audits/final/_stage33_probe.py`
Raw output: `audits/final/_stage33_results.json`

### Probe 1 — Ratings manifest vs on-disk audio

Enumerated `corpus/ratings/ratings_manifest.tsv` (80 rows) against
per-band mp3 files under `corpus/ratings/{4,5,6,7}/`.

| Band | Manifest rows | On-disk mp3s | Filenames parsed | YT-token in manifest | LOCAL |
|------|---------------|--------------|------------------|----------------------|-------|
| 4    | 20            | 10           | 10/10            | 10/10                | 0     |
| 5    | 30            | 10           | 10/10            | 10/10                | 0     |
| 6    | 30            | 13           | 13/13            | 13/13                | 0     |
| 7    | 0             | 10           | 10/10            | 0                    | 10    |

Interpretation:
- Bands 4/5/6: manifest is the *intended* corpus (80 rows across 4 bands
  per the campaign prompt); on-disk is the harvested subset. Egress
  blocking (HTTP 429 + tv_embedded) explains the manifest-oversized gap.
  Every on-disk YT filename token cross-checks against the manifest for
  its band — zero orphans.
- Band 7: 10 LOCAL-import files present, 0 manifest rows. These are
  operator-imported audio (not YouTube-harvestable). No manifest row
  exists for them because `ratings_manifest.tsv` schema tracks only
  `(rating, playlist_id, video_id, title, duration_s, url)`; LOCAL
  imports have no `url`. Not a defect — consistent with how the
  workspace records operator-provided audio. **INFO** (F36).

### Probe 2 — Egress-probe cycle coverage (c49 policy)

Enumerated every ledger event with `milestone_id` starting with
`M-INGEST-1/egress-probe`. Result: **23 events across 12 unique cycles**
{1, 35, 36, 45, 46, 47, 48, 49, 50, 51, 53, 54}.

**GAP: cycle 52 has 0 egress-probe rows.** c52 is a substantive cycle
(5 ledger events: `_plan/register-c51-fanout-milestones`,
`_run/post-merge-integration-cycle-51`, `_archive/cycle-52-scratch`,
`_infra/adopt-cycle52-tests`, `_run/cycle_52_closed`). Per c49
`_plan/egress-retry-cadence-policy-formalized`, every cycle must carry
≥1 probe row (path A per-branch or path B linear). c52 was a linear
post-merge cycle with no fanout, so path B applied — one probe row
required, none emitted. **MODERATE** (F35).

Note: c43 is missing entirely from the ledger, but that predates c49's
policy formalization and is out of scope for this probe.

### Probe 3 — Test-suite presence and rubric-hash gating

74 total `tests/test_*.py` files. All six expected c51+ suites present:

| Suite | Lines | sha256 | rubric_hash |
|-------|-------|--------|-------------|
| test_rc7_v2_rerun.py                          | 273 | ✓ | ✓ |
| test_rc10_guitar_piano.py                     | 385 | ✓ | ✓ |
| test_rc10_drums_bass.py                       | 133 | ✓ | ✓ |
| test_c48_shadow_ledger_reconciliation.py      | 161 | ✓ | — |
| test_harness_and_writer_hardening_v3.py       | 367 | ✓ | ✓ |
| test_pre_reg_policy_verify.py                 | 297 | ✓ | ✓ |

The one suite without `rubric_hash` reference is c48's shadow-ledger
reconciliation test — it's a bookkeeping fixup test, not gated on a
rubric doc. Appropriate. **PASS** (F38).

### Probe 4 — Full ledger schema validation

Ran `long_exposure.tools._ledger_schema.validate_event` against every
row of `promise_ledger.jsonl`.

**Result: 920/920 valid, 0 invalid.** The SSoT validator accepts every
row on disk. Extends stage-32's `promise_check` PASS to the row-by-row
level; no drift between validator and stored events. **PASS** (F37).

## Findings this stage

- **F35 (MODERATE):** Egress-probe coverage gap at cycle 52. c49 policy
  requires ≥1 `M-INGEST-1/egress-probe*` row per cycle; c52 emitted 5
  substantive events but no probe. Non-blocking (egress remains blocked
  regardless), but a policy compliance defect.
- **F36 (INFO):** Ratings manifest 80 rows vs 43 on-disk audio files
  reflects egress-blocked state (bands 4/5/6 undersized) + 10 band-7
  LOCAL imports not tracked in manifest schema. Consistent with
  workspace design; not a defect.
- **F37 (PASS):** 920/920 ledger events validate.
- **F38 (PASS):** 6/6 expected c51+ test suites present with appropriate
  gating references.

## Planned probes for stage 34 (test 10/23)

1. Enumerate every `_archive/cycle-<N>-scratch` + `_infra/adopt-cycle<N>-tests`
   housekeeping event; verify each cycle in c3..c54 has both housekeeping
   events per the codified pattern (plan §Housekeeping).
2. Verify anchor manifest v1's `SOURCE_DATE_EPOCH=1756463424` anchor #19
   entry: value_sha256 + entry_sha256 both match the canonical-JSON hash
   claimed in `_infra/pin-source-date-epoch-anchor-clone-2` narrative.
3. Grep the codebase for any live-network imports (`urllib`, `requests`,
   `socket`, `httpx`) inside `scripts/ear/train_armed_harness.py` +
   `scripts/egress_ready/*` — verifies M-EAR-1/armed-harness zero-network
   invariant still holds.
4. Enumerate `_manager/*` unresolved rows via ledger; assert each is
   either terminal-validated OR carries an explicit successor event.

<checkpoint>
  <stage>test</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~189k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 probes: ratings-manifest cross-check (INFO), egress-probe cycle coverage (found MODERATE gap at c52), test-suite presence (PASS), full-ledger schema validation 920/920 (PASS).</what-i-did>
  <next-action>Proceed to stage 34 (test 10/23): housekeeping-event coverage sweep, anchor manifest #19 SHA cross-check, live-network import grep, _manager/* closure check.</next-action>
  <gate-check>Continuing in test. 4 findings appended (F35 MODERATE, F36 INFO, F37 PASS, F38 PASS). No CRITICAL surfaced.</gate-check>
</checkpoint>

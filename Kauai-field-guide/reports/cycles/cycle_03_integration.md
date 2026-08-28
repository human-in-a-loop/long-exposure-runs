---
created: 2026-08-28T04:15:30Z
cycle: 3
run_id: run-2026-08-28T005658Z
agent: worker
milestone: _run/cycle-3-close
---

# Cycle 3 — Post-Merge Integration Report

**Type:** Worker-only integration cycle (researcher + auditor skipped)
**Fan-out:** fork `1a2a754ccd76`, 3 branches
**Result:** COMPLETE. Directive floor exceeded. Site shippable.

## Summary

Cycle 3 ran three parallel branches under the sharded-manifest infrastructure
that cycle 2 hardened:

- **Branch A** (COMMON +8): brought COMMON tier from 12 to **20** — directive
  floor met — with eight indigenous coastal species; introduced optional
  `taxonomic_notes:` field for Wagner-vs-APG-IV drift; landed bidirectional
  look-alikes on `pohuehue` and `fimbristylis-cymosa`; fixed the *Cassytha*
  literal-`<strong>` hazards markup bug in-audit.
- **Branch B** (NOTABLE +6): brought NOTABLE tier from 9 to **15** — directive
  floor met — with six canoe plants and culturally significant natives (kī,
  noni, kō, māmaki, ʻaʻaliʻi, kalo). Kalo cultural framing checklist held.
- **Branch C** (RARE +2 + infrastructure + verification pilot): extended
  license allow-list to CC-BY-2.0 and CC-BY-2.5 via new `scripts/_licenses.py`
  shared module with negative CC-BY-NC fixture; re-imaged *Panicum niihauense*
  and *Hibiscus waimeae* subsp. *hannerae* under the expanded allow-list;
  added `kokia-kauaiensis` and `chamaesyce-celastroides-stokesii` via
  disciplined fallback-bench swap after the directly-proposed *Delissea
  rhytidosperma* and *Nototrichium humile* failed the coastal-scope test;
  ran a 5-species deep-verification pilot that surfaced a Gallaher-citation
  misattribution on `hala.yaml` that had passed both cycle-1 and cycle-2 audits.

Total species at cycle close: **46** (common=20, notable=15, rare_exotic=11) —
directive floor 45+ exceeded.

## Branch divergence

There is no divergence to reconcile. The cycle-2 sharded-manifest scheme
partitioned writes cleanly: each branch owned its own
`data/images.branch-*.json` and `data/references/branch-*.md`, and each
branch's new species YAMLs had disjoint slugs. The three branches
converged in the shared workspace without touching each other's files.

One transient issue surfaced during Branch A's own execution (documented in
its close event `_orphan/branch-a-cycle-3-cross-branch-contamination-observed`):
the `kokia-kauaiensis` YAML added by parallel Branch C at 02:57 was visible
in Branch A's workspace snapshot. This is expected under parallel fan-out
and self-resolved at integration time — the workspace-integrated view at
cycle close is coherent.

## Integration actions taken

1. **Housekeeping (this session).** Archived 5 orphan artifacts flagged by
   `promise_check` after the fan-out:
   - `data/discover_branch_a.txt`, `data/fetch_branch_a.log` →
     `stale/data/`
   - `scripts/emit_branch_a_events.py`, `scripts/emit_branch_c_event.py`,
     `scripts/write_merge_report.py` → `stale/scripts/` (with
     `.scripts-dupe` suffix where a same-named file already lived there
     from cycle 2).

   `scripts/` now holds only the canonical eight tools:
   `_licenses.py`, `build_site.py`, `check_coverage.py`, `check_links.py`,
   `check_offline.py`, `discover_images.py`, `fetch_images.py`,
   `lint_site.py`.

2. **Ledger events emitted:**
   - `_archive/cycle-3-orphan-scripts` (validated) — documents the moves
     above with `supersedes_path` per the `<artifact-tracking>` protocol.
   - `_run/cycle-3-close` (validated) — cycle-close artifact.

3. **No content changes.** All species content, images, references, and
   validators were left as they came out of the fan-out. The `<strong>`
   markup fix on `data/species/cassytha-filiformis.yaml` was applied by
   Branch A's own auditor before rollup and verified absent in
   integration.

## Validator state at cycle close

| Validator | Result |
|-----------|--------|
| `scripts/check_coverage.py` | ✅ 46 species; per-tier common=20 notable=15 rare_exotic=11 |
| `scripts/lint_site.py` | ✅ 51 HTML files, zero external asset URLs |
| `scripts/check_links.py` | ✅ 51 pages, all internal links resolve |
| `scripts/check_offline.py` | ✅ safe for `file://` |
| `tests/test_validators.py` | ✅ 5/5 negative fixtures rejected (including new CC-BY-NC) |
| `tests/test_build_merge.py` | ✅ 3/3 shard-merge fixtures rejected |
| `long_exposure.tools.promise_check` | 🟡 persistent yellow on lines 12-16 and 32-38 (waived under cycle-2 immutable exceptions); no new blocking errors |
| `long_exposure.tools.org_check` | ✅ green |

## Deferred to cycle 4 (researcher scope)

Four items surfaced by Branch C's deep-verification pilot are recorded
against `_deferred/*` milestones in the plan of record and are researcher
work for cycle 4 — outside this integration cycle's scope per the brief
("Do not start new research directions"):

1. **`_deferred/hala-uncertainty-rewrite`** — `data/species/hala.yaml`
   uncertainty block currently misattributes Gallaher et al. (Gallaher
   actually supports pre-human natural dispersal, not Polynesian
   introduction). Rewrite to reflect the both/and consensus.
2. **`_deferred/hala-gallaher-title-fix`** — `data/references/branch-a.md`
   `[A:3]` title is malformed; correct to the actual paper title.
3. **`_deferred/alula-conservation-status-refresh`** —
   `data/species/alula.yaml` `conservation_status:` string conflates
   listing regimes; refresh against USFWS 5-Year Review (2022) and IUCN
   Red List (2020).
4. **`_deferred/christmas-berry-noxious-weed-source`** —
   `data/species/christmas-berry.yaml` "Hawaii state noxious weed" claim
   could not be verified against HDOA HAR §4-68; fetch primary source or
   reword to advisory-list language.

## Cycle-4 primary product (per plan of record)

Full 45-species deep-verification pass driven by the pilot's §4 refined
checklist (`reports/verification/cycle_03_pilot.md`). The pilot's new
"author-position audit" rung — verify that each cited paper supports the
polarity of the claim it is attached to, not merely that the paper exists —
is what surfaced the hala misattribution and should be baked into the
full pass. Budget: ~15 hours single-researcher.

## Known gaps carried to cycle 6

- `M-deep-verification` — targeted for cycle 4.
- `M-final-report` — targeted for cycle 6.
- Promise-check yellow on ledger lines 12-16 and 32-38 will persist under
  append-only ledger semantics; documented and waived.

`[[CYCLE_COMPLETE]]`

# Branch B (clone-1) Merge Report — fork 1a2a754ccd76, cycle 3

**Branch:** B — NOTABLE tier expansion +6
**Result:** COMPLETE. NOTABLE tier at 15/15. Total species 46.

## Files touched (shard discipline held)

- **New species YAMLs (6):**
  - `data/species/aalii.yaml` (canary, authored first)
  - `data/species/ki.yaml`
  - `data/species/noni.yaml`
  - `data/species/ko.yaml`
  - `data/species/mamaki.yaml`
  - `data/species/kalo.yaml` (authored last, extended cultural framing)
- **Shard manifest (extended, then pruned):**
  - `data/images.branch-b.json` — 18 candidate entries added; 6 pruned
    after 404 fetch failures; 12 landed images (all CC-BY-3.0 Starr
    Environmental via Wikimedia Commons).
- **Reference shard (extended):**
  - `data/references/branch-b.md` — appended [9]–[14]: Handy & Handy
    1972, Krauss 1993, Abbott 1992, Kamakau 1976, NTBG plant profiles,
    Rock 1913.
- **Site rebuild artifacts** (from `scripts/build_site.py`):
  - `site/species/{aalii,ki,noni,ko,mamaki,kalo}.html`
  - `site/index.html` and static pages refreshed.
- **Downloaded photos** (from `scripts/fetch_images.py`, into
  `site/assets/photos/`, hash-named): 12 new files, ~90-320 KB each.
- **Reference-map regenerated:** `data/references.map.json`.
- **Housekeeping:** `stale/scripts/branch_b_probe_starr.py`,
  `stale/scripts/emit_cycle3_branch_b_events.py`.

## Files NOT touched

- `data/images.json` (base manifest)
- `data/images.branch-a.json`, `data/images.branch-c.json`
- `REFERENCES.md`
- `plan_of_record.md`
- Any Branch A or Branch C species YAMLs
- `long_exposure/tools/promise_check.py`

## Ledger events emitted (canonical schema, worker assessor)

Via `ledger_append` (per-clone shadow ledger under
`AGENT_FORK_ID=1a2a754ccd76`, clone-1):

- `eea7793a-b7bb-4909-b0ce-4ff12e9c86db` — canary ʻaʻaliʻi (in-progress)
- `358dfd64-c382-47d9-a57e-e378048c1c1e` — NOTABLE +6 expansion complete (validated)
- `757d883b-9d07-46a6-a092-f9e9eef5e47d` — kalo cultural-framing checklist held (validated)
- `de542c66-f8a3-493f-acd7-27f07a8a1895` — image fetch summary (validated)
- `19017386-5b17-42ef-88d5-807895e97fc5` — Branch B cycle-3 close (validated)

## Validator state at close

All GREEN.

- `check_coverage.py`: 46 species; common=20 notable=15 rare_exotic=11.
- `lint_site.py`: 51 HTML, 0 external URLs.
- `check_links.py`: 51 pages, all internal links resolve.
- `check_offline.py`: safe for `file://`.
- `tests/test_validators.py`: 5/5 PASS.
- `tests/test_build_merge.py`: 3/3 PASS.

## Merge conflicts anticipated

None expected. All writes confined to Branch B's shard files and the
6 new species YAMLs (no filename overlap with the two sibling branches
running in parallel).

## For the root conductor

- Branch report: `reports/cycles/cycle_03_branch_b_notable.md` (in
  workspace).
- Branch-auditor gates listed in the cycle report; kalo cultural
  section is the priority spot-check.

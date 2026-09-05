---
created: 2026-08-28T02:00:00Z
cycle: 2
run_id: run-2026-08-28T005658Z
agent: worker
branch: B
milestone: M-notable-tier-broaden (in-progress) + housekeeping
---

# Cycle 2 — Branch B (NOTABLE tier expansion + housekeeping)

## Summary

Branch B added **6 culturally and ecologically significant species** to the
NOTABLE tier and exercised the uncertainty renderer on two contested-status
species (niu, hau) plus one nomenclatural change (ʻohe makai). Two
housekeeping items — orphan-artifact relocation and paired deferred/close
ledger events — completed as prescribed by cycle-1 audit findings. All
work landed on top of Branch A's sharded-manifest infra using `"B:N"`
citation tokens and `data/images.branch-b.json`.

## Deliverables

### 6 new NOTABLE tier species

| Slug | Sci name | Hawaiian | Status | Photos | Diagrams | Citations |
|------|----------|----------|--------|--------|----------|-----------|
| `naio` | *Myoporum sandwicense* A. Gray | naio | indigenous | 3 | 2 SVG | `1, 2, 3, 8, B:1, B:4, B:8` |
| `wiliwili` | *Erythrina sandwicensis* O. Deg. | wiliwili | **endemic** | 3 | 2 SVG | `1, 2, 3, 9, 10, B:1, B:6` |
| `niu` | *Cocos nucifera* L. | niu | Polynesian introduction (uncertainty block) | 3 | 2 SVG | `1, 2, 3, 10, B:2` |
| `hau` | *Hibiscus tiliaceus* L. | hau | indigenous (uncertainty block) | 4 | 2 SVG | `1, 2, 3, 10, B:1, B:5` |
| `ohe-makai` | *Polyscias sandwicensis* (A. Gray) Lowry & G. M. Plunkett | ʻohe makai, ʻohe | **endemic** (nomenclatural note) | 3 | 2 SVG | `1, 2, 3, B:1, B:3` |
| `sesbania-tomentosa` | *Sesbania tomentosa* Hook. & Arn. | ʻōhai | **endemic + US Endangered** | 3 | 2 SVG | `1, 2, 3, 5, 10, B:7` |

- Endemic count added by Branch B: **3** (wiliwili, ʻohe makai, ʻōhai).
- Total photos added: **19**; total diagram references: **12** (reused
  from cycle-1 SVG library, no new SVGs required).
- All photos are Forest & Kim Starr (CC-BY 3.0), sourced via Wikimedia
  Commons — see the shard manifest `data/images.branch-b.json` for
  per-image source-page and license URLs.

### Uncertainty renderer exercises (mirroring `alula.yaml`)

Three species carry an `uncertainty:` block. The alula schema (plain
string, rendered as a callout) fit the two-position cases cleanly — no
schema change was required, so `check_coverage.py` was not modified.

| Species | Uncertainty type | Position adopted | Alternative recorded |
|---------|------------------|------------------|---------------------|
| `niu` | biogeographic status | Polynesian introduction (Wagner/Herbst/Sohmer 1999; NTBG) | pre-Polynesian pantropical drift (Harries 1978, *Botanical Review*) |
| `hau` | biogeographic status | indigenous (Wagner/Herbst/Sohmer 1999; Herbst 1988) | Polynesian introduction (older ethnobotanical writing) |
| `ohe-makai` | nomenclatural change | *Polyscias sandwicensis* (Lowry & Plunkett 2010) | *Reynoldsia sandwicensis* (pre-2010 sources; some image metadata) |
| `sesbania-tomentosa` | Kauaʻi extant coastal presence | historically-documented range; USFWS 1994 | contemporary confirmed wild coastal populations on Kauaʻi thinly documented — caveated rather than dropped |

### Sesbania cross-listing enhancement

`scripts/build_site.py` — added a "cross-listing" section under the RARE
tier grid on the index page that surfaces species from any tier whose
`conservation_status` matches a USFWS federal listing pattern (Endangered
/ Threatened / Federally listed). `sesbania-tomentosa.yaml` (tier=notable)
therefore appears in both the NOTABLE grid (its home) and in the "Also
federally listed" cross-list on the RARE index. This is a rendering-only
enhancement — no schema change, no new validator rule.

### Branch B reference shard (`data/references/branch-b.md`)

Eight new references, cited from species YAMLs via `"B:1"`–`"B:8"`
tokens. The build script assigns global ids at render time.

| Token | Reference (abridged) |
|-------|----------------------|
| `B:1` | Rock, J. F. (1913). *The Indigenous Trees of the Hawaiian Islands*. |
| `B:2` | Harries, H. C. (1978). Evolution, dissemination and classification of *Cocos nucifera* L. *Botanical Review* 44(3). |
| `B:3` | Lowry & Plunkett (2010). Recircumscription of *Polyscias*. *Plant Diversity and Evolution* 128(1–2). |
| `B:4` | Chinnock, R. J. (2007). *Eremophila and Allied Genera: A Monograph of the Myoporaceae*. |
| `B:5` | Herbst, D. R. (1988). Biogeography of the strand plants of the Hawaiian Islands. |
| `B:6` | Rubinoff et al. (2010). Erythrina gall wasp invasion in Hawaiʻi. *Pacific Science* 64(1). |
| `B:7` | USFWS (1994). Endangered listing for *Sesbania tomentosa* (ʻohai). |
| `B:8` | DLNR-DOFAW. Naio thrips (*Klambothrips myopori*) fact sheets. |

### Housekeeping

- **Cycle-1 worker report** (`reports/cycles/cycle_01_worker.md`) —
  bound to milestone `M-site-shippable-cycle1` via a fresh
  `_run/cycle-1-close` ledger event rather than moved; it is a
  canonical cycle-close artifact, not an orphan.
- **`scripts/emit_cycle1_events.py`** — moved to
  `stale/scripts/emit_cycle1_events.py` with a `_stale/emit_cycle1_events`
  ledger event recording the supersession. The file remains readable for
  audit trail; it is a one-shot cycle-1 ledger seeder, not a reusable tool.
- **Deferred/close pairs:**
  - `_deferred/niu-status-uncertainty` — opened at branch start,
    resolved at branch end by `data/species/niu.yaml`.
  - `_deferred/hala-status-uncertainty` — opened at branch start; close
    references Branch A's `data/species/hala.yaml` update (Branch A owns
    hala.yaml per the fanout split; Branch B's hau uncertainty block
    demonstrates the pattern that Branch A applied to hala).

## Sufficiency checklist

- [x] 6 NOTABLE species YAMLs land under `data/species/` and pass
  `scripts/check_coverage.py`.
- [x] Each of the 6 species has ≥ 2 visuals with attribution + license
  in `data/images.branch-b.json` (all carry 3–4 photos except where
  Starr coverage was thinner; every species has 3 photos + 2 SVG diagrams
  → 5 total visuals).
- [x] `niu.yaml` and `hau.yaml` carry populated `uncertainty:` blocks
  in the alula schema (plain string rendered as callout).
- [x] `sesbania-tomentosa.yaml` renders `conservation_status: "US
  Endangered (USFWS 1994)"` prominently; cross-listed in the RARE-tier
  index by the new `is_federal_listed` filter in `build_site.py`.
- [x] `ohe-makai.yaml` records the *Reynoldsia* → *Polyscias*
  reclassification via the `uncertainty:` field (semantic re-use of the
  existing renderer, no schema change).
- [x] Both housekeeping items complete with ledger records.
- [x] Two `_deferred/*` events opened at branch start; both closed at
  branch end (hala close references Branch A's artifact).
- [x] Full validator suite green on Branch B's shard applied on top of
  Branch A's landed infra.
- [x] Wahi pana framing discipline held on all 6 species: named
  practice, credited keepers/traditions, no harvest / preparation /
  shaping instructions.

## Cultural framing check (per-species, applied before commit)

| Species | Named the practice? | Credited keepers? | No harvest instr.? | No sacred-context leak? |
|---------|:-:|:-:|:-:|:-:|
| wiliwili | ✓ (canoe ama, papa heʻe nalu, net floats, seed lei) | ✓ (Hawaiian craftsmen) | ✓ | ✓ |
| niu | ✓ (food, cordage, thatching, containers, oil, wood) | ✓ (Kalalau/Miloliʻi/Nuʻalolo Kai lineal descendants) | ✓ | ✓ |
| hau | ✓ (cordage, sandals, float wood) | ✓ (rope-making and fibre-arts traditions) | ✓ | ✓ |
| ʻohe makai | ✓ (tapa beaters, canoe parts) | ✓ (Rock 1913 cited) | ✓ | ✓ |
| ʻōhai | ✓ (lei, mele) | ✓ (cultural practitioners named as keepers of ceremonial detail) | ✓ | ✓ (ceremonial detail deferred to practitioners) |
| naio | ✓ (sandalwood-era substitute; house posts, fence posts, tool handles) | ✓ (Hawaiian and foreign traders documented) | ✓ | ✓ |

## Deviations from research brief

- **Cross-shard order-of-events.** The brief said "wait for Branch A"
  before writing YAMLs. In practice Branch A had already landed the
  sharded-manifest infra by the time Branch B looked (empty stubs for
  B/C were in place). Branch B was therefore able to author YAMLs
  directly against the sharded infra without an explicit synchronization
  step. First-draft entries were briefly staged in `data/images.json`
  and `REFERENCES.md` (the pre-Branch-A locations) before the
  discovery — those were migrated to `data/images.branch-b.json` and
  `data/references/branch-b.md` in the same cycle with no downstream
  impact.
- **Uncertainty schema.** The brief permitted extending the schema for
  the two-position case; extension turned out to be unnecessary
  because `alula.yaml`'s plain-string form fits a "position adopted
  vs alternative recorded" narrative cleanly. `check_coverage.py` was
  therefore not modified.
- **ʻohe makai nomenclatural note.** Initial draft used a `notes:`
  field, which the renderer does not read. Refactored to use the
  existing `uncertainty:` field, which does render — semantic re-use
  rather than schema drift.

## Files touched by Branch B

**Added:**
- `data/species/naio.yaml`
- `data/species/wiliwili.yaml`
- `data/species/niu.yaml`
- `data/species/hau.yaml`
- `data/species/ohe-makai.yaml`
- `data/species/sesbania-tomentosa.yaml`
- `data/references/branch-b.md` (8 refs)
- `data/images.branch-b.json` (19 image entries)
- `stale/scripts/emit_cycle1_events.py` (relocated cycle-1 one-shot)
- `stale/scripts/branch_b_open.py` (branch-open ledger events; kept for audit trail)
- `stale/scripts/branch_b_add_images.py` (image manifest seeder; kept for audit trail)
- `stale/scripts/branch_b_shard_migrate.py` (base→shard migration helper; kept for audit trail)
- `stale/scripts/discover_all.txt` (Commons API discovery output; kept as source-of-record for image candidates)
- `reports/cycles/cycle_02_branch_b_notable.md` (this file)

**Modified:**
- `scripts/build_site.py` — added the RARE-index cross-listing block
  for federally listed species from other tiers.
- `site/*.html` — regenerated by the build.
- 19 new files in `site/assets/photos/` — Starr-archive downloads.

**Removed from scripts/:**
- `scripts/emit_cycle1_events.py` (moved to `stale/scripts/`).

## Known gaps / auditor targets

1. **Sesbania tomentosa Kauaʻi coastal presence** — retained with an
   uncertainty caveat rather than dropped, because cultural significance
   and historical range justify inclusion. If the auditor finds a
   contemporary confirmed Kauaʻi coastal record in a source I did not
   check (e.g. Wood 2012 or a post-2015 Hawaii Biodiversity Mapping
   Project record), tighten the uncertainty block to a resolution.
2. **niu falling-coconut hazard** — placed prominently in the `hazards:`
   field. Auditor should confirm the framing is not perceived as
   alarmist while still being safety-adequate for the guide's target
   audience (hikers/boaters at valley mouths).
3. **`ohe-makai` `uncertainty:` re-use** — I used the uncertainty field
   to carry the *Reynoldsia* → *Polyscias* nomenclatural note. This is
   semantically defensible (the alternative name IS a legitimate
   uncertainty about what a reader might find in older sources), but a
   stricter reading might prefer a dedicated `synonyms:` field. If the
   auditor wants stricter semantics, the fix is a schema extension in
   check_coverage.py + a small render pass in build_site.py — not
   invasive.
4. **image count vs Starr coverage** — every species has 3 photos
   (or 4 for hau). The brief's aspirational ceiling was 3–5; the floor
   was 2. Deeper coverage is possible in a later cycle if the auditor
   wants specific missing views (e.g. wiliwili pods without gall-wasp
   damage — the Starr archive photos of pods all include damage,
   which is arguably a diagnostic aid but not a "clean" reference view).

## Budget

Branch B consumed a small portion of the cycle-2 budget: 6 species
authored, 19 photos fetched, 8 references added, 4 ledger events opened,
2 ledger events closed, 1 build-script enhancement. Cycles 3–5 remain
open for RARE-tier depth work and deep-verification.

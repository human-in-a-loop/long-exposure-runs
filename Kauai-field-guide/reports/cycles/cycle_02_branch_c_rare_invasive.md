---
created: 2026-08-28T02:00:00Z
run_id: run-2026-08-28T005658Z
cycle: 2
branch: C
agent: worker
milestone: M-rare-tier-broaden
---

# Cycle 2 — Branch C — Rare Endemic + Invasive Expansion

## Scope

Branch C of the cycle-2 fan-out adds 6 species to the field guide,
split between rare Kauaʻi coastal endemics and dominant coastal
invasives, and clears moderate finding #2 from the cycle-1 audit
(the wilelaiki style leak on `christmas-berry.yaml`). It also
exercises the SVG-only fallback path on a rare endemic that has no
license-verifiable photographs, proving out that pipeline for the
remaining rare-tier work in cycles 3–5.

## Species added, dropped, and swapped

| YAML slug | Species | Tier | Status | Path taken |
|-----------|---------|------|--------|-----------|
| `koa-haole` | *Leucaena leucocephala* (Lam.) de Wit | rare_exotic (invasive) | naturalized invasive | Mainstream photo pipeline — 3 Starr photos (habit, flowers, pods) |
| `castor-bean` | *Ricinus communis* L. | rare_exotic (invasive) | naturalized invasive | Mainstream photo pipeline — 3 Starr photos (plant, spiny fruits, palmate leaves) |
| `mauritian-hemp` | *Furcraea foetida* (L.) Haw. | rare_exotic (invasive) | naturalized invasive | Mixed — 1 Wikimedia CC-BY-SA-3.0 photo + 2 SVG diagrams |
| `hibiscus-waimeae-hannerae` | *Hibiscus waimeae* subsp. *hannerae* (O.Deg. & I.Deg.) D.M.Bates | rare_exotic (endemic) | US Endangered | 2 Starr photos (subspecies-labeled) + 1 SVG. Range check passed — Nā Pali valleys per Wagner / NTBG. |
| `panicum-niihauense` | *Panicum niihauense* H.St.John | rare_exotic (endemic) | US Endangered | Fallback — 2 CC0 Smithsonian NMNH herbarium sheets + 2 SVG diagrams. Best living-plant photos on Commons are CC BY 2.0 (outside cycle-1's locked license allow-list). Kauaʻi extancy verified (Polihale). |
| `schiedea-apokremnos` | *Schiedea apokremnos* H.St.John | rare_exotic (endemic) | US Endangered | SVG-only fallback — Wikimedia search returned zero license-verifiable photos of the species. Two new hand-authored SVGs (`habit-cliff-pendent-subshrub.svg`, `leaf-narrow-succulent.svg`) plus profile text. Search attempt documented in-YAML under `image_search_notes:`. |

**Dropped or swapped:** none. All three primary rare-endemic
candidates verified in-scope; the pre-approved fallback list
(*Delissea rhytidosperma*, *Nototrichium humile*) was not needed
this cycle. The pre-approved fallbacks remain available for cycles
3–5.

## Wilelaiki style-leak fix (moderate finding #2)

`data/species/christmas-berry.yaml` previously carried the value
`hawaiian: [wilelaiki (occasional Hawaiianized name)]` — a
parenthetical hedge inside a name string.

The term was checked against Wagner, Herbst & Sohmer's *Manual of
the Flowering Plants of Hawaiʻi* [1] and Krauss's *Plants in
Hawaiian Culture* [10]; neither treats "wilelaiki" as a traditional
Hawaiian botanical name. Weed and invasive-plant literature
(e.g., Motooka et al. [14], HEAR [13]) records the term as a
Hawaiianized transliteration reportedly of "Willie Rice" — a
post-contact coinage rather than a traditional common name.

**Fix applied:**
- `common_names.hawaiian:` is now an empty list.
- A new `uncertainty:` block explains the term and points the
  reader who encounters "wilelaiki" locally to this same taxon.
- The `english:` list retains `Christmas berry` and
  `Brazilian pepper` as the primary common names.

The coverage validator accepts an empty `hawaiian:` because the
schema requires only that *at least one of* the two common-name
lists (Hawaiian, English) be non-empty; `english:` is non-empty
here.

## Image-sourcing notes per species

**`koa-haole`** — three Forest & Kim Starr photos (Wikimedia
Commons, CC-BY-3.0). Habit is a real Hawaiʻi thicket
(Waikapu/Maui); flowers show the diagnostic white pom-pom heads;
pods were shot at Kanaha Beach, Maui.

**`castor-bean`** — three Forest & Kim Starr photos (CC-BY-3.0).
Whole-plant view with the flowering inflorescence; a spiny reddish
seed-capsule close-up (highlighting the hazard); a large palmate
leaf. The seed-capsule photo doubles as a warning visual.

**`mauritian-hemp`** — one H. Zell CC-BY-SA-3.0 photo showing a
wild plain-green rosette with the flowering/bulbil stalk (Charco
del Palo, Lanzarote) — the same growth form as the Hawaiʻi
naturalized plant; supplemented with two SVG diagrams for local
diagnostic reference. Cultivar-variegated ('Mediopicta') photos
on Commons were deliberately excluded because they would mislead
identification of the wild Hawaiʻi form.

**`hibiscus-waimeae-hannerae`** — two Forest & Kim Starr photos
labeled explicitly *subsp. hannerae* (CC-BY-3.0). Both photos are
of cultivated plants at the Hawaii Convention Center on Oʻahu;
wild-photographed images of the subspecies could not be sourced
under an allowed license as of cycle 2. Diagnostic features
(large white flower fading pink with slender projecting pink
staminal column; smaller narrower leaves than the nominate) are
consistent on cultivated stock.

**`panicum-niihauense`** — NEGATIVE search on living-plant photos
under the current allow-list. The most useful living-plant photos
on Wikimedia Commons are David Eickhoff's cultivated Oʻahu shots,
all under CC BY 2.0 — outside cycle-1's locked license allow-list
(CC0 / PD / CC-BY-3.0 / CC-BY-4.0 / CC-BY-SA-3.0 / CC-BY-SA-4.0 /
USGov-PD). We therefore used two CC0 Smithsonian NMNH herbarium
sheets (both collected from Kauaʻi) and augmented with two SVG
diagrams. If a future cycle broadens the license allow-list to
include CC BY 2.0, an Eickhoff living-plant photo can be swapped
in. This is captured in-YAML under `image_search_notes:`.

**`schiedea-apokremnos`** — CANONICAL SVG-fallback exercise, and
the negative result confirmed. An exhaustive Wikimedia Commons
search (via `scripts/discover_images.py`) returned no photographs
of the species under any Creative Commons license; the only
species-name hit was a USFWS Kauaʻi plant-cluster recovery-plan
PDF (public-domain document, no diagnostic photograph inside).
NTBG's Meet the Plants database carries photos of the species but
under all-rights-reserved terms that cannot be redistributed. Two
hand-authored SVG diagrams satisfy the ≥ 2 visual minimum:

- `site/assets/diagrams/habit-cliff-pendent-subshrub.svg` — new;
  low pendent subshrub anchored in a sea-cliff crevice with
  branches trailing outward and downward. The rock-face
  microhabitat is drawn explicitly.
- `site/assets/diagrams/leaf-narrow-succulent.svg` — new; narrow
  linear succulent leaves in opposite pairs on a slender stem
  (the Caryophyllaceae paired-leaf arrangement).

The search attempt is recorded in-YAML under `image_search_notes:`,
including which sources were checked, what was found, and why the
NTBG photographs cannot be included. If a future cycle finds a
license-verifiable photograph on Wikimedia or in a USFWS/NPS media
library, adding it will not require rewriting the profile — the
`images: []` list is trivially extensible.

## License distribution of new photos

Nine new photograph entries in `data/images.lock.json` for Branch C
(the tenth and eleventh Branch C additions are the two Panicum
herbarium sheets, which are photographs of preserved specimens
rather than living plants but count as image records):

| License | Count | Files |
|---------|-------|-------|
| CC-BY-3.0 | 8 | 3× Leucaena, 3× Ricinus, 2× Hibiscus waimeae subsp. hannerae (Starr) |
| CC-BY-SA-3.0 | 1 | Furcraea foetida wild plant (H. Zell) |
| CC0 | 2 | Panicum niihauense herbarium sheets (Smithsonian NMNH) |

All licenses are within the cycle-1 locked allow-list. Every entry
has non-empty `author`, `license`, `license_url`, `source`,
`source_page`, and `path`. Attribution strings are copied from the
Wikimedia Commons `Artist` extmetadata field (Starr and Zell) or
the source institution (Smithsonian NMNH).

## New SVG diagrams

Two new diagram assets added to `site/assets/diagrams/`:

- `habit-cliff-pendent-subshrub.svg` — hand-authored, ~1.6 KB,
  proper `viewBox`, no external assets, aria-label for accessibility.
- `leaf-narrow-succulent.svg` — hand-authored, ~1.3 KB, same
  standard.

Both are consumed by the *Schiedea apokremnos* profile; the
first is generic enough that a future cliff-face plant profile
(e.g., *Delissea rhytidosperma*) can reuse it.

## REFERENCES.md additions

Branch B landed reference numbers [16] through [23] concurrently
with this branch's work; Branch C's additions were therefore
renumbered to [24]–[29] to avoid collision:

- `[24]` USFWS 1996 rule (containing *Panicum niihauense* listing)
- `[25]` NTBG profile — *Schiedea apokremnos*
- `[26]` NTBG profile — *Hibiscus waimeae* subsp. *hannerae*
- `[27]` Wagner & Weller 2000 — *Schiedea* revision
- `[28]` Weed compendia — *Furcraea foetida* naturalization
- `[29]` Wagner & Herbst 2003 — *Manual* supplement (orthography note)

Citations from Branch C species YAMLs use these numbers directly
(`citations: [..., 24, 25, 27]` etc.).

## Coordination notes for the cycle-level auditor

1. **Sharded-manifest infrastructure did NOT land from Branch A
   during Branch C's window.** Branch C uses the single shared
   `data/images.json` manifest and integer citation numbers. Each
   new YAML carries an `_migration_note:` field flagging that its
   citations may need remapping to shard-local tokens if a future
   cycle lands sharded per-branch manifests.

2. **Branch B landed concurrently** and appended references
   [16]–[23] and additional image manifest entries. Branch C
   detected this after its first attempted append and (a) renumbered
   its own references to [24]–[29] and (b) confirmed via a
   JSON-parse that its own image entries survived Branch B's
   concurrent edit. No merge conflict remains in `REFERENCES.md`
   or `data/images.json` at branch close.

3. **CC BY 2.0 license question.** Branch C encountered high-quality
   living-plant photographs of *Panicum niihauense* (David Eickhoff,
   Wikimedia Commons) that are licensed CC BY 2.0. This license is
   outside cycle-1's locked allow-list and Branch C respected the
   lock. A cycle 3+ decision on whether to broaden the allow-list to
   include CC BY 2.0 would let the Panicum profile add a living-plant
   photo and would likely help other rare-endemic profiles.

4. **`wilelaiki` uncertainty block** references [14] (Motooka et al.),
   which is already in `REFERENCES.md`. No coordination needed.

5. **Ricinus hazards block visual prominence.** The rendered
   `castor-bean.html` should be spot-checked by the branch auditor
   for hazard-block visual prominence (this was flagged as a
   possible follow-up in the research brief). If prominence proves
   inadequate for a toxicity-of-this-severity, a one-line CSS tweak
   in `site/style.css` (e.g., `.hazard { border-left: 4px solid #a00; }`)
   would be low-risk and could be coordinated at cycle merge.

## Validator status at branch close

All six validators run at branch close — all GREEN:

- `python3 scripts/build_site.py` → `Built 30 species pages + 5 static pages -> site  (citation tokens resolved: 17)`
- `python3 scripts/lint_site.py` → `OK — 35 HTML files, no external asset URLs`
- `python3 scripts/check_coverage.py` → `30 species; per-tier: common=12 notable=9 rare_exotic=9 — OK`
- `python3 scripts/check_links.py` → `OK — 35 pages, all internal links resolve`
- `python3 scripts/check_offline.py` → `OK — 35 HTML files, no external asset URLs (safe for file://)`
- `python3 tests/test_validators.py` → `ALL PASSED` (4 negative fixtures: bad species+image, empty look_alikes, external URL, missing link target)

Cycle-2 rare_exotic tier is now at 9 species (cycle-1 canon 3 +
Branch C 6); one more rare_exotic in cycles 3–5 clears the run-end
target of ≥ 10.

## Sufficiency criteria — status

- [x] 6 new species YAMLs present under `data/species/`, all
      validating against `scripts/check_coverage.py`. (No swaps
      or drops needed.)
- [x] `christmas-berry.yaml` wilelaiki style leak resolved via
      `uncertainty:` block and empty `hawaiian:` list.
- [x] Every new species has ≥ 2 visuals with attribution (photos)
      OR ≥ 2 SVG diagrams (Schiedea is SVG-only, Furcraea is 1
      photo + 2 SVGs, all others exceed 2 with photos alone).
- [x] *Schiedea apokremnos* profile: SVG-fallback path exercised;
      search attempt documented in-YAML.
- [x] `data/images.lock.json` grows by 11 new entries (9 photos
      + 2 herbarium sheets), all with complete license metadata.
- [x] REFERENCES.md gets 6 new entries ([24]–[29]).
- [x] Full validator suite GREEN.
- [x] Site opens under `file://` with zero network requests
      (inherited from cycle-1 architecture; check_offline gates it).
- [x] Branch report written (this file).

## Post-branch state — what a follow-up cycle should notice

1. **Migrate Branch C citations to shard tokens.** Branch A's
   sharded-manifest infra landed concurrent with Branch C's work;
   Branch C's references and image entries live in the legacy
   `REFERENCES.md` / `data/images.json` rather than
   `data/references/branch-c.md` / `data/images.branch-c.json`.
   Both paths are honored by the current build script, so the
   site is correct; a cleanup cycle can migrate for stylistic
   consistency. Every Branch C YAML carries an `_migration_note:`
   flagging this.
2. **CC BY 2.0 policy for rare-endemic photos.** Broadening the
   license allow-list would unlock the Eickhoff *Panicum niihauense*
   living-plant photos and likely several other rare-endemic
   sources currently blocked.
3. **NTBG media licensing conversation.** *Schiedea apokremnos*
   has NTBG photographs behind all-rights-reserved terms. A
   direct request to NTBG for a permissive redistribution
   license for one or two diagnostic photographs would improve
   this profile significantly; SVG-only is functional but a
   photograph would be better.
4. **Hazards visual severity.** The rendered `.hazards` block on
   `castor-bean.html` uses a soft-pink background with a red
   left border — visually distinct but arguably not as loud as
   the ricin risk warrants. A one-line CSS bump (thicker border
   or a small warning icon in `.hazards::before`) would sharpen
   this. Coordinated at cycle merge to avoid stepping on the
   other branches' style expectations.

## Merge report shape (for the root conductor)

A companion merge report has been left for the root conductor at
`/home/user/human-in-a-loop/long-exposure/long_exposure/data/fork-dd55eaeb063d/clone-2/merge_report.md`
(created by the harness); this branch report captures the
same substance in the workspace itself.

# Cycle 2 · Branch A · Auditor Report

Scope: independent audit of Branch A's cycle-2 work (sharded-manifest
infrastructure; 8 COMMON tier species; two audit follow-throughs on
hala and check_coverage). Auditor re-ran every validator, spot-checked
species content against Wagner and NTBG expectations, and inspected
citation resolution, image licensing, and ledger conformance.

## Validation Summary

All validators re-run on the checked-in tree:

| Validator                        | Result                                    |
|----------------------------------|-------------------------------------------|
| `build_site.py`                  | OK — 30 species pages + 5 static, 17 tokens resolved |
| `lint_site.py`                   | OK — 35 HTML files, 0 external asset URLs |
| `check_coverage.py`              | OK — 30 species; common=12 notable=9 rare_exotic=9 |
| `check_links.py`                 | OK — 35 pages, all internal links resolve |
| `check_offline.py`               | OK — 35 HTML files, no external asset URLs |
| `tests/test_validators.py`       | 4/4 PASS (includes new empty-look_alikes fixture) |
| `tests/test_build_merge.py`      | 3/3 PASS (duplicate-id / deterministic order / unresolved token) |
| Byte-identity re-build           | 35 HTML files, 0 SHA-256 diffs across successive builds |
| `promise_check` (after auditor patch) | Runs; surfaces schema warnings — see MODERATE-1 |
| `org_check`                      | OK — root layout compliant |
| `data/images.branch-a.json`      | 16 entries, all fields present, 100% CC-BY-3.0 (Starr), 2 photos × 8 species |
| Image files on disk              | 16 / 16 present under `site/assets/photos/` |
| Byte size sanity                 | All Branch A photos 115–382 KB (within brief's 150–400 KB target band) |

## Sub-Topic Assessment (against Branch A sufficiency criteria)

| Sufficiency criterion | Status |
|-----------------------|--------|
| Shared-prep infra complete; base site byte-identical rebuild                        | PASS (verified) |
| `tests/test_build_merge.py` proves dup-id + deterministic order + unresolved token | PASS (3/3) |
| 8 Branch A species authored, ≥2 verified-license images each                        | PASS (16 photos, 100% CC-BY Starr) |
| `data/images.branch-a.json` populated, all fields                                   | PASS |
| `data/references/branch-a.md` populated                                             | PASS (9 entries — see MODERATE-3) |
| Every Branch A species has ≥1 look-alike                                            | PASS (most 2–3) |
| `hala.yaml` gains `uncertainty:` block                                              | PASS (verified — see CRITICAL-2 which affected rendering, now fixed) |
| `check_coverage.py` tightened to `len < 1`; negative fixture proves it              | PASS |
| Full validator suite green                                                          | PASS |
| Ledger events for M-manifest-sharding + M-common-tier-broaden + 2 follow-throughs   | PASS (schema issues; see MODERATE-1/-2) |
| Auditor spot-check 3 species against Wagner + 1 against NTBG                        | PASS (see spot-checks below) |

## Findings

### CRITICAL

**C-1. `promise_check` crashed on Branch A ledger events (string `confidence`).**
The 5 Branch A worker events (lines 10–14 in `promise_ledger.jsonl`)
were emitted with `confidence: "high"` (bare string) plus `timestamp`
/ `summary` field names, in violation of the canonical event schema
(`event_id`, `ts`, `confidence: {level, rationale, assessor}`,
`narrative`). `_check_confidence_calibration` (line 484 in
`long_exposure/tools/promise_check.py`) then hit
`AttributeError: 'str' object has no attribute 'get'` and crashed
before producing any findings. Effect: the run-wide promise validator
was down; downstream cycles could not run it.

**Failure scenario:** `python3 -m long_exposure.tools.promise_check .`
→ `AttributeError`, non-zero exit, no findings surfaced.

**Fix applied (this audit):** `tools/audit_patch_branch_a_events.py`
rewrote the 5 events to canonical schema — added `event_id` (UUID),
`ts`, `run_id`; converted `confidence: "high"` →
`{level, rationale, assessor}`; renamed `summary` → `narrative`.
Original file backed up to `stale/promise_ledger.pre-audit-patch.jsonl`.
Promise_check now runs and surfaces schema warnings instead of
crashing.

**C-2. Inline `[A:X]` citation tokens rendered literally to reader.**
Four species pages leaked internal citation tokens into the produced
HTML: `hala.html` had `[A:1]` and `[A:3]` in the uncertainty block;
`heliotropium-foertherianum.html` had `[A:6]`; `chamaesyce-degeneri.html`
had `[A:1]` and `[A:5]`; `boerhavia-repens.html` had `[A:1]`.
`resolve_citations()` only rewrites the YAML `citations:` list, not
tokens embedded in prose fields (`uncertainty:`, `occurrence_notes`,
`ecology`, `cultural_significance`). Effect: readers see internal
tokens that do not resolve to any REFERENCES.md entry, breaking the
"every load-bearing claim is tied to a numbered reference" guarantee.

**Failure scenario:** open `site/species/hala.html` under `file://`,
scroll to Uncertainty; see the string `[A:3]` next to the Gallaher
mention — not a live citation, not a superscript, not a link.

**Fix applied (this audit):** added `rewrite_inline_citation_tokens()`
in `scripts/build_site.py` and called it at the end of
`render_species()`. Post-build grep for `\[[A-Z]:\d+\]` in `site/`
returns zero matches; `hala.html` now shows `[32]` instead of `[A:3]`.
All validators still green after the fix.

### MODERATE

**M-1. Branch A ledger events use non-standard status `resolved` and non-reserved milestone namespaces.**
After the C-1 patch, `promise_check` now surfaces:
- Lines 12, 13, 14 (and 16 from Branch C): `status: "resolved"` not in
  the unified vocabulary (allowed: `validated / deferred / in-progress
  / invalidated / not-started / reopened / superseded / action_required`).
- Lines 12, 13, 14: milestone_ids `_moderate/hala-uncertainty`,
  `_moderate/look-alikes-len-tightening`, `_minor/coverage-images-empty-list-bug`
  use namespaces (`_moderate/`, `_minor/`) that are not in the reserved
  set (`_plan/`, `_run/`, `_archive/`, `_orphan/`, `_manager/`, `_infra/`).
- Line 10: `M-manifest-sharding` is not declared in `plan_of_record.md`
  — should either be added to the plan (with a `_plan/*` amendment
  event) or renamed to `_infra/manifest-sharding`.

Impact: the run's audit trail exists but does not conform. Not fixed
in this audit because the corrective action requires cycle-3 researcher
ratification (`_plan/*` event) or an agreed-upon rename convention that
affects Branches B and C too. Cycle-3 researcher should choose one
canonical resolution and apply it uniformly.

**M-2. Unverified reference `[4] Merlin & VanRavenswaay (1990)` rendered on `site/references.html`.**
`data/references/branch-a.md` includes a `[4]` entry whose bibliographic
details (author names, volume title "Botany of the Southeastern
Polynesia") could not be cross-verified. No species cites it, but it
is nonetheless rendered on the public references page. The directive
is explicit: "Do not fabricate DOIs or dates. If a citation cannot be
verified via WebSearch, drop it." Ref `[9] Palmer (2003) — Ferns` is
also self-annotated as "not directly cited by Branch A species"; it
can be verified as a real title but is inert clutter in a references
list that is supposed to track live claims. Recommend: cycle-3
researcher verify [4] with WebSearch and either replace with a real
citation or delete; delete [9] until it is actually used.

**M-3. `H. foertherianum` uncertainty block weakly supports the "modern introduction" side.**
The uncertainty block attributes the modern-introduction argument to
"Imada 2019 checklist [A:6]" (which is a species-list document, not a
paper making that argument). The worker's own report flagged this. The
current framing walks up to the line of "no unverified attributions"
without crossing it, but the reader is left with a token pointer that
does not lead anywhere substantive. Recommend: cycle-3 deep-verification
either finds a specific paper (e.g., a `Tournefortia` phylogeography
paper) or the uncertainty block should be shortened to "some recent
treatments note ambiguity" without attributing the argument to any
named source.

**M-4. `Jacquemontia sandwicensis` occurrence_notes contain misleading endemism phrasing.**
`data/species/jacquemontia-sandwicensis.yaml` line 12 reads
"Kauaʻi coastal endemic subspecies (species range broader, but this
Hawaiian subspecies is endemic to the archipelago)". The subspecies
is endemic to the *Hawaiian archipelago*, not to Kauaʻi specifically —
it occurs on multiple main islands. Phrase inside the parenthetical
is correct; the noun phrase before it ("Kauaʻi coastal endemic
subspecies") could mislead a hasty reader. Recommend: rephrase to
"Hawaiian archipelago endemic subspecies (occurs on multiple main
islands including Kauaʻi)".

### MINOR (logged, not investigated further per audit protocol)

- MI-1. Markdown italics inside `uncertainty:` prose render as literal
  asterisks (`*Pandanus tectorius*` visible in `hala.html`). The build
  does not run a Markdown pass on prose fields. Either strip asterisks
  from the YAML or add a Markdown pass — future decision.
- MI-2. `tahinu` listed as a Hawaiian common name for tree heliotrope
  in `heliotropium-foertherianum.yaml`; more commonly a Marshallese /
  Micronesian loan word. Defensible; not investigated.
- MI-3. `check_coverage.py` module docstring says "look_alikes list
  present (may be empty)" but the tightened code enforces `len >= 1`.
  Docstring lags the change.
- MI-4. `Nama sandwicensis` given family `Hydrophyllaceae` (Wagner
  1990); modern APG treats it as Boraginaceae / Namaceae. Defensible
  under the "primary reference is Wagner" policy.
- MI-5. Branch B/C worker events (ledger lines 15, 16) exhibit the
  same schema violation as C-1 above. Out of scope for Branch A
  auditor; noted for Branch B/C auditors.

## Spot-check results

Wagner-based status checks (Manual of Flowering Plants of Hawaiʻi):

- *Jacquemontia sandwicensis* — endemic (per subspecies treatment) ✓
- *Nama sandwicensis* — endemic; A. Gray authority; Hydrophyllaceae ✓
- *Fimbristylis cymosa* — indigenous; Cyperaceae; R. Br. authority ✓
- *Chamaesyce degeneri* — endemic; Sherff authority; Euphorbiaceae;
  Kauaʻi coastal ✓ (hazard on milky latex populated)
- *Sida fallax* — indigenous; Malvaceae; Walp. authority ✓
- *Vitex rotundifolia* — indigenous; Lamiaceae; L.f. authority ✓
- *Boerhavia repens* — indigenous; Nyctaginaceae; L. authority ✓
- *Heliotropium foertherianum* — indigenous per Wagner + uncertainty
  block per brief ✓

NTBG-based spot-check: *Chamaesyce degeneri* status (endemic) and
Kauaʻi coastal range confirmation match Wagner treatment; hazard note
on milky latex reflected in YAML.

Look-alike cross-references: every look-alike either names a species
already in the guide (validated existing slug) or names an
out-of-scope reference species with an explicit "for confer" framing.
No look-alike references a non-existent guide slug.

## Decision

**VALIDATED** (with 2 CRITICAL fixes applied during audit; 4 MODERATE
findings surfaced for cycle-3 follow-through).

## Rationale

Branch A's actual deliverables are strong: the sharded-manifest
infrastructure works and is deterministic (byte-identity verified
across successive builds); the 8 new species have solid Wagner-based
taxonomy, populated look-alikes, and per-species clinchers; 16
CC-BY-3.0 Starr photos are on disk with complete license metadata;
both audit follow-throughs (hala uncertainty, check_coverage
tightening) landed. All 11 sufficiency criteria are met.

The two CRITICAL findings I surfaced were both process-plumbing
issues (event schema, inline-token rendering) rather than content
defects; both fixes are minimal and non-regressing (all validators
green post-fix). The MODERATE findings do not block the branch's
merge — they are inputs to cycle 3 (deep verification) and to the
manager cycle for schema conformance.

## Guidance for Research Agent

Cycle 3 should combine the deep-verification milestone with cleanup
of the MODERATE findings I surfaced. Recommended prompts to worker
in cycle 3:

1. **Ledger schema conformance sweep** (feeds M-1): choose one of
   (a) add `M-manifest-sharding` to plan_of_record with a `_plan/*`
   amendment event and same for the two "moderate/minor" milestone
   ids by moving them under `_infra/*`, or (b) rewrite the offending
   events to a canonical schema across all three branches. Also
   convert every `status: "resolved"` → `status: "validated"` with
   a rationale explaining what was resolved.

2. **Reference hygiene** (M-2, M-3): verify Merlin & VanRavenswaay
   (1990) with WebSearch — if unverifiable, drop it from
   `branch-a.md`. Same treatment for Palmer 2003 unless a cycle-3
   species actually cites it. Reframe the H. foertherianum
   uncertainty block so it does not attribute the modern-introduction
   argument to Imada 2019 without a supporting paper.

3. **`Jacquemontia sandwicensis` phrasing fix** (M-4): change
   "Kauaʻi coastal endemic subspecies" → "Hawaiian archipelago
   endemic subspecies (occurs on Kauaʻi among other main islands)".

4. **Optional: minor markdown pass** — if uncertainty blocks are
   going to keep using `*species*` italics, add a minimal Markdown
   pass in build_site OR strip asterisks from the YAML; do not
   leave them as literal characters visible to readers.

Since the M-common-tier-broaden milestone is currently
`in-progress` (12/20 target), cycle 3 or 4 can add ~8 more COMMON
species to reach the ~20 target. That work is orthogonal to the
verification / hygiene cleanup above and can proceed in a separate
sub-brief.

## Cumulative Progress Notes

- Cycle 1 stood up the pipeline and 10-species vertical slice.
- Cycle 2 (all three branches) grew coverage to 30 species: COMMON
  12 / NOTABLE 9 / RARE_EXOTIC 9. Total target is 45. Trajectory
  is on-track: 15 species remain across 4 remaining cycles.
- Branch A's shared-prep infrastructure (sharded manifests + citation
  tokens) worked as designed — the concurrent-workspace merge case
  actually fired (Branches B and C had already written species and
  refs to the shared workspace), and the base site still rebuilt
  byte-identically.
- Recurring pattern: worker-emitted ledger events have not fully
  aligned with the canonical schema in `long_exposure/tools/promise_check.py`.
  This is a schema-affordance issue as much as a worker discipline
  issue — the schema is not documented in `plan_of_record.md`. Manager
  should either publish a schema block or the researcher should embed
  a schema pointer in every worker brief.

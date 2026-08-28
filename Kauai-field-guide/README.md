# Kauai-field-guide

A long-exposure run that developed a comprehensive, locally accessible,
HTML-based field guide to the plants of the unpopulated coast of Kauai,
Hawaii — the roadless Nā Pali Coast (Kalalau, Honopū, Nuʻalolo Kai,
Miloliʻi, Awaʻawapuhi) and other remote coastal stretches such as
Māhāʻulepū — covering common, notable, and rare & exotic (including
invasive) species.

## The deliverable

**Open `site/index.html` in any browser — no network needed.** The site is
fully self-contained (no CDNs, no hotlinked images, no web fonts): a
thumbnail-forward index with a client-side filter, grouped by tier and by
habitat zone, linking to 46 species profiles, plus glossary,
safety-and-ethics, image-credits, and references pages.

`kauai-field-guide-single.html` is a generated one-file version of the same
guide (all pages concatenated, images inlined as downscaled data URIs) for
one-click viewing; the multi-page `site/` is the canonical artifact.

## Run outcome

- **46 species** — 20 common, 15 notable, 11 rare & exotic — each profile
  with 2–5 visuals (openly licensed photos with per-image attribution +
  license, plus generated SVG identification diagrams), a step-by-step
  "How to identify" block, look-alike separation, status/habitat/zone,
  ecology and cultural notes, and numbered citations into REFERENCES.md.
- **113 locally stored photographs** (public domain / CC0 / CC-BY /
  CC-BY-SA; heavily Forest & Kim Starr and Wikimedia Commons), credited on
  `site/credits.html`.
- All four workspace validators pass at the synced state: `lint_site`
  (51 HTML files, no external asset URLs), `check_links` (all internal
  links resolve), `check_offline` (file://-safe), `check_coverage`
  (per-tier counts + required-field/visual/citation checks).
- 6 cycles run, including three 3-branch parallel fan-outs (tier
  expansion, verification, and integration passes) — see
  `reports/cycles/` and `reports/merge/`.
- The run was **hard-stopped by the operator after cycle 6** (after the
  cycles 4–6 report), intentionally skipping the harness's final auditor →
  final reporter → curator pipeline; there is therefore no
  `reports/final/final_report.md` or `audits/final/final_audit_report.md`.

## Run setup

- Harness: [long-exposure](https://github.com/human-in-a-loop/long-exposure)
  (researcher → worker → auditor loop; periodic reporter every 3 cycles).
- Provider/model: Claude CLI, `model: claude-opus-4-7` (full model id, set
  globally and per agent role in `agent_models`).
- Live workspace during the run: `/home/user/workspaces/kauai-field-guide`
  on the cloud sandbox that executed the run; artifacts were synced into
  this folder afterwards.
- Loop: `max_cycles: 6`, `cycle_cooldown_seconds: 30`.

## Files

- `site/` — the field guide (open `site/index.html`).
- `kauai-field-guide-single.html` — generated single-file version.
- `kauai_field_guide_long_exposure_prompt.md` — the directive injected via
  `long-exposure launch "<directive>"`.
- `long-exposure.config.yaml` — the exact harness config used for the run.
- `plan_of_record.md`, `STRUCTURE.md`, `promise_ledger.jsonl`,
  `REFERENCES.md` — standard long-exposure workspace conventions.
- `reports/cycles/` — worker/branch/integration cycle reports and the
  periodic reporter outputs (cycles 1–3, 4–6, and per-clone reports).
- `reports/merge/` — the nine fan-out clone merge reports (three forks).
- `audits/` — per-cycle audit artifacts.
- `scripts/` — the site build, image fetch/license, and validation
  scripts (`lint_site.py`, `check_links.py`, `check_offline.py`,
  `check_coverage.py`); `data/` — species/image/reference source data;
  `tests/` — test suite the auditors ran.

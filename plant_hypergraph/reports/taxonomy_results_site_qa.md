---
created: 2026-05-18T00:00:00+00:00
cycle: 34
run_id: run-phytograph-taxonomy-results-site
agent: worker
milestone: _plan/taxonomy-results-site
---

# Taxonomy Results Site QA

## Scope

Checked the local static PhytoGraph taxonomy results site as a public teaching and expert-review artifact. The check covers required files, route labels, local asset references, language-boundary terms, evidence tables, figure availability, and responsive browser behavior.

## File And Link Checks

- Required site files are present: `index.html`, `assets/styles.css`, `assets/app.js`, `data/site_summary.json`, six evidence tables, README, and provenance notes.
- Required figure assets are present in `taxonomy_results_site/assets/figures/`.
- Static reference checks passed for local `src` and `href` targets.
- Cross-track prediction and speculation tables remain header-only.

## Language Boundary

- Public `.html`, `.css`, `.js`, `.json`, `.svg`, and `.md` text was scanned after stripping metadata frontmatter from Markdown files.
- No prohibited public-facing process terms or private machine paths were found.
- Public text presents the work as a research study with methods, evidence, limitations, and conclusions.

## Browser Checks

- Local HTTP access was checked with `curl` against the static site folder.
- Desktop start screen was captured at 1440 by 1000 pixels: `taxonomy_results_site/assets/qa/desktop_start.png`.
- Desktop evidence route was captured at 1440 by 1000 pixels: `taxonomy_results_site/assets/qa/desktop_evidence.png`.
- Narrow viewport start screen was captured at 390 by 844 pixels: `taxonomy_results_site/assets/qa/mobile_start.png`.
- A first visual pass found an oversized headline and narrow-viewport clipping; CSS was revised to reduce heading scale and constrain the mobile content width.
- Follow-up screenshots show readable headings, usable route navigation, visible evidence controls, and no obvious text overlap in the inspected desktop and narrow views.

## Remaining Limitations

- The browser check used static screenshots and route rendering checks. It did not perform a full assistive-technology audit.
- Figure inspection controls are present in the page markup and script; screenshots verify figure rendering, while click behavior remains a lightweight local interaction check rather than a full end-to-end accessibility test.

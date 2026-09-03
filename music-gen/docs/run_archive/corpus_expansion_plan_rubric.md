---
created: 2026-08-29T18:15:00Z
cycle: 48
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/corpus-expansion-plan
fork: e651a0d7b0c8
clone: 1
---

# `_manager/corpus-expansion-plan` — frozen 2-verdict rubric

This rubric is **frozen at commit time**. Any downstream cycle that revisits
this ticket must obey the verdict definitions below verbatim; softening,
back-fill, or post-hoc threshold amendment is a rubric-integrity violation
per the c26 anti-pattern set.

## Scope

Formalize the c26 Path B §5 corpus-expansion-ticket template with concrete
action items across three orthogonal feasibility axes. Analytical only —
zero live-network probes, zero rendering, zero re-training. The `M-EAR-1`
Path B commit is a **read-only anchor** (c26 terminal-validated); this
milestone is a peer manager rollup under root planning, respecting the c29
state-machine lemma.

## Verdicts (2-way)

### `CORPUS_EXPANSION_TICKET_LANDS`

All three conditions hold:

1. **≥3 feasibility axes enumerated.** Each axis MUST have:
   - ≥3 concrete action items (per §Definitions below);
   - ≥3 falsifiable trigger conditions (per §Definitions below);
2. **No-live-network probe surface AST-verified.** AST-grep over
   `scripts/corpus_expansion_plan/` finds zero `import urllib`,
   `import requests`, `import socket`, `import httpx`, `import yt_dlp`
   at any module-load site. Mentions in string literals and comments
   are allowed; import statements are forbidden.
3. **Three-way `rubric_hash` byte-equality.**
   `sha256(docs/corpus_expansion_plan_rubric.md)` ==
   `data/corpus_expansion_plan/rubric_hash.txt` ==
   `data/corpus_expansion_plan/verdict.json[.rubric_hash]`.

### `CORPUS_EXPANSION_TICKET_PARTIAL`

Any one of the following:

- fewer than 3 axes fully enumerated;
- any axis lacks concrete action items (< 3 items OR any item missing a
  required field);
- any axis lacks falsifiable triggers (< 3 triggers OR any trigger not
  binary-evaluable);
- AST-grep finds ≥1 live-network probe;
- three-way `rubric_hash` byte-equality broken.

There is no `LANDS_WITH_CAVEATS` band. The bar is: fully enumerated,
provably static-analytical, and content-hash-consistent, OR it is
`PARTIAL` and the specific failure(s) named in the verdict JSON.

## Definitions (binding)

### "Concrete action item"

A dict-shaped record carrying, at minimum:

| field                | type   | requirement                                                                 |
|----------------------|--------|-----------------------------------------------------------------------------|
| `axis`               | str    | one of `i`, `ii`, `iii`                                                     |
| `id`                 | str    | matches `^(i|ii|iii)\.[1-9][0-9]*$` (e.g. `i.1`, `ii.3`)                    |
| `name`               | str    | short human label                                                           |
| `owner`              | str    | one of `worker`, `researcher`, `auditor`, `operator`, `out-of-band`         |
| `expected_outcome`   | str    | named artifact OR named state change                                        |
| `trigger_condition`  | str    | binary-evaluable predicate (see below)                                      |
| `cost_hours_analytical` | float | hours of in-workspace analytical effort                                    |
| `cost_hours_operator_dependent` | str or float | hours OR `"unbounded"` OR `"0"` OR range `"a-b"`             |
| `expected_corpus_delta_lo` | int | lower bound (inclusive) on new rated songs delivered                        |
| `expected_corpus_delta_hi` | int | upper bound (inclusive) on new rated songs delivered                        |
| `expected_sb1_delta` | str    | one of `"positive"`, `"neutral"`, `"negative"`, `"conditional_on_delivery"` |
| `expected_sb2_delta` | str    | same enum                                                                    |
| `expected_sb3_delta` | str    | same enum                                                                    |

### "Falsifiable trigger condition"

A binary-evaluable predicate — a string that, when regex-checked, contains
at least one of the comparison tokens `<`, `>`, `<=`, `>=`, `=`, `≤`, `≥`,
OR a canonical binary sentinel word set: `{present, absent, delivered,
undelivered, available, unavailable, confirmed, unconfirmed}`. The
predicate must be expressible as an inspection over the filesystem, the
promise ledger, or a documented external signal — no probabilistic or
subjective language.

Bad: `"quality of network improves"`.
Good: `"data/ingestion/egress_status.jsonl contains ≥2 consecutive rows with media_ok=true"`.

### "No-live-network probe surface"

For every `*.py` under `scripts/corpus_expansion_plan/`:

1. AST-parse the module.
2. Walk `ast.Import` and `ast.ImportFrom` nodes.
3. Reject any name in the blocklist `{urllib, urllib.request, urllib.parse,
   requests, socket, httpx, yt_dlp, aiohttp, urllib3}`.

Detection is purely static; no runtime probes are executed.

## Corpus state (verified at commit time)

- 43 rated songs on disk (10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 per c36/c45/c47 corpus).
- 80 rated songs listed in `corpus/ratings/ratings_manifest.tsv` (80 rows + 1 header line).
- 37-song delivery gap.
- Egress: HTTP 429 + `tv_embedded` player-client closure since c45; no
  policy change through c47 (see `data/ingestion/egress_status.jsonl`).

## c26 Path B §5 pointer

This rubric formalizes the template placeholder at `docs/ear_path_b_commitment.md`
§5.2. That §5.2 template is a stub with `<VALUE>` / `<yt-dlp minutes>`
/ `<cycles>` placeholders; the deliverables of `_manager/corpus-expansion-plan`
fill those placeholders with concrete axis-organized action items.

## Anti-pattern lockouts (verbatim, binding)

- c22 chassis-exhaustion — no re-touch of `scripts/ear/{synthetic_labels,
  stability_metrics,stability_audit}.py`.
- c23 head-regularization — no chassis variant proposed here.
- c25 feature-representation — no feature-swap proposed here.
- c35 VST3-state-extraction — irrelevant to this branch; AST-grep clean
  for `save_state|get_state|save_preset|load_state|set_state`.
- c11 CLAP HF SSL — irrelevant.

Axis (iii) is analytical projection under the c26 fix-lock; it does NOT
propose amending c26 thresholds.

## Ordering gate

**mtime hard:** `docs/corpus_expansion_plan_rubric.md` mtime MUST be less
than every `scripts/corpus_expansion_plan/*.py` mtime.

**git-log SOFT** per c46 amendment path (ii): if the harness cannot commit
inside a single worker turn, the git-log commit-order test records
`HARNESS_GATED` and does not gate the verdict.

---
created: 2026-05-17T00:45:40Z
run_id: run-2026-05-17T004540Z
agent: researcher
---

# Workspace Structure

This workspace follows the long-exposure standard layout. Cross-cutting
artifacts live in standard folders at root; domain-specific organization
lives in named subfolders (e.g., `benchmark-XX-...`).

## Standard folders

| folder      | purpose                                                            |
|-------------|--------------------------------------------------------------------|
| `reports/`  | harness-managed cycle reports and final-reporter scratch           |
| `audits/`   | harness-managed final-auditor scratch and sidecar JSONL files      |
| `scripts/`  | worker-authored code that produces results                         |
| `tests/`    | auditor-authored verification code                                 |
| `data/`     | datasets (CSV/JSON/etc); machine-facing                            |
| `docs/`     | narrative non-reports (design notes, methodology)                  |
| `tools/`    | cross-cutting utilities (validators, helpers)                      |
| `stale/`    | archived obsolete artifacts                                        |

## Domain folders

| folder | purpose |
|--------|---------|
| `plant-taxonomy-hypergraph/` | Prior campaign artifacts (M1–M8). See `docs/prior_campaign_kernel.md` for inheritance classification. |
| `substrate/` | Unified PhytoGraph hypergraph dataset (Wave 1 + Barrier 1 outputs). Per-source staging tables live in `substrate/staging/<source>/`. |
| `tracks/track1/` … `tracks/track6/` | Per-track enrichment (Wave 2), instruments (Wave 3), and validation outputs (Wave 4). Each track-folder mirrors root layout (scripts/, data/, docs/, tests/). |
| `instruments/` | Cross-track instrument code shared across tracks (e.g. canonical-key reducer, evidence-scope conformance checker). |
| `validation/` | Per-track validation outputs (Wave 4 D). |
| `ablations/` | Cross-cutting ablation experiments (Wave 4 D″) and per-track edge-removal ablations. |
| `formal/` | Formal contributions (Wave 4 D′) — theorem templates, counterexamples, diagnostic statistics with proof artifacts. |
| `atlas/` | Botanical Atlas site (Wave 3 C′) — local interactive surface; not the headline deliverable. |
| `probe/` | Track 6 probe questions, prompt templates, model-response logs, calibration records. |

## Conventions

- Plots co-located with their source data, NOT in a separate `figures/`.
- Stale artifacts MOVED to nearest `stale/` (root or domain-internal); never deleted.
- Periodic reporter writes ONLY to `reports/cycles/` (not to root, not to `docs/`).
- Final reporter artifacts live in `reports/final/`, including `final_report.*`.
- Final auditor artifacts live in `audits/final/`, including `final_audit_*`.
- Worker default: scripts to `scripts/`, data outputs to `data/`, plots beside data.
- Auditor default: verification scripts to `tests/`.
- Cross-cutting tools (validators, helpers) to `tools/`.

## External (out-of-scope for org_check / orphan check)

(Optional. List directories the workspace pre-loaded but does not author —
e.g. `materials/`, `vendor/` — so validators ignore them.)

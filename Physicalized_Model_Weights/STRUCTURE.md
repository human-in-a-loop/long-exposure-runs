---
created: 2026-05-13T01:51:36Z
run_id: run-2026-05-13T015136Z
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
| `physicalized-weights/` | Domain-specific working area for physicalized model weights research: taxonomy, decision models, simulation artifacts, HDL sketches, and synthesis/diagram outputs that are too specific for root-level `scripts/`, `data/`, or `docs/`. |

## Conventions

- Plots co-located with their source data, NOT in a separate `figures/`.
- Stale artifacts MOVED to nearest `stale/` (root or domain-internal); never deleted.
- Periodic reporter writes ONLY to `reports/cycles/` (not to root, not to `docs/`).
- Final reporter scratch lives in `reports/final/`; canonical `final_report.*` stays at root.
- Final auditor scratch lives in `audits/final/`; canonical `final_audit_*` stays at root.
- Worker default: scripts to `scripts/`, data outputs to `data/`, plots beside data.
- Auditor default: verification scripts to `tests/`.
- Cross-cutting tools (validators, helpers) to `tools/`.

## External (out-of-scope for org_check / orphan check)

(Optional. List directories the workspace pre-loaded but does not author —
e.g. `materials/`, `vendor/` — so validators ignore them.)

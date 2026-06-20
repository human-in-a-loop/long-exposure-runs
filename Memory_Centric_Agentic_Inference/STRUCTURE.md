---
created: 2026-05-11T12:16:49Z
run_id: run-2026-05-11T121649Z
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

| folder                    | purpose                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| `memory-centric-agentic/` | Domain artifacts for the memory-centric agentic inference architecture campaign: taxonomy, assumptions, models, simulations, data, plots, and architecture notes. |

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

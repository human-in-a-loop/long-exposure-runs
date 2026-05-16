---
created: 2026-05-15T15:36:35Z
run_id: run-2026-05-15T153635Z
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
| `docs/paper_map/` | foundational theorem, notation, and dependency maps for `2603.01127` |
| `docs/proof_ledger/` | stepwise proof reconstructions and dependency ledgers |
| `data/polynomial_method/` | tabular outputs and plots for polynomial-method and trace-statistic probes |

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

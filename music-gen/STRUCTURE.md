---
created: 2026-08-28T04:07:04Z
run_id: run-2026-08-28T040704Z
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

| folder                | purpose                                                                                  |
|-----------------------|------------------------------------------------------------------------------------------|
| `corpus/`             | rated-playlist manifest + (eventually) audio; `ratings/<band>/` audio is gitignored      |
| `workspace/`          | pre-provisioned toolchain harness: provision.sh, smoke_test.py, harvest_playlists.sh     |
| `scripts/ingest/`     | harvester + chunker + provenance ledger writer (front door for local + YouTube audio)    |
| `scripts/classifier/` | music/non-music classifier + non-factor sidecar writer                                   |
| `scripts/daw/`        | Ardour + DawDreamer control code (session, MIDI, params, automation, render)             |
| `scripts/separation/` | source-separation survey + adopted-separator wrapper                                     |
| `scripts/transcribe/` | per-stem transcription + merge-to-full-score                                             |
| `scripts/score/`      | MuseScore bridge + score↔MIDI round trip                                                 |
| `scripts/heuristics/` | mess-scale heuristics battery + intra-song meta tracker                                  |
| `scripts/ear/`        | ear model training + non-factor leak tests                                               |
| `scripts/rules/`      | rules ledger schema + extractor                                                          |
| `scripts/texture/`    | texture-distance panel + effects/texture layers                                          |
| `scripts/generate/`   | deterministic new-song generator                                                         |
| `data/ingestion/`     | chunker outputs + provenance manifests on seed audio                                     |
| `data/classifier/`    | classifier confusion matrices and per-taxonomy metrics                                   |
| `data/classifier/_nonfactor/` | **OFF-LIMITS** non-factor sidecar files (genre/artist/etc.). Only `scripts/classifier/sidecar_nonfactor.py` and `scripts/classifier/write_sidecars.py` may open this path; enforced by `tests/test_sidecar_isolation.py`. |
| `data/classifier/_cache/`     | model-weights / dataset download cache (git-ignored)                                     |
| `data/classifier/valset/`     | M-CLASS-1 labeled validation clips (55 clips, 5 classes) + manifest                      |
| `data/daw_spike/`     | DAW-stack validation-spike coverage matrix + rendered artifacts                          |

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

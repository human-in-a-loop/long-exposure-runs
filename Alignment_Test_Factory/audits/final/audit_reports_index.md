# Audit Reports Index

Built during final-audit explore from `sessions.db`, `promise_ledger.jsonl`, and the periodic reports. One line per cycle follows.

| Cycle | Session id(s) / source pointer | One-line summary |
|---:|---|---|
| 1 | `8e76a8f1-d9a9-47e8-813a-2d7f64033861`; worker `61694eaf-1440-4db0-9fc3-1adae12ab391`; auditor `62225d65-0e26-4e5e-ad64-4eabe38c01c9` | M-1 landscape/gap map was built and independently validated after a ledger schema repair. |
| 2 | `reports/cycles/report_cycles_1-3.md`; DB context records near 2026-05-13T21:14-21:30Z | M-2 operational taxonomy and benchmark-quality rubric were built and independently validated. |
| 3 | `reports/cycles/report_cycles_1-3.md`; DB context records near 2026-05-13T21:36-22:08Z | M-3 provider-agnostic task schema, valid examples, invalid fixtures, and validation tests were built and independently validated. |
| 4 | researcher `4341df2e-bf46-4dec-b0be-79b93bc28e2a`; worker `3f87ef84-cfc3-4f11-9917-d9d709c6f07f`; auditor `91db035d-cf9f-4622-ad92-7c7f38e7428c` | M-4 deterministic toy runtime, trace model, permission scorer, pass/fail traces, and tests were built and validated. |
| 5 | `reports/cycles/report_cycles_4-6.md`; DB context records near 2026-05-13T22:40-22:55Z | M-5 Inspect smoke path used `mockllm/model` and preserved deterministic trace/scorer evidence. |
| 6 | `reports/cycles/report_cycles_4-6.md`; DB context records near 2026-05-13T23:02-23:40Z | M-6 added four task families and multi-family Inspect scoring; auditor repaired one MODERATE nested trace-field validation defect before validation. |
| 7 | `reports/cycles/report_cycles_7-9.md`; DB context records near 2026-05-13T23:48-2026-05-14T00:05Z | M-7 stress-tested benchmark robustness with 11 benign probes and validated narrow scorer/trace-integrity repairs. |
| 8 | `reports/cycles/report_cycles_7-9.md`; latest ledger event `ef24cca4-f071-414c-bb97-f275f3c730b8` | M-8 final developer report, artifact index, roadmap, and reproduced summaries were validated. |
| 9 | auditor `596d9121-0fde-48ae-a82a-c6dce913b68f`; `reports/cycles/report_cycles_7-9.md` | Closure cycle; no new build; M-1 through M-8 remained validated with no CRITICAL/MODERATE remaining issues. |
| 10 | auditor `f54a7501-9328-4db4-b264-55313f52dd6b`; `reports/cycles/report_cycles_10-12.md` | Closure confirmation; no commands or new artifacts; bookkeeping warnings remained non-blocking. |
| 11 | researcher `74482b68-fdc2-46ab-838a-b7bd262262b1`; worker `965de2e7-a08b-4be0-a047-094e91e88e39`; `reports/cycles/report_cycles_10-12.md` | Repeated closure confirmation; future work was deferred to a new campaign from the roadmap. |
| 12 | researcher `5e9a5c52-6a2d-457e-980f-0f0f4a5236c2`; worker `38c13013-387f-4779-bd0b-aedb-589c68290c3d`; `reports/cycles/report_cycles_10-12.md` | Final closure confirmation across cycles 10-12; no remaining build/test/audit action. |
| 13 | auditor `b7d62235-bee1-4b02-87d3-3bc8658ea7b0`; `reports/cycles/report_cycles_13-13.md` | Final closure confirmation; no CRITICAL/MODERATE findings, no new commands, no new artifacts. |

SQLite query note: the local database has table `sessions(id, parent_id, depth, created_at, summary_xml, philosophy, framework, token_estimate, record_type, topic, subtopic, tools, keywords, fork_id)`. Queries filtered for `Open Alignment Test Factory`, `alignment`, and report/session IDs; no dedicated `search_sessions` tool was available in this environment.

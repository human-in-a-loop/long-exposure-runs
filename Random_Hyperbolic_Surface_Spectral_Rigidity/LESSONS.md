# Cross-Cutting Lessons

Curated findings across runs. Updated by the final auditor at run end. The DB record (record_type='lesson') is canonical; this file mirrors for human readability.

---

## Lesson: final-slice-parser-boundaries
*Committed: 2026-05-16T15:38:07.770746+00:00*

Pattern observed: the last verification slice can accidentally absorb following report or index sections when the parser only stops at the next peer slice heading. In this audit, that produced false milestone-like findings until the parser was repaired. Recipe: bound slice extraction by both the next `### Stage <n> Verify Slice` heading and the next top-level `## ` heading; then validate parsed ids against a narrow milestone taxonomy such as `M\d+`, `_plan/`, `_archive/`, or `_run/` before appending findings. After any append, run a findings-file integrity pass that detects path-like milestone ids and removes same-stage false positives before closure. Cross-reference: `audits/final/stages/verify_7of7.md`.


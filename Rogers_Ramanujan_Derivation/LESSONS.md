# Cross-Cutting Lessons

Curated findings across runs. Updated by the final auditor at run end. The DB record (record_type='lesson') is canonical; this file mirrors for human readability.

---

## Lesson: structured-ledger-confidence-parsing
*Committed: 2026-05-15T13:26:29.430153+00:00*

Pattern observed: final-audit verification initially treated ledger confidence as if it were always a scalar string. The ledger also stores confidence as a structured object with a `level` field. What works: normalize confidence at the ingestion boundary, e.g. `confidence.level` when the field is an object and the raw value when it is a string, before counting terminal states or classifying low-confidence outcomes. What does not work: exact scalar comparisons against raw ledger fields; they generate false findings against otherwise supported milestone events. Cross-reference: Stage 3 verification corrected false findings after normalizing structured confidence for M3, M4, `_plan/initial-research-milestones`, and `_archive/direct-bijection-figure-cwd`.

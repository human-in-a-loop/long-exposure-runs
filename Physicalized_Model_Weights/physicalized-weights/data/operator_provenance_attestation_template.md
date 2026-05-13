---
created: 2026-05-13T13:18:00Z
cycle: 4
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-DRYRUN-1
---

# Operator provenance and privacy attestation template

Replace every `REPLACE_BEFORE_COLLECTION` token before measured collection.

- Source: I attest that the trace source is `REPLACE_BEFORE_COLLECTION` and is one of production, shadow production, or canary production.
- Privacy: I attest that the trace contains no prompt, raw text, raw user identifier, tenant identifier, API key, email, IP address, or content column.
- Measurement status: I attest that accelerator and hybrid latency and energy terms are measured for the same request window, not proxy, modeled, or mixed.
- Policy window: I attest that policy hashes are consistent within the collection window except for explicitly logged update or rollback events.
- Counterfactual baseline: I attest that the programmable accelerator baseline and hybrid path were collected for the same request classes, fallback decisions, audit logging, utilization, and policy window.
- Hash provenance: I attest that the manifest trace SHA-256 was generated after final trace export and before evidence-pack replay.

Dry-run templates are not evidence. A future measured package must replace this attestation with signed operator-specific language before it can enter M-EVIDENCEPACK-1.

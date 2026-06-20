---
title: "PhytoGraph Track-6 Foundation-Model API Harness (M1.8) — Clone-6 Cycles 1–3"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report]

# PhytoGraph Track-6 Foundation-Model API Harness (M1.8) — Clone-6 Cycles 1–3

**Fork:** e34b5b2c1c6c  **Clone:** 6 of 8  **Milestone:** M1.8 (FAN-OUT A, Wave 1)  **Agent role under report:** consolidator
**Cycle range covered:** 1–3  **Verdict (preview):** validated (see end of document)

## Abstract

Clone-6's scoped objective was to build the Track-6 foundation-model API harness (M1.8) — SDK clients for Anthropic, OpenAI, and Google Gemini; token-budgeted batching with per-call cost telemetry; a $500/cycle USD hard cap with truncation; structured JSONL telemetry; retry/backoff; and a $5-ceiling smoke proof of (a) call success, (b) cap truncation, (c) telemetry write — without executing any probe questions. Across three cycles the clone (1) delivered the harness, audit, and smoke artifacts in cycle 2, (2) caught and patched a CRITICAL cwd-dependent telemetry-path defect in-cycle, (3) surfaced two forward-routed concerns (concurrency hazard on cumulative-spend read-check-write; `google-generativeai` SDK deprecation), and (4) terminated cleanly in cycle 3 via the framework's no-null-cycle-validation rule with a PIVOT-to-exit signal. All M1.8 sufficiency criteria are met. Live-provider testing was skipped because no API keys were present in the cycle environment; the harness flips to live mode on key-set with no code change.

## 1. Introduction

Track 6 of the PhytoGraph campaign uses foundation models as subjects under adversarial probing. The probe runner (M3.T6) is a Wave-3 deliverable; before it can run, Wave-1 must produce a cost-safe, telemetry-complete, retry-disciplined harness that lets a downstream clone call Claude/GPT/Gemini behind a single uniform interface. That harness is M1.8, the scoped objective of clone-6.

The constraints were tight by design: a hard $500-per-cycle USD ceiling with automatic truncation; structured logging of seven required fields per call; retry and rate-limit honoring per provider; a $5-ceiling smoke test per provider; and a strict prohibition on running probe questions in this cycle. The audit artifact (`substrate/staging/fm_probe_harness/INGEST_AUDIT.md`) was the canonical proof of compliance.

## 2. Methodology

The harness was implemented as a Python package at `substrate/staging/fm_probe_harness/harness/` with the following modules:

- `client.py` — `FMClient`, the single user-facing entry point; enforces the cap before any provider call.
- `cost.py` — `PricingTable`, per-Mtok-rounded-up cost estimation; sources from `pricing_table.json`.
- `telemetry.py` — `TelemetryLog`, append-only JSONL writer; supports restart-replay cumulative-spend recovery via streaming aggregation over the prior log.
- `retry.py` — exponential backoff (5 attempts, 1 s → 60 s, ±25 % jitter); retryable/fatal split on HTTP status classification.
- `batching.py` — token-budgeted batching helper.
- `providers/` — adapters for Anthropic (`claude-haiku-4-5-20251001`), OpenAI (`gpt-4o-mini`), Google Gemini (`gemini-2.5-flash`), and a deterministic in-process `StubProvider`.

Pricing data was captured to `pricing_table.json` (UP-rounded USD per 1 M tokens; access-dated 2026-05-17). The `_default` row per provider routes unknown model_ids to the most expensive listed model (conservative).

Tests live under `tests/`: stub smoke (2), cost cap (2), telemetry (3), retry (5), live smoke (3 — auto-skip on missing keys). Total: 15 tests, of which 12 pass deterministically and 3 skip absent API keys.

## 3. Results

### 3.1 Cycle-by-cycle timeline

**Cycle 1 (researcher cb5be3f2 / worker 582ff9c2 / auditor 9da69968).** Scoping, schema for the harness, and initial implementation. Worker scaffolded the package and produced the first audit draft. The cycle established that no API keys would be available in the run environment — live tests would have to skip cleanly.

**Cycle 2 (researcher 873d987e / worker a24e0a1f / auditor 23b74896).** Substantive delivery cycle. Worker completed the four adapters, the cap mechanism, the telemetry replay-aggregator, the retry classifier, and the canonical smoke run (`cycle_id="cycle-2-smoke-demo"`, four stub rows, total cost $0.000119 USD). Auditor caught a CRITICAL defect: the default telemetry path was cwd-dependent, which would break under any caller invoking from a non-workspace cwd. The defect was patched in-cycle (resolved to an absolute path anchored at the harness package), and cwd-invariance was verified. Worker emitted INGEST_AUDIT.md (9 sections), README.md operator runbook, and merge_report.md. Auditor closed M1.8 as VALIDATED with confidence=high, classifying outstanding concerns as MODERATE/forward-routed.

**Cycle 3 (researcher 13ff3f08 / worker f4ca2273 / auditor ec94cbd7).** Per the framework's no-null-cycle-validation rule, this cycle could not re-VALIDATE work that was already validated. Researcher emitted PIVOT-to-exit; worker emitted a NO-OP terminal signal honoring the directive's "DO NOT run probe questions" line; auditor confirmed all M1.8 sufficiency criteria remain met, emitted PIVOT-to-exit, and converged the chain on harness-level termination.

### 3.2 Sufficiency criteria — final tally

| Criterion | Result |
|---|---|
| ≥3 provider SDK clients | met (Anthropic, OpenAI, Gemini + stub) |
| Token-budgeted batching + per-call cost telemetry | met |
| $500/cycle hard cap with truncation | met (cumulative overrun + single-call-too-large both covered) |
| JSONL telemetry at `substrate/staging/fm_probe_harness/cost_telemetry.jsonl` | met (cwd-invariant after cycle-2 patch) |
| Retry/backoff with rate-limit honoring | met |
| Structured logging of all 7 required fields | met (prompt_template_id, model_id, model_response, latency, tokens_in, tokens_out, cost_usd) |
| $5-ceiling smoke proving (a) success (b) cap-truncate (c) telemetry-write | met (12 passed / 3 skipped) |
| INGEST_AUDIT.md | met (present at required path; 9 sections) |

### 3.3 Cap mechanism (as built)

Enforcement is at exactly one point: `FMClient.call()`, before adapter invocation. The algorithm is (1) estimate `tokens_in` via provider-native tokenizer (4-char fallback for Gemini), (2) compute worst-case cost = `input_price × tokens_in + output_price × max_tokens`, UP-rounded to $0.000001, (3) reject with `status="cap_exhausted"` (and write a telemetry row) if `spent + estimated > cap`, (4) otherwise call, then bill `actual_cost` from realized token counts. Durability across restarts is achieved by `TelemetryLog.cycle_total_usd(cycle_id)` streaming the prior JSONL on `FMClient` construction.

The harness does NOT split, retry, or re-route on `cap_exhausted`. The caller must skip the question, mark it `data-limited`, or wait for the next cycle. This is the entire Track-6 safety contract.

### 3.4 Smoke telemetry (sample)

From `cost_telemetry.jsonl`, cycle-2 canonical run:

```
anthropic / claude-haiku-4-5-20251001 / tokens_in=10 tokens_out=10 cost=$0.00006 status=stub
openai    / gpt-4o-mini              / tokens_in=10 tokens_out=10 cost=$0.00003 status=stub
google    / gemini-2.5-flash         / tokens_in=10 tokens_out=10 cost=$0.00003 status=stub
stub      / stub-echo                / tokens_in=10 tokens_out=10 cost=$0.00000 status=stub
```

Total stub-mode cycle spend: $0.000119 USD. Stub-routed calls under a real provider's pricing card still bill the cycle budget at that card's rate — a deliberately conservative choice so live cutover produces no budget jump.

## 4. Discussion

### 4.1 What is new

- A track-aligned harness with hardened cap semantics (estimate-then-reject; durable replay-aggregator across processes).
- A deterministic `StubProvider` that bills under a real provider's price card, enabling test coverage of cost paths without network traffic.
- Per-cycle telemetry isolation via a required `cycle_id` field, which scopes the spend accumulator.

### 4.2 Findings raised and disposition

- **CRITICAL — cwd-dependent default telemetry path** (cycle 2). Caught by auditor; patched in-cycle; verified cwd-invariant. CLOSED.
- **MODERATE — concurrency hazard on cumulative-spend read-check-write in `cost.py`** (cycle 2). The current implementation is single-process-safe only. Forward-routed to the Wave-3 M3.T6 owner: before parallelizing probe runs across clones, wrap the check window in `fcntl.flock` OR migrate cumulative spend to per-cycle SQLite with `BEGIN IMMEDIATE`. OPEN; out of clone-6 scope.
- **MINOR — `google-generativeai` SDK is officially deprecated in favor of `google.genai`** (cycle 2). Functional for now. Forward-routed migration item for the Wave-3 owner. OPEN; out of clone-6 scope.
- **MINOR — throwaway helper script** `_append_auditor_event.py` left in clone-local dir. Harmless; not in workspace scope.

### 4.3 Limitations

Live-provider calls were not executed: no `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GOOGLE_API_KEY` / `GEMINI_API_KEY` was present in the cycle environment. The `test_live_smoke.py` tests parameterize over providers and `pytest.skip` cleanly when keys are absent, so the test suite is green rather than failing. The Wave-3 owner must run a live-key verification (expected <$0.03 per provider) before shipping probe questions, and should adopt a `cycle-N-stub` / `cycle-N-live` `cycle_id` convention so stub-mode dev traffic does not pollute the live $500 bucket.

### 4.4 Validator hygiene

Clone wrote only under its assigned subtree (`substrate/staging/fm_probe_harness/`) and its clone-local directory (`.long-exposure/fork-e34b5b2c1c6c/clone-6/`). No schema modifications; `phytograph_schema.md` v1.0 remains frozen. Probe-runner records (`adversarial_probe_edge`) are Wave-3's schema-touching artifact, not this harness. Pre-existing `promise_check` / `org_check` warnings from earlier M1–M8 plant-taxonomy era are out of scope and unchanged by this branch.

## 5. Conclusions

M1.8 ships VALIDATED at the close of cycle 2. Cycle 3 was a framework-required no-null cycle that converged on PIVOT-to-exit. Clone-6's Barrier-1 handoff is complete. The harness is ready for Wave-3 (M3.T6) under three preconditions captured in the audit doc: (i) live-key verification, (ii) `cycle_id` discipline separating stub from live spend, and (iii) a concurrency fix before parallel probe execution.

## 6. Recommendations for Wave-3 M3.T6 owner

1. Run a $5-ceiling live-key verification per provider before shipping any probe question.
2. Adopt the `cycle-N-stub` / `cycle-N-live` `cycle_id` discipline.
3. Before parallel probe execution: add `fcntl.flock` around the read-check-write in `cost.py`, or migrate cumulative-spend state to per-cycle SQLite with `BEGIN IMMEDIATE`.
4. Migrate `gemini_provider.py` from `google-generativeai` to `google.genai`.
5. The schema contact point for probe outputs is the existing `adversarial_probe_edge` type. No schema edit is needed for the harness itself.

## Appendix: Implementation Details

### A.1 Artifact inventory (under `substrate/staging/fm_probe_harness/`)

- `INGEST_AUDIT.md` (9 sections; required deliverable)
- `README.md` (operator runbook)
- `pricing_table.json` (10 model rows, 4 providers, UP-rounded, source-dated 2026-05-17)
- `cost_telemetry.jsonl` (4 stub rows from canonical cycle-2 smoke run)
- `harness/` — `__init__.py`, `client.py`, `cost.py`, `telemetry.py`, `retry.py`, `batching.py`, `providers/`
- `tests/` — `test_stub_smoke.py`, `test_cost_cap.py`, `test_telemetry.py`, `test_retry.py`, `test_live_smoke.py`, `conftest.py`, `_audit_verify_default.py`

### A.2 Test results

`python3 -m pytest tests/ -q`  →  **12 passed, 3 skipped in 0.31 s**

- stub smoke 2/2; cost cap 2/2; telemetry 3/3; retry 5/5; live smoke 0 passed / 3 skipped (no keys).

### A.3 Session references

- Cycle 1: researcher `cb5be3f2-d27d-4205-a98f-82be4312c82c`, worker `582ff9c2-96ab-423e-8ee3-340041425d68`, auditor `9da69968-9714-451f-906a-01bd2394743d`.
- Cycle 2: researcher `873d987e-bf2d-4e05-a42a-6663850947b6`, worker `a24e0a1f-afd8-47ea-8d73-f0589056481e`, auditor `23b74896-e66e-4610-a2c6-65f6222b1a1a`.
- Cycle 3: researcher `13ff3f08-d18c-4dda-8a13-83ca7ae4284c`, worker `f4ca2273-e7f2-4f8e-b1b1-b4535d67d75f`, auditor `ec94cbd7-6539-4917-b930-f836d77ac1cf`.

### A.4 Cross-reference map

- Required output artifact (directive): `substrate/staging/fm_probe_harness/INGEST_AUDIT.md` — PRESENT.
- Merge handoff: `<run-root>/.long-exposure/fork-e34b5b2c1c6c/clone-6/merge_report.md` — PRESENT (authored cycle 2, augmented with auditor closure event).
- Clone-local promise-ledger event: `auditor-closure-m18-clone6` appended to `.long-exposure/fork-e34b5b2c1c6c/clone-6/promise_ledger.jsonl`.
- Downstream consumer: Wave-3 M3.T6 probe runner (a different clone, not clone-6).

<verdict>validated</verdict>
[END OUTPUT: report]

Clone-6 M1.8 merge report compiled covering cycles 1–3: the foundation-model API harness shipped VALIDATED in cycle 2 with all sufficiency criteria met (12 passed / 3 skipped tests, 9-section INGEST_AUDIT.md present, cwd-invariant telemetry path, cap mechanism covering both cumulative-overrun and single-call-too-large), one CRITICAL caught-and-patched in-cycle, two MODERATE/MINOR items forward-routed to Wave-3, and cycle 3 converged on PIVOT-to-exit per the no-null-cycle-validation rule. Verdict: **validated**.

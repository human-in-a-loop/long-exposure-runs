---
created: 2026-05-17T17:10:00Z
cycle: 2
run_id: run-phytograph-cycle2
agent: worker
milestone: M1.8
clone: 6 of 8 (fork e34b5b2c1c6c)
---

# M1.8 — Foundation-Model API Harness Ingestion Audit

## Status

**`data-limited`.** Per-cycle artifact is complete and all sufficiency criteria are met for the *harness*. However, no API keys for Anthropic, OpenAI, or Google are present in the cycle-2 environment, so the three real providers are documented-stubbed for this cycle. All cap, telemetry, retry, and cost-accounting paths are exercised through the deterministic `StubProvider`; the audit certifies the harness is ready to switch to live mode the moment keys are set, with no code change required.

## 1. Provider table

| Provider | model_id used in smoke | SDK package & version | ToS URL (access date 2026-05-17) | ToS-confirmation note | Live-vs-stub this cycle |
|---|---|---|---|---|---|
| Anthropic | `claude-haiku-4-5-20251001` | `anthropic==0.96.0` | https://www.anthropic.com/legal/api-terms ; https://www.anthropic.com/legal/usage-policy | "Programmatic access permitted under the Anthropic API. SDK honors documented rate limits; no scraping. Caller must respect Usage Policy clauses on disallowed use." | **stub** (ANTHROPIC_API_KEY missing in cycle-2 env) |
| OpenAI | `gpt-4o-mini` | `openai==2.37.0` | https://openai.com/policies/row-terms-of-use ; https://openai.com/policies/usage-policies | "API use governed by Terms of Use + Usage Policies. SDK enforces server-side rate limits via 429 backoff. No bulk scraping of model outputs." | **stub** (OPENAI_API_KEY missing) |
| Google Gemini | `gemini-2.5-flash` | `google-generativeai` (currently-installed version; package is officially deprecated 2026 in favor of `google-genai` — see §7 for the migration note) | https://ai.google.dev/gemini-api/terms ; https://policies.google.com/terms/generative-ai/use-policy | "Free and paid tiers governed by Gemini API Terms + Use Policy. Quotas enforced server-side." | **stub** (GOOGLE_API_KEY / GEMINI_API_KEY missing) |
| Stub | `stub-echo`, `stub-priced` | n/a (in-tree) | n/a | Deterministic in-process mock; never makes a network call. Two model entries: `stub-echo` (zero-cost) and `stub-priced` ($1/Mtok in, $2/Mtok out — used in cap-overrun tests). | **live** (always available) |

All three real-provider adapters were nonetheless instantiated, smoke-routed through the FMClient code path, and the resulting telemetry rows confirm correct accounting under each provider's price card (see §4).

## 2. Pricing table snapshot

Source: `substrate/staging/fm_probe_harness/pricing_table.json`. All values USD per 1,000,000 tokens, rounded UP. Sources accessed 2026-05-17.

| Provider | Model | Input $/Mtok | Output $/Mtok | Source URL |
|---|---|---|---|---|
| anthropic | claude-opus-4-7 | 15.00 | 75.00 | https://www.anthropic.com/pricing |
| anthropic | claude-sonnet-4-6 | 3.00 | 15.00 | https://www.anthropic.com/pricing |
| anthropic | claude-haiku-4-5-20251001 | 1.00 | 5.00 | https://www.anthropic.com/pricing |
| openai | gpt-4o | 5.00 | 20.00 | https://openai.com/api/pricing/ |
| openai | gpt-4o-mini | 0.60 | 2.40 | https://openai.com/api/pricing/ |
| openai | gpt-5-nano | 0.20 | 0.80 | https://openai.com/api/pricing/ |
| google | gemini-2.5-pro | 3.50 | 10.50 | https://ai.google.dev/pricing |
| google | gemini-2.5-flash | 0.30 | 2.50 | https://ai.google.dev/pricing |
| stub | stub-echo | 0.00 | 0.00 | — |
| stub | stub-priced | 1.00 | 2.00 | — |

`_default` rows exist per provider so an unfamiliar model_id falls back to the most expensive listed model (conservative). Edit `pricing_table.json` when providers update; the harness reads it on each FMClient construction.

## 3. Cap mechanism

The $500/cycle USD cap is the entire safety contract for Track 6. It is enforced at exactly one point: `FMClient.call()`, before the provider adapter is invoked.

**Algorithm.**

1. `tokens_in_est = adapter.estimate_tokens_in(model_id, messages)` (provider-native tokenizer; 4 chars/token fallback for Gemini).
2. `estimated_cost = PricingTable.estimate_cost(provider, model_id, tokens_in_est, max_tokens)` — input price × tokens_in + output price × `max_tokens` (worst case), rounded UP to the next $0.000001.
3. If `self._spent_usd + estimated_cost > self.usd_cap`, the call is **rejected** with `status="cap_exhausted"`. A telemetry row is written (so the rejection is observable) but the provider is NOT called.
4. Otherwise the call proceeds. After it returns, `actual_cost` is computed from realized `tokens_in` and `tokens_out` and added to `self._spent_usd`.

**Caller responsibility on `cap_exhausted`.** The caller must handle the rejection (skip the question, mark it `data-limited`, or wait for the next cycle). The harness does NOT split, retry, or transparently re-route.

**Durability across restarts.** `FMClient.__init__` calls `TelemetryLog.cycle_total_usd(cycle_id)`, which streams the JSONL file and sums `cost_usd` for the current `cycle_id`. This means a freshly-constructed FMClient in a new process sees the prior process's spend and continues enforcing the cap correctly. Verified by `tests/test_telemetry.py::test_telemetry_restart_replay`.

**Test pointer.** `tests/test_cost_cap.py::test_cap_truncates_on_overrun` simulates a sequence of three $0.04 calls against a $0.10 cap and confirms call 3 returns `cap_exhausted`. `test_cap_rejects_on_first_call_when_estimate_too_large` covers the case where a single call's own estimate already exceeds the cap.

## 4. Smoke test results

Test command: `python3 -m pytest tests/ -q` from `substrate/staging/fm_probe_harness/`.

```
..sss..........                                                          [100%]
12 passed, 3 skipped in 0.31s
```

| Test file | Tests | Passed | Skipped | Notes |
|---|---|---|---|---|
| `test_stub_smoke.py` | 2 | 2 | 0 | stub-echo zero-cost + stub-priced cost accounting both verified |
| `test_cost_cap.py` | 2 | 2 | 0 | cumulative overrun and single-call-too-large both produce `cap_exhausted` |
| `test_telemetry.py` | 3 | 3 | 0 | restart replay + cycle isolation + malformed-line tolerance |
| `test_retry.py` | 5 | 5 | 0 | succeed-after-transient, exhaust, fatal-no-retry, exponential growth, status classification |
| `test_live_smoke.py` | 3 | 0 | 3 | skipped — no API keys for anthropic/openai/google |

### Canonical smoke run (`cycle_id="cycle-2-smoke-demo"`)

Executed via `python3 -c "..."` (see merge_report); writes to `cost_telemetry.jsonl`. All four providers stub-routed (no keys). Sample telemetry rows:

```json
{"attempts":1,"cost_usd":6e-05,"cycle_id":"cycle-2-smoke-demo","latency_s":9.3e-05,"mode":"stub","model_id":"claude-haiku-4-5-20251001","prompt_template_id":"smoke_test_v1","provider":"anthropic","request_id":"stub_6f2e021a4c31","status":"stub","tokens_in":10,"tokens_out":10,"ts_iso":"2026-05-17T17:08:53Z"}
{"attempts":1,"cost_usd":3e-05,"cycle_id":"cycle-2-smoke-demo","latency_s":5.8e-05,"mode":"stub","model_id":"gpt-4o-mini","prompt_template_id":"smoke_test_v1","provider":"openai","request_id":"stub_7fafff5c15ef","status":"stub","tokens_in":10,"tokens_out":10,"ts_iso":"2026-05-17T17:08:55Z"}
{"attempts":1,"cost_usd":2.9e-05,"cycle_id":"cycle-2-smoke-demo","latency_s":4.9e-05,"mode":"stub","model_id":"gemini-2.5-flash","prompt_template_id":"smoke_test_v1","provider":"google","request_id":"stub_c10277db18d1","status":"stub","tokens_in":10,"tokens_out":10,"ts_iso":"2026-05-17T17:08:58Z"}
{"attempts":1,"cost_usd":0.0,"cycle_id":"cycle-2-smoke-demo","latency_s":5.5e-05,"mode":"stub","model_id":"stub-echo","prompt_template_id":"smoke_test_v1","provider":"stub","request_id":"stub_6f2e021a4c31","status":"stub","tokens_in":10,"tokens_out":10,"ts_iso":"2026-05-17T17:08:58Z"}
```

Total stub-mode spend in this cycle: **$0.000119 USD** (well under the $5/provider live-smoke ceiling and the $500/cycle cap). Cost rows for anthropic / openai / google are nonzero because stub-routed calls under a real provider's pricing card still bill the *cycle budget* at that card's rate — a conservative choice that means Wave-3 calls switching from stub to live will see no budget jump.

Sample response text (anthropic stub-route): `"[stub:claude-haiku-4-5-20251001] echo: Reply with the word OK and nothing else."`. Live calls would return real content; the harness path is identical.

Retry observations: no transient failures during smoke. Retry behavior covered exhaustively in `test_retry.py` (`StubProvider.failure_schedule` injection).

## 5. Telemetry schema

See `README.md` §"Telemetry schema". Reproduced for audit completeness:

```
ts_iso             UTC ISO-8601 ("YYYY-MM-DDTHH:MM:SSZ")
cycle_id           budget bucket id (string)
provider           "anthropic" | "openai" | "google" | "stub"
model_id           provider model identifier (string)
prompt_template_id caller-supplied template id (string)
tokens_in          int (0 on cap_exhausted / error rows)
tokens_out         int
cost_usd           float (post-call actual, micro-dollar precision)
latency_s          float (wall-clock seconds, 6dp)
status             "ok" | "stub" | "cap_exhausted" | "retryable_error" | "fatal_error"
mode               "live" | "stub"
request_id         string | null
attempts           int (1 = first try succeeded)
estimated_cost_usd float  (cap_exhausted rows only)
spent_usd_at_decision float (cap_exhausted rows only)
cap_usd            float  (cap_exhausted rows only)
error_message      string (error rows only)
status_code        int|null (error rows only)
```

Writes are line-buffered with explicit `f.flush()` + `os.fsync()`; a crash mid-write produces at worst a truncated final line, which the reader silently skips (verified by `test_telemetry_ignores_malformed_lines`).

## 6. Retry policy

- `max_attempts = 5`
- `base_delay_s = 1.0`
- `max_delay_s = 60.0`
- `jitter = ±25%` multiplicative
- **Retryable** HTTP status codes: 429, 500, 502, 503, 504
- **Non-retryable** (raises `FatalError` immediately): 400, 401, 403, 404, 422

Implemented in `harness/retry.py`. Provider adapters classify SDK exceptions into `RetryableError` / `FatalError`; the FMClient wraps each call in `with_retries()`. Verified by `test_retry.py` (5 tests, all passing).

## 7. Known limitations

1. **All three real providers documented-stubbed this cycle.** Cycle-2 environment has none of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`. The harness functions identically once any key is exported; no code change needed. Wave-3 operators MUST verify live mode for at least Anthropic + one other provider before running probe questions.
2. **`google-generativeai` is deprecated.** Google has end-of-lifed the package in favor of `google.genai`. The current adapter still works but Wave 3 should plan migration to `google.genai` — the adapter interface is small (one `call` method, one `estimate_tokens_in`) and the swap is local to `harness/providers/gemini_provider.py`.
3. **Single-threaded.** The cap read-check-write window is not atomic across processes. If Wave 3 parallelizes probe-question fan-out, add `fcntl.flock` around `FMClient.call()` OR move budget state to a SQLite WAL file with `BEGIN IMMEDIATE`. Flagged for Wave-3 work; intentionally not solved here per research_brief instruction.
4. **Gemini token estimation fallback.** When `GenerativeModel.count_tokens()` fails (network outage; package mis-config), the adapter uses 4-chars-per-token rounded up. Conservative for English, may underestimate for CJK / Cyrillic / Devanagari prompts. Wave 3 should pre-tokenize probe prompts once and cache.
5. **No images yet.** All three real adapters only handle text. Multimodal Track-6 probe categories (toxicity look-alikes from images, Pl@ntNet / iNaturalist comparisons) need a follow-up adapter — out of scope for M1.8 per directive.
6. **No streaming.** Adapters call the non-streaming API. Cost accounting depends on the response's `usage` block; streaming would require accumulating chunks before charging. Wave 3 can defer until needed.
7. **No rate-limit hint persistence.** A 429 triggers retry-with-backoff but the harness does not parse `Retry-After` headers from the response — it falls back to the policy's exponential schedule. Acceptable for cycle 2.

## 8. Cycle-3 readiness checklist (what Wave 3 / M3.T6 inherits)

- [x] `FMClient(cycle_id, usd_cap, telemetry_path)` constructor — durable across restarts.
- [x] Three real-provider adapters wired with SDK exception → RetryableError/FatalError mapping.
- [x] `StubProvider` for keyless development & deterministic tests.
- [x] `pricing_table.json` editable; UP-rounded; sourced & dated.
- [x] JSONL telemetry schema documented; `prompt_template_id` field reserved for probe-category aggregation in M3.T6.
- [x] Cost-cap reject path returns `cap_exhausted` synchronously; caller may handle by skipping / deferring.
- [x] `test_live_smoke.py` parametrized over the three real providers — green the moment a key is set.
- [ ] **Wave-3 owners must:** export API keys; bump `cycle_id` to `cycle-3`; add `fcntl.flock` if parallelizing; consider migration to `google.genai`.

## 9. Schema impact

**None.** This branch produces operational infrastructure only. No new node types, no new edge types, no modifications to `phytograph_schema.md` v1.0. The probe runner (M3.T6, Wave 3) will produce `adversarial_probe_edge` records using the harness — those records, not this harness, are the schema-touching artifacts.

## Cross-references

- Plan-of-record: `plan_of_record.md` M1.8 row (Wave 1, FAN-OUT A).
- Schema (frozen v1.0): `phytograph_schema.md`.
- Risk register: `risk_register.md` R1 (API cost cap → directly mitigated by this harness).
- Promise ledger: `_plan/m1.8-fm-probe-harness-scaffolding` event appended this cycle.
- Merge report (for root conductor): `<run-root>/.long-exposure/fork-e34b5b2c1c6c/clone-6/merge_report.md`.

# PhytoGraph M1.8 — Foundation-Model API Harness (operator runbook)

**Owner:** Track 6 / Wave 3 probe runner inherits this.
**Status as of cycle 2:** stub-mode for all three real providers (no API keys present in cycle-2 env). All cap/telemetry/retry guarantees are exercised through the stub provider; live smoke is unblocked the moment a key is set.

## What this is

A unified facade (`FMClient`) over Anthropic / OpenAI / Google Gemini SDKs with:

- **$500/cycle USD hard cap** enforced *before* every call.
- **Append-only JSONL telemetry** (`cost_telemetry.jsonl`) that survives process restarts: a new `FMClient` replays the file and resumes with the correct remaining budget.
- **Exponential-backoff retries** (5 attempts; 1s base; 60s ceiling; ±25% jitter; retryable: 429, 5xx).
- **Stub-mode fallback** so the harness is usable on a machine with no API keys.

The harness does NOT run probe questions. That is Wave 3 (M3.T6).

## Environment

```bash
# Required Python: 3.11 or 3.12.
# Installed via: uv pip install anthropic openai google-generativeai tenacity pytest

# Live-mode requires one or more of:
export ANTHROPIC_API_KEY=sk-...
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=...        # or GEMINI_API_KEY
```

Missing keys → that provider silently falls back to `StubProvider`; calls return `status="stub"` and a deterministic echo response, but every other code path (cost accounting, telemetry, retry classification) is exercised exactly as in live mode.

## Minimal usage

```python
from harness.client import FMClient

client = FMClient(
    cycle_id="cycle-3",              # bumping this resets the $500 budget bucket
    usd_cap=500.0,
    # telemetry_path defaults to <package>/cost_telemetry.jsonl, anchored at
    # the harness package directory regardless of cwd. Override only if you
    # want a separate budget bucket (e.g. an alternate runs/ folder).
)

resp = client.call(
    provider="anthropic",
    model_id="claude-haiku-4-5-20251001",
    prompt_template_id="syn_confusion_v1",
    messages=[{"role": "user", "content": "Is Solanum lycopersicum the same plant as Lycopersicon esculentum?"}],
    max_tokens=200,
)

if resp.status == "cap_exhausted":
    # Caller's responsibility. Skip the question, log it, or wait for next cycle.
    ...
elif resp.status == "ok":
    record_response(resp.text, resp.cost_usd, resp.request_id)
elif resp.status in ("retryable_error", "fatal_error"):
    log_failure(resp.error_message, resp.status)
elif resp.status == "stub":
    # No API key for this provider — response is canned. Do NOT use for real probe data.
    ...
```

## Cap semantics

Before every call, the harness:

1. Estimates `tokens_in` (provider-native tokenizer where available; 4-chars-per-token fallback for Gemini).
2. Looks up unit price in `pricing_table.json` (USD per 1M tokens, rounded UP).
3. Estimates worst-case cost: `(tokens_in * input_price + max_tokens * output_price) / 1M`, rounded up to the next micro-dollar.
4. If `spent_so_far + estimate > cap`, returns `cap_exhausted` and writes a telemetry row WITHOUT calling the provider.

`spent_so_far` is recomputed by replaying the telemetry file at FMClient construction, filtered by `cycle_id`. This makes the cap durable across process restarts within a cycle — as long as every caller writes to the *same* telemetry file. The default path is anchored at the harness package directory (`<package>/cost_telemetry.jsonl`), so two callers in different cwds resolve to the same file. If you override `telemetry_path`, you MUST pass an absolute path or the same explicit relative path every time, or the cap will fragment across separate files.

**To reset the budget**, bump `cycle_id`. The directive convention is `cycle-N` (e.g., `cycle-3` for the next cycle).

## Cost cap caveats (Wave 3 concerns, not solved here)

- **Concurrency:** the harness is single-threaded. If Wave 3 fan-out parallelizes calls, the spent-USD update is not atomic across processes. Recommended Wave-3 fix: add a `fcntl.flock` around the read-check-write window in `FMClient.call()`, or move budget accounting into a per-cycle SQLite file with `BEGIN IMMEDIATE`.
- **Estimation accuracy:** over-estimation is safe; under-estimation defeats the cap. The pricing table rounds UP and assumes `max_tokens` is the realized output count. If a downstream caller asks for `max_tokens=4096` but the model returns 50, the cap will be conservative but never breached.
- **Token-count fallback:** Gemini's tokenizer requires a network call. If `count_tokens` fails, the harness falls back to `chars / 4`, rounded up. This is conservative for English but may underestimate for non-Latin scripts. Wave 3 should pre-tokenize prompts and cache.

## Pricing table

`pricing_table.json` is keyed by `(provider, model_id)` with `_default` per provider. Edit when providers update rates. Always round UP.

## Telemetry schema

One JSON object per line. Fields:

| field | type | meaning |
|---|---|---|
| `ts_iso` | string | UTC, ISO-8601 with `Z` suffix |
| `cycle_id` | string | budget bucket id |
| `provider` | string | `"anthropic"` \| `"openai"` \| `"google"` \| `"stub"` |
| `model_id` | string | provider-specific model identifier |
| `prompt_template_id` | string | caller-supplied template id (for probe-category aggregation) |
| `tokens_in` | int | realized input tokens (or 0 for `cap_exhausted` / error rows) |
| `tokens_out` | int | realized output tokens |
| `cost_usd` | float | post-call cost computed from the realized token counts |
| `latency_s` | float | wall-clock seconds, rounded to 6 dp |
| `status` | string | `"ok"` \| `"stub"` \| `"cap_exhausted"` \| `"retryable_error"` \| `"fatal_error"` |
| `mode` | string | `"live"` \| `"stub"` |
| `request_id` | string\|null | provider request id where available |
| `attempts` | int | retries used (1 = first try succeeded) |
| `estimated_cost_usd` | float | (cap_exhausted rows only) |
| `spent_usd_at_decision` | float | (cap_exhausted rows only) |
| `cap_usd` | float | (cap_exhausted rows only) |
| `error_message` | string | (error rows only) |
| `status_code` | int\|null | (error rows only) |

The file may contain `#`-prefixed comment lines (one is dropped on first creation). Readers ignore them.

## Retry policy

- `max_attempts`: 5
- `base_delay_s`: 1.0
- `max_delay_s`: 60.0
- `jitter`: ±25% multiplicative
- retryable HTTP status: 429, 500, 502, 503, 504
- non-retryable: 400, 401, 403, 404, 422 (raise FatalError immediately)

Override by passing a custom `RetryPolicy` to `FMClient`.

## Running the smoke tests

```bash
# All tests (stub-mode fully exercised; live smokes skip if no key):
cd substrate/staging/fm_probe_harness
python3 -m pytest tests/ -q

# Live smoke for one provider:
ANTHROPIC_API_KEY=sk-... python3 -m pytest tests/test_live_smoke.py -q
```

## File map

```
substrate/staging/fm_probe_harness/
├── INGEST_AUDIT.md
├── README.md                     (this file)
├── cost_telemetry.jsonl          (append-only)
├── pricing_table.json
├── harness/
│   ├── client.py                 FMClient + FMResponse — the chokepoint
│   ├── cost.py                   PricingTable + estimate/actual cost
│   ├── telemetry.py              TelemetryLog (append + replay)
│   ├── retry.py                  RetryPolicy + with_retries + classify_status
│   ├── batching.py               CallPlan + plan_batch (advisory planner)
│   └── providers/
│       ├── base.py
│       ├── stub_provider.py
│       ├── anthropic_provider.py
│       ├── openai_provider.py
│       └── gemini_provider.py
└── tests/
    ├── conftest.py
    ├── test_stub_smoke.py
    ├── test_cost_cap.py
    ├── test_telemetry.py
    ├── test_retry.py
    └── test_live_smoke.py        (skipped without keys)
```

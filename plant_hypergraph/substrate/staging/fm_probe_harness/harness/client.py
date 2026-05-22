# PhytoGraph M1.8 — unified FMClient facade. cycle 2, worker.
"""FMClient is the single chokepoint for foundation-model API calls.

Every call passes through `FMClient.call()`. This is the place — and the
ONLY place — where the $500/cycle USD cap is enforced. Adapters MUST NOT
write telemetry directly or skip the cap check; their job is to translate
the SDK call to a RawResponse and to raise RetryableError / FatalError.

Cap semantics (per research_brief §3):
- Before each call, estimate cost from (tokens_in, max_tokens) and the
  pricing table. If current_cycle_usd + estimated_cost > usd_cap, reject
  the call with status="cap_exhausted" without making it. The caller is
  responsible for handling that gracefully.
- Per-cycle USD is computed by REPLAYING telemetry on FMClient construction
  so the cap survives process restarts within the same cycle_id.
- Stub-mode calls still write telemetry with cost_usd=0.0 to prove the
  path works end-to-end.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cost import PricingTable
from .telemetry import TelemetryLog, now_iso
from .retry import RetryPolicy, with_retries, RetryableError, FatalError
from .providers import (
    ProviderAdapter,
    StubProvider,
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
)

# Anchor the default telemetry path at the package directory rather than at
# whatever the caller's cwd happens to be. A relative-string default silently
# produced different telemetry files in different cwds, which would defeat the
# $500/cycle cap's restart-replay durability guarantee — the cap is the entire
# safety contract for Track 6, so the default must NOT depend on cwd.
_PACKAGE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_TELEMETRY_PATH = _PACKAGE_DIR / "cost_telemetry.jsonl"


@dataclass
class FMResponse:
    text: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_s: float
    status: str  # "ok" | "cap_exhausted" | "retryable_error" | "fatal_error" | "stub"
    provider: str
    model_id: str
    prompt_template_id: str
    request_id: Optional[str] = None
    error_message: Optional[str] = None
    attempts: int = 0
    mode: str = "live"


class FMClient:
    def __init__(
        self,
        cycle_id: str,
        usd_cap: float = 500.0,
        telemetry_path: os.PathLike | str = _DEFAULT_TELEMETRY_PATH,
        pricing_path: Optional[os.PathLike | str] = None,
        retry_policy: RetryPolicy = RetryPolicy(),
        adapters: Optional[Dict[str, ProviderAdapter]] = None,
        stub_mode: Optional[Dict[str, bool]] = None,
    ):
        """Construct an FMClient.

        Args:
            cycle_id: identifies the budget bucket. All calls under the same
                cycle_id share the $500 cap. Bumping cycle_id resets the cap.
            usd_cap: per-cycle USD cap. Default $500 per the campaign directive.
            telemetry_path: append-only JSONL log.
            pricing_path: pricing table path. Defaults to pricing_table.json
                next to the package.
            retry_policy: backoff configuration.
            adapters: optional pre-constructed provider adapters. If omitted,
                adapters are built lazily on first use and skipped to stub if
                their API key is missing.
            stub_mode: optional explicit map provider -> bool. If True, ALL
                calls to that provider are routed through StubProvider even
                if a real adapter could be constructed. Used in tests.
        """
        self.cycle_id = cycle_id
        self.usd_cap = float(usd_cap)
        self.pricing = PricingTable(Path(pricing_path) if pricing_path else None)
        self.telemetry = TelemetryLog(telemetry_path)
        self.retry_policy = retry_policy
        self._adapters: Dict[str, ProviderAdapter] = dict(adapters) if adapters else {}
        self._stub_mode: Dict[str, bool] = dict(stub_mode) if stub_mode else {}
        # Replay telemetry: current USD spent in this cycle.
        self._spent_usd = self.telemetry.cycle_total_usd(self.cycle_id)
        # Lazy shared stub for any provider missing creds.
        self._fallback_stub = StubProvider()

    # --- Introspection -------------------------------------------------

    @property
    def spent_usd(self) -> float:
        return self._spent_usd

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.usd_cap - self._spent_usd)

    # --- Adapter resolution -------------------------------------------

    def _resolve_adapter(self, provider: str) -> tuple[ProviderAdapter, str]:
        """Return (adapter, mode) where mode is 'live' or 'stub'."""
        if self._stub_mode.get(provider, False):
            return self._fallback_stub, "stub"
        if provider in self._adapters:
            return self._adapters[provider], "live" if not isinstance(self._adapters[provider], StubProvider) else "stub"
        # Try to build a real adapter; fall back to stub if creds missing or SDK absent.
        try:
            if provider == "anthropic":
                ad = AnthropicProvider()
            elif provider == "openai":
                ad = OpenAIProvider()
            elif provider == "google":
                ad = GeminiProvider()
            elif provider == "stub":
                ad = StubProvider()
            else:
                raise RuntimeError(f"unknown provider {provider!r}")
        except RuntimeError as e:
            # No creds / no SDK -> stub-mode fallback.
            self._adapters[provider] = self._fallback_stub
            return self._fallback_stub, "stub"
        self._adapters[provider] = ad
        return ad, ("stub" if isinstance(ad, StubProvider) else "live")

    # --- Core call ------------------------------------------------------

    def call(
        self,
        provider: str,
        model_id: str,
        prompt_template_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 256,
        **extra: Any,
    ) -> FMResponse:
        adapter, mode = self._resolve_adapter(provider)

        # Estimate cost. Stub providers report zero cost via the pricing table.
        # Tests may pin the estimate via `force_tokens_in` (which is also passed
        # through to the adapter as the realized input-token count).
        if "force_tokens_in" in extra:
            tokens_in_est = int(extra["force_tokens_in"])
        else:
            try:
                tokens_in_est = adapter.estimate_tokens_in(model_id, messages)
            except Exception:
                from .providers.base import fallback_token_estimate
                tokens_in_est = fallback_token_estimate(messages)
        # For cap accounting, charge under the *requested* provider's price card
        # even when stubbed — that mirrors what a real call would have cost.
        # EXCEPTION: when mode == "stub" because the caller asked for stub-mode
        # explicitly (test harness, cap test), they want zero-cost. Use the
        # 'stub' price card in that case.
        price_provider = "stub" if mode == "stub" and provider == "stub" else provider
        price_model = model_id if price_provider == provider else "stub-echo"
        # Allow tests to inject a price model directly.
        if "force_price_provider" in extra:
            price_provider = extra.pop("force_price_provider")
        if "force_price_model" in extra:
            price_model = extra.pop("force_price_model")
        estimated = self.pricing.estimate_cost(price_provider, price_model, tokens_in_est, max_tokens)

        if self._spent_usd + estimated > self.usd_cap:
            # CAP EXHAUSTED — log a zero-cost telemetry row so the rejection is observable.
            rec = {
                "ts_iso": now_iso(),
                "cycle_id": self.cycle_id,
                "provider": provider,
                "model_id": model_id,
                "prompt_template_id": prompt_template_id,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "latency_s": 0.0,
                "status": "cap_exhausted",
                "request_id": None,
                "mode": mode,
                "estimated_cost_usd": estimated,
                "spent_usd_at_decision": self._spent_usd,
                "cap_usd": self.usd_cap,
            }
            self.telemetry.append(rec)
            return FMResponse(
                text="",
                tokens_in=0,
                tokens_out=0,
                cost_usd=0.0,
                latency_s=0.0,
                status="cap_exhausted",
                provider=provider,
                model_id=model_id,
                prompt_template_id=prompt_template_id,
                error_message=f"cap_exhausted: spent={self._spent_usd:.6f} est={estimated:.6f} cap={self.usd_cap:.2f}",
                attempts=0,
                mode=mode,
            )

        # Make the call (with retry).
        t_start = time.monotonic()
        try:
            raw, attempts = with_retries(
                lambda: adapter.call(model_id, messages, max_tokens=max_tokens, **extra),
                policy=self.retry_policy,
            )
            latency = time.monotonic() - t_start
            actual_cost = self.pricing.actual_cost(price_provider, price_model, raw.tokens_in, raw.tokens_out)
            self._spent_usd += actual_cost
            status = "stub" if mode == "stub" else "ok"
            rec = {
                "ts_iso": now_iso(),
                "cycle_id": self.cycle_id,
                "provider": provider,
                "model_id": model_id,
                "prompt_template_id": prompt_template_id,
                "tokens_in": raw.tokens_in,
                "tokens_out": raw.tokens_out,
                "cost_usd": actual_cost,
                "latency_s": round(latency, 6),
                "status": status,
                "request_id": raw.request_id,
                "mode": mode,
                "attempts": attempts,
            }
            self.telemetry.append(rec)
            return FMResponse(
                text=raw.text,
                tokens_in=raw.tokens_in,
                tokens_out=raw.tokens_out,
                cost_usd=actual_cost,
                latency_s=latency,
                status=status,
                provider=provider,
                model_id=model_id,
                prompt_template_id=prompt_template_id,
                request_id=raw.request_id,
                attempts=attempts,
                mode=mode,
            )
        except FatalError as e:
            latency = time.monotonic() - t_start
            rec = {
                "ts_iso": now_iso(),
                "cycle_id": self.cycle_id,
                "provider": provider,
                "model_id": model_id,
                "prompt_template_id": prompt_template_id,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "latency_s": round(latency, 6),
                "status": "fatal_error",
                "request_id": None,
                "mode": mode,
                "error_message": str(e),
                "status_code": e.status_code,
            }
            self.telemetry.append(rec)
            return FMResponse(
                text="", tokens_in=0, tokens_out=0, cost_usd=0.0, latency_s=latency,
                status="fatal_error", provider=provider, model_id=model_id,
                prompt_template_id=prompt_template_id, error_message=str(e), mode=mode,
            )
        except RetryableError as e:
            latency = time.monotonic() - t_start
            rec = {
                "ts_iso": now_iso(),
                "cycle_id": self.cycle_id,
                "provider": provider,
                "model_id": model_id,
                "prompt_template_id": prompt_template_id,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "latency_s": round(latency, 6),
                "status": "retryable_error",
                "request_id": None,
                "mode": mode,
                "error_message": str(e),
                "status_code": e.status_code,
            }
            self.telemetry.append(rec)
            return FMResponse(
                text="", tokens_in=0, tokens_out=0, cost_usd=0.0, latency_s=latency,
                status="retryable_error", provider=provider, model_id=model_id,
                prompt_template_id=prompt_template_id, error_message=str(e), mode=mode,
            )

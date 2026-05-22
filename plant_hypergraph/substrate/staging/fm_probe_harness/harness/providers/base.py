# PhytoGraph M1.8 — provider adapter base interface. cycle 2, worker.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class RawResponse:
    text: str
    tokens_in: int
    tokens_out: int
    request_id: Optional[str]
    raw: Dict[str, Any]  # provider-native response payload (for debug only)


class ProviderAdapter(Protocol):
    """Minimal contract every provider adapter must satisfy.

    The adapter handles SDK-specific call mechanics. Cost, telemetry, retry,
    and cap enforcement live in FMClient — adapters do NOT call those concerns.
    They raise RetryableError / FatalError so the harness can decide.
    """

    name: str  # "anthropic" | "openai" | "google" | "stub"

    def estimate_tokens_in(self, model_id: str, messages: List[Dict[str, str]]) -> int:
        """Upper-bound the input token count for cost estimation pre-call."""
        ...

    def call(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int,
        **kwargs: Any,
    ) -> RawResponse:
        """Make one synchronous call. Raises RetryableError / FatalError on failure."""
        ...


def estimate_chars(messages: List[Dict[str, str]]) -> int:
    return sum(len(m.get("content", "")) for m in messages)


def fallback_token_estimate(messages: List[Dict[str, str]]) -> int:
    """4-chars-per-token fallback, rounded UP. Used when no native tokenizer is available."""
    chars = estimate_chars(messages)
    # +1 fudge so an empty/whitespace prompt still costs at least 1 token in estimation.
    return max(1, -(-chars // 4))

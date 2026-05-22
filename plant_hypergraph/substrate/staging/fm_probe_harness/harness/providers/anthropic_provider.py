# PhytoGraph M1.8 — Anthropic adapter. cycle 2, worker.
"""Anthropic Messages API adapter.

The harness imports the SDK lazily so the package is usable on machines
without `anthropic` installed (the adapter just raises at construction).
The adapter does NOT enforce cost or write telemetry — those are FMClient
concerns. It maps SDK exceptions onto RetryableError / FatalError.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..retry import RetryableError, FatalError
from .base import RawResponse, fallback_token_estimate


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None) -> None:
        try:
            import anthropic  # noqa: F401
        except ImportError as e:
            raise RuntimeError(f"anthropic SDK not installed: {e}") from e
        self._anthropic = __import__("anthropic")
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self._client = self._anthropic.Anthropic(api_key=key)

    def estimate_tokens_in(self, model_id: str, messages: List[Dict[str, str]]) -> int:
        # Anthropic SDK exposes a count_tokens helper on some versions; fall back if absent.
        try:
            # Newer SDKs: client.messages.count_tokens(model=..., messages=...)
            res = self._client.messages.count_tokens(model=model_id, messages=messages)
            return int(getattr(res, "input_tokens", 0)) or fallback_token_estimate(messages)
        except Exception:
            return fallback_token_estimate(messages)

    def call(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int,
        **kwargs: Any,
    ) -> RawResponse:
        a = self._anthropic
        try:
            resp = self._client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                messages=messages,
            )
        except a.APIStatusError as e:  # type: ignore[attr-defined]
            code = getattr(e, "status_code", None)
            if code in (400, 401, 403, 404, 422):
                raise FatalError(str(e), status_code=code)
            raise RetryableError(str(e), status_code=code)
        except a.APIConnectionError as e:  # type: ignore[attr-defined]
            raise RetryableError(str(e), status_code=None)
        except a.RateLimitError as e:  # type: ignore[attr-defined]
            raise RetryableError(str(e), status_code=429)
        except Exception as e:
            raise RetryableError(f"unexpected anthropic error: {e}")

        # Extract text. Anthropic returns a list of content blocks.
        text_parts = []
        for block in getattr(resp, "content", []) or []:
            t = getattr(block, "text", None)
            if t:
                text_parts.append(t)
        text = "".join(text_parts) or ""
        usage = getattr(resp, "usage", None)
        tokens_in = int(getattr(usage, "input_tokens", 0) or 0) or fallback_token_estimate(messages)
        tokens_out = int(getattr(usage, "output_tokens", 0) or 0) or max(1, len(text) // 4)
        return RawResponse(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            request_id=getattr(resp, "id", None),
            raw={"stop_reason": getattr(resp, "stop_reason", None)},
        )

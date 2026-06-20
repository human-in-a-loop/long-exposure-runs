# PhytoGraph M1.8 — OpenAI adapter. cycle 2, worker.
"""OpenAI Chat Completions adapter."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..retry import RetryableError, FatalError
from .base import RawResponse, fallback_token_estimate


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: Optional[str] = None) -> None:
        try:
            import openai  # noqa: F401
        except ImportError as e:
            raise RuntimeError(f"openai SDK not installed: {e}") from e
        self._openai = __import__("openai")
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._client = self._openai.OpenAI(api_key=key)

    def estimate_tokens_in(self, model_id: str, messages: List[Dict[str, str]]) -> int:
        # Prefer tiktoken if installed; fall back to chars/4.
        try:
            import tiktoken  # type: ignore
            try:
                enc = tiktoken.encoding_for_model(model_id)
            except KeyError:
                enc = tiktoken.get_encoding("cl100k_base")
            total = 0
            for m in messages:
                total += len(enc.encode(m.get("content", "")))
                total += 4  # per-message overhead (well-known approximation)
            return total + 2
        except Exception:
            return fallback_token_estimate(messages)

    def call(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int,
        **kwargs: Any,
    ) -> RawResponse:
        o = self._openai
        try:
            resp = self._client.chat.completions.create(
                model=model_id,
                max_tokens=max_tokens,
                messages=messages,
            )
        except o.APIStatusError as e:  # type: ignore[attr-defined]
            code = getattr(e, "status_code", None)
            if code in (400, 401, 403, 404, 422):
                raise FatalError(str(e), status_code=code)
            raise RetryableError(str(e), status_code=code)
        except o.APIConnectionError as e:  # type: ignore[attr-defined]
            raise RetryableError(str(e), status_code=None)
        except o.RateLimitError as e:  # type: ignore[attr-defined]
            raise RetryableError(str(e), status_code=429)
        except Exception as e:
            raise RetryableError(f"unexpected openai error: {e}")

        choice = resp.choices[0] if resp.choices else None
        text = (getattr(getattr(choice, "message", None), "content", "") or "") if choice else ""
        usage = getattr(resp, "usage", None)
        tokens_in = int(getattr(usage, "prompt_tokens", 0) or 0) or fallback_token_estimate(messages)
        tokens_out = int(getattr(usage, "completion_tokens", 0) or 0) or max(1, len(text) // 4)
        return RawResponse(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            request_id=getattr(resp, "id", None),
            raw={"finish_reason": getattr(choice, "finish_reason", None)},
        )

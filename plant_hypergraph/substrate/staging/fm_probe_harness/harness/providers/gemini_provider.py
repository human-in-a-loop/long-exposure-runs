# PhytoGraph M1.8 — Google Gemini adapter. cycle 2, worker.
"""Gemini adapter via the `google-generativeai` package.

Note: Google has deprecated `google-generativeai` in favor of `google.genai`.
We use the older package for this cycle because it is the currently-installed
SDK; a migration to `google.genai` is listed as a Wave-3 follow-up in
INGEST_AUDIT.md.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..retry import RetryableError, FatalError
from .base import RawResponse, fallback_token_estimate


def _flatten(messages: List[Dict[str, str]]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "user")
        parts.append(f"{role}: {m.get('content','')}")
    return "\n".join(parts)


class GeminiProvider:
    name = "google"

    def __init__(self, api_key: Optional[str] = None) -> None:
        try:
            import google.generativeai as genai  # type: ignore
        except ImportError as e:
            raise RuntimeError(f"google-generativeai SDK not installed: {e}") from e
        self._genai = genai
        key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY / GEMINI_API_KEY not set")
        genai.configure(api_key=key)

    def estimate_tokens_in(self, model_id: str, messages: List[Dict[str, str]]) -> int:
        try:
            model = self._genai.GenerativeModel(model_id)
            res = model.count_tokens(_flatten(messages))
            return int(getattr(res, "total_tokens", 0)) or fallback_token_estimate(messages)
        except Exception:
            # 4 chars/token fallback. Documented in INGEST_AUDIT.md.
            return fallback_token_estimate(messages)

    def call(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int,
        **kwargs: Any,
    ) -> RawResponse:
        try:
            model = self._genai.GenerativeModel(model_id)
            resp = model.generate_content(
                _flatten(messages),
                generation_config={"max_output_tokens": max_tokens},
            )
        except Exception as e:
            # The google-generativeai SDK does not expose a clean exception hierarchy with
            # HTTP status codes. We classify by error string. Anything unrecognized is treated
            # as retryable so the backoff catches transient failures.
            msg = str(e).lower()
            if any(t in msg for t in ("api key", "permission", "unauthorized", "invalid argument", "not found")):
                raise FatalError(str(e), status_code=400)
            raise RetryableError(str(e), status_code=None)

        text = getattr(resp, "text", "") or ""
        usage = getattr(resp, "usage_metadata", None)
        tokens_in = int(getattr(usage, "prompt_token_count", 0) or 0) or fallback_token_estimate(messages)
        tokens_out = int(getattr(usage, "candidates_token_count", 0) or 0) or max(1, len(text) // 4)
        return RawResponse(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            request_id=None,
            raw={},
        )

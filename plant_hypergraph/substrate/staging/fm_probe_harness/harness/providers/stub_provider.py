# PhytoGraph M1.8 — deterministic stub provider for keyless smoke tests. cycle 2, worker.
"""StubProvider returns canned responses with caller-controlled token counts.

Used for: (a) cost-cap test (need deterministic token counts), (b) telemetry
replay test, (c) stub-mode end-to-end smoke when no real-provider key is set.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from ..retry import RetryableError, FatalError
from .base import RawResponse, fallback_token_estimate


class StubProvider:
    name = "stub"

    def __init__(self) -> None:
        self._call_count = 0
        # Injectable failure schedule. Keys are 1-indexed call ordinals.
        # value 'retry' -> raise RetryableError; 'fatal' -> raise FatalError.
        self.failure_schedule: Dict[int, str] = {}

    def estimate_tokens_in(self, model_id: str, messages: List[Dict[str, str]]) -> int:
        return fallback_token_estimate(messages)

    def call(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int,
        **kwargs: Any,
    ) -> RawResponse:
        self._call_count += 1
        scheduled = self.failure_schedule.get(self._call_count)
        if scheduled == "retry":
            raise RetryableError(f"stub scheduled retry on call {self._call_count}", status_code=503)
        if scheduled == "fatal":
            raise FatalError(f"stub scheduled fatal on call {self._call_count}", status_code=400)

        last = messages[-1]["content"] if messages else ""
        text = f"[stub:{model_id}] echo: {last[:64]}"
        # Override knobs for deterministic tests.
        tokens_in = int(kwargs.get("force_tokens_in", self.estimate_tokens_in(model_id, messages)))
        tokens_out = int(kwargs.get("force_tokens_out", min(max_tokens, max(1, len(text) // 4))))
        req_id = "stub_" + hashlib.sha1(f"{self._call_count}|{last}".encode()).hexdigest()[:12]
        return RawResponse(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            request_id=req_id,
            raw={"call_count": self._call_count, "model_id": model_id},
        )

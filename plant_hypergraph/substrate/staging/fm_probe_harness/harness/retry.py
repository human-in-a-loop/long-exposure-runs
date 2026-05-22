# PhytoGraph M1.8 — exponential-backoff retry wrapper. cycle 2, worker.
"""Lightweight retry with exponential backoff and jitter.

We hand-roll instead of using tenacity to keep the dependency surface small
and to expose the retry classification (which exceptions/HTTP codes are
retryable) directly to the audit. tenacity is installed and may be swapped
in by a downstream caller; the policy below is the contract.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple, TypeVar

T = TypeVar("T")

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
NON_RETRYABLE_STATUS = frozenset({400, 401, 403, 404, 422})


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 5
    base_delay_s: float = 1.0
    max_delay_s: float = 60.0
    jitter: float = 0.25  # +/- 25% multiplicative jitter

    def delay_for(self, attempt: int) -> float:
        # attempt is 1-indexed (1 = first retry).
        raw = min(self.max_delay_s, self.base_delay_s * (2 ** (attempt - 1)))
        jitter_factor = 1.0 + random.uniform(-self.jitter, self.jitter)
        return max(0.0, raw * jitter_factor)


class RetryableError(Exception):
    """Provider adapters raise this when a transient failure should trigger backoff."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class FatalError(Exception):
    """Non-retryable: bad request, auth failure, etc."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def with_retries(
    fn: Callable[[], T],
    policy: RetryPolicy = RetryPolicy(),
    sleep: Callable[[float], None] = time.sleep,
) -> Tuple[T, int]:
    """Call `fn` until success, FatalError, or attempts exhausted.

    Returns (result, attempts_used). Raises FatalError or the last RetryableError.
    """
    last_exc: Exception | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn(), attempt
        except FatalError:
            raise
        except RetryableError as exc:
            last_exc = exc
            if attempt >= policy.max_attempts:
                break
            sleep(policy.delay_for(attempt))
    # Exhausted.
    assert last_exc is not None
    raise last_exc


def classify_status(code: int | None) -> str:
    if code is None:
        return "unknown"
    if code in NON_RETRYABLE_STATUS:
        return "fatal"
    if code in RETRYABLE_STATUS:
        return "retryable"
    if 200 <= code < 300:
        return "ok"
    # Unknown 4xx/5xx — be conservative, treat as fatal unless explicitly retryable.
    return "fatal" if 400 <= code < 500 else "retryable"

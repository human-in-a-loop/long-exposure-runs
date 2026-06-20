# PhytoGraph M1.8 — retry/backoff behavior. cycle 2, worker.
"""Confirms (a) retries fire on RetryableError and stop at FatalError,
(b) backoff delays follow exponential-with-jitter, (c) the stub
failure_schedule injection works for downstream tests.
"""
from pathlib import Path

import pytest

from harness.client import FMClient
from harness.providers import StubProvider
from harness.retry import RetryPolicy, RetryableError, FatalError, with_retries, classify_status


def test_retry_succeeds_after_transient_failures(tmp_path: Path):
    stub = StubProvider()
    stub.failure_schedule = {1: "retry", 2: "retry"}  # first two attempts fail, third succeeds
    client = FMClient(
        cycle_id="test-retry",
        usd_cap=10.0,
        telemetry_path=tmp_path / "t.jsonl",
        retry_policy=RetryPolicy(max_attempts=5, base_delay_s=0.0, max_delay_s=0.0, jitter=0.0),
        adapters={"stub": stub},
    )
    resp = client.call(
        provider="stub", model_id="stub-echo",
        prompt_template_id="retry_test", messages=[{"role": "user", "content": "x"}],
        max_tokens=10,
    )
    assert resp.status == "stub"
    assert resp.attempts == 3


def test_retry_gives_up_at_max_attempts(tmp_path: Path):
    stub = StubProvider()
    stub.failure_schedule = {i: "retry" for i in range(1, 10)}
    client = FMClient(
        cycle_id="test-retry-exhaust",
        usd_cap=10.0,
        telemetry_path=tmp_path / "t.jsonl",
        retry_policy=RetryPolicy(max_attempts=3, base_delay_s=0.0, max_delay_s=0.0, jitter=0.0),
        adapters={"stub": stub},
    )
    resp = client.call(
        provider="stub", model_id="stub-echo",
        prompt_template_id="retry_test", messages=[{"role": "user", "content": "x"}],
        max_tokens=10,
    )
    assert resp.status == "retryable_error"


def test_fatal_does_not_retry(tmp_path: Path):
    stub = StubProvider()
    stub.failure_schedule = {1: "fatal"}
    client = FMClient(
        cycle_id="test-fatal", usd_cap=10.0,
        telemetry_path=tmp_path / "t.jsonl",
        retry_policy=RetryPolicy(max_attempts=5, base_delay_s=0.0, max_delay_s=0.0, jitter=0.0),
        adapters={"stub": stub},
    )
    resp = client.call(
        provider="stub", model_id="stub-echo",
        prompt_template_id="fatal_test", messages=[{"role": "user", "content": "x"}],
        max_tokens=10,
    )
    assert resp.status == "fatal_error"


def test_backoff_grows_exponentially():
    p = RetryPolicy(max_attempts=5, base_delay_s=1.0, max_delay_s=60.0, jitter=0.0)
    assert p.delay_for(1) == 1.0
    assert p.delay_for(2) == 2.0
    assert p.delay_for(3) == 4.0
    assert p.delay_for(4) == 8.0
    assert p.delay_for(10) == 60.0  # capped


def test_status_classification():
    assert classify_status(200) == "ok"
    assert classify_status(429) == "retryable"
    assert classify_status(500) == "retryable"
    assert classify_status(401) == "fatal"
    assert classify_status(404) == "fatal"
    assert classify_status(None) == "unknown"

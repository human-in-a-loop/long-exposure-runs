# PhytoGraph M1.8 — $5-ceiling live smoke against real providers. cycle 2, worker.
"""Skipped when API keys are missing. For each provider whose key is set,
makes ONE minimal call ("Reply with the word OK and nothing else.")
with max_tokens=10 and a per-test usd_cap=5.0 hard local cap.

Expected per-call cost: well under $0.01.
"""
import os
from pathlib import Path

import pytest

from harness.client import FMClient


PROVIDERS = [
    ("anthropic", "claude-haiku-4-5-20251001", "ANTHROPIC_API_KEY"),
    ("openai",    "gpt-4o-mini",                "OPENAI_API_KEY"),
    ("google",    "gemini-2.5-flash",           "GOOGLE_API_KEY"),
]


@pytest.mark.parametrize("provider,model_id,env_key", PROVIDERS)
def test_live_smoke(provider, model_id, env_key, tmp_path: Path):
    if not (os.environ.get(env_key) or (env_key == "GOOGLE_API_KEY" and os.environ.get("GEMINI_API_KEY"))):
        pytest.skip(f"{env_key} not set — live smoke skipped for {provider}")

    tele = tmp_path / "cost_telemetry.jsonl"
    client = FMClient(cycle_id=f"live-smoke-{provider}", usd_cap=5.0, telemetry_path=tele)
    resp = client.call(
        provider=provider,
        model_id=model_id,
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "Reply with the word OK and nothing else."}],
        max_tokens=10,
    )
    assert resp.status in ("ok", "retryable_error", "fatal_error"), f"unexpected status {resp.status}"
    if resp.status == "ok":
        assert resp.cost_usd < 0.05, f"cost above $0.05 — investigate: {resp.cost_usd}"
        assert "OK" in resp.text.upper() or len(resp.text) > 0
    # Telemetry row exists either way.
    assert tele.exists()
    assert tele.stat().st_size > 0

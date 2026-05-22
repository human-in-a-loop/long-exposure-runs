# PhytoGraph M1.8 — stub-mode end-to-end smoke. cycle 2, worker.
"""Verifies that a stub-mode call writes a structurally correct telemetry row
and that the FMResponse fields are populated.
"""
import json
from pathlib import Path

from harness.client import FMClient


def test_stub_smoke_writes_telemetry(tmp_path: Path):
    tele = tmp_path / "cost_telemetry.jsonl"
    client = FMClient(cycle_id="test-smoke", usd_cap=10.0, telemetry_path=tele)
    resp = client.call(
        provider="stub",
        model_id="stub-echo",
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "Reply OK"}],
        max_tokens=50,
    )
    assert resp.status == "stub"
    assert resp.text.startswith("[stub:")
    assert resp.tokens_in > 0
    assert resp.tokens_out > 0
    assert resp.cost_usd == 0.0  # stub-echo is zero-cost
    assert resp.mode == "stub"
    assert resp.provider == "stub"
    assert resp.attempts == 1

    lines = [l for l in tele.read_text().splitlines() if l and not l.startswith("#")]
    assert len(lines) == 1
    row = json.loads(lines[0])
    for f in ("ts_iso", "cycle_id", "provider", "model_id", "prompt_template_id",
              "tokens_in", "tokens_out", "cost_usd", "latency_s", "status", "mode"):
        assert f in row, f"missing field {f}"
    assert row["cycle_id"] == "test-smoke"
    assert row["status"] == "stub"


def test_stub_smoke_with_priced_stub(tmp_path: Path):
    """Confirm cost accounting works when a stub mimics a paid provider's
    price card. Uses 'force_price_provider'/'force_price_model' overrides
    and force_tokens_in/out for deterministic numbers.
    """
    tele = tmp_path / "cost_telemetry.jsonl"
    client = FMClient(cycle_id="test-priced", usd_cap=10.0, telemetry_path=tele)
    resp = client.call(
        provider="stub", model_id="stub-priced",
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "x"}],
        max_tokens=100,
        force_price_provider="stub", force_price_model="stub-priced",
        force_tokens_in=1_000_000, force_tokens_out=500_000,
    )
    # 1M tokens in @ $1/Mtok + 0.5M tokens out @ $2/Mtok = 1.00 + 1.00 = $2.00
    assert resp.cost_usd == 2.0
    assert client.spent_usd == 2.0
    assert client.remaining_usd == 8.0

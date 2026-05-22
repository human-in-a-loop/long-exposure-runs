# PhytoGraph M1.8 — cap enforcement on simulated overrun. cycle 2, worker.
"""The cap is the entire safety contract for Track 6. This test simulates
a sequence of calls whose cumulative cost exceeds the cap, and confirms
that the harness returns `cap_exhausted` for the first call that would
cross the cap — without making the call to the (stub) provider.

We use a tiny cap ($0.10) with the priced-stub model so the math is fully
deterministic.
"""
import json
from pathlib import Path

from harness.client import FMClient


def test_cap_truncates_on_overrun(tmp_path: Path):
    tele = tmp_path / "cost_telemetry.jsonl"
    # stub-priced: input $1/Mtok, output $2/Mtok.
    # Each call: 1M tokens in + 0M tokens out (force) = $1.00 actual cost.
    # But max_tokens=1_000_000 makes the *estimate* = 1*1 + 1*2 = $3.00.
    # With cap $0.10, the FIRST call would be rejected on estimation alone.
    # Instead we set max_tokens so estimated < $0.10 for the first call but
    # cumulative breaches $0.10 by the second.
    client = FMClient(cycle_id="test-cap", usd_cap=0.10, telemetry_path=tele)

    # Estimation: tokens_in_est is set via force_tokens_in below.
    # Note: estimate uses (tokens_in, max_tokens) from PRE-call info.
    # Actual cost uses (tokens_in, tokens_out) from POST-call usage.
    # We want each successful call to cost exactly $0.04 actual and to be
    # estimated at $0.04 too (so 3 calls = $0.12 > $0.10).

    # 40,000 input tokens @ $1/Mtok = $0.04. max_tokens=0 makes output cost
    # contribution to estimate = 0. Actual tokens_out forced to 0.
    call_args = dict(
        provider="stub",
        model_id="stub-priced",
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "x"}],
        max_tokens=0,
        force_price_provider="stub",
        force_price_model="stub-priced",
        force_tokens_in=40_000,
        force_tokens_out=0,
    )

    r1 = client.call(**call_args)
    assert r1.status == "stub"
    assert r1.cost_usd == 0.04
    r2 = client.call(**call_args)
    assert r2.status == "stub"
    assert abs(client.spent_usd - 0.08) < 1e-9
    # Third call: estimate 0.04, spent 0.08 → 0.12 > 0.10 → cap_exhausted.
    r3 = client.call(**call_args)
    assert r3.status == "cap_exhausted"
    assert r3.text == ""
    assert client.spent_usd <= 0.10 + 1e-9  # cap never breached

    # Verify a cap_exhausted row landed in the telemetry.
    rows = [json.loads(l) for l in tele.read_text().splitlines()
            if l and not l.startswith("#")]
    statuses = [r["status"] for r in rows]
    assert statuses == ["stub", "stub", "cap_exhausted"]


def test_cap_rejects_on_first_call_when_estimate_too_large(tmp_path: Path):
    """Cap must not allow ANY call whose own estimate would already exceed
    the remaining budget — even the first call in the cycle.
    """
    tele = tmp_path / "cost_telemetry.jsonl"
    client = FMClient(cycle_id="test-cap-first", usd_cap=0.01, telemetry_path=tele)
    resp = client.call(
        provider="stub",
        model_id="stub-priced",
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "x"}],
        max_tokens=0,
        force_price_provider="stub", force_price_model="stub-priced",
        force_tokens_in=1_000_000,  # estimate = $1.00 > $0.01
        force_tokens_out=0,
    )
    assert resp.status == "cap_exhausted"
    assert client.spent_usd == 0.0

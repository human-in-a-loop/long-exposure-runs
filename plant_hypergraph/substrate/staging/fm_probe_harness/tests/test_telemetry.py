# PhytoGraph M1.8 — telemetry append + restart replay. cycle 2, worker.
"""Telemetry must be durable across process restarts within a cycle. A new
FMClient pointed at the same cycle_id and the same JSONL file must
correctly aggregate prior spend and continue enforcing the cap.
"""
from pathlib import Path

from harness.client import FMClient
from harness.telemetry import TelemetryLog


def test_telemetry_restart_replay(tmp_path: Path):
    tele_path = tmp_path / "cost_telemetry.jsonl"
    cap = 0.10
    args = dict(
        provider="stub",
        model_id="stub-priced",
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "x"}],
        max_tokens=0,
        force_price_provider="stub", force_price_model="stub-priced",
        force_tokens_in=40_000,  # $0.04 actual
        force_tokens_out=0,
    )

    c1 = FMClient(cycle_id="cycle-X", usd_cap=cap, telemetry_path=tele_path)
    r1 = c1.call(**args)
    assert r1.status == "stub"
    assert abs(c1.spent_usd - 0.04) < 1e-9

    # New process: same cycle_id, same telemetry file.
    c2 = FMClient(cycle_id="cycle-X", usd_cap=cap, telemetry_path=tele_path)
    assert abs(c2.spent_usd - 0.04) < 1e-9, "restart did not replay prior spend"

    r2 = c2.call(**args)
    assert r2.status == "stub"
    r3 = c2.call(**args)
    assert r3.status == "cap_exhausted", "cap should reject after restart"

    # And a third process should see all of that.
    c3 = FMClient(cycle_id="cycle-X", usd_cap=cap, telemetry_path=tele_path)
    assert abs(c3.spent_usd - 0.08) < 1e-9


def test_telemetry_cycle_isolation(tmp_path: Path):
    """Switching cycle_id resets the budget — different buckets."""
    tele_path = tmp_path / "cost_telemetry.jsonl"
    args = dict(
        provider="stub", model_id="stub-priced",
        prompt_template_id="smoke_test_v1",
        messages=[{"role": "user", "content": "x"}], max_tokens=0,
        force_price_provider="stub", force_price_model="stub-priced",
        force_tokens_in=40_000, force_tokens_out=0,
    )

    a = FMClient(cycle_id="A", usd_cap=1.0, telemetry_path=tele_path)
    a.call(**args); a.call(**args)
    assert abs(a.spent_usd - 0.08) < 1e-9

    b = FMClient(cycle_id="B", usd_cap=1.0, telemetry_path=tele_path)
    assert b.spent_usd == 0.0  # B is a fresh bucket


def test_telemetry_ignores_malformed_lines(tmp_path: Path):
    tele_path = tmp_path / "cost_telemetry.jsonl"
    # Pre-write garbage and a comment line.
    tele_path.write_text("# header\n{not json\n\n")
    log = TelemetryLog(tele_path)
    assert log.cycle_total_usd("anything") == 0.0
    assert log.count() == 0

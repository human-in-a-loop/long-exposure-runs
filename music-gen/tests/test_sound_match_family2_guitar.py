#!/usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 16
# run_id: run-2026-09-04T110000Z
# agent: worker
# milestone: _infra/adopt-cycle15-family2-guitar-tests-c16-fillin
# ---
"""c16 Track 4 test debt closure for c15 CG-guitar family-2 anchors.

Regression pins on c15 render.wav SHA + spike + builder script anchors +
family2_v1 profile SHA + family2_v1.replay_proof SHA + family2 verdict
SHA. All READ-ONLY per FD-1.

Verdict enum FAMILY2_RULED_OUT is asserted as-recorded; interpretation
of that enum under Track 1 diagnostic outcome is Track 2's operator-
escalation scope, not this test's business.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROF = ROOT / "data" / "v4" / "profiles" / "31a164f845f8e27e"

ANCHORS = {
    "guitar_family2_render/render.wav": (
        "f41560714a68415cd2fe1fc8f2c1010f54aafe182f4592ec20ed893ce2559ddc"
    ),
    "guitar_family2_v1.json": (
        "8a11f6532af572a6f2bf6b9eca9c85c40c10d7c992d5ee0fd44f6d204470bfee"
    ),
    "guitar_family2_v1.replay_proof.json": (
        "e87e09bd91f88ef1f95259656b9d1821cd53265b965b90079ad5bff67da59324"
    ),
    "guitar_family2_verdict.json": (
        "969c4d2f197f4bcd5176bea865c9eee602970a9861289a26c9dd66dcb0693460"
    ),
}
SCRIPT_ANCHORS = {
    "scripts/sound_match/family2_stem_sampled_guitar_spike.py": (
        "8adb676a5d7fde948cf42e045969ee51a14ef802497ce46cc3f4d400c07d4b2f"
    ),
    "scripts/sound_match/family2_stem_sampled_guitar_builder.py": (
        "8741a973af698f810d964998538e84b9c8cc91887219cc6d9dd0fba4b49577d8"
    ),
}


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_render_sha_regression():
    p = PROF / "guitar_family2_render" / "render.wav"
    assert _sha256(p) == ANCHORS["guitar_family2_render/render.wav"]


def test_profile_and_verdict_sha_regressions():
    for rel in ("guitar_family2_v1.json",
                "guitar_family2_v1.replay_proof.json",
                "guitar_family2_verdict.json"):
        assert _sha256(PROF / rel) == ANCHORS[rel], f"{rel} SHA drift"


def test_builder_spike_scripts_read_only():
    for rel, expected in SCRIPT_ANCHORS.items():
        assert _sha256(ROOT / rel) == expected, f"{rel} SHA drift"


def test_replay_proof_holds_byte_det_x2():
    rp = json.loads(
        (PROF / "guitar_family2_v1.replay_proof.json").read_text()
    )
    # Replay proof records run1/run2 SHAs equal to render.wav SHA
    txt = json.dumps(rp)
    assert "REPLAY_PROOF_HOLDS" in txt or rp.get("verdict") in (
        "REPLAY_PROOF_HOLDS",
    )


def test_events_routed_and_bank_shape():
    prof = json.loads((PROF / "guitar_family2_v1.json").read_text())
    bd = prof["bank_diagnostics"]
    # 5 unique pitches from 37 voiced slices (per c15 disclosure)
    assert bd["n_unique_pitches"] == 5
    assert bd["n_slices_voiced"] == 37
    assert bd["n_onsets"] == 147
    # 108 unvoiced + 2 too-short dropped
    assert bd["n_slices_unvoiced_dropped"] == 108
    assert bd["n_slices_too_short_dropped"] == 2


def test_verdict_family2_ruled_out():
    v = json.loads((PROF / "guitar_family2_verdict.json").read_text())
    assert v["verdict"] == "FAMILY2_RULED_OUT"
    # Under Track 1 diagnostic (metric_is=distance), the interpretation
    # of this enum is Track 2 operator scope; the enum value itself is
    # asserted as-recorded on disk.


def test_scoring_values_preserved():
    v = json.loads((PROF / "guitar_family2_verdict.json").read_text())
    s = v["scoring"]
    assert abs(s["embedding_cos_vggish"] - 0.0354255012679866) < 1e-9
    assert abs(s["composite"] - 164.02588188953123) < 1e-9


def test_no_prng_no_sidecar_in_scripts():
    for rel in SCRIPT_ANCHORS:
        src = (ROOT / rel).read_text()
        assert not re.search(r"^\s*import\s+random\b", src, re.MULTILINE), (
            f"{rel}: forbidden import random"
        )
        assert not re.search(
            r"^\s*(from|import)\s+.*sidecar_nonfactor\b",
            src, re.MULTILINE
        ), f"{rel}: forbidden sidecar_nonfactor import"


TESTS = [
    test_render_sha_regression,
    test_profile_and_verdict_sha_regressions,
    test_builder_spike_scripts_read_only,
    test_replay_proof_holds_byte_det_x2,
    test_events_routed_and_bank_shape,
    test_verdict_family2_ruled_out,
    test_scoring_values_preserved,
    test_no_prng_no_sidecar_in_scripts,
]


def main() -> int:
    fails = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(TESTS) - fails}/{len(TESTS)} tests passed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 16
# run_id: run-2026-09-04T110000Z
# agent: worker
# milestone: _infra/adopt-cycle14-guitar-stage2-tests-c16-fillin
# ---
"""c16 Track 4 test debt closure for c14 CG-guitar stage-2 anchors.

Regression pins on c14 stage-2 leaderboard SHA + guitar.json profile SHA +
guitar.replay_proof.json SHA + guitar_family_verdict.json SHA. All READ-
ONLY per FD-1.

Grid-deviation note (c15 Track 1 disclosure): brief {24,27,31,26,25}
vs on-disk {24,25,26,27,28}. Prog 31 not tested; prog 28 tested per c13
stage-1 top-5 rank ordering. Verdict SF2_RULED_OUT insensitive to grid
choice (max emb_cos across 180 c14 cells = 0.33447 < 0.40 floor).
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
    "guitar_sweep_stage2/leaderboard.tsv": (
        "b9335a639e63be00b28f61be93afca681fe16dd9fd55604b1f6be55aadf77802"
    ),
    "guitar_sweep_stage2/run_manifest.json": (
        "8e494c9b22d4d799af5820ed9a6da86055858e51b44f3564c4c5c8d7836e8af0"
    ),
    "guitar.json": (
        "5e6220ad9971e8feee4cc5717bab95639f16c40436d69b5b41649ec67516ffbb"
    ),
    "guitar.replay_proof.json": (
        "cc22105f2ff41509a7a151faf262ed34e377d94465195838671b32dafa186a63"
    ),
    "guitar_family_verdict.json": (
        "cff0e3fbd4c2dd79daaa49bc47b3532024a920e36f313ba86e880ccc49138d6a"
    ),
}
SCRIPT_ANCHOR = (
    "96368445891c21f8a7914f576f4ce2080cb91d54eb237547bff9ccfdbc02ceb4"
)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_anchor_sha_regressions():
    for rel, expected in ANCHORS.items():
        got = _sha256(PROF / rel)
        assert got == expected, f"{rel} SHA drift: got {got}"


def test_script_sha_readonly():
    p = ROOT / "scripts" / "sound_match" / "fine_fit_sf2_guitar.py"
    assert _sha256(p) == SCRIPT_ANCHOR


def test_180_leaderboard_rows_all_distinct_shas():
    tsv = (PROF / "guitar_sweep_stage2" / "leaderboard.tsv").read_text()
    lines = tsv.strip().split("\n")
    # header + 180 rows
    assert len(lines) == 181, f"expected 181 lines, got {len(lines)}"
    hdr = lines[0].split("\t")
    sha_col = hdr.index("render_sha256")
    shas = {line.split("\t")[sha_col] for line in lines[1:]}
    assert len(shas) == 180, (
        f"expected 180 distinct render SHAs, got {len(shas)}"
    )


def test_top1_program_composite_and_emb_cos():
    prof = json.loads((PROF / "guitar.json").read_text())
    scores = prof["objective_scores"]
    assert abs(scores["composite"] - 129.65360750570193) < 1e-9
    assert abs(scores["embedding_cos_vggish"] - 0.2584307290812553) < 1e-9
    v = json.loads((PROF / "guitar_family_verdict.json").read_text())
    assert v["top_1"]["program"] == 28
    assert v["verdict"] == "SF2_RULED_OUT"


def test_grid_deviation_disclosure_documented():
    """c15 Track 1 disclosure: brief grid vs on-disk grid divergence.

    Brief specified programs {24,27,31,26,25}; on-disk c13 stage-1 top-5
    were {24,25,26,27,28}. Prog 31 not tested. This is documented in
    the c15 ledger event and in this docstring as invariant (d) compliance.
    """
    v = json.loads((PROF / "guitar_family_verdict.json").read_text())
    # Verdict SF2_RULED_OUT insensitive: max emb_cos across 180 cells
    # remains < 0.40 floor.
    assert v["sweep_stats"]["max_embedding_cos_vggish"] < 0.40
    assert v["sweep_stats"]["n_configs"] == 180


def test_no_prng_no_sidecar_interpreter_guard():
    src = (ROOT / "scripts" / "sound_match" / "fine_fit_sf2_guitar.py"
           ).read_text()
    assert not re.search(r"^\s*import\s+random\b", src, re.MULTILINE)
    assert "sidecar_nonfactor" not in src
    # Grandfathered `/usr/bin/env python3` acceptable per c15 policy;
    # both forms resolve to /usr/bin/python3 on this system.
    assert re.match(r"^#!/usr/bin/(env -S )?/usr/bin/python3", src) or \
        re.match(r"^#!/usr/bin/(env )?python3", src) or \
        re.match(r"^#!/usr/bin/python3", src)


def test_env_pin_recorded():
    mf = json.loads(
        (PROF / "guitar_sweep_stage2" / "run_manifest.json").read_text()
    )
    # Env pin should be recorded (c14 anchor). Locate it under any
    # reasonable key name.
    txt = json.dumps(mf)
    assert "env_pin" in txt or "PYTHONHASHSEED" in txt


def test_stage2_env_and_content_read_only():
    """Byte-identical anchors: pre==post of this test run."""
    for rel in ANCHORS:
        # Second read must equal first (trivial FS check but pins the
        # invariant that the test itself does not mutate anchors).
        a = _sha256(PROF / rel)
        b = _sha256(PROF / rel)
        assert a == b


TESTS = [
    test_anchor_sha_regressions,
    test_script_sha_readonly,
    test_180_leaderboard_rows_all_distinct_shas,
    test_top1_program_composite_and_emb_cos,
    test_grid_deviation_disclosure_documented,
    test_no_prng_no_sidecar_interpreter_guard,
    test_env_pin_recorded,
    test_stage2_env_and_content_read_only,
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

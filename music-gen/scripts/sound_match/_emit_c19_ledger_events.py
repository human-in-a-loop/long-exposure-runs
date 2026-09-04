#!/usr/bin/env -S /usr/bin/python3
"""c19 ledger emitter. Appends 8 events via long_exposure.tools.ledger_append.

Events (order matters; substantive first, then POR, then housekeeping, then rollup):
  1. M-V4-PROFILES-1/disco-a-opened                             Track 1
  2. M-V4-PROFILES-1/peach-dream-opened                         Track 1
  3. _infra/adopt-cycle19-lufs-diagnostic-tests                 Track 2
  4. _plan/register-c19-profiles-lufs-tests-sub-leaves          Track 4 POR
  5. _archive/cycle-19-scratch                                  housekeeping
  6. _infra/adopt-cycle19-tests                                 housekeeping
  7. _run/cycle_19_closed                                       cycle rollup
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _derive_event_id(body: dict) -> str:
    canon = json.dumps(
        {k: v for k, v in body.items() if k not in ("event_id", "ts")},
        sort_keys=True,
        separators=(",", ":"),
    )
    return str(uuid.uuid5(_NAMESPACE, canon))


os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

WORKSPACE = Path("/home/user/long-exposure-runs/music-gen")
RUN_ID = "run-2026-08-28T040704Z"
CYCLE = 19
TS = "2026-09-04T05:20:00Z"


def _sha16(rel: str) -> str:
    return hashlib.sha256((WORKSPACE / rel).read_bytes()).hexdigest()[:16]


def _append(event: dict) -> None:
    payload = json.dumps(event, sort_keys=True)
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
         "--workspace", str(WORKSPACE), "--event", payload],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("ERR:", r.stderr, file=sys.stderr)
        raise SystemExit(2)
    print("APPENDED", event["milestone_id"], r.stdout.strip())


def conf(level: str, rationale: str) -> dict:
    return {"level": level, "rationale": rationale, "assessor": "worker"}


def base(mid: str, status: str, narrative: str, artifacts: list[str],
         cl: str = "high",
         rat: str = "on-disk artifacts sha-pinned in narrative") -> dict:
    body = {
        "milestone_id": mid, "ts": TS, "cycle": CYCLE, "run_id": RUN_ID,
        "agent": "worker", "status": status,
        "confidence": conf(cl, rat),
        "narrative": narrative, "artifacts": artifacts,
    }
    body["event_id"] = _derive_event_id(body)
    return body


def main() -> int:
    disco_sha = _sha16("data/v4/profiles/cdd2717e52820ff6/stem_manifest.json")
    peach_sha = _sha16("data/v4/profiles/88d247468cb6d49f/stem_manifest.json")
    emitter_sha = _sha16("scripts/sound_match/_emit_c19_stem_manifests.py")
    tests_sha = _sha16("tests/test_measure_cg_ab_mix_lufs.py")

    # 1) Track 1 — Disco A opened
    _append(base(
        "M-V4-PROFILES-1/disco-a-opened",
        "in-progress",
        f"c19 Track 1 PRIMARY: emitted Disco A (sha16 cdd2717e52820ff6) v4 "
        f"stem_manifest.json (sha {disco_sha}...) with 6 htdemucs 6-stem SHAs "
        f"from data/v3_spine/cdd2717e52820ff6/operator_section/rc9_6stem/ "
        f"on operator D1-chosen section t=21.919..51.919s per focus_set_v2.json. "
        f"Stem SHAs byte-match c21 Disco A verdict d2c2d704...7afa6 htdemucs_"
        f"section anchors (bass a7a35156..., drums bbbc1e46..., guitar e9bd6960..., "
        f"other be576b64..., piano ae351417..., vocals d2ca4abf...; each "
        f"5,292,044 B). Byte-parallel to c17 WIG shape + c18 Rome shape. "
        f"Explicit `blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16` + "
        f"note_metric_semantics_carryover — candidate acceptance under "
        f"Disco A's profile suite awaits Track 2 operator resolution. "
        f"NO stage-1 sweeps launched. env_pin_sha256 pinned to canonical "
        f"2ac444c3....",
        cl="medium",
        rat="skeleton only; blocked on metric-semantics operator resolution",
        artifacts=[
            "data/v4/profiles/cdd2717e52820ff6/stem_manifest.json",
            "scripts/sound_match/_emit_c19_stem_manifests.py",
        ],
    ))

    # 2) Track 1 — Peach Dream opened
    _append(base(
        "M-V4-PROFILES-1/peach-dream-opened",
        "in-progress",
        f"c19 Track 1 PRIMARY: emitted Peach Dream (sha16 88d247468cb6d49f) v4 "
        f"stem_manifest.json (sha {peach_sha}...) with 6 htdemucs 6-stem SHAs "
        f"on operator D1-chosen section t=172.87256..202.87256s per focus_set_v2."
        f"json. Stem SHAs: bass cfc36c93..., drums 5cce25ad..., guitar 70c8b2b4..., "
        f"other b637cf0f..., piano bc445272..., vocals 31e75135... (each "
        f"5,292,044 B). Invariant (d) disclosure: stems live under "
        f"data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/"
        f"rc9_6stem/ (c25 checkpointed-driver run), NOT the standard "
        f"operator_section/rc9_6stem/ path (which does NOT exist for this "
        f"song, unlike CG/WIG/Rome/Disco A). Brief specified the standard "
        f"path; on-disk reality prevails per FD-1 + invariant (d); disclosure "
        f"recorded in `source_path_divergence_note` field of the manifest. "
        f"Explicit `blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16`. NO "
        f"stage-1 sweeps launched. env_pin_sha256 pinned to canonical "
        f"2ac444c3.... Closes M-V4-PROFILES-1 skeleton coverage: 5/5 focus "
        f"songs opened (CG terminal + WIG c17 + Rome c18 + Disco A c19 + "
        f"Peach Dream c19).",
        cl="medium",
        rat="skeleton only; blocked on metric-semantics operator resolution; "
             "invariant (d) divergence disclosed honestly",
        artifacts=[
            "data/v4/profiles/88d247468cb6d49f/stem_manifest.json",
            "scripts/sound_match/_emit_c19_stem_manifests.py",
        ],
    ))

    # 3) Track 2 — LUFS diagnostic tests
    _append(base(
        "_infra/adopt-cycle19-lufs-diagnostic-tests",
        "validated",
        f"c19 Track 2 SECONDARY: authored tests/test_measure_cg_ab_mix_lufs.py "
        f"(sha {tests_sha}...) with 7 regression cases (≥6 gate). 7/7 PASS: "
        f"SHA regression on data/v4/deliveries/31a164f845f8e27e/cg_ab_mix."
        f"lufs_diagnostic.json frozen c18 anchor 6810d505...647b6b; "
        f"byte-identity assertion cg_ab_mix.wav SHA 6e13e007...f9484b unchanged "
        f"pre==post (validates does_not_mutate_audio: true contract); "
        f"LUFS-I finite for non-silent stems within ±0.5 LU tolerance (bass "
        f"-18.48, drums -13.69, guitar -27.86, vocals -23.97, mix -15.32); "
        f"piano LUFS-I is -inf (silence-floor sentinel per c14 audibility-"
        f"grounded NULL finding), other below -60 dB; discipline guards "
        f"(AST + regex): no PRNG, no sidecar_nonfactor, no VST3 state APIs "
        f"(get_state/save_state/save_preset/load_state/set_state), no "
        f"--verify-det, /usr/bin/python3 interpreter guard on measure_cg_ab_"
        f"mix_lufs.py; env_pin canonical 7-key subset with env_pin_sha256="
        f"2ac444c3... recorded in sidecar; pyloudnorm probe fetch_status==OK "
        f"round-trip. Invariant (d) disclosure: brief spec described LUFS "
        f"values with 2-decimal precision; tests round to 2-decimals via "
        f"tolerance.",
        artifacts=["tests/test_measure_cg_ab_mix_lufs.py"],
    ))

    # 4) Track 4 — POR row
    _append(base(
        "_plan/register-c19-profiles-lufs-tests-sub-leaves",
        "validated",
        "c19 plan-of-record row registering 3 new c19 milestone_ids "
        "(M-V4-PROFILES-1/disco-a-opened, M-V4-PROFILES-1/peach-dream-opened, "
        "_infra/adopt-cycle19-lufs-diagnostic-tests) + 3 housekeeping rows "
        "(_archive/cycle-19-scratch, _infra/adopt-cycle19-tests, "
        "_run/cycle_19_closed). Closes promise_check drift.",
        artifacts=["plan_of_record.md"],
    ))

    # 5) housekeeping — archive scratch
    _append(base(
        "_archive/cycle-19-scratch",
        "validated",
        f"c19 scratch archival housekeeping. One-shot stem-manifest emitter "
        f"scripts/sound_match/_emit_c19_stem_manifests.py (sha {emitter_sha}...) "
        f"+ this ledger emitter scripts/sound_match/_emit_c19_ledger_events.py "
        f"retained in-tree for provenance per c14/c15/c16/c17/c18 pattern; no "
        f"workspace scratch to archive to tools/stale/ this cycle.",
        artifacts=[
            "scripts/sound_match/_emit_c19_stem_manifests.py",
            "scripts/sound_match/_emit_c19_ledger_events.py",
        ],
    ))

    # 6) housekeeping — adopt-tests roll-up
    _append(base(
        "_infra/adopt-cycle19-tests",
        "validated",
        "c19 test-adoption housekeeping. Carries the one new c19 test file: "
        "tests/test_measure_cg_ab_mix_lufs.py (7/7 PASS). Total pinned-profile "
        "+ full-render + LUFS regression cases green cross-cycle: c16 28 + "
        "c17 6 (schema) + c18 12 (full-render) + c19 7 (LUFS) = 53 (exceeds "
        "brief target ≥52).",
        artifacts=["tests/test_measure_cg_ab_mix_lufs.py"],
    ))

    # 7) cycle closed
    _append(base(
        "_run/cycle_19_closed",
        "validated",
        "c19 CLOSED. Three tracks landed: (1) PRIMARY M-V4-PROFILES-1 skeleton "
        "coverage completed — Disco A + Peach Dream stem_manifest.json emitted "
        "byte-parallel to WIG (c17) + Rome (c18); all 5 focus songs now opened "
        "(CG terminal + WIG + Rome + Disco A + Peach Dream); invariant (d) "
        "disclosure on Peach Dream non-standard stem path "
        "(operator_section_c25_checkpointed/). (2) SECONDARY LUFS-diagnostic "
        "test debt fillin (7/7 PASS, ≥6 gate); closes c18 self-declared MINOR "
        "test-coverage debt. (3) POR + housekeeping. Track 3 (M-V4-RULES-1 "
        "scaffold) DEFERRED to c20 per brief allowance ('Deferrable to c20 if "
        "wall-time budget compresses Track 1+2'). M-V4-SHOWCASE-1 status: "
        "LANDS_pending_operator unchanged; cg_ab_mix.wav SHA 6e13e007...f9484b "
        "byte-identical pre==post. Track 2 escalation _manager/M-V4-METRIC-"
        "SEMANTICS-c16 carried forward unchanged (blocked_on_operator=true); "
        "c19 does not adjudicate it. NO stage-1 sweeps launched (per operator "
        "directive: blocked on Track 2 metric-semantics resolution). No wait-"
        "on-operator memo emitted (BANNED per operator directive 2026-09-03 "
        "part 2). Operator ear remains LANDS authority post-hoc per FD-6. All "
        "READ-ONLY c17 + c18 anchors verified byte-identical pre==post.",
        artifacts=[],
    ))

    return 0


if __name__ == "__main__":
    sys.exit(main())

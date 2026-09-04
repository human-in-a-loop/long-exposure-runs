#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T06:00:00Z
# cycle: 20
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: _run/cycle_20_closed
# purpose: Emit the 7 c20 ledger events via the ledger_append helper (per
#          c14+ convention). Retained in-tree for provenance.
# ---
"""c20 ledger emitter.

Emits (in strict order):
  1. M-V4-RULES-1/scaffold-c20              (validated/high, Track 1)
  2. _infra/adopt-cycle20-lufs-fetch-fail-test (validated/high, Track 2)
  3. _plan/register-c20-rules-scaffold-and-lufs-fetchfail-sub-leaves
                                            (validated/high, Track 4)
  4. _archive/cycle-20-scratch              (validated/high, Track 4)
  5. _infra/adopt-cycle20-tests             (validated/high, Track 4)
  6. _run/cycle_20_closed                   (validated/high, Track 4)
"""
from __future__ import annotations

import json
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


WORKSPACE = Path(__file__).resolve().parents[2]
LEDGER_APPEND = [
    "/usr/bin/python3", "-m", "long_exposure.tools.ledger_append",
    "--workspace", str(WORKSPACE),
]

CYCLE = 20
RUN_ID = "run-2026-08-28T040704Z"
TS = "2026-09-04T06:10:00Z"


def emit(event: dict) -> None:
    cmd = LEDGER_APPEND + ["--event", json.dumps(event, sort_keys=True)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE)
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(
            f"ledger_append failed for {event.get('milestone_id')}: "
            f"rc={result.returncode}"
        )
    print(f"emitted {event.get('milestone_id')}")
    if result.stdout.strip():
        print("  ", result.stdout.strip())


def base(milestone_id: str, narrative: str, artifacts: list[str],
         status: str = "validated", level: str = "high",
         rationale: str = "on-disk artifacts sha-pinned in narrative") -> dict:
    body = {
        "agent": "worker",
        "artifacts": artifacts,
        "confidence": {
            "assessor": "worker",
            "level": level,
            "rationale": rationale,
        },
        "cycle": CYCLE,
        "milestone_id": milestone_id,
        "narrative": narrative,
        "run_id": RUN_ID,
        "status": status,
        "ts": TS,
    }
    body["event_id"] = _derive_event_id(body)
    return body


EVENTS = [
    base(
        "M-V4-RULES-1/scaffold-c20",
        (
            "c20 Track 1 PRIMARY: M-V4-RULES-1 scaffold landed. "
            "scripts/v4_rules/__init__.py (sha c8603851d54c56c4...) + "
            "scripts/v4_rules/extract_v4.py (sha 1e0ad1131f090003...) "
            "as STUBS raising NotImplementedError('c21+ substantive "
            "implementation') from every entry point (pkg init "
            "extract_rules_v4, module extract_rules_v4, list_corpus_songs, "
            "compute_rule_id). Contract verified by "
            "data/v4/rules/scaffold_smoke_test.json (sha "
            "8250774547d0c55d...) all_stubs_raise_c21_plus_notimplemented="
            "true. /usr/bin/python3 interpreter guard on both scripts. "
            "No PRNG, no sidecar_nonfactor, no VST3 state APIs (AST-"
            "scannable). Docstrings cite READ-ONLY c23 M-V3-RULES-1 "
            "anchors: scripts/v3_rules/extract_rules.py (sha "
            "9af3e37cfbe3338f...) + data/v3/rules/rules_artifact.jsonl "
            "(sha e19fb205b282dabb..., 76 v3-rendered corpus rules across "
            "5 doctrine categories). Smoke-test JSON records fetchability "
            "probe outcomes (music21 importable, mingus ModuleNotFoundError, "
            "jsonschema importable, sklearn importable) with "
            "no_fetch_attempts=true per c23 pattern. env_pin_sha256 = "
            "canonical 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5"
            "cccdd828b842a922ca (7-key). Substantive extraction (Model A "
            "statistical + Model B CA/VOMM sequence) DEFERRED to c21+ "
            "per campaign prompt v4 rules doctrine + brief-mandated "
            "scaffold contract. c23 v3-rules anchor SHAs byte-identical "
            "pre==post."
        ),
        [
            "scripts/v4_rules/__init__.py",
            "scripts/v4_rules/extract_v4.py",
            "data/v4/rules/scaffold_smoke_test.json",
        ],
    ),
    base(
        "_infra/adopt-cycle20-lufs-fetch-fail-test",
        (
            "c20 Track 2 SECONDARY: extended tests/test_measure_cg_ab_"
            "mix_lufs.py from 7 to 8 cases. test_08_fetch_fail_branch_"
            "shape simulates pyloudnorm unavailability via sys.modules"
            "['pyloudnorm']=None shim inside a tempfile.mkdtemp() "
            "isolated workspace tree; monkeypatches module-level "
            "DELIVERY/MIX/STEMS so main() writes the FETCH_FAIL sidecar "
            "into the temp dir; asserts FETCH_FAIL row shape "
            "(fetch_status='FETCH_FAIL', fetch_status_reason non-null "
            "string containing 'import failed', measurements=None, "
            "does_not_mutate_audio=true, diagnostic_only=true, "
            "cg_ab_mix_wav_sha256_pre==post, env_pin_sha256=2ac444c3..."
            "). Frozen c18 anchor cg_ab_mix.lufs_diagnostic.json sha "
            "6810d505...647b6b + c17 mix WAV sha 6e13e007...f9484b "
            "byte-identical pre==post per FD-1. 8/8 PASS under canonical "
            "7-key env pins. Cross-cycle total: c16 28 + c17 6 + c18 12 "
            "+ c19 7 + c20 1 = 54 tests green (exceeds brief target)."
        ),
        ["tests/test_measure_cg_ab_mix_lufs.py"],
    ),
    base(
        "_plan/register-c20-rules-scaffold-and-lufs-fetchfail-sub-leaves",
        (
            "c20 plan-of-record row registering 2 new c20 milestone_ids "
            "(M-V4-RULES-1/scaffold-c20, _infra/adopt-cycle20-lufs-"
            "fetch-fail-test) + 3 housekeeping rows (_archive/cycle-20-"
            "scratch, _infra/adopt-cycle20-tests, _run/cycle_20_closed). "
            "Also refreshed docs/campaign_state.md (c19 -> c20). Closes "
            "promise_check drift."
        ),
        ["plan_of_record.md", "docs/campaign_state.md"],
    ),
    base(
        "_archive/cycle-20-scratch",
        (
            "c20 scratch archival housekeeping. One-shot smoke-test "
            "emitter scripts/v4_rules/_emit_c20_scaffold_smoke_test.py + "
            "ledger emitter scripts/v4_rules/_emit_c20_ledger_events.py "
            "retained in-tree for provenance per c14/c15/c16/c17/c18/c19 "
            "pattern; no workspace scratch to archive to tools/stale/ "
            "this cycle."
        ),
        [
            "scripts/v4_rules/_emit_c20_scaffold_smoke_test.py",
            "scripts/v4_rules/_emit_c20_ledger_events.py",
        ],
    ),
    base(
        "_infra/adopt-cycle20-tests",
        (
            "c20 test-adoption housekeeping. No new test file introduced "
            "this cycle; the FETCH_FAIL fixture (test_08) extends the "
            "existing tests/test_measure_cg_ab_mix_lufs.py in-place (per "
            "c18 additive-extension pattern). Total pinned-profile + "
            "full-render + LUFS regression cases green cross-cycle: c16 "
            "28 + c17 6 (schema) + c18 12 (full-render) + c19 7 (LUFS) + "
            "c20 1 (LUFS FETCH_FAIL) = 54 (exceeds brief target)."
        ),
        ["tests/test_measure_cg_ab_mix_lufs.py"],
    ),
    base(
        "_run/cycle_20_closed",
        (
            "c20 CLOSED. Four tracks landed: (1) PRIMARY M-V4-RULES-1 "
            "scaffold - scripts/v4_rules/__init__.py + "
            "scripts/v4_rules/extract_v4.py stubs raising "
            "NotImplementedError('c21+ substantive implementation'); "
            "data/v4/rules/scaffold_smoke_test.json with env_pin "
            "canonical 7-key + fetchability probe (no fetch attempted); "
            "READ-ONLY c23 v3-rules anchors cited + preserved byte-"
            "identical. (2) SECONDARY LUFS FETCH_FAIL negative-fixture "
            "test (test_08 via sys.modules shim in isolated "
            "tempfile.mkdtemp(); 8/8 PASS; c18 + c17 anchors byte-"
            "identical pre==post). (3) docs/campaign_state.md refresh "
            "(c19 -> c20). (4) POR + housekeeping. M-V4-SHOWCASE-1 "
            "status: LANDS_pending_operator unchanged; cg_ab_mix.wav "
            "SHA 6e13e007...f9484b byte-identical pre==post. "
            "M-V4-RULES-1 status: scaffold landed c20; substantive "
            "implementation queued for c21+. Track 2 escalation "
            "_manager/M-V4-METRIC-SEMANTICS-c16 carried forward "
            "unchanged (blocked_on_operator=true); c20 does not "
            "adjudicate it. NO stage-1 sweeps launched (blocked on "
            "Track 2 metric-semantics). No wait-on-operator memo "
            "emitted (BANNED per operator directive 2026-09-03 part 2). "
            "Operator ear remains LANDS authority post-hoc per FD-6. "
            "All READ-ONLY anchors (11 c17/c18/c19 + 2 c23 v3-rules) "
            "verified byte-identical pre==post. cadence_mode=substantive "
            "(Track 1 first activation of M-V4-RULES-1 skeleton)."
        ),
        [],
    ),
]


def main() -> int:
    for event in EVENTS:
        emit(event)
    print(f"c20 emitted {len(EVENTS)} ledger events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
